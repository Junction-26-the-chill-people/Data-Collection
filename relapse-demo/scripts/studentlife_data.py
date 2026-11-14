"""Convert licensed StudentLife derivative tables to CSV and paired daily viewer data.
Requires pandas and pinned pyreadr0.5.3; no R runtime. No health codes are scored.
"""
import sys,json,hashlib,math
from pathlib import Path
from datetime import datetime,timezone,timedelta
from collections import defaultdict,Counter
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.deps'))
import pandas as pd
import pyreadr
BASE=ROOT.parent/'datasets/location_sources/studentlife_zenodo'

def iso(t):return datetime.fromtimestamp(float(t),timezone.utc).isoformat().replace('+00:00','Z')
def day(t):return iso(t)[:10]
def finite(v):return isinstance(v,(int,float)) and math.isfinite(v)
def clean(v):
    if pd.isna(v):return None
    if hasattr(v,'item'):v=v.item()
    return v

def metres(a,b):
    p,q=math.radians(a['latitude']),math.radians(b['latitude']);dy=q-p;dx=math.radians(b['longitude']-a['longitude'])
    return 12742000*math.asin(min(1,math.sqrt(math.sin(dy/2)**2+math.cos(p)*math.cos(q)*math.sin(dx/2)**2)))

def atomictext(path,text):
    temporary=path.with_name(path.name+'.tmp');temporary.write_text(text,encoding='utf-8');temporary.replace(path)

