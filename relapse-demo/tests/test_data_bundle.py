"""Reproducibility and provenance tests for the synthetic + full real bundle."""
import hashlib,importlib.util,json,math,unittest
from datetime import datetime
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('bundle',ROOT/'scripts/build_demo_bundle.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
class BundleTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.people=builder.generate()
 def test_fixed_seed_reproduces_exact_values(self):
  self.assertEqual(self.people,builder.generate())
 def test_synthetic_provenance_ranges_and_routes(self):
  people=self.people;self.assertEqual(len(people),11)
  for p in people:
   self.assertTrue(p['synthetic']);self.assertEqual(len(p['records']),120);self.assertEqual(p['baselineIndices'],list(range(28)))
   for r in p['records']:
    self.assertTrue(r['synthetic']);self.assertEqual(r['participantId'],p['id']);self.assertEqual(r['subjectId'],p['id']);self.assertEqual(r['dayKey'],p['id']+':'+r['date']);self.assertEqual(r['timeZone'],p['timeZone'])
    for m in p['metrics']:
     v=r['values'][m['id']]
     if v is not None:
      self.assertTrue(math.isfinite(v));self.assertGreaterEqual(v,m['min'])
      if 'max' in m:self.assertLessEqual(v,m['max'])
    if r['missingPeriod']:self.assertTrue(all(v is None for v in r['values'].values()));self.assertIsNone(r['route']);self.assertEqual(r['trips'],[]);self.assertEqual(r['visits'],[])
    else:
     for trip in r['trips']:
      points=trip['points'];self.assertGreaterEqual(len(points),2)
      self.assertGreater(trip['durationSeconds'],0)
      self.assertLessEqual(trip['distanceMeters']/trip['durationSeconds'],1.46)
      for first,second in zip(points,points[1:]):
       elapsed=(datetime.fromisoformat(second['timestamp'])-datetime.fromisoformat(first['timestamp'])).total_seconds()
       self.assertGreaterEqual(elapsed,0)
       self.assertEqual(first['tripId'],second['tripId'])
       self.assertLessEqual(builder.haversine(first,second),1.46*elapsed+.02)
     for before,after in zip(r['trips'],r['trips'][1:]):
      self.assertLessEqual(datetime.fromisoformat(before['endedAt']),datetime.fromisoformat(after['startedAt']))
     distance=sum(t['distanceMeters'] for t in r['trips'])
     self.assertLessEqual(distance,r['values']['steps']*.72+.1)
     away=sum(t['durationSeconds'] for t in r['trips'])+sum((datetime.fromisoformat(v['departedAt'])-datetime.fromisoformat(v['arrivedAt'])).total_seconds() for v in r['visits'])
     self.assertLessEqual(away/3600,24-r['values']['home_hours']+.01)
 def test_routes_follow_published_street_nodes_and_edges(self):
  from personal_places import ALLOWED
  for index,p in enumerate(self.people):
   osm=ET.parse(ROOT/f'data/map-source/neighborhood-{index+1:02}.osm').getroot()
   nodes={n.attrib['id']:(float(n.attrib['lat']),float(n.attrib['lon'])) for n in osm.findall('node')};edges=set()
   for way in osm.findall('way'):
    tags={t.attrib['k']:t.attrib['v'] for t in way.findall('tag')}
    if tags.get('highway') not in ALLOWED or tags.get('access') in ['private','no'] or tags.get('foot')=='no' or tags.get('area')=='yes':continue
    ids=[x.attrib['ref'] for x in way.findall('nd')]
    for a,b in zip(ids,ids[1:]):edges.add((a,b));edges.add((b,a))
   bbox=p['mapGeometrySource']['bbox'];places={place['id']:place for place in p['places']}
   for place in places.values():self.assertTrue(bbox[0]<=place['lon']<=bbox[2] and bbox[1]<=place['lat']<=bbox[3])
   for record in p['records']:
    for trip in record['trips']:
     for point in trip['points']:
      self.assertEqual((point['lat'],point['lon']),nodes[point['osmNodeId']]);self.assertTrue(bbox[0]<=point['lon']<=bbox[2] and bbox[1]<=point['lat']<=bbox[3])
     for a,b in zip(trip['points'],trip['points'][1:]):self.assertIn((a['osmNodeId'],b['osmNodeId']),edges)
     for endpoint,key in [(trip['points'][0],'fromPlaceId'),(trip['points'][-1],'toPlaceId')]:self.assertEqual((endpoint['lat'],endpoint['lon']),(places[trip[key]]['lat'],places[trip[key]]['lon']))
 def test_distinct_neighborhoods_preserve_original_health(self):
  homes=[next((p['lat'],p['lon']) for p in person['places'] if p['id']=='home') for person in self.people]
  self.assertEqual(len(set(homes)),11)
  original=json.loads((ROOT/'tests/fixtures/pre-1.5-health-hashes.json').read_text())
  for person in self.people[:10]:
   values=json.dumps([r['values'] for r in person['records']],sort_keys=True,separators=(',',':'))
   protected=json.dumps({'phases':person['phases'],'records':[{k:v for k,v in r.items() if k not in ['trips','visits','locationTimeline','route','movementSummary']} for r in person['records']]},sort_keys=True,separators=(',',':'))
   identity=json.dumps({k:v for k,v in person.items() if k not in ['records','places','mapGeometrySource','routeProvenance']},sort_keys=True,separators=(',',':'))
   self.assertEqual(hashlib.sha256(identity.encode()).hexdigest(),original[person['id']]['identitySha256'])
   self.assertEqual(hashlib.sha256(values.encode()).hexdigest(),original[person['id']]['valuesSha256'])
   self.assertEqual(hashlib.sha256(protected.encode()).hexdigest(),original[person['id']]['protectedSha256'])
  for i in range(11):self.assertLess((ROOT/f'data/neighborhood-{i+1:02}.js').stat().st_size,2_000_000)
 def test_personal_locations_follow_story_phases(self):
  for index in [1,7,10]:
   person=self.people[index];early=person['records'][:28];late=person['records'][95:]
   destinations=lambda records:{v['placeId'] for r in records for v in r['visits']}
   mean_visits=lambda records:sum(len(r['visits']) for r in records)/len(records)
   mean_distance=lambda records:sum(r['movementSummary']['mappedWalkingMeters'] or 0 for r in records)/len(records)
   self.assertLess(len(destinations(late)),len(destinations(early)))
   self.assertLess(mean_visits(late),mean_visits(early));self.assertLess(mean_distance(late),mean_distance(early))
  oskar=self.people[3]
  usual={v['placeId'] for r in oskar['records'][:28] for v in r['visits']}
  travel={v['placeId'] for r in oskar['records'][49:85] for v in r['visits']}
  self.assertTrue(travel);self.assertTrue(usual.isdisjoint(travel))
 def test_contexts_are_explicit_and_synthetic_only(self):
  people=self.people
  illness=people[5];fitness=people[6]
  self.assertEqual([r['periodIndex'] for r in illness['records'] if any(c['type']=='illness' for c in r['contexts'])],list(range(45,66)))
  self.assertEqual([r['periodIndex'] for r in illness['records'] if any(c['type']=='recovery' for c in r['contexts'])],list(range(66,81)))
  self.assertEqual([r['periodIndex'] for r in fitness['records'] if r['contexts']],list(range(41,76)))
  for p in people:
   for r in p['records']:
    for c in r['contexts']:self.assertEqual(c['source'],'synthetic');self.assertIs(c['confirmed'],True)
 def test_complete_generated_day_linkage_and_time_budget(self):
  for p in self.people[8:10]:
   self.assertEqual(p['timeZone'],'UTC');self.assertGreaterEqual(len(p['places']),3);self.assertLessEqual(len(p['places']),5)
   for r in p['records']:
    self.assertEqual(r['subjectId'],p['id']);self.assertEqual(r['participantId'],p['id']);self.assertEqual(r['dayKey'],p['id']+':'+r['date']);self.assertEqual(r['timeZone'],p['timeZone'])
    timeline=r['locationTimeline'];self.assertEqual(r['movementSummary']['scope'],'complete_generated_day')
    self.assertEqual(datetime.fromisoformat(timeline[0]['startedAt']).date().isoformat(),r['date'])
    total=0;home=0
    for index,event in enumerate(timeline):
     start=datetime.fromisoformat(event['startedAt']);end=datetime.fromisoformat(event['endedAt']);duration=(end-start).total_seconds();self.assertGreater(duration,0);total+=duration
     if index:self.assertEqual(timeline[index-1]['endedAt'],event['startedAt'])
     if event['kind']=='stay' and event['placeId']=='home':home+=duration
     if event['kind']=='walk':self.assertIn(event['tripId'],[t['id'] for t in r['trips']])
    self.assertAlmostEqual(total,86400,places=5);self.assertAlmostEqual(home/3600,r['values']['home_hours'],places=3)
    self.assertAlmostEqual(r['movementSummary']['homeSeconds'],home,places=3)
    self.assertAlmostEqual(r['movementSummary']['awaySeconds'],86400-home,places=3)
  bad=self.people[8]['records'][64];next_day=self.people[8]['records'][65]
  self.assertEqual(bad['values']['home_hours'],24);self.assertEqual(bad['trips'],[]);self.assertLess(bad['values']['sleep_hours'],3);self.assertGreater(next_day['values']['sleep_hours'],6);self.assertGreater(len(next_day['trips']),0)
 def test_real_source_rows_retained_without_imputation(self):
  d=json.loads((ROOT/'data/demo-data.json').read_text());real=[p for p in d['participants'] if p.get('datasetId')=='psyche-d'];self.assertEqual(len(real),4948)
  source=json.loads((ROOT/'.tmp/all-records/demo-data.json').read_text());original={p['id']:p['records'] for p in source['participants']}
  ids=[]
  for p in real:
   self.assertEqual(p['records'],original[p['id']],'Research source records must remain byte-value equivalent')
   self.assertFalse(p['synthetic']);self.assertTrue(all(not r.get('contexts') for r in p['records']))
   for r in p['records']:
    if r.get('missingPeriod'):self.assertIsNone(r['sourceRecordId']);self.assertTrue(all(v is None for v in r['values'].values()))
    else:ids.append(r['sourceRecordId'])
  self.assertEqual(len(ids),35694);self.assertEqual(len(set(ids)),35694)
if __name__=='__main__':unittest.main()
