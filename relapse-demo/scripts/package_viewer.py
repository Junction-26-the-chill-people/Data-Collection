"""Package a standalone viewer, with all local assets and attribution, without research originals."""
from pathlib import Path
import hashlib,json,re,zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'work'/'WITHIN-demo.zip'
FILES=['index.html','app.js','engine.js','insights.js','styles.css','movement-map.js','movement-map.css','locations.html','location-explorer.js','location-explorer.css','ATTRIBUTION.md','CHANGELOG.md','AGENTS.md','START-DEMO.cmd','STOP-DEMO.cmd','scripts/preview_server.py','data/demo-data.js','data/nfi-overview.js','data/map-streets.js','data/location-samples.js','docs/PSYCHE-D-LICENSE.pdf','docs/engine.md','docs/maps.md','docs/location-dataset-audit.md','docs/location-dataset-audit.json','docs/verification.md','docs/location-followup.md','docs/performance-review.md','docs/presentation-integration.md']
FILES += ['release.json','data/studentlife-data.js','data/hanover-streets.js','docs/studentlife.md','docs/studentlife-audit.json','docs/paired-daily-data.md','docs/noteworthy-display.md','docs/paired-review.md']
FILES += ['companion-signals.js','tour.js','favicon.svg','docs/integration-contract.md','docs/v2-monthly-preservation.json','docs/v2-test-results.json','docs/synthetic-story-checks.json','docs/repository-tests.json']
FILES += [str(p.relative_to(ROOT)).replace('\\','/') for p in sorted((ROOT/'data').glob('neighborhood-*.js'))]
FILES += [str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'vendor').rglob('*') if p.is_file()]
README='''# WITHIN demo - daily-linked/1.5.0 (within-ui/3.0.0)\n\nExtract this entire ZIP into a folder, then open index.html. Click Demo tour (or open index.html?tour=1) for a guided 11-step walkthrough. Teammate component integration: docs/integration-contract.md. Keep the data and vendor folders beside it.\n\nStart with Selected day; use previous/next or the date picker. Summaries show meaningful changes; Show all measurements reveals everything. Sofia on 2026-03-10 illustrates one harder day: noted, never flagged on its own. Noah shows a sustained pattern and Mila a slow drift against her original anchor. The Personal/Clinical switch changes detail while preserving the assessment. The map includes local streets, buildings and parks; no internet or server is needed for that layout. locations.html opens the independent GPS-source explorer.\n\nOptional online street tiles: use START-DEMO.cmd (requires an installed Python 3 runtime). STOP-DEMO.cmd ends the preview. Online tiles are optional.\n\nThis viewer contains all 4,948 PSYCHE-D research histories and eleven separately identified daily stories. Choose StudentLife - GPS + check-ins for49sourceIDs,3,389days and2,116days with same-person GPS/check-ins. The default StudentLife10/2013-03-30 has an offline Hanover street map. This recorded source remains unscored; raw responses are not silently converted to mood or risk. The GPS explorer includes 50 source trajectories from a 10,000-trajectory audit. Do not join those traces to a health record. See ATTRIBUTION.md for source licenses and transformations. The index is an experimental behavior-change measure, not a calibrated relapse probability.\n\nCompare release.json and CHANGELOG.md before integration; asset-manifest.json records the exact viewer files. See docs/studentlife.md and docs/paired-daily-data.md for source linkage. This is a viewer package, not the complete raw research archive or reproducible preprocessing environment. Full working sources: https://github.com/Junction-26-the-chill-people/Data-Collection/tree/main/relapse-demo.\n'''
OUT.parent.mkdir(exist_ok=True)
manifest={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in FILES}
for html in ['index.html','locations.html']:
 for target in re.findall(r'(?:src|href)="([^"#]+)"',(ROOT/html).read_text(encoding='utf-8-sig')):
  if target.startswith(('http:','https:')):continue
  assert target.split('#')[0] in manifest,(html,target)
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
 for p in FILES:z.write(ROOT/p,'WITHIN-demo/'+p)
 z.writestr('WITHIN-demo/README.md',README)
 z.writestr('WITHIN-demo/asset-manifest.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(OUT) as z:
 assert z.testzip() is None
 for p,digest in manifest.items():assert hashlib.sha256(z.read('WITHIN-demo/'+p)).hexdigest()==digest
print(json.dumps({'archive':str(OUT),'files':len(FILES)+2,'bytes':OUT.stat().st_size,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'localHTMLDependenciesVerified':True},indent=2))
