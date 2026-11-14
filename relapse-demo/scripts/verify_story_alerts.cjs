'use strict';
// Deliberately authored software story, not model calibration or clinical validation.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const E=require('../engine.js');
function verifyMila(data){
 const p=data.participants.find(p=>p.id==='sim-11');assert(p,'Mila must be present');
 assert.equal(p.records.length,120);assert.deepEqual(p.baselineIndices,Array.from({length:28},(_,i)=>i));
 const analysis=E.analyze(p.records,{metrics:p.metrics,baselineIndices:p.baselineIndices,granularity:'day',windowSize:1,adaptive:true});
 const firstDriftIndex=analysis.points.findIndex(q=>q.alertState==='flag_drift');
 const firstSustainedIndex=analysis.points.findIndex(q=>q.alertState==='flag_sustained');
 assert(firstDriftIndex>=79&&firstDriftIndex<=99,'First slow drift must occur on Day80?100');
 assert(firstSustainedIndex<0||firstSustainedIndex>=firstDriftIndex,'Sustained must not precede slow drift');
 for(let i=28;i<70;i++)assert(analysis.points.slice(Math.max(28,i-6),i+1).filter(q=>q.score>=35).length<=2,'No early high-day cluster');
 assert.equal(analysis.points[p.defaultIndex].alertState,'flag_drift','Default story view must show drift');
 return {seed:p.generatorParameters.seed,firstDriftIndex,firstDriftDay:firstDriftIndex+1,firstDriftDate:p.records[firstDriftIndex].date,firstSustainedIndex:firstSustainedIndex<0?null:firstSustainedIndex,defaultIndex:p.defaultIndex,signalAtFirstDrift:analysis.points[firstDriftIndex].score,domains:analysis.points[firstDriftIndex].drift.domains};
}
module.exports=verifyMila;
if(require.main===module){const filename=process.argv[2]||path.join(__dirname,'../data/demo-data.json');console.log(JSON.stringify({modelVersion:E.MODEL_VERSION,mila:verifyMila(JSON.parse(fs.readFileSync(filename,'utf8')))},null,2));}
