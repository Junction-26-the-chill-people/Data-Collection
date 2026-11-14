"""Verify downloaded originals without loading dataset objects or making network requests."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parents[1]/'datasets'
m=json.loads((root/'download-manifest.json').read_text(encoding='utf-8'))
verified=missing=failed=0
for f in m['files']:
 p=root/f['dataset']/'raw'/f['filename']
 if not p.is_file():
  missing+=1;print('MISSING',f['dataset'],f['filename']);continue
 alg=f['algorithm'];h=hashlib.sha1() if alg=='git-sha1' else hashlib.new(alg)
 sha=hashlib.sha256()
 if alg=='git-sha1':h.update(('blob '+str(p.stat().st_size)+'\0').encode())
 with p.open('rb') as stream:
  while chunk:=stream.read(8*1024*1024):h.update(chunk);sha.update(chunk)
 ok=p.stat().st_size==f['size'] and h.hexdigest()==f['expected']
 if f.get('sha256'):ok=ok and sha.hexdigest()==f['sha256']
 if ok:verified+=1
 else:failed+=1;print('CHECKSUM_FAILED',f['dataset'],f['filename'])
print(f'Verified={verified}; missing={missing}; corrupt={failed}')
sys.exit(1 if missing or failed else 0)
