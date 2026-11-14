"""Check the shipped data inventory, without executing or downloading source files."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'datasets/repository-manifest.json').read_text(encoding='utf-8'))
failures=[]
for entry in manifest['files']:
    path=(ROOT/entry['path']).resolve()
    if not path.is_relative_to(ROOT.resolve()):raise ValueError('Path escapes repository')
    if not path.is_file():failures.append(entry['path']+' missing');continue
    if path.stat().st_size!=entry['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest()!=entry['sha256']:failures.append(entry['path']+' checksum mismatch')
print(json.dumps({'checkedFiles':len(manifest['files']),'failures':failures},indent=2))
sys.exit(bool(failures))
