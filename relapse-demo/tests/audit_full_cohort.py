"""Independent full-source/cohort audit. No clinical-performance estimates.
Run after: python scripts/prepare_data.py --all --output-dir .tmp/full-cohort
"""
from pathlib import Path
import argparse,csv,hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.deps'))
import pyarrow.parquet as pq
import pandas as pd
source=ROOT.parent/'datasets/psyche_d/raw/anon_processed_df_parquet'
df=pq.read_table(source).to_pandas()
with (source.parent/'Feature explanations - anonymized data - Sheet1.tsv').open(encoding='utf-8-sig') as f: dictionary={r['Feature name']:r for r in csv.DictReader(f,delimiter='\t')}
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,default=ROOT/'.tmp/full-cohort/demo-data.json');ap.add_argument('--output',type=Path,default=ROOT/'docs/full-cohort-audit.json');args=ap.parse_args()
data=json.loads(args.input.read_text())
source_stats={};baseline={};errors=[]
bounds={'steps':(0,None),'sleep_hours':(0,24),'sleep_efficiency':(0,100),'bedtime_hour':(0,48),'short_sleep_nights':(0,7),'active_days':(0,7)}
for m in data['metrics']:
 col=m['sourceColumn'];series=df[col];factor=1/60 if m['id']=='sleep_hours' else 100 if m['id']=='sleep_efficiency' else 1
 v=series*factor;lo,hi=bounds[m['id']]
 source_stats[m['id']]={'sourceColumn':col,'sourceDefinition':dictionary[col]['Description'],'sourceNotes':dictionary[col]['Notes'],'transformationFactor':factor,'missing':int(series.isna().sum()),'zero':int((v==0).sum()),'min':float(v.min()),'max':float(v.max()),'outsideLogicalBounds':int(((v<lo)|((v>hi) if hi is not None else False)).sum()),'infinite':int((~series.isna() & ~series.map(lambda x:math.isfinite(x))).sum())}
 baseline[m['id']]={'eligibleReferenceSets':0,'floorDominated':0,'referenceContainsZero':0,'constantReference':0}
observed=padded=mapped=0;baseline_labels={'participantsWithAnyReferenceEndpoint':0,'participantsWithAnyReferenceEndpointAtLeast10':0,'participantsWithNoReferenceEndpoint':0}
for p in data['participants']:
 periods=[r['periodIndex'] for r in p['records']]
 assert len(periods)==len(set(periods))
 assert all(b-a==1 for a,b in zip(periods,periods[1:]))
 selected=[p['records'][i] for i in p['baselineIndices']]
 assert len(selected)==min(3,sum(not r.get('missingPeriod') for r in p['records'])) and all(not r.get('missingPeriod') for r in selected)
 labels=[r['labels']['phq9_end'] for r in selected if r['labels']['phq9_end'] is not None]
 baseline_labels['participantsWithAnyReferenceEndpoint']+=bool(labels)
 baseline_labels['participantsWithAnyReferenceEndpointAtLeast10']+=any(v>=10 for v in labels)
 baseline_labels['participantsWithNoReferenceEndpoint']+=not bool(labels)
 for m in data['metrics']:
  vals=[r['values'][m['id']] for r in selected if r['values'][m['id']] is not None]
  if len(vals)<3:continue
  center=float(pd.Series(vals).median());mad=float(pd.Series([abs(v-center) for v in vals]).median());b=baseline[m['id']]
  b['eligibleReferenceSets']+=1;b['floorDominated']+=1.4826*mad<=m['floor'];b['referenceContainsZero']+=0 in vals;b['constantReference']+=max(vals)==min(vals)
 for r in p['records']:
  if r.get('missingPeriod'):
   padded+=1;assert all(v is None for v in r['values'].values());assert all(v is None for v in r['labels'].values());continue
  observed+=1;row=df.loc[r['sourceRecordId']]
  for m in data['metrics']:
   raw=float(row[m['sourceColumn']]);actual=r['values'][m['id']]
   if math.isnan(raw):assert actual is None;continue
   # Exact transformation order currently used by normalization, independently reconstructed.
   expected=round(raw,4)
   if m['id']=='sleep_hours':expected=round(expected/60,4)
   if m['id']=='sleep_efficiency':expected=round(expected*100,4)
   assert actual==expected,(r['sourceRecordId'],m['id'],actual,expected)
   mapped+=1
cols=[m['sourceColumn'] for m in data['metrics']]
corr=df[cols].corr(method='spearman').round(4)
report={'scope':data['selection']+' All source rows are also inspected for ranges and missingness.','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sourceRows':len(df),'sourceParticipants':int(df.index.to_series().str.split('_').str[0].nunique()),'auditedParticipants':len(data['participants']),'excludedParticipants':4948-len(data['participants']),'participantsWithFewerThanThreeObservedRecords':sum(sum(not r.get('missingPeriod') for r in p['records'])<3 for p in data['participants']),'observedRecords':observed,'explicitMissingSlots':padded,'exactMappedValuesChecked':mapped,'metrics':source_stats,'baselineQuality':baseline,'referenceEndpointContext':baseline_labels,'spearmanCorrelations':{m['id']:{n['id']:float(corr.loc[m['sourceColumn'],n['sourceColumn']]) for n in data['metrics']} for m in data['metrics']},'cautions':['PHQ endpoint context is not contemporaneous daily mood or a validated baseline label.','Zero recorded sleep can reflect measurement or preprocessing artifacts; absence of sleep is not established.','No clinical prediction/accuracy is measured by this audit.','Eligibility selects longer observed histories and cannot generalize to short-history or poorly monitored users.']}
args.output.write_text(json.dumps(report,indent=2,allow_nan=False),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['spearmanCorrelations','metrics']},indent=2))
