/* Dependency-free, deterministic research change detector. No clinical calibration. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.RoutineEngine=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const MODEL_VERSION='routine-change/2.1.0';
const finite=x=>typeof x==='number'&&Number.isFinite(x);
const clamp=(x,a,b)=>Math.min(b,Math.max(a,x));
const adverse=(delta,direction)=>Math.max(0,direction==='lower'?-delta:direction==='higher'?delta:Math.abs(delta));
const deviation=(delta,direction,scale)=>{const z=adverse(delta,direction)/scale;return finite(z)?z:Number.MAX_VALUE;};
const featureScore=z=>100*clamp((z-1)/3,0,1);
const CONTEXT_METRICS={illness:['steps','sleep_hours','sleep_efficiency','bedtime_hour','heart_rate','home_hours'],recovery:['steps','sleep_hours','sleep_efficiency','bedtime_hour','heart_rate','home_hours'],intentional_activity_change:['steps','home_hours','heart_rate']};
function confirmedContexts(record){return Array.isArray(record.contexts)?record.contexts.filter(c=>c&&c.confirmed===true&&typeof c.source==='string'&&c.source.length>0&&['illness','recovery','intentional_activity_change'].includes(c.type)):[];}

function median(values){const a=values.filter(finite).slice().sort((a,b)=>a-b);if(!a.length)return null;const m=Math.floor(a.length/2);return a.length%2?a[m]:a[m-1]/2+a[m]/2;}
function value(record,id){const v=record&&!record.missingPeriod&&record.values&&record.values[id];return finite(v)?v:null;}

function deepFreeze(v){if(v&&typeof v==='object'){Object.values(v).forEach(deepFreeze);Object.freeze(v);}return v;}
// steps is a fraction of the anchor; all other relativeMin entries use absolute
// native metric units. Callers converting units must also convert these minima.
const ALERT_DEFAULTS=deepFreeze({enabled:true,tolerance:{z:1},adapt:{alpha:.05,maxWeight:.25},driftCap:{scaleMultiple:.5,relative:.10},noted:{index:.35},sustained:{index:.35,k:5,m:7,minObserved:4},watch:{k:3,m:7},hysteresis:{clearBelow:.20,observedDays:3},drift:{window:14,trendWindow:28,z:2,mkP:.05,minMetrics:2,relativeMin:{steps:.25,sleep_hours:1,sleep_efficiency:5,bedtime_hour:1,heart_rate:5,mood:.8,home_hours:2,active_days:2,short_sleep_nights:2}},domains:{sleep:['sleep_hours','sleep_efficiency','bedtime_hour','short_sleep_nights'],activity:['steps','active_days'],mood:['mood'],physiology:['heart_rate'],place:['home_hours']}});
function alertConfig(input){
 if(input!==undefined&&(!input||typeof input!=='object'||Array.isArray(input)))throw new TypeError('alerting must be a configuration object');
 const a=input||{},c={...ALERT_DEFAULTS,...a};
 for(const key of ['tolerance','adapt','driftCap','noted','sustained','watch','hysteresis','drift']){if(a[key]!==undefined&&(!a[key]||typeof a[key]!=='object'||Array.isArray(a[key])))throw new TypeError('Invalid alerting '+key);c[key]={...ALERT_DEFAULTS[key],...a[key]};}
 if(a.domains!==undefined&&(!a.domains||typeof a.domains!=='object'||Array.isArray(a.domains)))throw new TypeError('alerting.domains must be an object');
 if(a.drift?.relativeMin!==undefined&&(!a.drift.relativeMin||typeof a.drift.relativeMin!=='object'||Array.isArray(a.drift.relativeMin)))throw new TypeError('drift.relativeMin must be an object');
 c.drift.relativeMin={...ALERT_DEFAULTS.drift.relativeMin,...a.drift?.relativeMin};c.domains={...ALERT_DEFAULTS.domains,...a.domains};
 if(!finite(c.hysteresis.clearBelow)||c.hysteresis.clearBelow<=0||c.hysteresis.clearBelow>=Math.min(c.noted.index,c.sustained.index)||!Number.isInteger(c.hysteresis.observedDays)||c.hysteresis.observedDays<2||c.hysteresis.observedDays>366)throw new RangeError('Hysteresis requires a lower clearing threshold and 2..366 observed days');
 if(typeof c.enabled!=='boolean')throw new TypeError('alerting.enabled must be boolean');
 for(const v of [c.tolerance.z,c.driftCap.scaleMultiple,c.driftCap.relative,c.drift.z])if(!finite(v)||v<0)throw new RangeError('Alert scales must be finite and nonnegative');
 for(const v of [c.noted.index,c.sustained.index])if(!finite(v)||v<=0||v>1)throw new RangeError('Alert index thresholds must lie in (0,1]');
 if(!finite(c.adapt.alpha)||c.adapt.alpha<=0||c.adapt.alpha>1||!finite(c.adapt.maxWeight)||c.adapt.maxWeight<0||c.adapt.maxWeight>.25)throw new RangeError('Invalid alert adaptation parameters');
 for(const v of [c.sustained.k,c.sustained.m,c.sustained.minObserved,c.watch.k,c.watch.m,c.drift.window,c.drift.trendWindow,c.drift.minMetrics])if(!Number.isInteger(v)||v<1)throw new RangeError('Alert counts must be positive integers');
 if(c.sustained.k<2||c.watch.k<2||c.sustained.minObserved<2||c.sustained.k>c.sustained.m||c.sustained.minObserved>c.sustained.m||c.watch.k>c.watch.m||c.watch.k>c.sustained.k||c.watch.m!==c.sustained.m||c.drift.trendWindow<c.drift.window||c.drift.window<2||c.drift.trendWindow>366||c.sustained.m>366)throw new RangeError('Inconsistent or unbounded alert windows');
 if(!finite(c.drift.mkP)||c.drift.mkP<=0||c.drift.mkP>=1)throw new RangeError('MK p threshold must lie in (0,1)');
 if(Object.values(c.drift.relativeMin).some(v=>!finite(v)||v<0))throw new RangeError('Drift minima must be nonnegative');
 const ids=new Set();for(const list of Object.values(c.domains)){if(!Array.isArray(list))throw new TypeError('Alert domains must be arrays');for(const id of list){if(typeof id!=='string'||!id||ids.has(id))throw new TypeError('Alert domains must contain unique metric IDs');ids.add(id);}}
 c.domains=Object.fromEntries(Object.entries(c.domains).map(([k,v])=>[k,v.slice()]));return c;
}
function theilSen(samples){const slopes=[];for(let i=0;i<samples.length;i++)for(let j=i+1;j<samples.length;j++){const dx=samples[j].x-samples[i].x;if(dx>0)slopes.push((samples[j].y-samples[i].y)/dx);}return median(slopes)??0;}
function mannKendall(samples){
 const ys=samples.map(s=>typeof s==='number'?s:s.y),n=ys.length;if(n<10)return 1;
 let sum=0;for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)sum+=Math.sign(ys[j]-ys[i]);
 const ties=new Map();ys.forEach(y=>ties.set(y,(ties.get(y)||0)+1));const correction=[...ties.values()].reduce((s,t)=>s+t*(t-1)*(2*t+5),0);
 const variance=(n*(n-1)*(2*n+5)-correction)/18;if(variance<=0||sum===0)return 1;
 const z=(Math.abs(sum)-1)/Math.sqrt(variance);
 // Two-sided normal tail, Abramowitz-Stegun 7.1.26 approximation.
 const x=z/Math.SQRT2,t=1/(1+.3275911*x),erfc=(((((1.061405429*t-1.453152027)*t+1.421413741)*t-.284496736)*t+.254829592)*t)*Math.exp(-x*x);
 return clamp(erfc,0,1);
}
function effectiveValues(ewma,baseline,metrics,o,c){return Object.fromEntries(metrics.map(m=>{const b=baseline.metrics[m.id];if(!finite(b.median))return[m.id,null];const cap=Math.max(c.driftCap.scaleMultiple*b.scale,c.driftCap.relative*Math.abs(b.median));return[m.id,o.adaptive?clamp(b.median+(ewma[m.id]-b.median)*o.adaptiveWeight,b.median-cap,b.median+cap):b.median];}));}
function updateEffectiveBaseline(record,index,day,previousState,currentState,ewma,baseline,metrics,o,c){
 const before=effectiveValues(ewma,baseline,metrics,o,c),contexts=confirmedContexts(record),available=metrics.filter(m=>baseline.metrics[m.id].eligible&&finite(value(record,m.id)));
 let reason=!o.adaptive?'disabled':!day.observed?'missing_or_undercovered':contexts.length?'confirmed_context':/^(watch|flag_)/.test(previousState||'')||/^(watch|flag_)/.test(currentState||'')?'alert_state':available.some(m=>deviation(value(record,m.id)-before[m.id],m.direction,baseline.metrics[m.id].scale)>c.tolerance.z)?'outside_tolerance':'accepted';
 const updates=[];
 for(const m of metrics){const b=baseline.metrics[m.id],v=value(record,m.id),old=ewma[m.id];let why=reason;if(!b.eligible||!finite(v))why='missing';
  if(why==='accepted'){const proposed=old+o.adaptiveAlpha*(v-old),cap=Math.max(c.driftCap.scaleMultiple*b.scale,c.driftCap.relative*Math.abs(b.median));ewma[m.id]=o.adaptiveWeight>0?clamp(proposed,b.median-cap,b.median+cap):b.median;}
  updates.push({index,period:record.period,id:m.id,status:why==='accepted'?'updated':'frozen',reason:why,before:old,after:ewma[m.id],contexts});
 }
 return {effective:effectiveValues(ewma,baseline,metrics,o,c),updates};
}
function persistenceState(days,index,lastBaseline,records,c){
 let from=Math.max(lastBaseline+1,index-c.sustained.m+1);
 // Indexed daily gaps represent absent calendar days, not adjacent observations.
 if(Number.isSafeInteger(records[index].periodIndex))while(from<index&&records[from].periodIndex<records[index].periodIndex-c.sustained.m+1)from++;
 const span=days.slice(from,index+1),observed=span.filter(d=>d?.observed);
 const rawHigh=observed.filter(d=>Math.max(d.anchoredScore,d.rawScore)>=c.sustained.index*100).length;
 const contextDays=records.slice(from,index+1).filter(r=>confirmedContexts(r).some(x=>['illness','intentional_activity_change'].includes(x.type))).length;
 const contextual=contextDays>=Math.ceil(c.sustained.m/2);
 const high=contextual?observed.filter(d=>d.contributors.some(q=>c.domains.mood.includes(q.id)&&Math.max(q.anchoredScore,q.score)>=c.sustained.index*100)).length:rawHigh;
 const stateFor=hi=>observed.length<c.sustained.minObserved?'insufficient_data':hi>=c.sustained.k?'flag_sustained':hi>=c.watch.k?'watch':days[index]?.observed&&Math.max(days[index].anchoredScore,days[index].rawScore)>=c.noted.index*100?'noted':'steady';
 return {state:stateFor(high),unsuppressedState:stateFor(rawHigh),persistence:{window:c.sustained.m,observedDays:observed.length,highDays:high,flaggedDays:high,threshold:c.sustained.index,k:c.sustained.k,unadjustedHighDays:rawHigh},contextual,contextSuppressed:rawHigh>=c.sustained.k&&high<c.sustained.k&&observed.length>=c.sustained.minObserved,contextDays};
}
function driftState(records,days,index,lastBaseline,baseline,metrics,c){
 const output=[],domains=new Set();
 for(const m of metrics){const b=baseline.metrics[m.id];if(!b.eligible)continue;const samples=[];
  for(let i=index;i>lastBaseline&&samples.length<c.drift.trendWindow;i--)if(days[i]?.observed&&finite(value(records[i],m.id)))samples.unshift({x:records[i].periodIndex??i,y:value(records[i],m.id)});
  const recent=samples.slice(-c.drift.window),recentMedian=recent.length>=c.drift.window?median(recent.map(s=>s.y)):null,change=finite(recentMedian)?recentMedian-b.median:null,zAnchor=finite(change)?deviation(change,m.direction,b.scale):null;
  const slopePerDay=theilSen(samples),mkP=mannKendall(samples),isAdverse=m.direction==='lower'?slopePerDay<0:m.direction==='higher'?slopePerDay>0:finite(change)&&change*slopePerDay>0;
  const minimum=Object.hasOwn(c.drift.relativeMin,m.id)?c.drift.relativeMin[m.id]:0,required=m.id==='steps'?minimum*Math.abs(b.median):minimum;
  const qualifies=finite(value(records[index],m.id))&&finite(change)&&zAnchor>=c.drift.z&&adverse(change,m.direction)>=required&&isAdverse&&mkP<c.drift.mkP;
  const domain=Object.keys(c.domains).find(k=>c.domains[k].includes(m.id));if(qualifies&&domain)domains.add(domain);
  output.push({id:m.id,anchorMedian:b.median,recentMedian,change,zAnchor,z:zAnchor,slopePerDay,slope:slopePerDay,mkP,adverse:isAdverse,qualifies,domain:domain||null,observedValues:samples.length});
 }
 return {triggered:domains.size>=Math.max(2,c.drift.minMetrics)||(domains.has('mood')&&domains.size>=2),domains:[...domains],metrics:output};
}
const oldToAlert={no_change:'steady',change_detected:'watch',review_suggested:'flag_sustained'};
const alertToOld={steady:'no_change',noted:'no_change',watch:'change_detected',flag_sustained:'review_suggested',flag_drift:'review_suggested'};
// Independent episode memory: never feeds back into scores, daily states or adaptation.
function ongoingPattern(previous,index,day,state,drift,c){
 const p=previous?{...previous}:{active:false,startedIndex:null,lastFlagIndex:null,lastFlagState:null,recoveryDays:0,clearedIndex:null};
 p.clearAfter=c.hysteresis.observedDays;p.clearBelow=c.hysteresis.clearBelow;p.observed=Boolean(day?.observed);
 if(!p.observed)return p; // Gaps pause consecutive *observed* recovery days.
 if(state.startsWith('flag_')){if(!p.active)p.startedIndex=index;p.active=true;p.lastFlagIndex=index;p.lastFlagState=state;p.recoveryDays=0;p.clearedIndex=null;}
 else if(p.active){
  const h=Math.max(day.anchoredScore,day.rawScore)/100;
  p.recoveryDays=finite(h)&&h<p.clearBelow&&!drift.triggered?p.recoveryDays+1:0;
  if(p.recoveryDays>=p.clearAfter){p.active=false;p.clearedIndex=index;}
 }
 return p;
}
function runAlerting(records,points,computePoint,baseline,metrics,o,c){
 const anchor=Object.fromEntries(metrics.map(m=>[m.id,baseline.metrics[m.id].median])),ewma={...anchor},snapshots=[],days=[],states=[],updates=[];let firstFlagIndex=null,firstFlagState=null,ongoing=null;
 for(let t=0;t<records.length;t++){
  if(t<=baseline.endIndex){const point=points[t];point.alertState=oldToAlert[point.status]||point.status;point.alertReason=null;point.anchorBaseline={...anchor};point.baselineUsed={...anchor};point.effectiveBaseline={...anchor};point.persistence={window:c.sustained.m,observedDays:0,highDays:0,flaggedDays:0,threshold:c.sustained.index,k:c.sustained.k};point.drift={triggered:false,domains:[],metrics:[]};point.ongoingPattern=ongoingPattern(null,t,null,point.alertState,point.drift,c);snapshots[t]={...anchor};states[t]=point.alertState;continue;}
  const before=snapshots[t-1]||anchor,day=computePoint(records[t],t,1,before);day.observed=!records[t].missingPeriod&&finite(day.score)&&day.coverage>=o.minCoverage;days[t]=day;
  const start=Math.max(baseline.endIndex+1,t-o.windowSize+1),used=snapshots[start-1]||anchor,point=computePoint(records[t],t,o.windowSize,used);points[t]=point;
  const persistence=persistenceState(days,t,baseline.endIndex,records,c),drift=day.observed?driftState(records,days,t,baseline.endIndex,baseline,metrics,c):{triggered:false,domains:[],metrics:[]};
  let state=!day.observed?'insufficient_data':drift.triggered?'flag_drift':persistence.state;states[t]=state;
  const update=updateEffectiveBaseline(records[t],t,day,states[t-1],state,ewma,baseline,metrics,o,c);updates.push(...update.updates);snapshots[t]=update.effective;
  ongoing=ongoingPattern(ongoing,t,day,state,drift,c);point.ongoingPattern=ongoing;
  if(!finite(point.score))state=point.status;
  point.alertState=state;point.alertReason=state==='noted'?'single_day':state==='watch'?'emerging':state==='flag_sustained'?'k_of_m':state==='flag_drift'?'drift':null;
  point.status=alertToOld[state]||state;point.persistence=persistence.persistence;point.drift=drift;point.anchorBaseline={...anchor};point.baselineUsed={...used};point.effectiveBaseline={...update.effective};
  point.daySignal={score:day.score,normalizedIndex:day.normalizedIndex,anchoredScore:day.anchoredScore,rawScore:day.rawScore,coverage:day.coverage,observed:day.observed,contributors:day.contributors};
  point.unsuppressedAlertState=drift.triggered?'flag_drift':persistence.unsuppressedState;
  point.contextPolicy='Daily Path A may count only mood-driven high days during confirmed illness/intentional-change context. Drift is never suppressed. Original anchored/raw scores and unsuppressedAlertState remain available; numeric context weights do not attenuate mood.';
  if(persistence.contextual){point.contextNote='Confirmed illness/intentional-change context covers '+persistence.contextDays+' of the last '+c.sustained.m+' calendar slots. Path A counts mood-driven evidence only; drift and original anchored/raw signals remain visible.';if(persistence.contextSuppressed)point.contextSuppressed=true;}
  point.adaptation.updates=updates.filter(u=>u.index<start);point.adaptation.nextUpdate=update.updates;
  for(const m of metrics)if(point.adaptation.metrics[m.id]){point.adaptation.metrics[m.id].effective=used[m.id];point.adaptation.metrics[m.id].ewma=o.adaptiveWeight>0?anchor[m.id]+(used[m.id]-anchor[m.id])/o.adaptiveWeight:anchor[m.id];}
  if(state==='noted')point.explanation="A harder day. One day on its own isn't a pattern.";
  else if(state==='watch')point.explanation='A few days have looked different.';
  else if(state==='flag_sustained')point.explanation='Several days in the recent window have looked different; a pattern worth a check-in.';
  else if(state==='flag_drift')point.explanation='A slow adverse change versus the original anchor spans at least two domains; a pattern worth a check-in.';
  else if(state==='steady')point.explanation='No persistent adverse pattern in the available observations.';
  else if(state==='insufficient_data'&&finite(point.score))point.explanation='Too few observed days to assess a persistent pattern.';
  if(firstFlagIndex===null&&state.startsWith('flag_')){firstFlagIndex=t;firstFlagState=state;}
 }
 return {version:MODEL_VERSION,enabled:true,config:c,firstFlagIndex,firstFlagState};
}

function analyze(records,options){
 if(!Array.isArray(records))throw new TypeError('records must be an ordered array');
 if(records.some(r=>!r||typeof r!=='object'||Array.isArray(r)||!r.values||typeof r.values!=='object'||Array.isArray(r.values)))throw new TypeError('Each record requires a values object');
 const indexed=records.some(r=>r.periodIndex!==undefined);
 if(indexed&&records.some((r,i)=>!Number.isSafeInteger(r.periodIndex)||(i>0&&r.periodIndex<=records[i-1].periodIndex)))throw new RangeError('periodIndex must be present, safe integer, unique and strictly increasing');
 if(records.some(r=>Object.values(r.values).some(v=>finite(v)&&Math.abs(v)>Number.MAX_SAFE_INTEGER)))throw new RangeError('Measurement magnitude exceeds safe arithmetic range');
 const ac=alertConfig(options?.alerting),dailyAlerts=options?.granularity==='day'&&ac.enabled;
 const o=Object.assign({windowSize:2,minBaseline:options&&options.granularity==='day'?7:3,minMetrics:2,minCoverage:0.6,baselineLabel:'User-selected reference',adaptive:dailyAlerts,adaptiveWeight:0.15,adaptiveAlpha:dailyAlerts?ac.adapt.alpha:0.1,contextWeights:{illness:1,recovery:1,intentional_activity_change:1}},options||{});
 if(!Array.isArray(o.metrics)||!o.metrics.length)throw new TypeError('Explicit metric definitions are required');
 for(const k of ['windowSize','minBaseline','minMetrics'])if(!Number.isInteger(o[k])||o[k]<1)throw new RangeError(k+' must be a positive integer');
 if(typeof o.adaptive!=='boolean')throw new TypeError('adaptive must be boolean');
 if(!finite(o.adaptiveWeight)||o.adaptiveWeight<0||o.adaptiveWeight>0.25)throw new RangeError('adaptiveWeight must be in [0,.25] to preserve the anchor');
 if(!finite(o.adaptiveAlpha)||o.adaptiveAlpha<=0||o.adaptiveAlpha>1)throw new RangeError('adaptiveAlpha must be in (0,1]');
 if(!o.contextWeights||typeof o.contextWeights!=='object'||['illness','recovery','intentional_activity_change'].some(k=>!finite(o.contextWeights[k])||o.contextWeights[k]<0||o.contextWeights[k]>1))throw new RangeError('Explicit context weights must lie in [0,1]');
 if(!finite(o.minCoverage)||o.minCoverage<=0||o.minCoverage>1)throw new RangeError('minCoverage must be in (0,1]');
 ac.adapt.alpha=o.adaptiveAlpha;ac.adapt.weight=o.adaptiveWeight;ac.adapt.enabled=o.adaptive;
 if(dailyAlerts&&o.adaptiveWeight>ac.adapt.maxWeight)throw new RangeError('adaptiveWeight exceeds alerting.adapt.maxWeight');
 const seen=new Set();
 const metrics=o.metrics.map(m=>{if(!m||typeof m.id!=='string'||!m.id.trim()||seen.has(m.id))throw new TypeError('Metric IDs must be unique');seen.add(m.id);if(!finite(m.floor)||m.floor<=0)throw new RangeError('Each metric needs a positive scale floor in its own units');if(!['lower','higher','both'].includes(m.direction))throw new TypeError('Invalid metric direction');const weight=m.weight===undefined?1:m.weight;if(!finite(weight)||weight<=0||weight>Number.MAX_SAFE_INTEGER)throw new RangeError('Metric weights must be positive');return Object.assign({},m,{weight});});
 for(const m of metrics){if(m.min!==undefined&&!finite(m.min)||m.max!==undefined&&!finite(m.max)||m.min!==undefined&&m.max!==undefined&&m.min>m.max)throw new RangeError('Invalid metric domain bounds');for(const r of records){const v=value(r,m.id);if(finite(v)&&(m.min!==undefined&&v<m.min||m.max!==undefined&&v>m.max))throw new RangeError('Measurement outside configured domain: '+m.id);}}
 if(o.baselineIndices!==undefined&&!Array.isArray(o.baselineIndices))throw new TypeError('baselineIndices must be an array');
 const indices=Array.from(new Set(o.baselineIndices||[])).sort((a,b)=>a-b);
 if(indices.some(i=>!Number.isInteger(i)||i<0||i>=records.length))throw new RangeError('Invalid baseline index');
 const selectedEnd=indices.length?indices[indices.length-1]:-1;
 const lastBaseline=o.referenceEndIndex===undefined?selectedEnd:o.referenceEndIndex;
 if(!Number.isInteger(lastBaseline)||lastBaseline<selectedEnd||lastBaseline>=records.length||lastBaseline< -1)throw new RangeError('referenceEndIndex must cover the selected baseline and lie within records');
 const baseline={label:o.baselineLabel,indices,endIndex:lastBaseline,variabilityKnown:indices.length>=3,metrics:Object.create(null),eligible:indices.length>=o.minBaseline,quality:indices.length<(o.granularity==='day'?7:3)?'low_evidence':'provisional',warning:indices.length===1?'Single-observation reference: variability is unknown; scale floors drive the comparison.':indices.length<(o.granularity==='day'?7:3)?'Short reference: variability estimates are unstable.':'Reference selection does not establish clinical wellness.'};
 metrics.forEach(m=>{const values=indices.map(i=>value(records[i],m.id)).filter(finite);const center=median(values);const mad=center===null?null:median(values.map(v=>Math.abs(v-center)));const count=values.length;baseline.metrics[m.id]={median:center,mad,scale:center===null?null:Math.max(1.4826*mad,m.floor),count,variabilityKnown:count>=3,eligible:count>=o.minBaseline&&count/Math.max(indices.length,1)>=o.minCoverage};});
 const totalWeight=metrics.reduce((s,m)=>s+m.weight,0);
 function computePoint(record,index,windowSize=o.windowSize,effectiveOverrides=null){
  const point={index,period:record.period===undefined?String(index):record.period,status:'insufficient_data',score:null,normalizedIndex:null,relapseVector:null,anchoredScore:null,rawScore:null,contextMultiplier:1,contexts:[],adaptation:{enabled:o.adaptive,weight:o.adaptive?o.adaptiveWeight:0,alpha:o.adaptiveAlpha,updates:[],metrics:Object.create(null)},coverage:0,contributors:[],windowIndices:[],explanation:''};
  if(indices.includes(index)){point.status='baseline';point.explanation='Selected reference observation; not scored.';return point;}
  if(index<=lastBaseline){point.explanation='Outside the reference selection and before the reference ends; not scored to avoid future-data leakage.';return point;}
  if(!baseline.eligible){point.explanation='Select at least '+o.minBaseline+' reference observations before monitoring. ';return point;}
  const start=Math.max(lastBaseline+1,index-windowSize+1);point.windowIndices=Array.from({length:index-start+1},(_,j)=>start+j);
  const positions=point.windowIndices.map(i=>records[i].periodIndex);
  if(positions.every(finite)&&positions.some((v,j)=>j>0&&v!==positions[j-1]+1)){point.explanation='Monitoring window contains missing periods; score withheld.';return point;}
  if(!metrics.some(m=>finite(value(record,m.id)))){point.explanation='No current measurements; prior observations cannot establish current state.';return point;}
  if(point.windowIndices.length<windowSize){point.status='collecting_window';point.explanation='Collecting a complete '+windowSize+'-observation monitoring window.';return point;}
  let coverageWeight=0;
  metrics.forEach(m=>{
   const b=baseline.metrics[m.id];const vals=point.windowIndices.map(i=>value(records[i],m.id)).filter(finite);const coverage=vals.length/windowSize;
   const hasCurrent=finite(value(record,m.id));
   if(b.eligible&&hasCurrent)coverageWeight+=m.weight*coverage;
   if(!b.eligible||!hasCurrent||coverage<o.minCoverage)return;
   let ewma=b.median;
   if(o.adaptive&&!dailyAlerts&&!effectiveOverrides){for(let prior=lastBaseline+1;prior<start;prior++){
    const observed=value(records[prior],m.id),contexts=confirmedContexts(records[prior]);let reason='accepted';
    if(!finite(observed))reason='missing';else if(contexts.length)reason='confirmed_context';else if(deviation(observed-b.median,m.direction,b.scale)>1)reason='anchored_adverse_shift';
    const before=ewma;if(reason==='accepted')ewma=ewma+o.adaptiveAlpha*(observed-ewma);
    point.adaptation.updates.push({index:prior,period:records[prior].period,id:m.id,status:reason==='accepted'?'updated':'frozen',reason,before,after:ewma,contexts});
   }}
   const effective=effectiveOverrides&&finite(effectiveOverrides[m.id])?effectiveOverrides[m.id]:o.adaptive?b.median*(1-o.adaptiveWeight)+ewma*o.adaptiveWeight:b.median;
   point.adaptation.metrics[m.id]={anchor:b.median,ewma,effective};
   const current=median(vals),delta=current-b.median,adaptiveDelta=current-effective;
   const anchoredZ=deviation(delta,m.direction,b.scale),z=deviation(adaptiveDelta,m.direction,b.scale);
   const anchoredScore=featureScore(anchoredZ),score=featureScore(z);
   const appliedContexts=[];
   const contextMultiplier=point.windowIndices.reduce((sum,i)=>{let multiplier=1;for(const c of confirmedContexts(records[i])){if(CONTEXT_METRICS[c.type].includes(m.id)&&finite(value(records[i],m.id))){multiplier=Math.min(multiplier,o.contextWeights[c.type]);appliedContexts.push(Object.assign({index:i},c));}}return sum+multiplier;},0)/windowSize;
   const adjustedScore=score*contextMultiplier;
   point.contributors.push({id:m.id,label:m.label||m.id,unit:m.unit||'',direction:m.direction,baseline:b.median,adaptiveReference:effective,current,delta,adaptiveDelta,anchoredZ,anchoredScore,relativeChange:b.median===0||!finite(delta/Math.abs(b.median))?null:delta/Math.abs(b.median),z,score,adjustedScore,contextMultiplier,appliedContexts,coverage,weight:m.weight});
  });
  point.coverage=coverageWeight/totalWeight;
  if(point.contributors.length<o.minMetrics||point.coverage<o.minCoverage){point.explanation='Insufficient comparable measurements: '+point.contributors.length+' eligible metrics; '+Math.round(point.coverage*100)+'% observation coverage.';return point;}
  const eligibleWeight=point.contributors.reduce((s,c)=>s+c.weight,0);
  point.anchoredScore=Math.round(point.contributors.reduce((s,c)=>s+c.anchoredScore*c.weight,0)/eligibleWeight);
  point.rawScore=Math.round(point.contributors.reduce((s,c)=>s+c.score*c.weight,0)/eligibleWeight);
  point.contexts=point.windowIndices.flatMap(i=>confirmedContexts(records[i]).map(c=>Object.assign({index:i},c)));
  const rawMean=point.contributors.reduce((s,c)=>s+c.score*c.weight,0)/eligibleWeight;
  const adjustedMean=point.contributors.reduce((s,c)=>s+c.adjustedScore*c.weight,0)/eligibleWeight;
  point.contextMultiplier=rawMean>0?adjustedMean/rawMean:1;
  point.score=Math.round(adjustedMean);
  point.normalizedIndex=point.score/100;point.relapseVector=point.normalizedIndex;
  point.signalScore=Math.max(point.anchoredScore,point.rawScore);
  point.contextPolicy='Opt-in metric-scoped contextual heuristic, proportional to flagged observations in this window; no causal attribution. Mood is never attenuated; context cannot reduce the unadjusted signal status.';
  point.status=point.signalScore>=50?'review_suggested':point.signalScore>=20?'change_detected':'no_change';
  point.contributors.sort((a,b)=>b.score*b.weight-a.score*a.weight);
  point.explanation=point.status==='no_change'?'No substantial directional deviation in the available measurements.':point.status==='change_detected'?'A directional change from the selected reference is present. Context and self-report are needed.':'Several measurements or a strongly weighted measurement differ from the selected reference. A supportive check-in may be appropriate.';
  if(point.contextMultiplier<1)point.explanation+=' Confirmed context adjusts only eligible physiological/activity metrics in proportion to its overlap with this window; mood and the unadjusted change status remain unchanged.';
  if(baseline.quality==='low_evidence')point.explanation+=' '+baseline.warning;
  return point;
 }
 const points=records.map((record,index)=>computePoint(record,index));
 let alerting;
 if(dailyAlerts)alerting=runAlerting(records,points,computePoint,baseline,metrics,o,ac);
 else{for(const point of points){point.alertState=oldToAlert[point.status]||point.status;point.alertReason=null;point.ongoingPattern=null;}alerting={version:MODEL_VERSION,enabled:false,config:{...ac,enabled:false},firstFlagIndex:null,firstFlagState:null};}
 return {modelVersion:MODEL_VERSION,alerting,scoreMeaning:'Directional behavior-change index; relapseVector is an integration alias, not a clinical relapse probability',baseline,points,latest:points.length?points[points.length-1]:null,config:{windowSize:o.windowSize,minBaseline:o.minBaseline,minMetrics:o.minMetrics,minCoverage:o.minCoverage,granularity:o.granularity||'observation',adaptive:o.adaptive,adaptiveWeight:o.adaptiveWeight,adaptiveAlpha:o.adaptiveAlpha,contextWeights:Object.assign({},o.contextWeights),contextMetricIds:Object.fromEntries(Object.entries(CONTEXT_METRICS).map(([k,v])=>[k,v.slice()]))}};
}
return {analyze,median,MODEL_VERSION,ALERT_DEFAULTS,theilSen,mannKendall};
});
