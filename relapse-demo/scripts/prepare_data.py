"""Normalize PSYCHE-D published aggregate records without inventing daily samples.
Requires pandas + pyarrow. Run from any cwd; paths default to this workspace.
"""
from pathlib import Path
import argparse,hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.deps'))
import pyarrow.parquet as pq

METRICS=[
 {'id':'steps','label':'Daily steps (period mean)','unit':'steps','direction':'lower','floor':1000,'weight':1,'sourceColumn':'steps_awake_mean','definition':'Mean steps while awake in source feature window.'},
 {'id':'sleep_hours','label':'Sleep duration (recent mean)','unit':'h','direction':'both','floor':0.75,'weight':1,'sourceColumn':'sleep_asleep_mean_recent','definition':'Mean nightly minutes asleep over source last 4 days, divided by 60.'},
 {'id':'sleep_efficiency','label':'Weekday sleep efficiency','unit':'%','direction':'lower','floor':5,'weight':0.5,'sourceColumn':'sleep_ratio_asleep_in_bed_weekday_mean','definition':'Weekday mean asleep/in-bed ratio multiplied by 100.'},
 {'id':'bedtime_hour','label':'Sleep onset (adjusted hour)','unit':'h','direction':'both','floor':1,'weight':0.5,'sourceColumn':'sleep_main_start_hour_adj_median','definition':'Source adjusted sleep-start hour; 28 means 04:00 next day. Linear shifted scale, not ordinary clock hour.'},
 {'id':'short_sleep_nights','label':'Short sleep nights (source week)','unit':'nights','direction':'higher','floor':1,'weight':0.5,'sourceColumn':'sleep__hyposomnia_count_','definition':'Number of nights with less than 5 hours asleep in source last 7 days.'},
 {'id':'active_days','label':'Active days (source week)','unit':'days','direction':'lower','floor':1,'weight':0.5,'sourceColumn':'steps__active_day_count_','definition':'Days with >10,000 steps in source last 7 days.'}
]
def clean(x):
 try:
  x=float(x)
  return round(x,4) if math.isfinite(x) else None
 except (TypeError,ValueError):return None

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,default=ROOT.parent/'datasets/psyche_d/raw/anon_processed_df_parquet');ap.add_argument('--participants','--max-participants',type=int,default=8);ap.add_argument('--all',action='store_true',help='Include all IDs with at least nine observed monthly records');ap.add_argument('--include-short-histories',action='store_true',help='Include every observed participant, retaining insufficient-baseline cases');ap.add_argument('--output-dir',type=Path,default=ROOT/'data');a=ap.parse_args()
 if a.participants<1:ap.error('--participants must be positive')
 df=pq.read_table(a.input).to_pandas(); shape=list(df.shape)
 df['_subject']=[int(str(i).split('_')[0]) for i in df.index];df['_month']=[int(str(i).split('_')[1]) for i in df.index]
 if df.duplicated(['_subject','_month']).any():raise ValueError('Duplicate participant/month source records')
 if not df['_month'].between(1,12).all():raise ValueError('Study month outside documented 1..12 range')
 counts=df.groupby('_subject').size(); ids=sorted(counts.index if a.include_short_histories else counts[counts>=9].index)
 if not a.all:ids=ids[:a.participants]
 participants=[]
 for sid in ids:
  records=[]
  for key,row in df[df['_subject']==sid].sort_values('_month').iterrows():
   values={m['id']:clean(row[m['sourceColumn']]) for m in METRICS}
   if values['sleep_hours'] is not None:values['sleep_hours']=round(values['sleep_hours']/60,4)
   if values['sleep_efficiency'] is not None:values['sleep_efficiency']=round(values['sleep_efficiency']*100,4)
   month=int(row['_month'])
   records.append({'period':f'Month {month:02d}','periodIndex':month,'sourceRecordId':str(key),'values':values,'labels':{'phq9_start':clean(row['phq9_score_start']),'phq9_end':clean(row['phq9_score_end'])},'featureCompleteness':sum(v is not None for v in values.values())/len(values)})
  observed={r['periodIndex']:r for r in records}
  records=[observed.get(month,{'period':f'Month {month:02d}','periodIndex':month,'sourceRecordId':None,'values':{m['id']:None for m in METRICS},'labels':{'phq9_start':None,'phq9_end':None},'featureCompleteness':0,'missingPeriod':True}) for month in range(min(observed),max(observed)+1)]
  participants.append({'id':f'psyche-{sid}','name':f'Participant {sid:04d}','source':'PSYCHE-D','granularity':'month','baselineIndices':[i for i,r in enumerate(records) if not r.get('missingPeriod')][:3],'baselineStatus':'provisional','baselineReason':'First three available chronological months; no confirmed happy period. PHQ-9 endpoint labels excluded from baseline selection and scoring.','records':records,'unavailable':['heart_rate','location','routes','time_at_home','daily_mood','daily_records']})
 result={'schemaVersion':'1.0.0','title':'PSYCHE-D observed trajectories','participants':participants,'metrics':METRICS,'defaultWindowSize':2,'cohortStats':{'rows':shape[0],'columns':shape[1],'uniqueParticipants':int(df['_subject'].nunique()),'eligibleParticipants':int((counts>=9).sum()),'displayedParticipants':len(ids)},'selection':f'{len(ids)} numeric participant IDs with source histories retained, sorted numerically; no selection by worsening labels or model score. Descriptive sample, not validation cohort.','sourceNotes':['Records are monthly indexed aggregate feature snapshots, not daily measurements. Each feature has its own retrospective window.','Initial three observed months are a provisional reference, not a confirmed known-good or happy period.','Feature completeness measures available normalized features, not device wear-time coverage.','PHQ-9 labels describe source three-month endpoints and are shown only as contextual research labels, excluded from engine input values.','No heart-rate, route, GPS, at-home or daily mood observations exist in this selected data.','PHQ-9 start/end values can be missing and must not be interpolated or copied to neighboring months.'],'provenance':{'sourceUrl':'https://zenodo.org/records/5085146','version':'0.1','license':'CC BY-NC 4.0','sourceSha256':hashlib.sha256(a.input.read_bytes()).hexdigest(),'preparedOn':'2026-11-14','sourceShape':shape}}
 out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
 text=json.dumps(result,indent=2,allow_nan=False)
 (out/'demo-data.json').write_text(text,encoding='utf-8')
 (out/'demo-data.js').write_text('/* Generated from published research aggregates. See docs/data-notes.md. */\nwindow.DEMO_DATA = '+text+';\n',encoding='utf-8')
 report={'sourceShape':shape,'uniqueParticipants':int(df['_subject'].nunique()),'selectedIds':[int(i) for i in ids],'selectedRecords':sum(not r.get('missingPeriod',False) for p in participants for r in p['records']),'timelineSlots':sum(len(p['records']) for p in participants),'missingByMetric':{m['id']:sum(r['values'][m['id']] is None for p in participants for r in p['records']) for m in METRICS},'featureDefinitions':METRICS}
 (out/'data-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 print(json.dumps({k:v for k,v in report.items() if k!='featureDefinitions'},indent=2))
if __name__=='__main__':main()
