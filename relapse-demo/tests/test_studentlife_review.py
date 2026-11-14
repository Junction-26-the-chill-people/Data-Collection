"""Independent standard-library audit of the paired StudentLife viewer data.

Reads already-decoded CSVs and the generated JSON; never loads RDS or imports
its adapter. Keep these tests independent of transformation implementation.
"""
import csv
import json
import math
import re
import unittest
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'datasets/location_sources/studentlife_zenodo/decoded'


def timestamp(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp()


def day(epoch):
    return datetime.fromtimestamp(float(epoch), timezone.utc).date().isoformat()


def distance(first, second):
    lat1, lat2 = math.radians(first['lat']), math.radians(second['lat'])
    dlat = lat2 - lat1
    dlon = math.radians(second['lon'] - first['lon'])
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 12742000 * math.atan2(math.sqrt(min(1, h)), math.sqrt(max(0, 1 - h)))


def optional_number(value):
    return None if value == '' else float(value)


class StudentLifeIndependentReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = json.loads((ROOT / 'data/studentlife-data.json').read_text(encoding='utf-8'))
        cls.tables = {}
        for name in ['gps', 'PAM', 'Sleep', 'PHQ-9']:
            with (SOURCE / (name + '.csv')).open(encoding='utf-8', newline='') as stream:
                cls.tables[name] = list(csv.DictReader(stream))
        cls.gps = defaultdict(list)
        cls.checks = defaultdict(list)
        cls.questionnaires = defaultdict(list)
        for row in cls.tables['gps']:
            cls.gps[(row['uid'], day(row['timestamp']))].append(row)
        for name in ['PAM', 'Sleep']:
            for row in cls.tables[name]:
                cls.checks[(row['uid'], day(row['timestamp']))].append((name, row))
        for row in cls.tables['PHQ-9']:
            cls.questionnaires[row['uid']].append(row)

    def test_full_source_counts_and_namespaces(self):
        self.assertEqual({k: len(v) for k, v in self.tables.items()},
                         {'gps': 202877, 'PAM': 9040, 'Sleep': 1644, 'PHQ-9': 84})
        people = self.bundle['participants']
        self.assertEqual(len(people), 49)
        self.assertEqual(sum(len(p['records']) for p in people), 3389)
        source_ids = {row['uid'] for row in self.tables['gps']}
        self.assertEqual({p['sourceId'] for p in people}, source_ids)
        self.assertEqual(self.bundle['source']['license'], 'CC-BY-4.0')
        self.assertFalse(self.bundle['source']['synthetic'])
        for person in people:
            self.assertEqual(person['id'], 'studentlife-' + person['sourceId'])
            self.assertFalse(person['synthetic'])

    def test_same_person_utc_day_joins_and_raw_answers(self):
        response_totals = Counter()
        for person in self.bundle['participants']:
            previous_date = None
            for index, record in enumerate(person['records']):
                key = (person['sourceId'], record['date'])
                self.assertEqual(record['participantId'], person['id'])
                self.assertEqual(record['subjectId'], person['id'])
                self.assertEqual(record['dayKey'], person['id'] + ':' + record['date'])
                self.assertEqual(record['timeZone'], 'UTC')
                self.assertEqual(record['periodIndex'], index)
                parsed = datetime.fromisoformat(record['date']).date()
                if previous_date is not None:
                    self.assertEqual(parsed, previous_date + timedelta(days=1))
                previous_date = parsed
                self.assertEqual(record['gpsSummary']['sourcePoints'], len(self.gps[key]))
                expected = sorted(self.checks[key], key=lambda item: float(item[1]['timestamp']))
                self.assertEqual(len(record['checkins']), len(expected))
                for got, (kind, source) in zip(record['checkins'], expected):
                    response_totals[kind] += 1
                    self.assertEqual(got['type'], kind)
                    self.assertEqual(timestamp(got['timestamp']), float(source['timestamp']))
                    self.assertEqual(got['timestamp'][:10], record['date'])
                    if kind == 'PAM':
                        self.assertEqual(got['pictureIndex'], optional_number(source['picture_idx']))
                    else:
                        for output, field in [('rawHourCode', 'hour'), ('rawQualityCode', 'rate'), ('rawSocialCode', 'social')]:
                            self.assertEqual(got[output], optional_number(source[field]))
                        self.assertEqual(got['location'], source['location'] or None)
        self.assertEqual(response_totals, {'PAM': 9040, 'Sleep': 1644})

    def test_displayed_gps_is_unchanged_source_with_quality_limits(self):
        total_points = 0
        for person in self.bundle['participants']:
            for record in person['records']:
                raw = self.gps[(person['sourceId'], record['date'])]
                source_points = {(float(row['timestamp']), float(row['latitude']), float(row['longitude']), float(row['accuracy'])) for row in raw}
                displayed = [point for trip in record['trips'] for point in trip['points']]
                total_points += len(displayed)
                self.assertLessEqual(len(displayed), 80)
                self.assertEqual(len(displayed), record['gpsSummary']['displayedPoints'])
                for point in displayed:
                    self.assertIn((timestamp(point['timestamp']), point['lat'], point['lon'], point['accuracy']), source_points)
                    self.assertTrue(all(math.isfinite(point[k]) for k in ['lat', 'lon', 'accuracy']))
                    self.assertTrue(-90 <= point['lat'] <= 90 and -180 <= point['lon'] <= 180)
                    self.assertTrue(0 <= point['accuracy'] <= 100)
                    self.assertEqual(point['timestamp'][:10], record['date'])
        self.assertEqual(total_points, 172715)

    def test_no_bridges_over_exclusions_gaps_or_speed_jumps(self):
        segments = 0
        singletons = 0
        for person in self.bundle['participants']:
            for record in person['records']:
                raw = sorted(self.gps[(person['sourceId'], record['date'])], key=lambda row: float(row['timestamp']))
                source_segment = {}
                current_segment = 0
                previous = None
                for row in raw:
                    point = {'lat': float(row['latitude']), 'lon': float(row['longitude']), 'accuracy': float(row['accuracy']), 'time': float(row['timestamp'])}
                    valid = all(math.isfinite(value) for value in point.values()) and -90 <= point['lat'] <= 90 and -180 <= point['lon'] <= 180 and 0 <= point['accuracy'] <= 100
                    if not valid:
                        previous = None
                        current_segment += 1
                        continue
                    if previous is not None:
                        elapsed = point['time'] - previous['time']
                        if elapsed <= 0 or elapsed > 1800 or distance(previous, point) / elapsed > 55:
                            current_segment += 1
                    source_segment[(point['time'], point['lat'], point['lon'], point['accuracy'])] = current_segment
                    previous = point
                for trip in record['trips']:
                    segments += 1
                    singletons += len(trip['points']) == 1
                    self.assertEqual(trip['mode'], 'unknown')
                    self.assertEqual(trip['startedAt'], trip['points'][0]['timestamp'])
                    self.assertEqual(trip['endedAt'], trip['points'][-1]['timestamp'])
                    retained_source_segments = set()
                    for point in trip['points']:
                        retained_source_segments.add(source_segment[(timestamp(point['timestamp']), point['lat'], point['lon'], point['accuracy'])])
                    self.assertEqual(len(retained_source_segments), 1)
                    for first, second in zip(trip['points'], trip['points'][1:]):
                        elapsed = timestamp(second['timestamp']) - timestamp(first['timestamp'])
                        self.assertTrue(0 < elapsed <= 1800)
                        self.assertLessEqual(distance(first, second) / elapsed, 55.00001)
        self.assertEqual(segments, 9575)
        self.assertEqual(singletons, 1900)

    def test_sleep_labels_match_preserved_questionnaire_options(self):
        definition = json.loads((SOURCE.parent / 'sleep-codebook.json').read_text(encoding='utf-8'))['definition']
        option_maps = {question['question_id']: {float(code): label.strip() for code, label in re.findall(r'\[(\d+)\]([^,]+)', question['options'])} for question in definition['questions']}
        self.assertEqual(option_maps['hour'][1], '<3')
        self.assertNotIn(0, option_maps['hour'])
        for person in self.bundle['participants']:
            for record in person['records']:
                for check in record['checkins']:
                    if check['type'] != 'Sleep':
                        continue
                    label = option_maps['hour'].get(check['rawHourCode'])
                    self.assertEqual(check['sleepDurationLabel'], label + ' hours' if label else 'Unmapped code')
                    self.assertEqual(check['sleepQualityLabel'], option_maps['rate'].get(check['rawQualityCode'], 'Unmapped code'))
                    self.assertIn('Submission date is not a verified sleep-night date', check['interpretation'])

    def test_health_codes_unscored_and_phq_context_not_daily(self):
        questionnaires = 0
        for person in self.bundle['participants']:
            self.assertEqual(person['metrics'], [])
            self.assertEqual(person['baselineIndices'], [])
            source = self.questionnaires[person['sourceId']]
            self.assertEqual(len(person['questionnaires']), len(source))
            questionnaires += len(source)
            for actual, original in zip(person['questionnaires'], source):
                self.assertEqual(str(actual['uid']), original['uid'])
                self.assertEqual(actual['type'], original['type'])
                for question in ['Q' + str(i) for i in range(1, 11)]:
                    self.assertEqual(actual[question], original[question] or None)
            for record in person['records']:
                self.assertEqual(record['values'], {})
                self.assertNotIn('questionnaires', record)
                self.assertNotIn('labels', record)
                self.assertTrue(all(check['type'] in ['PAM', 'Sleep'] for check in record['checkins']))
                if not record['gpsSummary']['sourcePoints']:
                    self.assertEqual(record['movementStatus'], 'gps_not_recorded')
                    self.assertEqual(record['trips'], [])
        self.assertEqual(questionnaires, 84)


if __name__ == '__main__':
    unittest.main()
