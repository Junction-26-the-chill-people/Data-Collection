/* Component-signal interface for teammates' detectors (screen time, social feed, companion app).
 * This file owns the CONTRACT and a FUSION PREVIEW. It does not implement those detectors.
 * For generated demo people only, it produces clearly-labelled demo component outputs so the
 * combined view can be demonstrated. Research participants never receive generated values. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.CompanionSignals=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const CONTRACT_VERSION='component-signal/0.1.0';
const FUSION_VERSION='combined-preview/0.1.0';
const MIN_COVERAGE=0.6, MIN_COMPONENTS=2;
const finite=x=>typeof x==='number'&&Number.isFinite(x);
const clamp=(x,a,b)=>Math.min(b,Math.max(a,x));
const COMPONENTS=Object.freeze([
 Object.freeze({id:'routine',label:'Routine & wearables',owner:'relapse-demo (this repository)',weight:0.5,icon:'◔'}),
 Object.freeze({id:'companion_checkin',label:'Companion check-ins',owner:'companion app',weight:0.2,icon:'✎'}),
 Object.freeze({id:'screen_time',label:'Screen time & app use',owner:'screen-time component',weight:0.15,icon:'▢'}),
 Object.freeze({id:'social_feed',label:'Social feed tone',owner:'social-feed component',weight:0.15,icon:'◎'})
]);
const FIELDS=Object.freeze(['contractVersion','componentId','componentVersion','participantRef','dayKey','index','coverage','synthetic','provenance','contributors','summary']);

function hash(str){let h=2166136261;for(let i=0;i<str.length;i++){h^=str.charCodeAt(i);h=Math.imul(h,16777619);}return h>>>0;}
function rng(seed){let a=seed>>>0;return()=>{a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
function median(xs){const a=xs.filter(finite).sort((x,y)=>x-y);if(!a.length)return null;const m=a.length>>1;return a.length%2?a[m]:(a[m-1]+a[m])/2;}
/* person:YYYY-MM-DD for daily records; person:period for monthly research summaries (never null when a period exists). */
function dayKeyOf(p,r){if(r&&typeof r.dayKey==='string'&&r.dayKey)return r.dayKey;if(!p||p.id===undefined||p.id===null||!r)return null;const when=r.date||r.period;return when?String(p.id)+':'+when:null;}

/* Validation applied to every component payload before it may be displayed or fused. */
function validate(signal,expected){
 const errors=[];
 if(!signal||typeof signal!=='object')return ['not_an_object'];
 if(signal.contractVersion!==CONTRACT_VERSION)errors.push('unsupported_contract_version');
 if(!COMPONENTS.some(c=>c.id===signal.componentId))errors.push('unknown_component');
 if(expected&&signal.participantRef!==expected.participantRef)errors.push('participant_mismatch');
 if(typeof signal.dayKey!=='string'||!signal.dayKey)errors.push('day_key_required');
 else if(expected&&signal.dayKey!==expected.dayKey)errors.push('day_mismatch');
 if(expected&&(typeof expected.dayKey!=='string'||!expected.dayKey))errors.push('expected_day_key_required');
 if(signal.index!==null&&(!finite(signal.index)||signal.index<0||signal.index>1))errors.push('index_out_of_range');
 if(!finite(signal.coverage)||signal.coverage<0||signal.coverage>1)errors.push('coverage_out_of_range');
 if(typeof signal.synthetic!=='boolean')errors.push('synthetic_flag_required');
 if(typeof signal.provenance!=='string'||!signal.provenance)errors.push('provenance_required');
 return errors;
}

/* Weighted mean over components that pass validation and coverage. Abstains below MIN_COMPONENTS.
 * Not a calibrated probability: a transparent preview of how component indices could be combined. */
function fuse(signals,expected){
 const accepted=[],rejected=[];
 for(const s of signals||[]){const errors=validate(s,expected);if(errors.length)rejected.push({componentId:s&&s.componentId,errors});else if(finite(s.index)&&s.coverage>=MIN_COVERAGE)accepted.push(s);else rejected.push({componentId:s.componentId,errors:[finite(s.index)?'low_coverage':'not_scored']});}
 const parts=accepted.map(s=>({componentId:s.componentId,index:s.index,weight:COMPONENTS.find(c=>c.id===s.componentId).weight,synthetic:s.synthetic}));
 const total=parts.reduce((a,c)=>a+c.weight,0);
 const index=parts.length>=MIN_COMPONENTS&&total>0?parts.reduce((a,c)=>a+c.index*c.weight,0)/total:null;
 return {fusionVersion:FUSION_VERSION,status:index===null?'insufficient_components':'combined',index:finite(index)?Math.round(index*1000)/1000:null,
  components:parts.map(c=>Object.assign({},c,{normalizedWeight:total?c.weight/total:0})),rejected,
  includesSynthetic:parts.some(c=>c.synthetic),minimumComponents:MIN_COMPONENTS,minimumCoverage:MIN_COVERAGE,
  meaning:'Experimental weighted combination of component change indices; not a relapse probability or diagnosis.'};
}

const REFLECTIONS={
 low:['Stayed in most of the day. Didn\'t feel like replying to anyone.','Tired again, even after a long night.','Skipped the walk. Everything felt like a lot.','Cancelled plans. Scrolled for hours instead.'],
 mid:['An okay day. A bit flat in the afternoon.','Busy, but got through it.','Short walk at lunch helped a little.','Quiet evening, early night.'],
 high:['Good walk by the water this morning.','Coffee with a friend — felt like myself.','Productive day, slept well.','Cooked dinner and called my sister.']
};

