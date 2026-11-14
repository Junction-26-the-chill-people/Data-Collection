'use strict';
// Software scenario checks only: deliberately generated behaviors, not clinical validation.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),E=require(path.join(root,'engine.js'));
const d=JSON.parse(fs.readFileSync(path.join(root,'data/demo-data.json'),'utf8'));
const results={},daily={};
for(const p of d.participants.filter(p=>p.synthetic)){
 const a=E.analyze(p.records,{metrics:p.metrics,baselineIndices:p.baselineIndices,windowSize:7,adaptive:true});
 daily[p.id]=E.analyze(p.records,{metrics:p.metrics,baselineIndices:p.baselineIndices,windowSize:1,granularity:'day',adaptive:true});
 const avg=(lo,hi)=>{const v=a.points.slice(lo,hi).map(q=>q.anchoredScore).filter(Number.isFinite);return v.reduce((x,y)=>x+y,0)/v.length;};
 results[p.id]={name:p.name,earlyMean:avg(28,40),lateMean:avg(95,120),peak:Math.max(...a.points.map(q=>q.anchoredScore||0)),latest:a.latest.anchoredScore};
 results[p.id].states=Object.fromEntries([...new Set(daily[p.id].points.map(q=>q.alertState))].map(state=>[state,daily[p.id].points.filter(q=>q.alertState===state).length]));results[p.id].firstFlagIndex=daily[p.id].alerting.firstFlagIndex;results[p.id].latestState=daily[p.id].latest.alertState;
 for(const q of a.points)if(Number.isFinite(q.score))assert(q.score>=0&&q.score<=100);
}
for(const id of ['sim-02','sim-08']){assert(results[id].lateMean>results[id].earlyMean+30);assert(results[id].lateMean>results['sim-01'].lateMean+30);}
assert(results['sim-01'].lateMean<5);
for(const id of ['sim-03','sim-06']){assert(results[id].peak>30);assert(results[id].latest<10);}
for(const id of ['sim-02','sim-08'])assert(daily[id].points.slice(80).some(q=>q.alertState==='flag_sustained'),id+' sustained phase');
assert.equal(daily['sim-09'].points[64].alertState,'noted');assert.equal(daily['sim-09'].points[64].status,'no_change');assert.equal(daily['sim-09'].points[65].alertState,'steady');
for(const id of ['sim-01','sim-07'])assert(!daily[id].points.some(q=>q.alertState.startsWith('flag_')),id+' must not flag');
assert(daily['sim-03'].points.slice(44,81).some(q=>q.alertState.startsWith('flag_')));assert.equal(daily['sim-03'].latest.alertState,'steady');
assert(daily['sim-06'].points.slice(44,65).some(q=>q.alertState==='flag_drift'&&q.contextNote),'Illness must annotate, never erase anchor drift');assert.equal(daily['sim-06'].latest.alertState,'steady');
results['sim-11'].slowDrift=require('../scripts/verify_story_alerts.cjs')(d);
fs.writeFileSync(path.join(root,'docs/synthetic-story-checks.json'),JSON.stringify({interpretation:'Generated software scenarios; no clinical validation or real-patient outcome claims',modelVersion:E.MODEL_VERSION,results},null,2));
console.log('PASS: 11 preserved/authored stories; sustained Noah/Jonas, noted Sofia, slow-drift Mila, stable Mara/Ada, recovery Lea/Emil, and bounded outputs');
