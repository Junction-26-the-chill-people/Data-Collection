"""Location-only per-person routines on bounded, attributed OSM public networks."""
from pathlib import Path
import json,math,heapq,hashlib,random,urllib.request,xml.etree.ElementTree as ET
from datetime import datetime,timedelta,timezone
ROOT=Path(__file__).resolve().parents[1]
REGIONS=[('Kallio',60.1848,24.9505),('Toolo',60.1795,24.9235),('Punavuori',60.1588,24.9398),('Kamppi',60.1687,24.9286),('Sornainen',60.1882,24.9648),('Hakaniemi',60.1800,24.9514),('Kaivopuisto',60.1555,24.9525),('Hietaniemi',60.1731,24.9100),('Kaisaniemi',60.1760,24.9450),('Eira',60.1539,24.9385),('Kruununhaka',60.1752,24.9562)]
ALLOWED={'footway','pedestrian','living_street','residential','service','path','steps','unclassified','tertiary','secondary'}
def distance(a,b):
 p,q=math.radians(a['lat']),math.radians(b['lat']);dy=q-p;dx=math.radians(b['lon']-a['lon'])
 return 12742000*math.asin(min(1,math.sqrt(math.sin(dy/2)**2+math.cos(p)*math.cos(q)*math.sin(dx/2)**2)))
def load_region(index,download=False):
 name,lat,lon=REGIONS[index];bbox=[round(lon-.006,6),round(lat-.003,6),round(lon+.006,6),round(lat+.003,6)]
 source=ROOT/f'data/map-source/neighborhood-{index+1:02}.osm';url='https://api.openstreetmap.org/api/0.6/map?bbox='+','.join(map(str,bbox))
 if not source.exists():
  if not download:raise FileNotFoundError(str(source)+'; run scripts/personal_places.py first')
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Junction26-research-demo/1.5'}),timeout=60) as response:payload=response.read(20_000_001)
  if len(payload)>20_000_000:raise ValueError('Bounded OSM response too large')
  ET.fromstring(payload);source.write_bytes(payload)
 tree=ET.parse(source).getroot();nodes={n.attrib['id']:{'lat':float(n.attrib['lat']),'lon':float(n.attrib['lon'])} for n in tree.findall('node')}
 inside=lambda p:bbox[0]<=p['lon']<=bbox[2] and bbox[1]<=p['lat']<=bbox[3]
 graph={};features=[]
 for way in tree.findall('way'):
  tags={t.attrib['k']:t.attrib['v'] for t in way.findall('tag')};ids=[n.attrib['ref'] for n in way.findall('nd')];coords=[nodes[n] for n in ids if n in nodes]
  kind='building' if tags.get('building') not in (None,'no') else 'park' if tags.get('leisure') in ['park','garden'] or tags.get('landuse') in ['grass','recreation_ground'] or tags.get('natural') in ['wood','scrub','grassland'] else None
  if kind and len(coords)>=4 and coords[0]==coords[-1] and all(inside(p) for p in coords):features.append({'type':'Feature','properties':{'osmWayId':way.attrib['id'],'kind':kind},'geometry':{'type':'Polygon','coordinates':[[[p['lon'],p['lat']] for p in coords]]}})
  if 'highway' not in tags or tags.get('access') in ['private','no'] or tags.get('area')=='yes':continue
  part=[]
  for nid in ids+[None]:
   point=nodes.get(nid)
   if point and inside(point):part.append([point['lon'],point['lat']])
   else:
    if len(part)>1:features.append({'type':'Feature','properties':{'osmWayId':way.attrib['id'],'kind':'road','highway':tags['highway']},'geometry':{'type':'LineString','coordinates':part}})
    part=[]
  if tags['highway'] not in ALLOWED or tags.get('foot')=='no':continue
  for a,b in zip(ids,ids[1:]):
   if a in nodes and b in nodes and inside(nodes[a]) and inside(nodes[b]):
    d=distance(nodes[a],nodes[b]);graph.setdefault(a,{})[b]=d;graph.setdefault(b,{})[a]=d
 provenance={'provider':'OpenStreetMap','region':name,'license':'ODbL-1.0','attribution':'OpenStreetMap contributors','url':'https://www.openstreetmap.org/copyright','extractUrl':url,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'bbox':bbox,'movement':'Synthetic timed walks on public street/path geometry; no actual participant locations'}
 geo={'type':'FeatureCollection','bbox':bbox,'features':features,'source':provenance}
 if download:
  text=json.dumps(geo,separators=(',',':'));assert len(text.encode())<2_000_000
  (ROOT/f'data/neighborhood-{index+1:02}.js').write_text('window.MAP_STREET_REGIONS=(window.MAP_STREET_REGIONS||[]).concat(['+text+']);\n',encoding='utf-8')
  print(name,len(features),len(text),flush=True)
 return nodes,graph,provenance

