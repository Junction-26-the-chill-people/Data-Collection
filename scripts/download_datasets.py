from pathlib import Path
import concurrent.futures,hashlib,json,time,urllib.request,urllib.error,urllib.parse
ROOT=Path(__file__).resolve().parents[1]/'datasets'
UA={'User-Agent':'Junction26-research-download/1.0'}
def load(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
hf=load('hf_info_metadata.json'); tree=load('hf_tree_metadata.json'); z=load('zenodo_metadata.json'); dry=load('dryad_files.json')
tasks=[]
for f in tree:
 if f['type']!='file':continue
 name=f['path']; lfs=f.get('lfs',{})
 tasks.append(dict(dataset='nfi_fared_digital_traces',filename=name,url='https://huggingface.co/datasets/'+hf['id']+'/resolve/'+hf['sha']+'/'+urllib.parse.quote(name),size=f['size'],algorithm='sha256' if lfs else 'git-sha1',expected=lfs.get('oid',f['oid']),revision=hf['sha']))
for f in z['files']:
 alg,checksum=f['checksum'].split(':',1)
 tasks.append(dict(dataset='psyche_d',filename=f['key'],url=f['links']['self'],size=f['size'],algorithm=alg,expected=checksum,revision='5085146'))
for f in dry['_embedded']['stash:files']:
 tasks.append(dict(dataset='finnish_immigrants',filename=f['path'],url='https://datadryad.org'+f['_links']['stash:download']['href'],size=f['size'],algorithm='sha256',expected=f['digest'],revision='410377'))

def verify(path,t):
 h=hashlib.sha256(); expected=hashlib.md5() if t['algorithm']=='md5' else hashlib.sha1() if t['algorithm']=='git-sha1' else hashlib.sha256()
 if t['algorithm']=='git-sha1':expected.update(('blob '+str(path.stat().st_size)+'\0').encode())
 with path.open('rb') as inp:
  while b:=inp.read(8*1024*1024):h.update(b);expected.update(b)
 if path.stat().st_size!=t['size'] or expected.hexdigest()!=t['expected']:raise ValueError('Size/checksum mismatch: '+t['filename'])
 return h.hexdigest()

def download(t):
 path=ROOT/t['dataset']/'raw'/t['filename'];path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():
  sha=verify(path,t);return dict(t,status='verified',sha256=sha,local_path=str(path))
 part=path.with_name(path.name+'.part')
 for attempt in range(1,4):
  try:
   offset=part.stat().st_size if part.exists() else 0
   if offset<t['size']:
    headers=dict(UA)
    if offset:headers['Range']='bytes='+str(offset)+'-'
    with urllib.request.urlopen(urllib.request.Request(t['url'],headers=headers),timeout=90) as response:
     if response.status!=206:offset=0
     with part.open('ab' if offset else 'wb') as out:
      done=offset;last=time.monotonic()
      while chunk:=response.read(4*1024*1024):
       out.write(chunk);done+=len(chunk)
       if time.monotonic()-last>20:
        print(t['dataset'],t['filename'],round(done/t['size']*100,1),'percent',flush=True);last=time.monotonic()
   sha=verify(part,t);part.replace(path)
   print('VERIFIED',t['dataset'],t['filename'],t['size'],flush=True)
   return dict(t,status='verified',sha256=sha,local_path=str(path))
  except Exception as e:
   print('RETRY',attempt,t['filename'],type(e).__name__,str(e)[:250],flush=True)
   if isinstance(e,ValueError) and part.exists():part.unlink()
   if attempt==3:return dict(t,status='failed',error=str(e))
   time.sleep(2)

results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for future in concurrent.futures.as_completed([ex.submit(download,t) for t in tasks]):
  results.append(future.result())
  (ROOT/'download-manifest.json').write_text(json.dumps({'downloaded_on':'2026-11-14','files':results},indent=2),encoding='utf-8')
print('SUMMARY',len(results),'files,',sum(t['status']=='verified' for t in results),'verified,',sum(t['size'] for t in results if t['status']=='verified'),'bytes',flush=True)
