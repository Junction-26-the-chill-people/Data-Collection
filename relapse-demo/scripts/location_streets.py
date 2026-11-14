"""Generate bounded offline public street context from the existing OSM extract."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];src=ROOT/'data/map-source/helsinki-esplanadi.osm'
xml=ET.parse(src).getroot();nodes={n.attrib['id']:[float(n.attrib['lon']),float(n.attrib['lat'])] for n in xml.findall('node')};bbox=[24.945,60.166,24.953,60.169]
def inside(p):return bbox[0]<=p[0]<=bbox[2] and bbox[1]<=p[1]<=bbox[3]
features=[]
for w in xml.findall('way'):
 tags={t.attrib['k']:t.attrib['v'] for t in w.findall('tag')}
 ids=[n.attrib['ref'] for n in w.findall('nd')]
 coords=[nodes[i] for i in ids if i in nodes]
 kind='building' if tags.get('building') not in (None,'no') else 'park' if tags.get('leisure') in ['park','garden'] or tags.get('landuse') in ['grass','recreation_ground'] or tags.get('natural') in ['wood','scrub','grassland'] else None
 if kind and len(coords)>=4 and coords[0]==coords[-1] and all(inside(c) for c in coords):
  features.append({'type':'Feature','properties':{'osmWayId':w.attrib['id'],'kind':kind,'name':tags.get('name','')},'geometry':{'type':'Polygon','coordinates':[coords]}})
 if 'highway' not in tags or tags.get('access') in ['private','no'] or tags.get('area')=='yes':continue
 ids=[n.attrib['ref'] for n in w.findall('nd')];part=[]
 for node in ids+[None]:
  coord=nodes.get(node)
  if coord is not None and inside(coord):part.append(coord)
  else:
   if len(part)>1:features.append({'type':'Feature','properties':{'osmWayId':w.attrib['id'],'kind':'road','highway':tags['highway'],'name':tags.get('name','')},'geometry':{'type':'LineString','coordinates':part}})
   part=[]
geo={'type':'FeatureCollection','bbox':bbox,'features':features,'source':{'provider':'OpenStreetMap','attribution':'© OpenStreetMap contributors','license':'ODbL-1.0','url':'https://www.openstreetmap.org/copyright','extractUrl':'https://api.openstreetmap.org/api/0.6/map?bbox=24.945,60.166,24.953,60.169','sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'notice':'Real mapped street geometry; personal traces in the demo are simulated.'}}
text=json.dumps(geo,separators=(',',':'),ensure_ascii=False)
(ROOT/'data/map-streets.geojson').write_text(text,encoding='utf-8');(ROOT/'data/map-streets.js').write_text('window.MAP_STREETS='+text+';\n',encoding='utf-8')
print({k:sum(f['properties']['kind']==k for f in features) for k in ['road','building','park']})
print('Features',len(features),'vertices',sum(len(f['geometry']['coordinates']) for f in features),'bytes',len(text.encode()))