def main():
    manifest=json.loads((BASE/'member-manifest.json').read_text());raw=BASE/'raw';tables={};decoded=BASE/'decoded';decoded.mkdir(exist_ok=True)
    for entry in manifest['files']:
        path=raw/entry['file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256']
        table=pyreadr.read_r(str(path))[None];tables[path.stem]=table;temporary=decoded/(path.stem+'.csv.tmp');table.to_csv(temporary,index=False);temporary.replace(decoded/(path.stem+'.csv'))
    gps,pam,sleep,phq=[tables[k] for k in ['gps','PAM','Sleep','PHQ-9']]
    grouped=defaultdict(lambda:defaultdict(lambda:{'gps':[],'checkins':[]}));audit={'sourceRows':{k:len(v) for k,v in tables.items()},'sourceUsers':{k:int(v.uid.nunique()) for k,v in tables.items()},'counts':Counter(),'maxAccuracyMeters':100,'maxGapSeconds':1800,'maxSpeedMps':55,'maxDisplayPointsPerDay':80,'dayGrouping':'UTC calendar days; source epoch seconds preserved. No device-local timezone inferred.'}
    for r in gps.to_dict('records'):
        r={k:clean(v) for k,v in r.items()};grouped[str(r['uid'])][day(r['timestamp'])]['gps'].append(r)
    for r in pam.to_dict('records'):
        grouped[str(r['uid'])][day(r['timestamp'])]['checkins'].append({'type':'PAM','timestamp':iso(r['timestamp']),'pictureIndex':clean(r['picture_idx']),'interpretation':'Raw photographic affect image-selection code; no ordinal mood conversion.'})
    for r in sleep.to_dict('records'):
        grouped[str(r['uid'])][day(r['timestamp'])]['checkins'].append({'type':'Sleep','timestamp':iso(r['timestamp']),'rawHourCode':clean(r['hour']),'rawQualityCode':clean(r['rate']),'sleepDurationLabel':('<3 hours' if r['hour']==1 else f"{r['hour']/2+2.5:g} hours" if 2<=r['hour']<=19 else 'Unmapped code'),'sleepQualityLabel':{1:'Very good',2:'Fairly good',3:'Fairly bad',4:'Very bad'}.get(r['rate'],'Unmapped code'),'location':clean(r['location']),'rawSocialCode':clean(r['social']),'interpretation':'Retrospective last-night sleep self-report; codebook labels shown, original codes preserved. Submission date is not a verified sleep-night date.'})
    source={'id':'studentlife','title':'StudentLife: recorded GPS + same-participant check-ins','url':'https://zenodo.org/records/3529253','doi':'10.5281/zenodo.3529253','version':'1.0.0','license':'CC-BY-4.0','synthetic':False,'publisher':'Daniel Fryer, StudentLife R-format derivative; original study Wang et al.(2014)','timeZone':'UTC','sleepCodebookURL':'https://github.com/frycast/studentlife/tree/master/tests/testthat/testdata/sample','clinicalLink':'Shared source uid and timestamp; no cross-study join. PHQpre/post contextual only.','limitations':['Derivative contains49GPS/PAM/sleep IDs; original paper describes48students. Preserve observed identifiers; do not silently delete one to match paper.','No verified heart rate, step count or wearable sleep measurements in these four tables.','PAM picture index and sleep answers retain raw codes. Sleep display labels follow source EMA definition; no numeric sleep duration or PHQ score is inferred.','Recorded point chords are not verified street routes; transport unknown. No home inference.','Only four ZIP members downloaded; CRC/localSHA256 checked, wholearchiveMD5 not checked.']}
    participants=[];default_candidates=[]
    for uid,days in sorted(grouped.items()):
        pid='studentlife-'+uid;records=[];start=datetime.fromisoformat(min(days));end=datetime.fromisoformat(max(days));current=start
        while current<=end:
            date=current.date().isoformat();d=days.get(date,{'gps':[],'checkins':[]});ordered=sorted(d['gps'],key=lambda r:r['timestamp']);accepted=[];segment=0;last=None;excluded=Counter()
            for r in ordered:
                if not all(finite(r[k]) for k in ['latitude','longitude','timestamp']) or not -90<=r['latitude']<=90 or not -180<=r['longitude']<=180:excluded['invalidCoordinates']+=1;last=None;segment+=1;continue
                if not finite(r['accuracy']) or r['accuracy']<0 or r['accuracy']>100:excluded['accuracyExcluded']+=1;last=None;segment+=1;continue
                if last:
                    dt=r['timestamp']-last['timestamp']
                    reason='nonIncreasingTime' if dt<=0 else 'longGap' if dt>1800 else 'speedJump' if metres(last,r)/dt>55 else None
                    if reason:excluded[reason]+=1;segment+=1
                accepted.append((r,segment));last=r
            chosen=accepted
            if len(accepted)>80:
                indices=sorted({round(i*(len(accepted)-1)/79) for i in range(80)});chosen=[accepted[i] for i in indices]
            trips=[];previous=None;old_segment=None
            for r,seg in chosen:
                if previous is None or seg!=old_segment or r['timestamp']-previous['timestamp']>1800:
                    trips.append({'id':f'{pid}-{date}-{len(trips)}','mode':'unknown','points':[]})
                trips[-1]['points'].append({'lat':r['latitude'],'lon':r['longitude'],'timestamp':iso(r['timestamp']),'accuracy':r['accuracy']});previous=r;old_segment=seg
            for trip in trips:trip['startedAt']=trip['points'][0]['timestamp'];trip['endedAt']=trip['points'][-1]['timestamp']
            checks=sorted(d['checkins'],key=lambda x:x['timestamp']);summary={'sourcePoints':len(ordered),'qualityAcceptedPoints':len(accepted),'displayedPoints':len(chosen),'displaySamplingOmitted':len(accepted)-len(chosen),**excluded}
            record={'period':date,'date':date,'periodIndex':len(records),'participantId':pid,'subjectId':pid,'dayKey':pid+':'+date,'timeZone':'UTC','values':{},'trips':trips,'checkins':checks,'gpsSummary':summary,'movementStatus':'recorded_gps_present' if chosen else 'no_quality_accepted_gps' if ordered else 'gps_not_recorded','source':'StudentLife derivative; observed, not synthetic'}
            records.append(record);audit['counts'].update({'participantDays':1,'gpsDays':bool(ordered),'qualityGpsDays':bool(chosen),'checkinDays':bool(checks),'pairedGpsCheckinDays':bool(chosen and checks),'displayedPoints':len(chosen),'acceptedPoints':len(accepted),'displaySamplingOmitted':len(accepted)-len(chosen)});audit['counts'].update(excluded)
            if chosen and checks:
                points=[r for r,s in chosen];box=[min(r['longitude'] for r in points),min(r['latitude'] for r in points),max(r['longitude'] for r in points),max(r['latitude'] for r in points)]
                if box[0]>-72.32 and box[2]<-72.25 and box[1]>43.68 and box[3]<43.74 and (box[2]-box[0]>.004 or box[3]-box[1]>.003):default_candidates.append((len(checks),len(chosen),uid,len(records)-1,date,box))
            current+=timedelta(days=1)
        contextual=[{k:clean(v) for k,v in r.items()} for r in phq[phq.uid.astype(str)==uid].to_dict('records')]
        candidates=[(len(r['checkins']),len(r['trips']),i) for i,r in enumerate(records) if r['trips'] and r['checkins']];default=max(candidates)[2] if candidates else 0
        participants.append({'id':pid,'sourceId':uid,'name':'StudentLife '+uid,'datasetId':'studentlife','granularity':'day','synthetic':False,'timeZone':'UTC','records':records,'metrics':[],'baselineIndices':[],'baselineStatus':'unavailable','baselineReason':'No verified numeric health outcome scale is scored in this paired GPS/check-in source.','defaultIndex':default,'questionnaires':contextual,'source':source['title'],'caseSummary':'Recorded coordinates and raw mood/sleep check-ins from the same source participant.','sourceNotes':source['limitations']})
    best=max(default_candidates);audit['default']={'participantId':'studentlife-'+best[2],'index':best[3],'date':best[4],'bounds':best[5],'selection':'Most raw check-ins then displayed GPS points among Hanover-area paired days spanning at least0.004longitude or0.003latitude degrees; display convenience, not evidence of clinical severity.'};audit['counts']=dict(audit['counts']);audit['source']=source
    for p in participants:
        if p['id']==audit['default']['participantId']:p['defaultIndex']=audit['default']['index']
    bundle={'source':source,'participants':participants,'metrics':[],'defaultParticipantId':audit['default']['participantId'],'audit':audit}
    payload=json.dumps(bundle,separators=(',',':'),allow_nan=False);atomictext(ROOT/'data/studentlife-data.json',payload);atomictext(ROOT/'data/studentlife-data.js','window.STUDENTLIFE_DATA='+payload+';\n');atomictext(ROOT/'docs/studentlife-audit.json',json.dumps(audit,indent=2));print(json.dumps({'counts':audit['counts'],'default':audit['default'],'participants':len(participants),'bytes':len(payload)},indent=2))
if __name__=='__main__':main()
