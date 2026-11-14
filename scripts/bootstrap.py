"""Restore exact, bundled data archives. Standard library only; no downloads."""
from pathlib import Path
import gzip,hashlib,json

ROOT=Path(__file__).resolve().parents[1]

def contained(relative):
    path=(ROOT/relative).resolve()
    if not path.is_relative_to(ROOT.resolve()):raise ValueError('Path escapes repository')
    return path

def bootstrap():
    manifest=json.loads((ROOT/'datasets/archive-manifest.json').read_text(encoding='utf-8'))
    for entry in manifest['archives']:
        archive=contained(entry['archive']);target=contained(entry['target'])
        packed=archive.read_bytes()
        if hashlib.sha256(packed).hexdigest()!=entry['archiveSha256']:raise ValueError('Archive checksum mismatch: '+entry['archive'])
        if target.exists():
            payload=target.read_bytes()
            if len(payload)!=entry['bytes'] or hashlib.sha256(payload).hexdigest()!=entry['sha256']:
                raise ValueError('Existing data differs; refusing overwrite: '+entry['target'])
            print('Verified existing',entry['target']);continue
        payload=gzip.decompress(packed)
        if len(payload)!=entry['bytes'] or hashlib.sha256(payload).hexdigest()!=entry['sha256']:raise ValueError('Restored checksum mismatch: '+entry['target'])
        target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as f:f.write(payload)
        print('Restored',entry['target'])
    (ROOT/'relapse-demo/.tmp').mkdir(exist_ok=True)
    (ROOT/'relapse-demo/work').mkdir(exist_ok=True)

if __name__=='__main__':bootstrap()
