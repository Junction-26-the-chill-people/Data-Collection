"""Audit SYN-RoadGps without executing repository code; export a separate map-only sample.
Run from any directory with Python standard library. Raw inputs remain immutable.
"""
import argparse,ast,csv,hashlib,json,math,re,statistics
from collections import Counter
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT.parent/'datasets/location_sources/syn_roadgps/raw'
REVISION='482d9f29bbee8282626e5136f16924366bcf5f6e'
URL='https://huggingface.co/datasets/Smile1120/SYN-RoadGps'

def literal(value, numpy_integer=False):
    # Accept the publisher's np.int64 decimal wrappers, never arbitrary calls.
    if numpy_integer:value=re.sub(r'np\.int64\((-?\d+)\)',r'\1',value)
    return ast.literal_eval(value)

def distance(a,b):
    lon1,lat1=a;lon2,lat2=b
    v=math.sin(math.radians(lat2-lat1)/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(math.radians(lon2-lon1)/2)**2
    return 6371000*2*math.asin(min(1,math.sqrt(v)))

def parse(row):
    gps=literal(row['gps_list']);times=literal(row['gene_trace_datetime']);roads=literal(row['gene_trace_road_id'],True);ratios=literal(row['gene_trace_rate'])
    if len({len(gps),len(times),len(roads),len(ratios)})!=1:raise ValueError('field lengths mismatch')
    if not gps:raise ValueError('empty trajectory')
    for pair in gps:
        if len(pair)!=2 or any(not isinstance(v,(float,int)) or not math.isfinite(v) for v in pair) or not -180<=pair[0]<=180 or not -90<=pair[1]<=90:raise ValueError('invalid coordinate')
    stamps=[]
    for value in times:
        stamp=datetime.fromisoformat(value.replace('Z','+00:00'))
        if stamp.tzinfo is None:raise ValueError('timestamp has no timezone')
        stamps.append(stamp.timestamp())
    if any(type(v)!=int for v in roads):raise ValueError('invalid road id')
    if any(not isinstance(v,(float,int)) or not math.isfinite(v) or not 0<=v<=1 for v in ratios):raise ValueError('invalid within-segment ratio')
    return gps,times,stamps,roads,ratios

def make_trace(index,gps,times,stamps,roads,ratios,max_speed=55,max_gap=300):
    points=[];splits=[];segment=0;length=0;full_length=0
    for i,(pair,time,road,ratio) in enumerate(zip(gps,times,roads,ratios)):
        if i:
            dt=stamps[i]-stamps[i-1];metres=distance(gps[i-1],pair);full_length+=metres
            reason='non_increasing_time' if dt<=0 else 'time_gap' if dt>max_gap else 'speed_above_threshold' if metres/dt>max_speed else None
            if reason:splits.append({'beforePointIndex':i,'reason':reason,'seconds':dt,'distanceMeters':round(metres,3)});segment+=1
            else:length+=metres
        points.append({'lat':pair[1],'lon':pair[0],'timestamp':time,'segmentId':f'{index}-{segment}','roadId':road,'withinSegmentRatio':ratio})
    return {'id':f'syn-roadgps-{index:05d}','sourceRow':index,'synthetic':True,'mode':'unspecified','clinicalLink':None,'points':points,'breaks':splits,'pointCount':len(points),'durationSeconds':stamps[-1]-stamps[0],'drawnChordDistanceMeters':round(length,2),'allChordDistanceMeters':round(full_length,2),'bounds':[min(p[0] for p in gps),min(p[1] for p in gps),max(p[0] for p in gps),max(p[1] for p in gps)]}

def run(raw=RAW,out=ROOT/'data',sample_count=50):
    expected='66e504de9fcbef38c7302ff3b0bc7ac7040ab6fbb91823d88fcbd5a05c27710e'
    if hashlib.sha256((raw/'RoadGPS.csv').read_bytes()).hexdigest()!=expected:raise ValueError('Source CSV differs from pinned publisher SHA256')
    counts=Counter();lengths=[];speeds=[];gaps=[];samples=[];road_ids=set();all_road_ids=Counter();bounds=[180,90,-180,-90];examples=[]
    with (raw/'RoadGPS.csv').open(encoding='utf-8',newline='') as f:
        for index,row in enumerate(csv.DictReader(f),1):
            counts['rows']+=1
            try:gps,times,stamps,roads,ratios=parse(row)
            except (ValueError,SyntaxError,TypeError) as error:
                counts['invalidRows']+=1
                if len(examples)<20:examples.append({'row':index,'error':str(error)})
                continue
            all_road_ids.update(roads)
            counts['validRows']+=1;counts['points']+=len(gps);lengths.append(len(gps));counts['singlePointRows']+=len(gps)==1
            for lon,lat in gps:bounds=[min(bounds[0],lon),min(bounds[1],lat),max(bounds[2],lon),max(bounds[3],lat)]
            breaks=0
            for a,b,t,u in zip(gps,gps[1:],stamps,stamps[1:]):
                dt=u-t;metres=distance(a,b);counts['edges']+=1;counts['nonIncreasingEdges']+=dt<=0;counts['repeatedPositionEdges']+=metres==0;counts['longGapEdges']+=dt>300;gaps.append(dt)
                if dt>0:
                    speed=metres/dt;speeds.append(speed);counts['speedAbove55mpsEdges']+=speed>55;breaks+=speed>55 or dt>300
                else:breaks+=1
            counts['rowsWithSplitEdges']+=breaks>0
            # Deterministic first N parse-valid multi-point source rows, including flaws.
            if len(samples)<sample_count and len(gps)>1:
                trace=make_trace(index,gps,times,stamps,roads,ratios);samples.append(trace);road_ids.update(roads)
    ordered=sorted(speeds)
    audit={'schemaVersion':'1.0','source':{'id':'syn-roadgps','publisher':'Smile1120','url':URL,'revision':REVISION,'license':'CC-BY-4.0','synthetic':True,'clinicalLink':None,'crs':'longitude/latitude degrees; datum not declared by publisher','timeEncoding':'ISO 8601 UTC strings','sourceSHA256':hashlib.sha256((raw/'RoadGPS.csv').read_bytes()).hexdigest()},'counts':dict(counts),'bounds':bounds,'pointCountPerTrajectory':{'min':min(lengths),'median':statistics.median(lengths),'max':max(lengths)},'edgeSpeedMps':{str(q):ordered[int((len(ordered)-1)*q)] for q in [0,.5,.95,.99,1]},'edgeGapSeconds':{'min':min(gaps),'median':statistics.median(gaps),'max':max(gaps)},'invalidExamples':examples,'sampling':f'First {sample_count} parse-valid multi-point rows in original CSV order; no quality ranking; all corpus rows audited.','drawingPolicy':{'maxSpeedMps':55,'maxGapSeconds':300,'splitNonIncreasingTimestamps':True,'noInterpolation':True,'interpretation':'Generic visualization integrity filter, not a walking-speed filter or clinical threshold. Preserve points, split segments; never connect across breaks.'},'limitations':['No person identifiers, mood, physiology, home labels, travel-mode labels or repeated daily routines are provided. Each row is an independent generated trajectory.','Publisher claims road-constrained generation; source is not independently clinically validated. Road coordinate datum is unspecified; road-overlay agreement with OSM is not guaranteed.','Coordinate-to-coordinate lines are sampled chords, not full routed geometry. Do not imply walking or map-match silently.']}
    # Audit IDs only. Do not export an unverified road-ID join or map alignment.
    features=[];available_ids=set()
    with (raw/'roadmap.geo').open(encoding='utf-8',newline='') as f:
        for row in csv.DictReader(f):available_ids.add(int(row['geo_id']))
    missing=set(all_road_ids)-available_ids
    audit['roadIdentifierAudit']={'geometryRows':len(available_ids),'geometryIdMin':min(available_ids),'geometryIdMax':max(available_ids),'traceUniqueRoadIds':len(all_road_ids),'traceRoadIdMin':min(all_road_ids),'traceRoadIdMax':max(all_road_ids),'traceUniqueRoadIdsAbsentFromGeometry':len(missing),'pointsWithRoadIdAbsentFromGeometry':sum(all_road_ids[x] for x in missing),'warning':'Trace road IDs cannot reliably join supplied geometry IDs. No source road geometry is exported; do not infer a map match.'}
    audit['localDatasets']=[{'id':'psyche-d','coordinateFields':[],'evidence':'Actual154-column parquet schema and feature dictionary; no latitude/longitude/GPS fields. Monthly aggregates cannot reconstruct routes.','license':'CC-BY-NC-4.0'},{'id':'nfi-fared','coordinateFields':[],'evidence':'All7 safely inspected pickle column schemas: Cache has altitude/course/speed/accuracy/time but no lat/lon. META_carrying_location means hand/pocket/rucksack, not a geographic location.','license':'Not supplied in downloaded card/metadata'},{'id':'dryad-finnish-immigrants','coordinateFields':[],'evidence':'Metadata human-subjects statement explicitly excludes GPS. Raw archive still unavailable; no fabricated file-level inspection.','license':'CC0-1.0'}]
    audit['exportedTraces']=len(samples);audit['exportedPoints']=sum(t['pointCount'] for t in samples);audit['exportedRoadSegments']=len(features)
    bundle={'schemaVersion':'1.0','source':audit['source'],'summary':audit,'traces':samples,'roads':{'type':'FeatureCollection','features':features}}
    out.mkdir(parents=True,exist_ok=True)
    (out/'location-traces.json').write_text(json.dumps(bundle,separators=(',',':'),allow_nan=False),encoding='utf-8')
    (out/'location-traces.js').write_text('window.LOCATION_TRACES='+json.dumps(bundle,separators=(',',':'),allow_nan=False)+';\n',encoding='utf-8')
    trajectories=[]
    for trace in samples:
        trips=[]
        for point in trace['points']:
            if not trips or trips[-1]['id']!=point['segmentId']:trips.append({'id':point['segmentId'],'mode':'unknown','points':[]})
            trips[-1]['points'].append({k:point[k] for k in ['lat','lon','timestamp']})
        trajectories.append({'id':trace['id'],'sourceRow':trace['sourceRow'],'synthetic':True,'record':{'period':trace['points'][0]['timestamp'][:10],'date':trace['points'][0]['timestamp'][:10],'trips':trips},'summary':{'points':trace['pointCount'],'breaks':len(trace['breaks']),'distanceMeters':trace['drawnChordDistanceMeters'],'durationSeconds':trace['durationSeconds']},'boundingBox':trace['bounds']})
    compact={'source':{**audit['source'],'title':'SYN-RoadGps: generated Beijing-area trajectories','qualitySummary':audit['counts'],'qualityWarnings':audit['limitations']+[audit['roadIdentifierAudit']['warning']]},'trajectories':trajectories,'summary':audit,'roads':bundle['roads']}
    (out/'location-samples.js').write_text('window.LOCATION_DATA='+json.dumps(compact,separators=(',',':'),allow_nan=False)+';\n',encoding='utf-8')
    (out/'location-samples.json').write_text(json.dumps(compact,separators=(',',':'),allow_nan=False),encoding='utf-8')
    (ROOT/'docs/location-dataset-audit.json').write_text(json.dumps(audit,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps({k:audit[k] for k in ['counts','roadIdentifierAudit','exportedTraces','exportedPoints','exportedRoadSegments']},indent=2))
    return bundle

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--raw',type=Path,default=RAW);parser.add_argument('--output-dir',type=Path,default=ROOT/'data');parser.add_argument('--sample-count',type=int,default=50);args=parser.parse_args()
    if args.sample_count<1:parser.error('sample-count must be positive')
    run(args.raw,args.output_dir,args.sample_count)
