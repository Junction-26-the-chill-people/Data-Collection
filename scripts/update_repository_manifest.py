"""Explicitly refresh the shipped dataset inventory after reviewed changes."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
restored={entry['target'] for entry in json.loads((ROOT/'datasets/archive-manifest.json').read_text())['archives']}
files=[]
for folder in [ROOT/'datasets',ROOT/'relapse-demo/data']:
    for path in sorted(folder.rglob('*')):
        if not path.is_file():continue
        relative=path.relative_to(ROOT).as_posix()
        if relative in restored or relative=='datasets/repository-manifest.json' or path.name.endswith(('.part','.pyc')):continue
        if ('nfi_fared_digital_traces' in path.parts and 'raw' in path.parts) or path.name=='sample_dataset.tar.bz2':continue
        files.append({'path':relative,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
manifest={'version':'repository-data/1.0.0','release':'daily-linked/1.5.0','note':'Inventory of shipped files, distinct from original publisher download availability. Restored archive targets are checked by bootstrap.py. No clinical validation is implied.','files':files}
(ROOT/'datasets/repository-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'files':len(files),'bytes':sum(f['bytes'] for f in files),'largestBytes':max(f['bytes'] for f in files)}))
