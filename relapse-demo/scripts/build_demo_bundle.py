"""Build a reproducible presentation bundle with real and fully synthetic people separate."""
from pathlib import Path
import argparse,hashlib,json,math,random,heapq,sys,copy,subprocess,xml.etree.ElementTree as ET
from datetime import datetime,timedelta,timezone
ROOT=Path(__file__).resolve().parents[1]
METRICS=[
 {'id':'steps','label':'Daily steps','unit':'steps','direction':'lower','floor':1000,'weight':1,'min':0},
 {'id':'sleep_hours','label':'Sleep duration','unit':'h','direction':'both','floor':0.75,'weight':1,'min':0,'max':24},
 {'id':'sleep_efficiency','label':'Sleep efficiency','unit':'%','direction':'lower','floor':5,'weight':0.5,'min':0,'max':100},
 {'id':'bedtime_hour','label':'Sleep onset (adjusted hour)','unit':'h','direction':'both','floor':1,'weight':0.5,'min':0,'max':48},
 {'id':'heart_rate','label':'Resting heart rate','unit':'bpm','direction':'both','floor':5,'weight':1,'min':0,'max':250},
 {'id':'mood','label':'Self-reported mood','unit':'/5','direction':'lower','floor':0.5,'weight':1,'min':1,'max':5},
 {'id':'home_hours','label':'Home dwell time','unit':'h/day','direction':'higher','floor':2,'weight':1,'min':0,'max':24}]