/* Demo outputs for generated people only. Derived deterministically from that same generated
 * person's own same-day self-reported mood relative to the selected reference, plus seeded noise.
 * Days without an observation (missingPeriod) receive no scored component values: nothing is guessed. */
function demoSignals(p,index,options){
 if(!p||!p.synthetic||!Array.isArray(p.records))return [];
 const r=p.records[index];if(!r)return [];
 const key=dayKeyOf(p,r),rand=rng(hash(String(p.id)+'|'+index));
 const chosen=options&&Array.isArray(options.referenceIndices)&&options.referenceIndices.length?options.referenceIndices:null;
 const refIdx=chosen||(Array.isArray(p.baselineIndices)&&p.baselineIndices.length?p.baselineIndices:p.records.slice(0,28).map((_,i)=>i));
 const refMood=median(refIdx.map(i=>p.records[i]&&p.records[i].values&&p.records[i].values.mood));
 const mood=r.values?r.values.mood:null;
 const drop=finite(mood)&&finite(refMood)?Math.max(0,refMood-mood):null;
 const person=rng(hash(String(p.id)));const baseMinutes=130+Math.round(person()*90),baseLate=8+Math.round(person()*14),baseNeg=0.14+person()*0.08;
 const common={contractVersion:CONTRACT_VERSION,participantRef:p.id,dayKey:key,synthetic:true,provenance:'demo-generator:companion-signals.js'};
 const out=[];
 const moodBucket=!finite(mood)?null:mood<2.6?'low':mood<3.6?'mid':'high';
 out.push(Object.assign({},common,{componentId:'companion_checkin',componentVersion:'demo/0.1.0',index:drop===null?null:Math.round(clamp((drop-0.25)/2.3,0,0.95)*100)/100,coverage:finite(mood)?1:0,
  contributors:finite(mood)?[{id:'mood',label:'Mood check-in',value:mood,unit:'/5',reference:refMood}]:[],
  summary:finite(mood)?'Mood check-in recorded':'No check-in today',reflection:moodBucket?REFLECTIONS[moodBucket][Math.floor(rand()*4)]:null}));
 if(r.missingPeriod){for(const id of ['screen_time','social_feed'])out.push(Object.assign({},common,{componentId:id,componentVersion:'demo/0.1.0',index:null,coverage:0,contributors:[],summary:'No observation for this day'}));return out;}
 const noise=()=>(rand()-0.5)*0.25;
 const d=drop===null?0.15*rand():drop;
 const minutes=Math.round(baseMinutes*(1+0.32*d+noise())),late=Math.max(0,Math.round(baseLate*(1+1.4*d)+noise()*20));
 out.push(Object.assign({},common,{componentId:'screen_time',componentVersion:'demo/0.1.0',index:Math.round(clamp(0.28*d+0.12*Math.min(2,Math.max(0,(late-baseLate)/Math.max(baseLate,1)))+noise()*0.15-0.04,0,0.95)*100)/100,coverage:Math.round((0.82+rand()*0.18)*100)/100,
  contributors:[{id:'screen_minutes',label:'Total screen time',value:minutes,unit:'min',reference:baseMinutes},{id:'late_night_minutes',label:'Use after midnight',value:late,unit:'min',reference:baseLate}],
  summary:minutes>baseMinutes*1.2?'More screen time than usual':'Screen time close to usual'}));
 const neg=clamp(baseNeg*(1+0.9*d)+noise()*0.08,0.02,0.9);
 out.push(Object.assign({},common,{componentId:'social_feed',componentVersion:'demo/0.1.0',index:Math.round(clamp(0.38*Math.max(0,(neg-baseNeg)/Math.max(baseNeg,0.05))+noise()*0.1-0.05,0,0.95)*100)/100,coverage:Math.round((0.7+rand()*0.3)*100)/100,
  contributors:[{id:'negative_share',label:'Low-mood content share',value:Math.round(neg*100),unit:'%',reference:Math.round(baseNeg*100)}],
  summary:neg>baseNeg*1.3?'Feed leaning toward low-mood content':'Feed tone close to usual'}));
 return out;
}

/* The routine engine's own point, expressed in the same contract. */
function routineSignal(p,index,point){
 const r=p&&p.records&&p.records[index];
 return {contractVersion:CONTRACT_VERSION,componentId:'routine',componentVersion:'routine-change/1.1.0',participantRef:p&&p.id,dayKey:dayKeyOf(p,r),
  index:point&&finite(point.score)?Math.round(point.score)/100:null,coverage:point&&finite(point.coverage)?point.coverage:0,
  synthetic:Boolean(p&&p.synthetic),provenance:p&&p.synthetic?'generated-demo-profile':'research-source:'+String(p&&p.source||'unknown'),
  contributors:(point&&point.contributors||[]).map(c=>({id:c.id,label:c.label,value:c.current,unit:c.unit,reference:c.baseline})),
  summary:point?point.status:'not_assessed'};
}

return Object.freeze({CONTRACT_VERSION,FUSION_VERSION,COMPONENTS,FIELDS,MIN_COVERAGE,MIN_COMPONENTS,validate,fuse,demoSignals,routineSignal,dayKeyOf});
});
