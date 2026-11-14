const assert=require('node:assert/strict'),E=require('../engine.js');
const metrics=[{id:'steps',direction:'lower',floor:1000},{id:'mood',direction:'lower',floor:.5},{id:'sleep_hours',direction:'both',floor:.75},{id:'heart_rate',direction:'both',floor:5},{id:'home_hours',direction:'higher',floor:2}];
const base={steps:8500,mood:3.9,sleep_hours:7.5,heart_rate:60,home_hours:16};
const opts={granularity:'day',metrics,baselineIndices:Array.from({length:28},(_,i)=>i),windowSize:1};
const rows=(n=120)=>Array.from({length:n},(_,i)=>({periodIndex:i,period:'Day '+i,values:{...base}}));
const bad=r=>{r.values={steps:500,mood:1,sleep_hours:2,heart_rate:85,home_hours:24};};
const isFlag=p=>p.alertState.startsWith('flag_');
let r=rows();bad(r[40]);let a=E.analyze(r,opts);assert.equal(a.points[40].alertState,'noted');assert.equal(a.points[40].status,'no_change');assert.equal(a.points[41].alertState,'steady');assert(!a.points.some(isFlag));
assert.equal(E.analyze(r,{...opts,windowSize:7}).points[40].alertState,'noted','overlapping display windows cannot erase independent daily evidence');
for(const [badDays,want] of [[[40,41,43,44,46],'flag_sustained'],[[40,43,46],'watch']]){r=rows();badDays.forEach(i=>bad(r[i]));a=E.analyze(r,opts);assert.equal(a.points[46].alertState,want);assert.equal(a.points[46].persistence.highDays,badDays.length);}
r=rows();for(let i=40;i<47;i++){if([40,43,46].includes(i))bad(r[i]);else{r[i].missingPeriod=true;r[i].values={steps:null,mood:null,sleep_hours:null,heart_rate:null,home_hours:null};}}a=E.analyze(r,opts);assert.equal(a.points[46].alertState,'insufficient_data');assert.equal(a.points[46].persistence.observedDays,3);assert.equal(a.points[46].persistence.highDays,3);assert(!a.points.slice(40,47).some(isFlag));
// Slow decline with independent stable sensor domains diluting the daily signal.
r=rows(220);for(let i=28;i<r.length;i++){const weeks=(i-28)/7;r[i].values.steps=8500*(1-.015*weeks);r[i].values.mood=Math.max(1,3.9-.1*weeks);}a=E.analyze(r,opts);const driftAt=a.points.findIndex(p=>p.alertState==='flag_drift');assert(driftAt>28);assert(!a.points.slice(0,driftAt).some(p=>p.alertState==='flag_sustained'));assert(a.points[driftAt].drift.domains.includes('activity'));assert(a.points[driftAt].drift.domains.includes('mood'));
for(const p of a.points){const b=a.baseline.metrics.steps;assert(Math.abs(p.effectiveBaseline.steps-b.median)<=Math.max(.5*b.scale,.1*Math.abs(b.median))+1e-8);}
const sleepOnly=[{id:'sleep_hours',direction:'lower',floor:.5},{id:'sleep_efficiency',direction:'lower',floor:5}];const sr=rows().map((x,i)=>({...x,values:{sleep_hours:8-Math.max(0,i-28)*.04,sleep_efficiency:95-Math.max(0,i-28)*.3}}));const sa=E.analyze(sr,{...opts,metrics:sleepOnly});assert(!sa.points.some(p=>p.alertState==='flag_drift'));
const illness={type:'illness',source:'user_report',confirmed:true};r=rows();for(let i=40;i<=50;i++){bad(r[i]);r[i].values.mood=base.mood;r[i].contexts=[illness];}a=E.analyze(r,opts);assert.equal(a.points[46].contextSuppressed,true);assert.notEqual(a.points[46].alertState,'flag_sustained');assert.equal(a.points[46].unsuppressedAlertState,'flag_sustained');assert(a.points[46].daySignal.anchoredScore>=35);
for(let i=40;i<=50;i++)r[i].values.mood=1;a=E.analyze(r,opts);assert.equal(a.points[46].alertState,'flag_sustained');for(let i=40;i<=50;i++)r[i].contexts=[{...illness,type:'intentional_activity_change'}];assert.equal(E.analyze(r,opts).points[46].alertState,'flag_sustained');
// Actual baseline adaptation accepts quiet observations, and freezes unsafe days.
r=rows();for(let i=28;i<35;i++)r[i].values.steps=8100;r[35].contexts=[illness];r[35].values.steps=8100;r[36].values.steps=100;r[37].missingPeriod=true;for(let i=40;i<47;i++)bad(r[i]);a=E.analyze(r,opts);assert(a.points[34].effectiveBaseline.steps<base.steps);for(const i of [35,36,37,42,43,44,45,46])assert.equal(a.points[i].effectiveBaseline.steps,a.points[i-1].effectiveBaseline.steps,'freeze day '+i);
for(const p of a.points)assert(p.adaptation.updates.every(u=>u.index<(p.windowIndices[0]??0)),'window cannot train itself');
// Prefix determinism and full immutable input.
function freeze(x){if(x&&typeof x==='object'){Object.values(x).forEach(freeze);Object.freeze(x);}return x;}freeze(r);assert.doesNotThrow(()=>E.analyze(r,opts));
for(let j=0;j<50;j++){const t=28+(j*17)%90,changed=structuredClone(r);for(let i=t+1;i<changed.length;i++)changed[i].values={...base,steps:3000,mood:1};assert.deepEqual(E.analyze(changed,opts).points.slice(0,t+1),a.points.slice(0,t+1),'future leakage at '+t);}
// Explicit unit conversion includes absolute minima; fractional steps minimum stays unchanged.
const scaled=structuredClone(r);for(const row of scaled)for(const id of ['steps','mood'])if(typeof row.values[id]==='number')row.values[id]*=1000;
const scaledMetrics=metrics.map(m=>['steps','mood'].includes(m.id)?{...m,floor:m.floor*1000}:m);
const converted=E.analyze(scaled,{...opts,metrics:scaledMetrics,alerting:{drift:{relativeMin:{mood:800}}}});assert.deepEqual(converted.points.map(p=>p.alertState),a.points.map(p=>p.alertState));
const line=Array.from({length:28},(_,i)=>({x:i*2,y:3*i*2+7}));assert.equal(E.theilSen(line),3);assert(E.mannKendall(line)<.001);const constant=line.map(p=>({...p,y:5}));assert.equal(E.theilSen(constant),0);assert.equal(E.mannKendall(constant),1);
let seed=0x58a7;const random=()=>{seed=(1664525*seed+1013904223)>>>0;return(seed+.5)/4294967296;};const gaussian=()=>Math.sqrt(-2*Math.log(random()))*Math.cos(2*Math.PI*random());let falseFlags=0,noiseNonsignificant=0;
for(let trial=0;trial<400;trial++){const stable=rows().map(x=>({...x,values:{steps:8500+gaussian()*600,mood:3.9+gaussian()*.2,sleep_hours:7.5+gaussian()*.25,heart_rate:60+gaussian()*2,home_hours:16+gaussian()*.5}}));const result=E.analyze(stable,opts);if(result.points.some(isFlag))falseFlags++;const noise=Array.from({length:28},(_,x)=>({x,y:gaussian()}));if(E.mannKendall(noise)>.05)noiseNonsignificant++;}
assert(falseFlags/400<.02);assert(noiseNonsignificant>340);console.log('Stable-series false-flag rate:',falseFlags+'/400',100*falseFlags/400+'%; MK nonsignificant noise:',noiseNonsignificant+'/400');
const mapped={steady:'no_change',noted:'no_change',watch:'change_detected',flag_sustained:'review_suggested',flag_drift:'review_suggested'};for(const p of a.points){assert('status'in p&&'score'in p&&'contributors'in p&&'windowIndices'in p);assert.equal(p.status,mapped[p.alertState]||p.alertState);}
assert(Object.isFrozen(E.ALERT_DEFAULTS));assert(Object.isFrozen(E.ALERT_DEFAULTS.drift.relativeMin));for(const config of [{sustained:{k:8}},{watch:{m:8}},{drift:{mkP:0}},{tolerance:{z:-1}},{adapt:{maxWeight:.9}},{drift:{relativeMin:{steps:-.2}}},{domains:{extra:['steps']}}])assert.throws(()=>E.analyze(rows(),{...opts,alerting:config}));
assert.equal(E.analyze(rows(),{...opts,granularity:'month'}).alerting.enabled,false);assert.equal(E.analyze(rows(),{...opts,alerting:{enabled:false}}).alerting.enabled,false);
console.log('PASS daily alerting: isolated/sustained/watch/drift, missingness, two domains, contexts, capped adaptation, 50 prefixes, immutable inputs, converted units, known trend statistics, validated defaults and legacy status mapping. Slow-drift first index:',driftAt);

for(const config of [{drift:{relativeMin:[]}},{domains:null},{drift:null}])assert.throws(()=>E.analyze(rows(),{...opts,alerting:config}));
assert.equal(E.analyze(rows(),{...opts,adaptiveAlpha:.12}).alerting.config.adapt.alpha,.12);
console.log('PASS nested alert config validation and effective exported parameters.');

assert.throws(()=>E.analyze(rows(),{...opts,alerting:{domains:{activity:['steps','steps']}}}));

for(const config of [{sustained:{k:1},watch:{k:1}},{sustained:{minObserved:1}}])assert.throws(()=>E.analyze(rows(),{...opts,alerting:config}));

// Omitted indexed calendar days cannot make seven sparse readings look like a week.
r=rows();for(let i=40;i<r.length;i++){r[i].periodIndex=40+3*(i-40);bad(r[i]);}a=E.analyze(r,opts);assert.equal(a.points[46].persistence.observedDays,3);assert.equal(a.points[46].alertState,'insufficient_data');assert(!a.points.slice(40,47).some(isFlag));console.log('PASS sparse indexed-calendar persistence abstention.');
