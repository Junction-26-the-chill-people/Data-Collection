const assert=require('node:assert/strict'),E=require('../engine.js');
const metrics=[{id:'steps',direction:'lower',floor:1000},{id:'sleep_hours',direction:'lower',floor:.5}];
const rec=(i,steps=8000,mood=4,contexts=[])=>({periodIndex:i,period:'Day '+i,values:{steps,sleep_hours:mood},contexts});
const opts={metrics,baselineIndices:[0,1,2],windowSize:2,minBaseline:3,adaptive:true,adaptiveWeight:.15,adaptiveAlpha:.1,contextWeights:{illness:.5,recovery:.75,intentional_activity_change:.5}};
const rows=Array.from({length:25},(_,i)=>rec(i,i<3?8000:7500,i<3?4:3.8));
let r=E.analyze(rows,opts),last=r.latest;
assert.ok(last.adaptation.metrics.steps.effective<8000);assert.ok(last.adaptation.metrics.steps.effective>7500);
assert.ok(last.adaptation.updates.every(u=>u.index<last.windowIndices[0]));
const mutated=rows.map(x=>({...x,values:{...x.values}}));mutated[24].values.steps=0;mutated[23].values.steps=0;
assert.deepEqual(E.analyze(mutated,opts).latest.adaptation,last.adaptation); // Current comparison cannot train its own reference.
assert.deepEqual(E.analyze(rows.slice(0,16),opts).points,r.points.slice(0,16));
const decline=Array.from({length:40},(_,i)=>rec(i,i<3?8000:1000,i<3?4:1));r=E.analyze(decline,opts);assert.equal(r.latest.adaptation.metrics.steps.effective,8000);assert.equal(r.latest.rawScore,r.latest.anchoredScore);assert.equal(r.latest.score,100);assert.equal(r.latest.normalizedIndex,1);assert.equal(r.latest.relapseVector,1);
assert.ok(r.latest.adaptation.updates.every(u=>u.reason==='anchored_adverse_shift'));
const illness={type:'illness',confirmed:true,source:'synthetic'};const sick=decline.map((x,i)=>({...x,contexts:i>=3?[illness]:[]}));r=E.analyze(sick,opts);assert.equal(r.latest.rawScore,100);assert.equal(r.latest.score,50);assert.equal(r.latest.normalizedIndex,.5);assert.equal(r.latest.contextMultiplier,.5);assert.ok(r.latest.adaptation.updates.every(u=>u.reason==='confirmed_context'));
const unconfirmed=sick.map(x=>({...x,contexts:[{...illness,confirmed:false}]}));assert.equal(E.analyze(unconfirmed,opts).latest.score,100);
const noSource=sick.map(x=>({...x,contexts:[{type:'illness',confirmed:true}]}));assert.equal(E.analyze(noSource,opts).latest.score,100);
const disabled=E.analyze(sick,{...opts,contextWeights:{illness:1,recovery:1,intentional_activity_change:1}});assert.equal(disabled.latest.score,100);assert.equal(disabled.latest.adaptation.metrics.steps.effective,8000);
const recovered=[...decline,...Array.from({length:5},(_,i)=>rec(40+i))];assert.equal(E.analyze(recovered,opts).latest.score,0);
const improve=[...decline.slice(0,3),...Array.from({length:10},(_,i)=>rec(i+3,10000,5))];assert.equal(E.analyze(improve,opts).latest.score,0);
const single=E.analyze([rec(0),rec(1,1000,1),rec(2,1000,1)],{...opts,baselineIndices:[0],minBaseline:1});assert.equal(single.baseline.quality,'low_evidence');assert.ok(single.baseline.warning.includes('variability is unknown'));assert.equal(single.latest.score,100);
assert.equal(E.analyze(rows,{metrics,baselineIndices:[0,1,2],granularity:'day'}).latest.score,null);
const end=E.analyze(rows,{...opts,referenceEndIndex:5});assert.equal(end.points[6].status,'collecting_window');assert.equal(end.baseline.endIndex,5);assert.throws(()=>E.analyze(rows,{...opts,referenceEndIndex:1}),RangeError);
assert.throws(()=>E.analyze(rows,{...opts,adaptiveWeight:.9}),RangeError);
console.log('PASS: adaptation excludes current window/future observations, freezes adverse shifts and confirmed context, preserves anchor, context provenance/downweighting, directional recovery/improvement, explicit low-evidence baseline and reference-end boundary.');

const moderate=[rec(0),rec(1),rec(2),rec(3,6000,3,[illness]),rec(4,6000,3,[illness])];const mod=E.analyze(moderate,{...opts,windowSize:2});assert.equal(mod.latest.anchoredScore,33);assert.equal(mod.latest.score,17);assert.equal(mod.latest.status,'change_detected');assert.ok(!mod.latest.explanation.startsWith('No substantial'));assert.equal(mod.latest.index,4);assert.equal(mod.latest.relapseVector,.17);assert.equal(E.analyze(moderate,{metrics,baselineIndices:[0,1,2],windowSize:2}).latest.contextMultiplier,1);
console.log('PASS: confirmed context never downgrades unadjusted change status; neutral defaults and ordinal index compatibility.');

const oneDay=[rec(0),rec(1),rec(2),...Array.from({length:7},(_,i)=>rec(i+3,1000,1,i===6?[illness]:[]))];const overlap=E.analyze(oneDay,{...opts,windowSize:7});assert.ok(Math.abs(overlap.latest.contributors[0].contextMultiplier-(1-.5/7))<1e-12);assert.equal(overlap.latest.score,93);assert.equal(overlap.latest.status,'review_suggested');
const moodRecords=Array.from({length:10},(_,i)=>({periodIndex:i,values:{steps:i<3?8000:1000,mood:i<3?4:1},contexts:i<3?[]:[{type:'intentional_activity_change',source:'synthetic',confirmed:true}]}));const moodResult=E.analyze(moodRecords,{...opts,metrics:[{id:'steps',direction:'lower',floor:1000},{id:'mood',direction:'lower',floor:.5}]});assert.equal(moodResult.latest.contributors.find(c=>c.id==='mood').contextMultiplier,1);assert.equal(moodResult.latest.score,75);assert.equal(moodResult.latest.status,'review_suggested');
console.log('PASS: one illness day in seven only attenuates eligible features by overlap; intentional activity context never suppresses mood.');