def shortest(graph,start):
 queue=[(0,start)];cost={start:0};parent={}
 while queue:
  dist,node=heapq.heappop(queue)
  if dist!=cost[node]:continue
  for neighbor,weight in graph[node].items():
   new=dist+weight
   if new<cost.get(neighbor,float('inf')):cost[neighbor]=new;parent[neighbor]=node;heapq.heappush(queue,(new,neighbor))
 return cost,parent

def network(index):
 nodes,graph,source=load_region(index);name,lat,lon=REGIONS[index]
 seen=set();components=[]
 for node in graph:
  if node in seen:continue
  stack=[node];seen.add(node);component=[]
  while stack:
   current=stack.pop();component.append(current)
   for neighbor in graph[current]:
    if neighbor not in seen:seen.add(neighbor);stack.append(neighbor)
  components.append(component)
 connected=max(components,key=len);home=min(connected,key=lambda n:distance(nodes[n],{'lat':lat,'lon':lon}));cost,parent=shortest(graph,home)
 chosen=[home];places=[]
 for target in [65,130,190,250]:
  candidates=[n for n in cost if n not in chosen and cost[n]>35]
  chosen.append(min(candidates,key=lambda n:abs(cost[n]-target)+sum(max(0,45-distance(nodes[n],nodes[x])) for x in chosen[1:])))
 labels=['Home area','Park walk','Grocery stop','Cafe visit','Library visit'];ids=['home','park','errand','cafe','library']
 for nid,label,pid in zip(chosen,labels,ids):places.append({'id':pid,'label':name+' - '+label,'name':name+' - '+label,'nodeId':nid,**nodes[nid]})
 paths={}
 for p in places:
  _,parents=shortest(graph,p['nodeId'])
  for q in places:
   if p==q:continue
   chain=[q['nodeId']]
   while chain[-1]!=p['nodeId']:chain.append(parents[chain[-1]])
   paths[(p['id'],q['id'])]=[{**nodes[n],'osmNodeId':n} for n in reversed(chain)]
 return places,paths,source

