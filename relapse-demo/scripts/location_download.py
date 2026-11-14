"""Verify saved GPS originals; optionally restore missing files from pinned URLs.
Existing mismatched originals are never overwritten. No publisher code is run.
"""
import argparse,hashlib,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent/'datasets/location_sources'

def verify(payload,entry):
    if len(payload)!=entry['bytes']:raise ValueError('size mismatch: '+entry['file'])
    if hashlib.sha256(payload).hexdigest()!=entry['sha256']:raise ValueError('SHA256 mismatch: '+entry['file'])
    digest=hashlib.sha256(payload).hexdigest() if entry['publisherAlgorithm']=='sha256' else hashlib.sha1(b'blob '+str(len(payload)).encode()+b'\0'+payload).hexdigest()
    if digest!=entry['publisherChecksum']:raise ValueError('publisher checksum mismatch: '+entry['file'])

def main(download=False):
    manifest=json.loads((BASE/'syn_roadgps_download_manifest.json').read_text(encoding='utf-8'))
    raw=BASE/'syn_roadgps/raw';raw.mkdir(parents=True,exist_ok=True)
    for entry in manifest['files']:
        path=raw/entry['file']
        if path.parent!=raw or Path(entry['file']).name!=entry['file']:raise ValueError('invalid manifest filename')
        if path.exists():payload=path.read_bytes()
        elif download:
            url=entry['url'];prefix='https://huggingface.co/datasets/Smile1120/SYN-RoadGps/resolve/'+manifest['revision']+'/'
            if not url.startswith(prefix):raise ValueError('URL is not the pinned public source')
            with urllib.request.urlopen(url,timeout=90) as response:payload=response.read(entry['bytes']+1)
            verify(payload,entry)
            with path.open('xb') as output:output.write(payload)
        else:raise FileNotFoundError(str(path)+'; use --download to restore pinned missing files')
        verify(payload,entry);print('Verified',entry['file'],len(payload))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--download',action='store_true');args=parser.parse_args();main(args.download)