def haversine(a,b):
 lat1,lon1,lat2,lon2=map(math.radians,[a['lat'],a['lon'],b['lat'],b['lon']]);return 6371000*2*math.asin(min(1,math.sqrt(math.sin((lat2-lat1)/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2)))

def street_network():
 source=ROOT/'data/map-source/helsinki-esplanadi.osm';tree=ET.parse(source).getroot()
 nodes={n.attrib['id']:{'lat':float(n.attrib['lat']),'lon':float(n.attrib['lon'])} for n in tree.findall('node')};graph={}
 for w in tree.findall('way'):
  tags={t.attrib['k']:t.attrib['v'] for t in w.findall('tag')}
  if tags.get('highway') not in ['footway','pedestrian','living_street','residential','service','path'] or tags.get('access') in ['private','no'] or tags.get('foot')=='no' or tags.get('area')=='yes':continue
  ids=[x.attrib['ref'] for x in w.findall('nd') if x.attrib['ref'] in nodes]
  for x,y in zip(ids,ids[1:]):
   distance=haversine(nodes[x],nodes[y])
   graph.setdefault(x,{})[y]=distance;graph.setdefault(y,{})[x]=distance
 seen=set();components=[]
 for node in graph:
  if node in seen:continue
  todo=[node];seen.add(node);component=[]
  while todo:
   x=todo.pop();component.append(x)
   for y in graph[x]:
    if y not in seen:seen.add(y);todo.append(y)
  components.append(component)
 component=max(components,key=len)
 def snap(lat,lon):return min(component,key=lambda i:haversine(nodes[i],{'lat':lat,'lon':lon}))
 specs=[('home','Home area',60.1685,24.9468),('park','Esplanadi walk',60.1674,24.949),('errand','Kluuvikatu errands',60.1682,24.9511),('west','West park path',60.1673,24.9460),('east','East park path',60.1675,24.9521),('north','Northern street stop',60.1687,24.9501)]
 places=[dict(id=id,label=name,name=name,nodeId=snap(lat,lon),**nodes[snap(lat,lon)]) for id,name,lat,lon in specs]
 for place in places:place.update(x=(place['lon']-24.945)/.008,y=(60.169-place['lat'])/.003)
 def path(start,end):
  q=[(0,start)];cost={start:0};parent={}
  while q:
   dist,x=heapq.heappop(q)
   if x==end:break
   if dist!=cost[x]:continue
   for y,d in graph[x].items():
    nd=dist+d
    if nd<cost.get(y,float('inf')):cost[y]=nd;parent[y]=x;heapq.heappush(q,(nd,y))
  route=[end]
  while route[-1]!=start:route.append(parent[route[-1]])
  return [dict(nodes[i],osmNodeId=i) for i in reversed(route)]
 routes={(p['id'],q['id']):path(p['nodeId'],q['nodeId']) for p in places for q in places if p!=q}
 return places,routes,{'provider':'OpenStreetMap','license':'ODbL-1.0','attribution':'© OpenStreetMap contributors','url':'https://www.openstreetmap.org/copyright','extractUrl':'https://api.openstreetmap.org/api/0.6/map?bbox=24.945,60.166,24.953,60.169','sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'movement':'Synthetic timed walks on public street/path geometry; no actual participant locations'}

def _generate_health_seed():
 places,paths,geometry_source=street_network();people=[]
 cases=[('Mara · steady rhythm','Regular walks and sleep with normal weekly variation.',110),('Noah · smaller days','Walks become less frequent, sleep shifts and time at home increases over several weeks.',86),('Lea · finding her rhythm again','A sustained disruption is followed by gradual recovery of daily routines.',110),('Oskar · away from routine','Travel changes timing and activity without a matching decline in self-reported mood.',69),('Iris · gaps in the signal','Intermittent device use demonstrates why absent data must not become a reassuring score.',77),('Emil · illness and recovery','Explicit reported illness explains a temporary disruption; raw change remains visible.',58),('Ada · a new fitness routine','An intentional sustained exercise change is reported and remains distinct from deterioration.',99),('Jonas · restless nights','Sleep and timing deteriorate first; activity and mood changes arrive later and persist.',94)]
 cases += [('Sofia - one difficult day','One isolated day of very poor sleep, low mood and staying home; usual routines return the next day. This is a demonstration, not a relapse label.',64),('Elias - different daily routes','A complete generated day links morning walks, errands and longer park visits to the same person and daily measurements.',83)]
 for case,(name,summary,default_index) in enumerate(cases):
  rng=random.Random(20261114+case);records=[];noise={k:0 for k in ['activity','sleep','mood','heart']}
  for day in range(1,121):
   date=datetime(2026,1,5,tzinfo=timezone.utc)+timedelta(days=day-1);weekend=date.weekday()>=5
   ramp=lambda start,duration:max(0,min(1,(day-start)/duration))
   decline=ramp(40,42) if case==1 else ramp(35,30)*max(0,min(1,(110-day)/28)) if case==2 else 1 if case==5 and 45<=day<=65 else max(0,(81-day)/15) if case==5 and 66<=day<=80 else ramp(40,35) if case==7 else 0
   travel=case==3 and 50<=day<=85;fitness=ramp(40,20) if case==6 else 0
   for k in noise:noise[k]=.55*noise[k]+rng.gauss(0,1)
   activity_decline=decline if case!=7 else ramp(62,35)
   sleep_decline=decline if case!=1 else ramp(48,33)
   contexts=[]
   if case==5 and 45<=day<=65:contexts=[{'type':'illness','source':'synthetic','confirmed':True}]
   elif case==5 and 66<=day<=80:contexts=[{'type':'recovery','source':'synthetic','confirmed':True}]
   elif case==6 and 41<=day<=75:contexts=[{'type':'intentional_activity_change','source':'synthetic','confirmed':True}]
   vals={'steps':max(400,8000+(1600 if weekend else 0)+noise['activity']*650-activity_decline*5900+(3000 if travel else 0)+fitness*4200),
    'sleep_hours':max(2.5,7.4+(.45 if weekend else 0)+noise['sleep']*.3-sleep_decline*2.7-(.4 if travel else 0)),
    'sleep_efficiency':max(55,min(99,93+rng.gauss(0,2)-sleep_decline*12)),
    'bedtime_hour':23+(.7 if weekend else 0)+rng.gauss(0,.35)+sleep_decline*1.9+(1.8 if travel else 0),
    'heart_rate':62+noise['heart']*2+(decline*(11 if case!=7 else 4))+(3 if travel else 0)-fitness*6,
    'mood':max(1,min(5,4+noise['mood']*.28-(activity_decline if case==7 else decline)*(1.7 if case!=5 else .8))),
    'home_hours':max(5,min(23.5,14+(1 if weekend else 0)+rng.gauss(0,1)+activity_decline*8-(5 if travel else 0)-fitness*2))}
   isolated_bad=case==8 and day==65
   if isolated_bad:vals.update(steps=350,sleep_hours=2.8,sleep_efficiency=58,bedtime_hour=27.2,heart_rate=79,mood=1.2,home_hours=24)
   vals={k:round(v,2) for k,v in vals.items()}
   missing=case==4 and (48<=day<=59 or day%13==0);partial=case==4 and 70<=day<=85
   trips=[];visits=[]
   def trip(origin,destination,start_seconds):
    route=paths[(origin,destination)];distance=sum(haversine(x,y) for x,y in zip(route,route[1:]));speed=rng.uniform(.85,1.45);duration=max(1,int(distance/speed));started=date+timedelta(seconds=start_seconds);tripid=f'{day}-{len(trips)+1}';points=[];elapsed=0
    for i,point in enumerate(route):
     if i:elapsed+=haversine(route[i-1],point)/speed
     points.append(dict(point,timestamp=(started+timedelta(seconds=elapsed)).isoformat(),tripId=tripid,segmentId=tripid,mode='walk',x=(point['lon']-24.945)/.008,y=(60.169-point['lat'])/.003))
    trips.append({'id':tripid,'tripId':tripid,'mode':'walk','fromPlaceId':origin,'toPlaceId':destination,'startedAt':started.isoformat(),'endedAt':points[-1]['timestamp'],'distanceMeters':round(distance,2),'durationSeconds':round(elapsed,2),'points':points,'synthetic':True})
    return start_seconds+elapsed
   if not missing and case<8:
    for destination,start,probability in [('park',8*3600+(3600 if weekend else 0),.87-.76*activity_decline),('errand',17*3600,.55-.43*activity_decline)]:
     if rng.random()<probability:
      begin=start+rng.randint(-900,900);arrival=trip('home',destination,begin);dwell=rng.randint(8,28)*60;visits.append({'placeId':destination,'arrivedAt':(date+timedelta(seconds=arrival)).isoformat(),'departedAt':(date+timedelta(seconds=arrival+dwell)).isoformat(),'synthetic':True});trip(destination,'home',arrival+dwell)
   if case>=8 and not isolated_bad:
    # All generated away-time is represented, with one continuous same-day itinerary.
    destinations=['park','east','errand','north'] if case==8 else (['west','park','east','errand'] if weekend else ['north','errand','east','park'])
    current='home';clock=8*3600+(3600 if weekend else 0)
    for destination in destinations+['home']:
     arrival=trip(current,destination,clock)
     if destination!='home':
      dwell=(rng.randint(20,40) if case==8 else rng.randint(35,70))*60
      visits.append({'placeId':destination,'arrivedAt':(date+timedelta(seconds=arrival)).isoformat(),'departedAt':(date+timedelta(seconds=arrival+dwell)).isoformat(),'synthetic':True})
      clock=arrival+dwell
     current=destination
   if not missing:
    walked=sum(t['distanceMeters'] for t in trips)
    vals['steps']=max(vals['steps'],math.ceil(walked/.72))
    away_seconds=sum(t['durationSeconds'] for t in trips)+sum((datetime.fromisoformat(v['departedAt'])-datetime.fromisoformat(v['arrivedAt'])).total_seconds() for v in visits)
    vals['home_hours']=round(min(vals['home_hours'],24-away_seconds/3600),2)
    if case>=8:
     vals['steps']=math.ceil(walked/.72)+(350 if isolated_bad else rng.randint(500,850))
     vals['home_hours']=round(24-away_seconds/3600,4)
   if missing:vals={k:None for k in vals}
   elif partial:
    for k in ['heart_rate','sleep_hours','sleep_efficiency']:vals[k]=None
   person_id=f'sim-{case+1:02d}';day_key=person_id+':'+date.date().isoformat();timeline=[]
   if case>=8:
    places_by_id={p['id']:p for p in places};cursor=date
    for t in trips:
     start=datetime.fromisoformat(t['startedAt']);stop=datetime.fromisoformat(t['endedAt']);place=places_by_id[t['fromPlaceId']]
     if start>cursor:timeline.append({'kind':'stay','placeId':place['id'],'lat':place['lat'],'lon':place['lon'],'startedAt':cursor.isoformat(),'endedAt':start.isoformat()})
     timeline.append({'kind':'walk','tripId':t['id'],'startedAt':start.isoformat(),'endedAt':stop.isoformat()});cursor=stop
    home=places_by_id['home'];timeline.append({'kind':'stay','placeId':'home','lat':home['lat'],'lon':home['lon'],'startedAt':cursor.isoformat(),'endedAt':(date+timedelta(days=1)).isoformat()})
   if case>=8:
    away_seconds=sum((datetime.fromisoformat(e['endedAt'])-datetime.fromisoformat(e['startedAt'])).total_seconds() for e in timeline if not(e['kind']=='stay' and e.get('placeId')=='home'))
    vals['home_hours']=round(24-away_seconds/3600,4)
   movement_summary={'mappedWalkingMeters':round(sum(t['distanceMeters'] for t in trips),2) if not missing else None,'mappedTripCount':len(trips) if not missing else None,'scope':'complete_generated_day' if case>=8 else 'selected_walking_trips','missingGps':missing,'synthetic':True,'awaySeconds':round(away_seconds,4) if case>=8 else None,'homeSeconds':round(86400-away_seconds,4) if case>=8 else None,'stepModel':'mapped walking distance / 0.72m stride + generated indoor steps' if case>=8 else 'generated total steps; mapped walking is a subset','provenance':'Same generated person and date; no external participant GPS paired to health'}
   records.append({'participantId':person_id,'subjectId':person_id,'timeZone':'UTC' if case>=8 else 'Europe/Helsinki','dayKey':day_key,'locationTimeline':timeline,'movementSummary':movement_summary,'period':f'Day {day:03d}','date':date.date().isoformat(),'periodIndex':day,'values':vals,'labels':{'phq9_start':None,'phq9_end':None},'featureCompleteness':sum(v is not None for v in vals.values())/len(vals),'missingPeriod':missing,'route':[point for t in trips for point in t['points']] if not missing else None,'trips':trips,'visits':visits,'movementCoverage':'Complete generated UTC day: timed street walks and stays; not measured GPS' if case>=8 else 'Selected local walking trips only; other away-time has no interpolated route','movementStatus':'device_missing' if missing else 'selected_walks_present' if trips else 'no_selected_walk','synthetic':True,'contexts':contexts})
  if case==8:phases=[{'label':'Usual rhythm','startIndex':0,'endIndex':63,'kind':'baseline'},{'label':'One difficult day','startIndex':64,'endIndex':64,'kind':'marked_change'},{'label':'Usual routine returns','startIndex':65,'endIndex':119,'kind':'recovery'}]
  elif case in [1,7]:phases=[{'label':'Usual rhythm','startIndex':0,'endIndex':27,'kind':'baseline'},{'label':'Early changes','startIndex':40,'endIndex':64,'kind':'early_change'},{'label':'Sustained disruption','startIndex':80,'endIndex':119,'kind':'marked_change'}]
  elif case in [2,5]:phases=[{'label':'Usual rhythm','startIndex':0,'endIndex':27,'kind':'baseline'},{'label':'Disruption' if case==2 else 'Reported illness','startIndex':44,'endIndex':64,'kind':'marked_change'},{'label':'Recovery','startIndex':80 if case==2 else 65,'endIndex':119,'kind':'recovery'}]
  else:phases=[{'label':'Usual rhythm','startIndex':0,'endIndex':27,'kind':'baseline'},{'label':'Travel period' if case==3 else 'Intentional routine change' if case==6 else 'Device gaps' if case==4 else 'Normal variation','startIndex':49,'endIndex':84,'kind':'early_change'}]
  people.append({'id':f'sim-{case+1:02d}','name':name,'caseSummary':summary,'defaultIndex':default_index,'phases':phases,'datasetId':'synthetic-daily','source':'Demo stories generated on OpenStreetMap street geometry','synthetic':True,'granularity':'day','timeZone':'UTC' if case>=8 else 'Europe/Helsinki','baselineIndices':list(range(28)),'baselineStatus':'synthetic-known-good','baselineLabel':'Simulated stable first 28 days','baselineReason':'Generator defines the reference period; all person measurements and trips are simulated.','metrics':METRICS,'routeProvenance':geometry_source['movement'],'mapGeometrySource':geometry_source,'places':places if case>=8 else places[:3],'records':records,'sourceNotes':['All personal measurements, contexts, visits and times are generated.','Street/path geometry is from OpenStreetMap contributors under ODbL; no actual person lives at the home-area marker.','Trips follow separate pedestrian-network paths; do not draw connectors between trip IDs.','Scenarios show behavioral patterns, not diagnoses or clinically verified relapse.','Real study participants are never imputed with these generated data.'],'unavailable':['actual_participant_gps','clinical_outcomes','actual_patient_data']})
 return people

def mila_health(seed=20261125):
 rng=random.Random(seed);records=[]
 for i in range(120):
  weeks=max(0,(i-28)/7);values={'steps':round(max(400,8500*(1-.03*weeks)+rng.gauss(0,1020)),2),'sleep_hours':round(max(2.5,7.5-.08*weeks+rng.gauss(0,.22)),2),'sleep_efficiency':round(max(55,min(99,93-.35*weeks+rng.gauss(0,1.5))),2),'bedtime_hour':round(23+.10*weeks+rng.gauss(0,.25),2),'heart_rate':round(62+rng.gauss(0,1.5),2),'mood':round(max(1,min(5,3.9-.13*weeks+rng.gauss(0,.35))),2),'home_hours':round(max(5,min(23.5,14+.25*weeks+rng.gauss(0,.7))),2)}
  records.append(values)
 return records

def generate():
 # Retain the original seeded generation unchanged, including RNG consumption and
 # route-dependent health values; only the new independent location pass changes routes.
 sys.path.insert(0,str(ROOT/'scripts'))
 from personal_places import relocate
 people=_generate_health_seed()
 mila=copy.deepcopy(people[0]);mila.update(id='sim-11',name='Mila - a slow fade',caseSummary='Nothing dramatic on any single day - just a gradual fade in movement, sleep and mood.',defaultIndex=99)
 mila['phases']=[{'label':'Usual rhythm','startIndex':0,'endIndex':27,'kind':'baseline'},{'label':'Slow change','startIndex':28,'endIndex':119,'kind':'early_change'}]
 mila['generatorParameters']={'seed':20261125,'stepsWeeklyFraction':.03,'sleepHoursWeekly':-.08,'bedtimeHoursWeekly':.10,'moodWeekly':-.13,'homeHoursWeekly':.25,'notice':'Illustrative rates use steps -3%/week and mood -0.13 points/week to cross unchanged anchor thresholds by Day 100. Seed selected from two candidates for a visible slow-drift example; no clinical calibration or validation is claimed.'}
 health=mila_health()
 for i,record in enumerate(mila['records']):
  values=health[i]
  record.update(participantId='sim-11',subjectId='sim-11',dayKey='sim-11:'+record['date'],values=values,contexts=[],missingPeriod=False,featureCompleteness=1)
  # Progressively fewer outings; the actual paths are supplied by relocation.
  count=2 if i<70 else 1 if i<100 else int(i%3==0)
  record['visits']=[{'placeId':name} for name in ['park','errand'][:count]]
  record['movementStatus']='selected_walks_present' if count else 'no_selected_walk'
 people.append(mila)
 return [relocate(person,index) for index,person in enumerate(people)]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--real-input',type=Path,default=ROOT/'.tmp/all-records/demo-data.json');ap.add_argument('--output-dir',type=Path,default=ROOT/'data');ap.add_argument('--verify-alerts',action='store_true',help='Verify Mila using the shipped JS engine after writing the bundle');ap.add_argument('--node',default='node',help='Node executable for --verify-alerts');a=ap.parse_args()
 data=json.loads(a.real_input.read_text());real=data['participants']
 for p in real:p['datasetId']='psyche-d';p['synthetic']=False
 synthetic=generate();data['participants']=real+synthetic
 data['datasets']=[{'id':'psyche-d','label':'PSYCHE-D research observations','synthetic':False,'participants':len(real),'source':'https://zenodo.org/records/5085146'},{'id':'synthetic-daily','label':'Synthetic daily device scenarios','synthetic':True,'participants':len(synthetic),'generatorSeed':20261114}]
 data['cohortStats']['syntheticParticipants']=len(synthetic)
 data['title']='Research observations and explicit daily simulations'
 a.output_dir.mkdir(parents=True,exist_ok=True)
 text=json.dumps(data,separators=(',',':'),allow_nan=False)
 (a.output_dir/'demo-data.json').write_text(text,encoding='utf-8');(a.output_dir/'demo-data.js').write_text('/* Real and synthetic participants remain separate. */\nwindow.DEMO_DATA='+text+';\n',encoding='utf-8')
 manifest={'realInput':str(a.real_input),'realInputSha256':hashlib.sha256(a.real_input.read_bytes()).hexdigest(),'realParticipants':len(real),'realRecords':sum(not r.get('missingPeriod') for p in real for r in p['records']),'realMissingSlots':sum(bool(r.get('missingPeriod')) for p in real for r in p['records']),'syntheticParticipants':len(synthetic),'syntheticSlots':sum(len(p['records']) for p in synthetic),'syntheticSeed':20261114,'realDataImputed':False,'outputSha256':hashlib.sha256(text.encode()).hexdigest()}
 (a.output_dir/'bundle-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(json.dumps(manifest,indent=2))
 if a.verify_alerts:subprocess.run([a.node,str(ROOT/'scripts/verify_story_alerts.cjs'),str(a.output_dir/'demo-data.json')],check=True)
if __name__=='__main__':main()
