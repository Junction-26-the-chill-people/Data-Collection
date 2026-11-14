"""Bundle bounded public OSM vectors for the StudentLife Hanover research view."""
from pathlib import Path
import hashlib,json,urllib.request,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
BBOX=[-72.294,43.699,-72.281,43.708]
URL='https://api.openstreetmap.org/api/0.6/map?bbox='+','.join(map(str,BBOX))
source=ROOT/'data/map-source/hanover.osm'
if not source.exists():
    request=urllib.request.Request(URL,headers={'User-Agent':'Junction26-research-demo/1.0'})
    with urllib.request.urlopen(request,timeout=45) as response:
        payload=response.read(20_000_001)
        if len(payload)>20_000_000:raise ValueError('OSM response exceeds bounded download limit')
        ET.fromstring(payload)
        source.write_bytes(payload)
xml=ET.parse(source).getroot()
nodes={n.attrib['id']:[float(n.attrib['lon']),float(n.attrib['lat'])] for n in xml.findall('node')}
def inside(p):return BBOX[0]<=p[0]<=BBOX[2] and BBOX[1]<=p[1]<=BBOX[3]
features=[]
for w in xml.findall('way'):
    tags={t.attrib['k']:t.attrib['v'] for t in w.findall('tag')}
    ids=[n.attrib['ref'] for n in w.findall('nd')]
    coords=[nodes[i] for i in ids if i in nodes]
    kind='building' if tags.get('building') not in (None,'no') else 'park' if tags.get('leisure') in ['park','garden'] or tags.get('landuse') in ['grass','recreation_ground'] or tags.get('natural') in ['wood','scrub','grassland'] else None
    if kind and len(coords)>=4 and coords[0]==coords[-1] and all(inside(c) for c in coords):
        features.append({'type':'Feature','properties':{'osmWayId':w.attrib['id'],'kind':kind,'name':tags.get('name','')},'geometry':{'type':'Polygon','coordinates':[coords]}})
    if 'highway' not in tags or tags.get('access') in ['private','no'] or tags.get('area')=='yes':continue
    part=[]
    for nid in ids+[None]:
        point=nodes.get(nid)
        if point is not None and inside(point):part.append(point)
        else:
            if len(part)>1:features.append({'type':'Feature','properties':{'osmWayId':w.attrib['id'],'kind':'road','highway':tags['highway'],'name':tags.get('name','')},'geometry':{'type':'LineString','coordinates':part}})
            part=[]
geo={'type':'FeatureCollection','bbox':BBOX,'features':features,'source':{'provider':'OpenStreetMap','region':'Hanover / Dartmouth','attribution':'OpenStreetMap contributors','license':'ODbL-1.0','url':'https://www.openstreetmap.org/copyright','extractUrl':URL,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'notice':'Current public street context for historical GPS fixes, not a reconstruction of 2013 streets. Coordinates are rendered as released; no road snapping.'}}
payload=json.dumps(geo,separators=(',',':'),ensure_ascii=False)
(ROOT/'data/hanover-streets.geojson').write_text(payload,encoding='utf-8')
(ROOT/'data/hanover-streets.js').write_text('window.MAP_STREET_REGIONS=(window.MAP_STREET_REGIONS||[]).concat(['+payload+']);\n',encoding='utf-8')
print(json.dumps({'features':len(features),'counts':{k:sum(f['properties']['kind']==k for f in features) for k in ['road','building','park']},'bytes':len(payload.encode()),'sourceBytes':source.stat().st_size,'bbox':BBOX}))
