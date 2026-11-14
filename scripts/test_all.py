"""Run every existing JS/Python suite from a fresh checkout, without npm."""
from pathlib import Path
import argparse,json,subprocess,sys,datetime,re
from bootstrap import bootstrap

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--node',default='node');args=parser.parse_args()
    bootstrap();demo=ROOT/'relapse-demo';report={'startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'javascript':[]}
    for test in sorted((demo/'tests').glob('*.cjs')):
        run=subprocess.run([args.node,str(test)],cwd=demo,capture_output=True,text=True,encoding='utf-8',errors='replace')
        output=(run.stdout+run.stderr).strip();print(test.name+': '+output,flush=True)
        report['javascript'].append({'file':test.name,'exitCode':run.returncode,'output':output})
    run=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py'],cwd=demo,capture_output=True,text=True,encoding='utf-8',errors='replace')
    output=(run.stdout+run.stderr).strip();print('PYTHON: '+output,flush=True)
    count=re.search(r'Ran (\d+) tests',output)
    report['python']={'exitCode':run.returncode,'tests':int(count[1]) if count else None,'output':output}
    report['passed']=run.returncode==0 and all(t['exitCode']==0 for t in report['javascript'])
    report['completedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    (demo/'work/repository-tests.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':report['passed'],'javascriptSuites':len(report['javascript']),'pythonTests':report['python']['tests']}))
    return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
