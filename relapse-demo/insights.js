/* Plain-language explanations of observed data; no diagnosis or inferred stress. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.RoutineInsights=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const finite=x=>typeof x==='number'&&Number.isFinite(x);
const num=(x,d=1)=>Number(x.toFixed(d)).toLocaleString('en-US');
const duration=h=>{const minutes=Math.round(Math.abs(h)*60);return `${Math.floor(minutes/60)} h ${String(minutes%60).padStart(2,'0')} min`;};
const clock=h=>{const minutes=((Math.round(h*60)%1440)+1440)%1440;return `${String(Math.floor(minutes/60)).padStart(2,'0')}:${String(minutes%60).padStart(2,'0')}`;};
// Display rules suppress small differences. They do not change the engine, label
// statistical outliers, estimate clinical risk, or remove any source observations.
const displayRules=Object.freeze(Object.fromEntries(Object.entries({
 steps:{minimumAbsolute:1000,minimumRelative:.20,unit:'steps'},
 sleep_hours:{minimumAbsolute:.75,minimumRelative:.10,unit:'h'},
 sleep_efficiency:{minimumAbsolute:5,minimumRelative:0,unit:'percentage points'},
 bedtime_hour:{minimumAbsolute:1,minimumRelative:0,unit:'h'},
 heart_rate:{minimumAbsolute:5,minimumRelative:.08,unit:'bpm'},
 mood:{minimumAbsolute:.5,minimumRelative:0,unit:'scale points'},
 home_hours:{minimumAbsolute:2,minimumRelative:.15,unit:'h/day'},
 short_sleep_nights:{minimumAbsolute:2,minimumRelative:0,unit:'nights'},
 active_days:{minimumAbsolute:2,minimumRelative:0,unit:'days'}
}).map(([id,rule])=>[id,Object.freeze(rule)])));
const displayPolicy=Object.freeze({version:'noteworthy-display/1.0.0',basis:'selected-reference-median',
 rule:'Both absolute and relative minimums must be met; a zero reference uses the absolute minimum only.',
 purpose:'Demo summary display thresholds, not clinical cutoffs or statistical significance. All measurements remain available.',rules:displayRules});
function noteworthyChange(c,rules=displayRules){
 if(!c||!finite(c.current)||!finite(c.baseline))return {noteworthy:false,reason:'missing_measurement'};
 const rule=rules?.[c.id];
 if(!rule||!finite(rule.minimumAbsolute)||rule.minimumAbsolute<=0||!finite(rule.minimumRelative)||rule.minimumRelative<0)return {noteworthy:false,reason:'no_valid_display_rule'};
 const absoluteChange=Math.abs(c.current-c.baseline),relativeChange=c.baseline===0?null:absoluteChange/Math.abs(c.baseline);
 if(!finite(absoluteChange)||(relativeChange!==null&&!finite(relativeChange)))return {noteworthy:false,reason:'invalid_difference'};
 const noteworthy=absoluteChange+1e-10>=rule.minimumAbsolute&&(relativeChange===null||relativeChange+1e-12>=rule.minimumRelative);
 return {noteworthy,reason:noteworthy?'display_threshold_met':'below_display_threshold',absoluteChange,relativeChange,rule};
}
function isNoteworthy(c,rules=displayRules){return noteworthyChange(c,rules).noteworthy;}
function summarize({assessment,records=[],baseline={},windowSize,granularity='day',noteworthyOnly=false,rules=displayRules}={}){
 if(!assessment||!finite(assessment.score))return [];
 const indices=Array.isArray(assessment.windowIndices)?assessment.windowIndices:[];
 const span=indices.length||windowSize||0,unit=granularity==='day'?'day':'month';
 const scope=span===1?`For the selected ${unit}`:`Over the selected ${span}-${unit} window`;
 const cards=[];
 for(const c of assessment.contributors||[]){
  if(!finite(c.current)||!finite(c.baseline))continue;
  const display=noteworthyChange(c,rules);
  if(noteworthyOnly&&!display.noteworthy)continue;
  const delta=c.current-c.baseline,abs=Math.abs(delta),same=abs<1e-8;
  const relative=c.baseline>0?delta/c.baseline:null;
  const pct=relative===null?null:Math.round(Math.abs(relative)*100);
  const trend=same?'about the same':delta<0?'lower':'higher';
  const observed=indices.filter(i=>!records[i]?.missingPeriod&&finite(records[i]?.values?.[c.id])).length;
  let title=c.label||c.id,sentence,measure,comparison;
  const ratio=relative===null?`${num(abs)} ${c.unit||''} ${trend}`:pct===0?'within 1% of your reference':`${pct}% ${trend}`;
  if(c.id==='steps') {title='Your activity';sentence=same?'Your recorded step count was about the same.':`Your recorded step count was ${ratio}.`;measure=`${num(c.current,0)} steps`;comparison=`${num(c.baseline,0)} steps`;}
  else if(c.id==='sleep_hours'){title='Your sleep';sentence=same?'Your recorded sleep duration was about the same.':relative===null?`Your recorded sleep duration changed by ${duration(delta)}.`:pct===0?'Your recorded sleep duration was within 1% of your reference.':`Your recorded sleep duration was ${pct}% ${delta<0?'shorter':'longer'}.`;measure=duration(c.current);comparison=duration(c.baseline);}
  else if(c.id==='sleep_efficiency'){title='Time asleep while in bed';sentence=same?'Your sleep efficiency was about the same.':`Your sleep efficiency was ${num(abs)} percentage points ${trend}.`;measure=`${num(c.current)}%`;comparison=`${num(c.baseline)}%`;}
  else if(c.id==='mood'){title='Your mood check-ins';sentence=same?'Your mood check-ins were about the same.':`Your mood check-ins were ${num(abs)} points ${trend} ${c.unit&&c.unit.startsWith('/')?'(out of '+c.unit.slice(1)+')':'on the recorded scale' }.`;measure=`${num(c.current)} ${c.unit||''}`;comparison=`${num(c.baseline)} ${c.unit||''}`;}
  else if(c.id==='heart_rate'){title='Your resting heart rate';sentence=same?'Your recorded resting heart rate was about the same.':`Your resting heart rate was ${num(abs)} bpm ${trend}.`;measure=`${num(c.current)} bpm`;comparison=`${num(c.baseline)} bpm`;}
  else if(c.id==='home_hours'){title='Your time at home';sentence=same?'Your recorded time at home was about the same.':`Your recorded time at home was ${duration(delta)} ${delta<0?'less':'more'} per day.`;measure=duration(c.current);comparison=duration(c.baseline);}
  else if(c.id==='bedtime_hour'){title='Your sleep timing';sentence=same?'Your recorded sleep start was about the same.':`Your sleep started ${duration(delta)} ${delta<0?'earlier':'later'}.`;measure=clock(c.current);comparison=clock(c.baseline);}
  else {sentence=`Your recorded ${String(c.label||c.id).toLowerCase()} was ${same?'about the same':ratio}.`;measure=`${num(c.current)} ${c.unit||''}`;comparison=`${num(c.baseline)} ${c.unit||''}`;}
  const refCount=baseline.metrics?.[c.id]?.count;
  let detail=`${scope}: ${span===1?(observed?'measurement available':'measurement unavailable'):`${observed} of ${span} ${unit}s have this measurement`}. ${span===1?'Recorded value':'Typical value (median)'}: ${measure}; selected reference: ${comparison}${finite(refCount)?` from ${refCount} observations`:''}.`;
  if(c.id==='sleep_hours'&&indices.some(i=>records[i]?.values?.sleep_hours===0))detail+=' Zero recorded sleep can reflect sensor or processing gaps; it does not prove no sleep.';
  if(c.id==='heart_rate')detail+=' Heart rate alone does not measure stress.';
  if(granularity!=='day')detail+=' These are monthly source summaries, not daily readings.';
  cards.push({id:c.id,title,sentence,detail,current:c.current,reference:c.baseline,delta,observedCount:observed,windowCount:span,comparisonBasis:'selected-reference-median',noteworthy:display.noteworthy,displayThreshold:display.rule||null,displayPolicyVersion:displayPolicy.version});
 }
 return cards;
}
return {summarize,isNoteworthy,noteworthyChange,displayPolicy};
});
