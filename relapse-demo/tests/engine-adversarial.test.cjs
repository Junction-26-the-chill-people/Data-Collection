const assert=require('node:assert/strict'),E=require('../engine.js');
const metrics=[{id:'a',direction:'lower',floor:2},{id:'b',direction:'higher',floor:1}];const opts={metrics,baselineIndices:[0,1,2],windowSize:3};
const rec=(a,b,i)=>({periodIndex:i,values:{a,b}});const records=[rec(10,4,0),rec(10,4,1),rec(10,4,2),rec(2,8,3),rec(2,8,4),rec(2,8,5)];
assert.throws(()=>E.analyze([records[0],records[0]],opts),RangeError);
assert.throws(()=>E.analyze([records[1],records[0]],opts),RangeError);
assert.throws(()=>E.analyze([records[0],{values:{a:1,b:1}}],opts),RangeError);
assert.throws(()=>E.analyze([null],opts),TypeError);
assert.throws(()=>E.analyze([{values:{a:1e308,b:1}}],opts),RangeError);
assert.throws(()=>E.analyze(records,{...opts,baselineIndices:'012'}),TypeError);
assert.throws(()=>E.analyze(records,{...opts,metrics:[null]}),TypeError);
const stale=records.map(x=>({...x,values:{...x.values}}));stale[5].values.b=null;assert.equal(E.analyze(stale,opts).latest.score,null);
assert.equal(E.analyze(records,{...opts,baselineIndices:[]}).latest.score,null);
assert.equal(E.analyze(records,{...opts,baselineIndices:[3,4,5]}).points[0].score,null);
const proto=records.map(r=>({values:JSON.parse('{"__proto__":1,"constructor":2}')}));assert.equal(E.analyze(proto,{...opts,metrics:[{id:'__proto__',direction:'both',floor:1},{id:'constructor',direction:'both',floor:1}]}).latest.score,0);
let seed=0x713A2;const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
let trials=0;
for(let n=0;n<400;n++){
 const rows=Array.from({length:12},(_,i)=>rec(20+random()*20,2+random()*7,i));const before=JSON.stringify(rows);const result=E.analyze(rows,opts);
 // Changing units and the scale floor together must preserve the index.
 const factors=[.01+random()*100,.01+random()*100];const scaled=rows.map(r=>({...r,values:{a:r.values.a*factors[0],b:r.values.b*factors[1]}}));
 const rescaled=E.analyze(scaled,{...opts,metrics:metrics.map((m,i)=>({...m,floor:m.floor*factors[i]}))});
 assert.deepEqual(result.points.map(p=>p.score),rescaled.points.map(p=>p.score));
 // Later observations cannot alter earlier frozen-baseline assessments.
 const prefix=E.analyze(rows.slice(0,8),opts);assert.deepEqual(prefix.points,result.points.slice(0,8));
 // Swapping labels/outcomes does not affect feature-only analysis.
 const labeled=rows.map(r=>({...r,labels:{phq9:random()*27,mood:random()}}));assert.deepEqual(E.analyze(labeled,opts).points,result.points);
 assert.equal(JSON.stringify(rows),before);
 // Nulls never lead to nonfinite output or conversion to a numeric zero sample.
 const sparse=rows.map((r,i)=>({...r,values:{a:i>2&&random()<.4?null:r.values.a,b:i>2&&random()<.4?null:r.values.b}}));const sr=E.analyze(sparse,opts);
 for(const p of sr.points){assert.ok(p.score===null||Number.isInteger(p.score)&&p.score>=0&&p.score<=100);assert.ok(Number.isFinite(p.coverage)&&p.coverage>=0&&p.coverage<=1);for(const c of p.contributors)assert.ok(Number.isFinite(c.z)&&Number.isFinite(c.current));}
 assert.ok(!JSON.stringify(sr).includes('NaN'));trials++;
}
// Uniformly stronger adverse movement cannot lower the change index on a fixed baseline.
let prior=0;for(let d=0;d<20;d++){const rs=[rec(10,4,0),rec(10,4,1),rec(10,4,2),rec(10-d,4+d,3),rec(10-d,4+d,4),rec(10-d,4+d,5)];const score=E.analyze(rs,opts).latest.score;assert.ok(score>=prior);prior=score;}
console.log('PASS: adversarial inputs, stale-feature regression, prototype-safe keys, 400 seeded property trials (unit invariance, no future leakage, outcome independence, missingness, immutability), monotonic adverse movement. Seed 0x713A2.');

assert.throws(()=>E.analyze(records,{...opts,metrics:[{...metrics[0],min:0,max:5},metrics[1]]}),RangeError);
assert.throws(()=>E.analyze(records,{...opts,metrics:[{...metrics[0],min:5,max:0},metrics[1]]}),RangeError);
console.log('PASS: configured physical-domain bounds reject invalid samples and invalid definitions.');
