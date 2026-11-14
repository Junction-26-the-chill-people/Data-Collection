'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'..'),C=require(path.join(root,'companion-signals.js'));
const data=JSON.parse(fs.readFileSync(path.join(root,'data/demo-data.json'),'utf8'));
const synthetic=data.participants.filter(p=>p.synthetic),research=data.participants.filter(p=>!p.synthetic).slice(0,50);
assert.equal(C.CONTRACT_VERSION,'component-signal/0.1.0');assert.equal(C.FUSION_VERSION,'combined-preview/0.1.0');
assert(Object.isFrozen(C.COMPONENTS)&&C.COMPONENTS.every(Object.isFrozen));
assert(Math.abs(C.COMPONENTS.reduce((a,c)=>a+c.weight,0)-1)<1e-9,'Component weights sum to 1');
// Research participants never receive generated component values.
for(const p of research)for(let i=0;i<p.records.length;i++)assert.deepEqual(C.demoSignals(p,i),[]);
assert.deepEqual(C.demoSignals(null,0),[]);assert.deepEqual(C.demoSignals({synthetic:true,records:[]},3),[]);
// Synthetic outputs: same person/day keys, bounded, deterministic, labelled synthetic, valid against contract.
let count=0;
for(const p of synthetic)for(let i=0;i<p.records.length;i++){
 const a=C.demoSignals(p,i),b=C.demoSignals(p,i),expected={participantRef:p.id,dayKey:C.dayKeyOf(p,p.records[i])};
 assert.deepEqual(a,b,'deterministic');assert.equal(a.length,3);
 for(const s of a){assert.deepEqual(C.validate(s,expected),[],p.id+' '+i+' '+s.componentId);assert.equal(s.synthetic,true);assert(/^demo-generator/.test(s.provenance));assert.equal(s.dayKey,p.records[i].dayKey);assert(s.index===null||(s.index>=0&&s.index<=0.95));count++;}
 const mood=p.records[i].values.mood;const check=a.find(s=>s.componentId==='companion_checkin');if(typeof mood!=='number')assert.equal(check.index,null,'missing mood is not scored');
}
// Stable story stays low; sustained deterioration is higher on average in its marked phase than in its reference.
const mean=(p,from,to,id)=>{let s=0,n=0;for(let i=from;i<=to;i++){const v=C.demoSignals(p,i).find(x=>x.componentId===id).index;if(typeof v==='number'){s+=v;n++;}}return s/n;};
const noah=synthetic.find(p=>p.id==='sim-02'),mara=synthetic.find(p=>p.id==='sim-01');
for(const id of ['companion_checkin','screen_time','social_feed']){assert(mean(noah,80,119,id)>mean(noah,0,27,id)+0.2,id);assert(mean(mara,0,119,id)<0.2,id);}
// Validation rejects identity/day mismatch, bad ranges, missing provenance and unknown components.
const base=C.demoSignals(noah,86)[1],exp={participantRef:'sim-02',dayKey:noah.records[86].dayKey};
assert(C.validate({...base,participantRef:'sim-03'},exp).includes('participant_mismatch'));
assert(C.validate({...base,dayKey:'sim-02:2026-04-02'},exp).includes('day_mismatch'));
assert(C.validate({...base,index:1.4},exp).includes('index_out_of_range'));
assert(C.validate({...base,coverage:-1},exp).includes('coverage_out_of_range'));
assert(C.validate({...base,synthetic:undefined},exp).includes('synthetic_flag_required'));
assert(C.validate({...base,provenance:''},exp).includes('provenance_required'));
assert(C.validate({...base,componentId:'horoscope'},exp).includes('unknown_component'));
assert(C.validate({...base,contractVersion:'component-signal/9.0.0'},exp).includes('unsupported_contract_version'));
assert.deepEqual(C.validate(null),['not_an_object']);
// Fusion: abstains below two components, excludes low coverage and mismatches, weights normalized.
const sig=(id,index,coverage=1,extra={})=>({contractVersion:C.CONTRACT_VERSION,componentId:id,participantRef:'u',dayKey:'u:2026-01-01',index,coverage,synthetic:false,provenance:'test',contributors:[],...extra});
const e={participantRef:'u',dayKey:'u:2026-01-01'};
let f=C.fuse([sig('routine',.6)],e);assert.equal(f.status,'insufficient_components');assert.equal(f.index,null);
f=C.fuse([sig('routine',.6),sig('screen_time',.2,.3)],e);assert.equal(f.index,null);assert.deepEqual(f.rejected[0].errors,['low_coverage']);
f=C.fuse([sig('routine',.6),sig('screen_time',.2)],e);assert.equal(f.status,'combined');assert(Math.abs(f.index-(.6*.5+.2*.15)/.65)<1e-3);assert(Math.abs(f.components.reduce((a,c)=>a+c.normalizedWeight,0)-1)<1e-9);assert.equal(f.includesSynthetic,false);
f=C.fuse([sig('routine',.6),sig('screen_time',.9,1,{participantRef:'other'}),sig('social_feed',null)],e);assert.equal(f.index,null);assert.equal(f.rejected.length,2);
f=C.fuse([sig('routine',0),sig('social_feed',0)],e);assert.equal(f.index,0,'zero is a valid combined value, not missing');
f=C.fuse([sig('routine',.5),sig('social_feed',.5,1,{synthetic:true})],e);assert.equal(f.includesSynthetic,true);assert(/not a relapse probability/.test(f.meaning));
// Routine adapter preserves null scores and research provenance.
const r=C.routineSignal(research[0],0,{score:null,coverage:0,status:'baseline',contributors:[]});assert.equal(r.index,null);assert.equal(r.synthetic,false);assert(/^research-source:/.test(r.provenance));
// Review fixes: no scored phone/feed values on unobserved days; selected reference respected; day keys required.
let missingDays=0;for(const p of synthetic)p.records.forEach((r,i)=>{if(!r.missingPeriod)return;missingDays++;const out=C.demoSignals(p,i);for(const s of out.filter(s=>s.componentId!=='companion_checkin')){assert.equal(s.index,null);assert.equal(s.coverage,0);}const f=C.fuse(out,{participantRef:p.id,dayKey:C.dayKeyOf(p,r)});assert.equal(f.index,null,'no combined value on an unobserved demo day '+p.id+' '+i);});assert(missingDays>0);
const late=noah.records.map((_,i)=>i).slice(80,108);assert.notEqual(C.demoSignals(noah,86)[0].contributors[0].reference,C.demoSignals(noah,86,{referenceIndices:late})[0].contributors[0].reference,'demo reference follows the selected reference');
assert(C.validate({...base,dayKey:null},exp).includes('day_key_required'));assert(C.validate({...base,dayKey:null},{participantRef:'sim-02',dayKey:null}).includes('day_key_required'));
const monthly=research[0];assert.equal(C.dayKeyOf(monthly,monthly.records[0]),monthly.id+':'+monthly.records[0].period);assert(C.validate({...base,participantRef:monthly.id,dayKey:monthly.id+':'+monthly.records[1].period},{participantRef:monthly.id,dayKey:C.dayKeyOf(monthly,monthly.records[0])}).includes('day_mismatch'),'monthly periods cannot be swapped');
console.log('PASS: component-signal contract — '+count+' synthetic payloads validated; research participants receive none; identity/day mismatch, range, provenance and version rejection; fusion abstention, coverage gate and normalized weights; unobserved demo days unscored; selected reference respected; required day keys incl. monthly periods.');
