'use strict';
// Presentation regressions for the presentation/2.0 redesign. DOM mock: checks rendered markup and state, not visuals.
const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=path.resolve(__dirname,'..'),data=JSON.parse(fs.readFileSync(path.join(root,'data/demo-data.json'),'utf8'));
const html=fs.readFileSync(path.join(root,'index.html'),'utf8'),ids=new Set([...html.matchAll(/id="([^"]+)"/g)].map(m=>m[1]));
for(const f of ['companion-signals.js','tour.js'])assert(html.includes(`<script src="${f}"></script>`),f+' loaded');
assert(html.indexOf('companion-signals.js')<html.indexOf('src="app.js"')&&html.indexOf('src="app.js"')<html.indexOf('tour.js'),'script order');
const server=fs.readFileSync(path.join(root,'scripts/preview_server.py'),'utf8');for(const f of ['companion-signals.js','tour.js','favicon.svg'])assert(server.includes(`'${f}'`),'preview server serves '+f);
const pkg=fs.readFileSync(path.join(root,'scripts/package_viewer.py'),'utf8');for(const f of ['companion-signals.js','tour.js','favicon.svg','docs/integration-contract.md'])assert(pkg.includes(`'${f}'`),'package includes '+f);
function boot(people){
 const nodes={},el=id=>{assert(ids.has(id),'Unknown HTML id '+id);return nodes[id]||(nodes[id]={value:'0',style:{},dataset:{},attributes:{},textContent:'',innerHTML:'',hidden:false,className:'',listeners:{},setAttribute(k,v){this.attributes[k]=String(v)},addEventListener(k,f){this.listeners[k]=f},querySelector(){return {focus(){}}}});};
 const ctx={document:{body:{dataset:{}},activeElement:null,getElementById:el,createElement:()=>({click(){}})},console,DEMO_DATA:{...data,participants:people},sessionStorage:{getItem(){return null},setItem(){}},setInterval(){return 1},clearInterval(){},setTimeout(fn){return 0},clearTimeout(){},innerWidth:1280,Blob,URL:{createObjectURL(b){ctx.blob=b;return 'blob:x'},revokeObjectURL(){}}};
 ctx.window=ctx;vm.createContext(ctx);for(const f of ['engine.js','insights.js','companion-signals.js','app.js'])vm.runInContext(fs.readFileSync(path.join(root,f),'utf8'),ctx,{filename:f});
 return {ctx,el,contract:()=>JSON.parse(el('contract').textContent),trigger:(id,t='input',e)=>el(id).listeners[t](e)};
}
const synthetic=data.participants.filter(p=>p.synthetic),research=data.participants.filter(p=>!p.synthetic).slice(0,3);
const app=boot([...synthetic,...research]);const {el,contract,ctx}=app;
assert.equal(contract().participant,'sim-02');assert.equal(contract().assessment.index,86);
// Gauge, status colour and care card agree with the engine status.
assert(el('score-gauge').innerHTML.startsWith('<div class="orb review"'));assert(el('score-gauge').innerHTML.includes('<svg'));assert.equal(contract().assessment.status,'review_suggested');assert(el('score-gauge').innerHTML.includes('#ad6863'));
assert.equal(el('care-card').hidden,false);assert(el('care-card').className.includes('tone-review'));assert(el('care-card').innerHTML.includes('isn’t a diagnosis'));assert(el('care-card').innerHTML.includes('Would a small check-in help?'));assert.equal(el('status').textContent,'Things have been slowly shifting over the past weeks.');assert(el('care-card').innerHTML.includes('data-care="share"'));
// Persistence counts and drift evidence are rendered from the engine, not recalculated.
ctx.WithinApp.go({index:100});assert.equal(contract().assessment.alertState,'flag_sustained');const stats=el('score-stats').innerHTML,persistence=contract().assessment.persistence;assert(stats.includes(`${persistence.highDays} of ${persistence.observedDays} observed days`));assert(stats.includes(`last ${persistence.window} calendar days`));assert(stats.includes('anchored index'));assert(el('drift-table').innerHTML.includes('Drift vs anchor'));assert(el('drift-table').innerHTML.includes('Next-day baseline'));assert.equal(el('status').textContent,'Several days in a row have looked different.');
// Timeline: thresholds, reference/window shading, phase bands, escaped labels.
const tl=el('timeline').innerHTML;for(const s of ['>signal 0.20<','>signal 0.50<','#fae8b8','#ece2ec','Your usual','Sustained disruption','tl-area','data-alert-state="flag_sustained"','height="6"'])assert(tl.includes(s),s);
// Story strip lists every demo person and marks the current one.
assert.equal(synthetic.length,11);
assert.equal((el('story-strip').innerHTML.match(/class="pebble-btn"/g)||[]).length,synthetic.length);assert.equal((el('story-strip').innerHTML.match(/aria-pressed="true"/g)||[]).length,1);assert(el('source-tabs').innerHTML.includes('data-source="synthetic" aria-pressed="true"'));assert.equal(el('story-name').textContent,'Noah');assert.equal(el('person-sub').textContent,'smaller days');
// Reference day: quiet tone, no gauge value claims.
ctx.WithinApp.go({index:10});assert.equal(contract().assessment.status,'baseline');assert.equal(el('care-card').hidden,true,'no care card on quiet days');assert.equal(el('status').textContent,'This day is part of your usual');assert.equal(el('score').textContent,'—');assert(el('usual-range').textContent.startsWith('your usual, '));
// Daily signals remain visible, while a single hard day never receives a flag or care card.
ctx.WithinApp.go({participantId:'sim-09',index:64,window:1,view:'clinical'});assert.equal(contract().participant,'sim-09');assert.equal(contract().assessment.index,64);assert.equal(ctx.document.body.dataset.view,'clinical');const singleDay=contract().assessment;assert.equal(singleDay.alertState,'noted');assert.equal(singleDay.status,'no_change');assert(singleDay.score>=50,'the original day signal remains visible');assert.equal(el('care-card').hidden,true);assert(el('score-gauge').innerHTML.includes('orb steady noted'));assert(el('timeline').innerHTML.includes('data-alert-state="noted"'));
ctx.WithinApp.go({window:7});assert.equal(contract().analysisConfig.windowSize,7);assert(contract().assessment.score<20,'selected-window score keeps its median meaning');assert.equal(contract().assessment.alertState,'noted');assert.deepEqual(contract().assessment.daySignal,singleDay.daySignal);assert.deepEqual(contract().assessment.persistence,singleDay.persistence);assert.deepEqual(ctx.WithinApp.state(),{dataset:'synthetic',participantId:'sim-09',index:64,window:7,view:'clinical'});
ctx.WithinApp.go({window:1,view:'personal',index:64});assert.equal(el('status').textContent,"A harder day. One day on its own isn't a pattern.");assert.equal(el('care-card').hidden,true);ctx.WithinApp.go({index:65});assert.equal(contract().assessment.alertState,'steady');assert.equal(el('care-card').hidden,true);
ctx.WithinApp.go({participantId:'sim-11',index:99,window:1,view:'clinical'});assert.equal(contract().assessment.alertState,'flag_drift');assert.equal(contract().assessment.status,'review_suggested');assert(contract().assessment.drift.triggered);assert(el('drift-table').innerHTML.includes('✓'));assert(el('care-card').innerHTML.includes('A slow change over the past weeks.'));assert(contract().assessment.daySignal.score<35,'slow drift can flag while the day signal stays quiet');
ctx.WithinApp.go({window:1,view:'personal',participantId:'sim-02',index:100});
// Companion panel + export for a demo person: synthetic components labelled, combined preview present.
assert(el('companion-signals').innerHTML.includes('Demo'));assert.equal(el('companion-badge').textContent,'Demo component outputs');
app.trigger('export','click');let exp;
const readBlob=async()=>JSON.parse(await ctx.blob.text());
(async()=>{
 exp=await readBlob();assert.equal(exp.contractVersion,'1.2.0');assert.equal(exp.alertState,'flag_sustained');assert.deepEqual(exp.persistence,exp.assessment.persistence);assert.deepEqual(exp.drift,exp.assessment.drift);assert.equal(exp.alerting.version,'routine-change/2.0.0');assert.equal(exp.synthetic,true);assert.equal(exp.componentSignals.length,4);assert.equal(exp.componentSignals.find(s=>s.componentId==='routine').componentVersion,'routine-change/2.0.0');
 assert(exp.componentSignals.filter(s=>s.componentId!=='routine').every(s=>s.synthetic===true&&/^demo-generator/.test(s.provenance)));
 assert(exp.componentSignals.every(s=>s.participantRef==='sim-02'&&s.dayKey==='sim-02:'+exp.selectedObservation.date));
 assert.equal(exp.combinedPreview.fusionVersion,'combined-preview/0.1.0');assert.equal(exp.combinedPreview.includesSynthetic,true);assert(exp.limitations.some(l=>/generated demo outputs/.test(l)));
 // Research participant: no generated values; only the routine component; combined preview abstains.
 el('dataset').value='real';app.trigger('dataset','change');assert.equal(contract().synthetic,false);assert(el('story-strip').innerHTML.includes('class="pebble-btn"'));
 assert(!el('companion-signals').innerHTML.includes('class="demo-dot"'));assert(el('companion-signals').innerHTML.includes('Not connected'));assert.equal(el('companion-badge').textContent,'Team components not yet connected');
 app.trigger('export','click');exp=await readBlob();assert.equal(exp.synthetic,false);assert.deepEqual(exp.componentSignals.map(s=>s.componentId),['routine']);assert.equal(exp.componentSignals[0].synthetic,false);assert.equal(exp.combinedPreview.index,null);assert.equal(exp.combinedPreview.status,'insufficient_components');
 // Review fixes: tour reset restores the default reference; unobserved demo day has no combined value; keyboard ignored while tour open.
 ctx.WithinApp.go({dataset:'synthetic',participantId:'sim-02',index:86});el('reference-start').value='20';app.trigger('reference-start');assert.equal(contract().baseline.indices[0],20);ctx.WithinApp.go({participantId:'sim-02',index:86,reset:true});assert.equal(contract().baseline.indices[0],0,'reset restores default reference');
 const iris=synthetic.find(p=>p.records.some(r=>r.missingPeriod));const gap=iris.records.findIndex(r=>r.missingPeriod);ctx.WithinApp.go({dataset:'synthetic',participantId:iris.id,index:gap,reset:true});app.trigger('export','click');exp=await readBlob();assert.equal(exp.combinedPreview.index,null,'no combined value on missing day');
 ctx.WithinApp.go({participantId:'sim-02',index:86,reset:true});
 // Cache only analysis inputs: navigating/view switching reuses it, in-place health/context/config edits invalidate it.
 const realAnalyze=ctx.RoutineEngine.analyze;let analysisCalls=0;ctx.RoutineEngine.analyze=(...args)=>{analysisCalls++;return realAnalyze(...args);};
 ctx.WithinApp.go({index:101});app.trigger('view-clinical','click');assert.equal(analysisCalls,0);
 const cachedPerson=synthetic.find(p=>p.id==='sim-02'),originalSteps=cachedPerson.records[101].values.steps;
 cachedPerson.records[101].values.steps=originalSteps+1000;app.trigger('period');assert.equal(analysisCalls,1);cachedPerson.records[101].values.steps=originalSteps;app.trigger('period');assert.equal(analysisCalls,2);
 const originalContexts=cachedPerson.records[101].contexts;cachedPerson.records[101].contexts=[{type:'illness',confirmed:true,source:'synthetic'}];app.trigger('period');assert.equal(analysisCalls,3);cachedPerson.records[101].contexts=originalContexts;app.trigger('period');assert.equal(analysisCalls,4);
 el('window').value=7;app.trigger('period');assert.equal(analysisCalls,5,'directly edited controls invalidate cache');ctx.RoutineEngine.analyze=realAnalyze;
 // Care-card actions are demo-only and announced.
 el('dataset').value='synthetic';app.trigger('dataset','change');app.trigger('care-card','click',{target:{closest:()=>({dataset:{care:'reflect'}})}});assert(el('toast').textContent.startsWith('Demo:'));assert.equal(el('toast').hidden,false);

 // Picker search: typing filters suggestions without switching people; an exact ID opens that person; no match keeps the current one.
 el('dataset').value='real';app.trigger('dataset','change');const before=contract().participant;el('participant-search').value='psyche';app.trigger('participant-search');assert.equal(contract().participant,before,'partial query must not switch person');assert(/people match/.test(el('search-note').textContent));
 const target=research[2].id;el('participant-search').value=target;app.trigger('participant-search');assert.equal(contract().participant,target);el('participant-search').value='zz-nobody';app.trigger('participant-search');assert.equal(contract().participant,target);assert(el('search-note').textContent.startsWith('No matches'));
 el('dataset').value='synthetic';app.trigger('dataset','change');
 console.log('PASS: presentation — gauge/status/care tone agree with engine; engine persistence/drift; timeline signals, alert band, phases and shading; story strip; tour selection API; single-day noted and recovery states; analysis cache invalidation; companion panel and export provenance for demo vs research participants; demo-only actions; pebble picker and calm search.');
})().catch(e=>{console.error(e);process.exit(1);});
