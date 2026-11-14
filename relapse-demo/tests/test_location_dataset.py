"""Source provenance, parser isolation, geometry and temporal integrity tests."""
import ast,csv,hashlib,importlib.util,json,math,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('location_dataset',ROOT/'scripts/location_dataset.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class LocationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.export=json.loads((ROOT/'data/location-samples.json').read_text());cls.full=json.loads((ROOT/'data/location-traces.json').read_text());cls.audit=json.loads((ROOT/'docs/location-dataset-audit.json').read_text())
    def test_publisher_manifest(self):
        manifest=json.loads((mod.RAW.parent.parent/'syn_roadgps_download_manifest.json').read_text())
        for entry in manifest['files']:
            payload=(mod.RAW/entry['file']).read_bytes();self.assertEqual(len(payload),entry['bytes']);self.assertEqual(hashlib.sha256(payload).hexdigest(),entry['sha256'])
            actual=hashlib.sha256(payload).hexdigest() if entry['publisherAlgorithm']=='sha256' else hashlib.sha1(b'blob '+str(len(payload)).encode()+b'\0'+payload).hexdigest()
            self.assertEqual(actual,entry['publisherChecksum'])
    def test_untrusted_calls_never_evaluate(self):
        self.assertEqual(mod.literal('[np.int64(42),np.int64(-3)]',True),[42,-3])
        for attack in ['[__import__("os").system("echo bad")]','[np.int64(__import__("os"))]','[float("nan")]']:
            with self.assertRaises((ValueError,SyntaxError)):mod.literal(attack,True)
    def test_all_corpus_quality_counts(self):
        c=self.audit['counts'];self.assertEqual(c['rows'],10000);self.assertEqual(c['points'],546273);self.assertEqual(c['speedAbove55mpsEdges'],606);self.assertEqual(c['rowsWithSplitEdges'],195);self.assertEqual(c['singlePointRows'],2);self.assertEqual(c['validRows'],10000);self.assertEqual(c['nonIncreasingEdges'],0)
        self.assertEqual(self.audit['roadIdentifierAudit']['pointsWithRoadIdAbsentFromGeometry'],272951)
    def test_source_points_unmodified(self):
        with (mod.RAW/'RoadGPS.csv').open(newline='') as f:
            rows=csv.DictReader(f)
            for trace in self.full['traces']:
                row=next(rows);gps,times,stamps,roads,ratios=mod.parse(row)
                self.assertEqual([(p['lon'],p['lat']) for p in trace['points']],gps)
                self.assertEqual([p['timestamp'] for p in trace['points']],times)
                self.assertEqual(trace,mod.make_trace(trace['sourceRow'],gps,times,stamps,roads,ratios))
    def test_viewer_preserves_every_point_and_break(self):
        self.assertEqual(len(self.export['trajectories']),50)
        for view,full in zip(self.export['trajectories'],self.full['traces']):
            flattened=[p for t in view['record']['trips'] for p in t['points']]
            self.assertEqual(flattened,[{k:p[k] for k in ['lat','lon','timestamp']} for p in full['points']]);self.assertEqual(len(view['record']['trips']),len(full['breaks'])+1)
            for trip in view['record']['trips']:
                self.assertEqual(trip['mode'],'unknown')
                for a,b in zip(trip['points'],trip['points'][1:]):
                    dt=(mod.datetime.fromisoformat(b['timestamp'].replace('Z','+00:00'))-mod.datetime.fromisoformat(a['timestamp'].replace('Z','+00:00'))).total_seconds();self.assertGreater(dt,0);self.assertLessEqual(dt,300);self.assertLessEqual(mod.distance((a['lon'],a['lat']),(b['lon'],b['lat']))/dt,55)
        self.assertTrue(self.export['source']['synthetic']);self.assertIsNone(self.export['source']['clinicalLink']);self.assertEqual(self.export['roads']['features'],[])
    def test_artificial_breaks_retain_points(self):
        trace=mod.make_trace(1,[(0,0),(0,1),(0,1.001),(0,1.002)],['a','b','c','d'],[0,1,1,500],[1]*4,[0]*4)
        self.assertEqual([x['reason'] for x in trace['breaks']],['speed_above_threshold','non_increasing_time','time_gap']);self.assertEqual(len(trace['points']),4);self.assertEqual(trace['drawnChordDistanceMeters'],0)
    def test_offline_context_within_bounds(self):
        geo=json.loads((ROOT/'data/map-streets.geojson').read_text());west,south,east,north=geo['bbox'];kinds={}
        for f in geo['features']:
            kinds[f['properties']['kind']]=kinds.get(f['properties']['kind'],0)+1
            coords=f['geometry']['coordinates']
            if f['geometry']['type']=='Polygon':
                coords=coords[0];self.assertEqual(coords[0],coords[-1]);self.assertGreaterEqual(len(coords),4)
            for lon,lat in coords:self.assertTrue(west<=lon<=east and south<=lat<=north)
        self.assertEqual(kinds,{'road':609,'building':57,'park':18})
if __name__=='__main__':unittest.main()
