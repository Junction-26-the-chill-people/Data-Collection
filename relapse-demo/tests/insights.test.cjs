const assert=require('node:assert/strict'),I=require('../insights.js');
const base={assessment:{score:20,windowIndices:[0,1],contributors:[]},records:[{values:{}},{values:{}}],baseline:{metrics:{}},windowSize:2,granularity:'day'};
function card(id,current,baseline,unit){const args=structuredClone(base);args.assessment.contributors=[{id,current,baseline,unit,label:id}];args.records.forEach(r=>r.values[id]=current);return I.summarize(args)[0];}
assert.match(card('sleep_hours',6,8,'h').sentence,/25% shorter/);
assert.match(card('sleep_efficiency',80,95,'%').sentence,/15 percentage points lower/);
assert.match(card('mood',2,4,'\/5').sentence,/2 points lower/);assert.ok(!card('mood',2,4,'\/5').sentence.includes('%'));
assert.match(card('heart_rate',70,60,'bpm').sentence,/10 bpm higher/);assert.match(card('heart_rate',70,60,'bpm').detail,/does not measure stress/);
assert.match(card('bedtime_hour',25,23,'h').sentence,/2 h 00 min later/);assert.match(card('bedtime_hour',25,23,'h').detail,/01:00/);
assert.ok(!card('steps',300,0,'steps').sentence.match(/Infinity|NaN|%/));
assert.match(card('steps',101,1000,'steps').sentence,/90% lower/);
assert.match(card('steps',999,1000,'steps').sentence,/within 1%/);
assert.deepEqual(I.summarize({assessment:{score:null,contributors:[{id:'steps',current:10,baseline:20}]}}),[]);
const g=structuredClone(base);g.assessment.contributors=[{id:'sleep_hours',current:0,baseline:8,unit:'h'}];g.records=[{values:{sleep_hours:0}},{missingPeriod:true,values:{sleep_hours:null}}];const c=I.summarize(g)[0];assert.equal(c.observedCount,1);assert.match(c.detail,/does not prove no sleep/);
g.granularity='month';assert.match(I.summarize(g)[0].detail,/monthly source summaries/);
console.log('PASS personal explanations: exact ratios, percentage points, mood-scale differences, missingness, zero references, no inferred stress, date cadence and bedtime rollover.');

// Summary filtering is separate from scoring and keeps large changes in either direction.
const change=(id,current,baseline)=>({id,current,baseline});
for(const [id,baseline] of Object.entries({steps:8000,sleep_hours:8,sleep_efficiency:95,bedtime_hour:23,heart_rate:60,mood:4,home_hours:16,short_sleep_nights:3,active_days:4})){
 assert.equal(I.isNoteworthy(change(id,baseline*1.003,baseline)),false,id+' must suppress a 0.3% change');
}
for(const c of [change('steps',6000,8000),change('steps',10000,8000),change('sleep_hours',7.2,8),change('sleep_efficiency',90,95),change('bedtime_hour',24,23),change('heart_rate',65,60),change('mood',3.5,4),change('home_hours',19,16),change('short_sleep_nights',3,1),change('active_days',1,3),change('steps',1000,0)])assert.equal(I.isNoteworthy(c),true,JSON.stringify(c));
for(const c of [change('steps',7200,8000),change('steps',2600,3500),change('sleep_hours',7.3,8),change('heart_rate',104,100),change('home_hours',18,16),change('mood',3.51,4),change('steps',null,8000),change('steps',NaN,8000),change('unregistered',2000,1)])assert.equal(I.isNoteworthy(c),false,JSON.stringify(c));
assert.equal(I.isNoteworthy(change('steps',100,0)),false);
assert.equal(I.isNoteworthy(change('steps',Infinity,1000)),false);
assert.equal(I.isNoteworthy(change('custom',8,10),{custom:{minimumAbsolute:1,minimumRelative:.1}}),true);
assert.equal(I.isNoteworthy(change('custom',8,10),{custom:{minimumAbsolute:-1,minimumRelative:0}}),false);
const filtered=structuredClone(base);filtered.assessment.contributors=[change('steps',8024,8000),change('mood',2,4)];
const unchanged=JSON.stringify(filtered);assert.equal(I.summarize(filtered).length,2);const notable=I.summarize({...filtered,noteworthyOnly:true});assert.deepEqual(notable.map(c=>c.id),['mood']);assert.equal(notable[0].displayPolicyVersion,'noteworthy-display/1.0.0');assert.equal(JSON.stringify(filtered),unchanged);
assert.equal(I.noteworthyChange(change('steps',null,8000)).reason,'missing_measurement');
assert.equal(I.displayPolicy.rules.steps.minimumRelative,.2);assert(Object.isFrozen(I.displayPolicy.rules.steps));
console.log('PASS noteworthy display: tinychanges suppressed; absolute+relative gates, large improvements, single-day changes, missingness, zero reference, custom rules, full-data retention and immutable policy.');