def relocate(person,index):
 places,paths,source=network(index);byid={p['id']:p for p in places};person['places']=places;person['mapGeometrySource']=source;person['routeProvenance']=source['movement']
 for record in person['records']:
  rng=random.Random(915000+index*1000+record['periodIndex']);date=datetime.fromisoformat(record['date']).replace(tzinfo=timezone.utc);complete=record['movementSummary']['scope']=='complete_generated_day';missing=record['missingPeriod'];old_visits=record['visits'];day=record['periodIndex'];ids=[]
  if not missing and old_visits:
   if complete:ids=['park','cafe','errand','library'] if day%7<5 else ['errand','park','library']
   elif index==3 and 50<=day<=85:ids=['cafe','library']
   else:
    ids=['park' if v['placeId']=='park' else 'errand' for v in old_visits]
    if index in [1,7,10] and day>75:ids=['park']
  budget=0 if missing else record['values']['steps']*.72
  away=0 if missing else round((24-record['values']['home_hours'])*3600,6)
  def length(destinations):
   itinerary=['home']+destinations+['home'];return sum(sum(distance(a,b) for a,b in zip(paths[x,y],paths[x,y][1:])) for x,y in zip(itinerary,itinerary[1:]) if x!=y)
  while ids and (length(ids)>budget or length(ids)/1.2>=away-60):
   if len(ids)==1 and ids[0]!='park':ids=['park']
   else:ids.pop()
  if old_visits and not missing and not ids and away>120 and length(['park'])<=budget:ids=['park']
  trips=[];visits=[];timeline=[];start=date+timedelta(hours=8);clock=start;totalwalk=length(ids)/1.2 if ids else 0
  dwell_total=max(0,away-totalwalk) if complete else min(max(0,away-totalwalk),len(ids)*rng.randint(8,25)*60)
  per_dwell=dwell_total/max(1,len(ids));previous='home'
  for destination in ids+(['home'] if ids else []):
   route=paths[previous,destination];trip_id=f'{record["dayKey"]}:{len(trips)+1}';points=[];elapsed=0
   for pos,p in enumerate(route):
    if pos:elapsed+=distance(route[pos-1],p)/1.2
    points.append({**p,'timestamp':(clock+timedelta(seconds=elapsed)).isoformat(),'tripId':trip_id,'segmentId':trip_id,'mode':'walk'})
   stop=datetime.fromisoformat(points[-1]['timestamp']);trips.append({'id':trip_id,'tripId':trip_id,'mode':'walk','fromPlaceId':previous,'toPlaceId':destination,'startedAt':clock.isoformat(),'endedAt':stop.isoformat(),'distanceMeters':round(elapsed*1.2,2),'durationSeconds':round(elapsed,6),'points':points,'synthetic':True})
   clock=stop
   if destination!='home':
    departure=clock+timedelta(seconds=per_dwell);visits.append({'placeId':destination,'arrivedAt':clock.isoformat(),'departedAt':departure.isoformat(),'synthetic':True});clock=departure
   previous=destination
  if complete:
   # Fit the preserved home_hours to microsecond precision by correcting the final dwell.
   if visits:
    difference=away-(datetime.fromisoformat(trips[-1]['endedAt'])-start).total_seconds()
    last_visit=visits[-1];last_visit['departedAt']=(datetime.fromisoformat(last_visit['departedAt'])+timedelta(seconds=difference)).isoformat()
    last=trips[-1];last['startedAt']=(datetime.fromisoformat(last['startedAt'])+timedelta(seconds=difference)).isoformat();last['endedAt']=(datetime.fromisoformat(last['endedAt'])+timedelta(seconds=difference)).isoformat()
    for point in last['points']:point['timestamp']=(datetime.fromisoformat(point['timestamp'])+timedelta(seconds=difference)).isoformat()
   cursor=date
   for trip in trips:
    begin=datetime.fromisoformat(trip['startedAt']);end=datetime.fromisoformat(trip['endedAt']);place=byid[trip['fromPlaceId']]
    if begin>cursor:timeline.append({'kind':'stay','placeId':place['id'],'lat':place['lat'],'lon':place['lon'],'startedAt':cursor.isoformat(),'endedAt':begin.isoformat()})
    timeline.append({'kind':'walk','tripId':trip['id'],'startedAt':begin.isoformat(),'endedAt':end.isoformat()});cursor=end
   timeline.append({'kind':'stay','placeId':'home','lat':byid['home']['lat'],'lon':byid['home']['lon'],'startedAt':cursor.isoformat(),'endedAt':(date+timedelta(days=1)).isoformat()})
  record.update(trips=trips,visits=visits,locationTimeline=timeline,route=None if missing else [p for t in trips for p in t['points']])
  record['movementSummary']={**record['movementSummary'],'mappedWalkingMeters':None if missing else round(sum(t['distanceMeters'] for t in trips),2),'mappedTripCount':None if missing else len(trips),'awaySeconds':away if complete else None,'homeSeconds':86400-away if complete else None,'stepModel':'Preserved generated total steps; mapped walking is a bounded subset','provenance':'Same generated person/date; individual OSM neighborhood, fictional routine place roles'}
 return person

if __name__=='__main__':
 for i in range(len(REGIONS)):load_region(i,download=True)
