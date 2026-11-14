import importlib.util, json, threading, unittest, urllib.request, urllib.error
from pathlib import Path
from http.server import ThreadingHTTPServer
spec=importlib.util.spec_from_file_location('preview',Path(__file__).resolve().parents[1]/'scripts/preview_server.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
class PreviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.server=ThreadingHTTPServer(('127.0.0.1',0),p.Handler);cls.server.stop_token='local-test-token'
  cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start();cls.base=f'http://127.0.0.1:{cls.server.server_port}'
 @classmethod
 def tearDownClass(cls): cls.server.shutdown();cls.server.server_close();cls.thread.join()
 def request(self,path,headers=None,method='GET'):
  req=urllib.request.Request(self.base+path,headers=headers or {},method=method)
  try: return urllib.request.urlopen(req,timeout=2)
  except urllib.error.HTTPError as exc:return exc
 def test_page_and_referrer_policy(self):
  with self.request('/') as r:
   self.assertEqual(r.status,200);self.assertIn(b'<!doctype html>',r.read().lower());self.assertEqual(r.headers['Referrer-Policy'],'strict-origin-when-cross-origin')
 def test_private_and_traversal_paths_not_exposed(self):
  for path in ['/.tmp/preview-server.json','/.deps/','/../AGENTS.md','/%2e%2e/AGENTS.md','/data/../../AGENTS.md','/data/','/START-DEMO.cmd','/scripts/preview_server.py','/data/%5c..%5c..%5cAGENTS.md']:
   with self.request(path) as r:self.assertEqual(r.status,404,path)
 def test_rebinding_host_rejected(self):
  with self.request('/',{'Host':'attacker.example'}) as r:self.assertEqual(r.status,403)
 def test_shutdown_requires_token(self):
  with self.request('/__within_stop',method='POST') as r:self.assertEqual(r.status,403)
  self.assertTrue(p.health(self.server.server_port))
 def test_known_assets_and_health(self):
  for asset in ['/engine.js','/movement-map.js','/movement-map.css','/vendor/leaflet/leaflet.js','/vendor/leaflet/leaflet.css','/data/map-streets.js']:
   with self.request(asset,method='HEAD') as r:self.assertEqual(r.status,200,asset)
  with self.request('/__within_health') as r:self.assertEqual(json.load(r)['workspace'],p.IDENTITY)
if __name__=='__main__':unittest.main()
