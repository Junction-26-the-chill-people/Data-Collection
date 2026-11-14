"""Decode inert numeric buffers and primitive lists after static pickle inspection.
No pickle objects, reducers or named constructors are executed.
"""
from pathlib import Path
import json,struct,math,hashlib,collections
from inspect_nfi_static import inspect_pickle
ROOT=Path(__file__).resolve().parents[1]
def array(node):
 if node['callable']['global']=='pandas._libs.arrays.__pyx_unpickle_NDArrayBacked':return array(node['state'][1])
 state=node['state'];shape=state[1];dtype=state[2]['args'][0];raw=state[4];count=math.prod(shape)
 if state[3]:raise ValueError('Fortran layout not implemented')
 if isinstance(raw,list):
  if len(raw)!=count:raise ValueError('Object buffer shape mismatch')
  return raw,shape,dtype
 formats={'f8':'d','i8':'q','M8':'q','f4':'f','i4':'i','b1':'?','u8':'Q'}
 if dtype not in formats:raise ValueError('Unsupported static dtype '+dtype)
 if state[3]:raise ValueError('Fortran layout not implemented')
 endian=state[2].get('state',(None,'<'))[1]
 if endian not in ('<','>','='):raise ValueError('Unsupported byte order')
 import sys
 if endian=='=':endian='<' if sys.byteorder=='little' else '>'
 fmt=endian+formats[dtype]
 vals=[v[0] for v in struct.iter_unpack(fmt,raw)]
 if len(vals)!=count:raise ValueError('Numeric buffer shape mismatch')
 return vals,shape,dtype

def columns(tree):
 blocks,axes=tree['state']['_mgr']['args'];names=array(axes[0]['args'][1]['data'])[0];index=axes[1]['args'][1];n=len(range(index['start'],index['stop'],index['step']));out={};dtypes={}
 for block in blocks:
  values,placement,_=block['args'];flat,shape,dtype=array(values)
  if len(shape)!=2 or shape[1]!=n:raise ValueError('Block row shape mismatch')
  positions=list(range(*placement['args']))
  if len(positions)!=shape[0]:raise ValueError('Block column shape mismatch')
  for j,pos in enumerate(positions):out[names[pos]]=flat[j*n:(j+1)*n];dtypes[names[pos]]=dtype
 if len(out)!=len(names):raise ValueError('Missing or duplicate column placement')
 return out,n,dtypes
def main():
 manifest=json.loads((ROOT.parent/'datasets/download-manifest.json').read_text())
 results=[]
 for p in (ROOT.parent/'datasets/nfi_fared_digital_traces/raw').glob('*.pkl'):
  expected=next(x['sha256'] for x in manifest['files'] if x['dataset']=='nfi_fared_digital_traces' and x['filename']==p.name)
  if hashlib.sha256(p.read_bytes()).hexdigest()!=expected:raise ValueError('Publisher checksum mismatch')
  c,n,dtypes=columns(inspect_pickle(p));summary={'file':p.name,'rows':n,'columns':list(c),'subjects':dict(collections.Counter(c['META_test_subject'])),'activityCounts':dict(collections.Counter(c['META_label_activity'])),'phones':dict(collections.Counter(c['META_telephone_type'])),'numericSummary':{}}
  for name,values in c.items():
   if dtypes[name]=='M8' or name.startswith('META_') or not values or not isinstance(values[0],(float,int)):continue
   finite=[x for x in values if isinstance(x,(float,int)) and math.isfinite(x)]
   if finite:summary['numericSummary'][name]={'finite':len(finite),'missing':n-len(finite),'min':min(finite),'max':max(finite),'mean':sum(finite)/len(finite)}
  results.append(summary);print(p.name,n,'rows',len(c),'columns',flush=True)
 report={'method':'Non-executing pickle opcode inspection + struct decoding of primitive numeric buffers. No global/reducer/constructor executed. Column shapes and publisher checksums validated.','files':results,'totalTraceRows':sum(f['rows'] for f in results),'gpsCoordinatesAvailable':False,'warning':'Rows across traces overlap in time and devices; do not sum as independent participants or activity duration. No depression labels or reliable geocoordinates.'}
 (ROOT/'docs/nfi-data-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 (ROOT/'data/nfi-overview.js').write_text('window.NFI_AUDIT='+json.dumps(report,separators=(',',':'))+';',encoding='utf-8')
 print('Total trace rows',report['totalTraceRows'])

if __name__=='__main__':main()
