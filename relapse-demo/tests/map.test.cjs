'use strict';
const assert=require('node:assert/strict');
class Element {constructor(){this.children=[];this.classList={add(){}};this.hidden=false;}appendChild(x){this.children.push(x);}replaceChildren(){this.children=[];}setAttribute(){}addEventListener(name,fn){this[name]=fn;}}
global.document={createElement:()=>new Element()};global.location={protocol:'file:'};
let mapCount=0,tileCount=0,layerOperation=0;
class Layer {constructor(coords){this.coords=coords;this.layers=new Set();this.handlers={};}addTo(target){target.layers.add(this);return this;}bindTooltip(html,options){this.tooltip=html;this.tooltipOptions=options;return this;}bindPopup(html){this.popup=html;return this;}bringToFront(){this.frontOrder=++layerOperation;return this;}setLatLngs(coords){this.writeOrder=++layerOperation;this.coords=coords;this.updates=(this.updates||0)+1;return this;}clearLayers(){this.layers.clear();}removeLayer(x){this.layers.delete(x);}on(event,fn){this.handlers[event]=fn;return this;}}
global.MAP_STREETS={type:'FeatureCollection',features:[]};
global.L={geoJSON:()=>new Layer(),map:()=>{mapCount++;const m=new Layer();Object.assign(m,{setView(){return this;},fitBounds(bounds){this.bounds=bounds;this.fits=(this.fits||0)+1;},invalidateSize(){},hasLayer(x){return this.layers.has(x);},remove(){this.removed=true;},attributionControl:{addAttribution(){}}});return m;},layerGroup:()=>new Layer(),control:{layers:()=>({addTo(){}})},polyline:coords=>new Layer(coords),circleMarker:coords=>new Layer(coords),marker:coords=>new Layer(coords),divIcon:x=>x,latLngBounds:x=>x,tileLayer:()=>{tileCount++;return new Layer();}};
const M=require('../movement-map.js');
const pt=(lat,lon,extra={})=>({lat,lon,...extra}),trip=(id,points)=>({id,mode:'walk',points});
const r={period:'Day 1',trips:[trip('A',[pt(60,24),pt(60.001,24)]),trip('B',[pt(61,25),pt(61.001,25)])]};
assert.equal(M.summarize(r).tripCount,2);assert.ok(Math.abs(M.summarize(r).distanceMeters-222.39)<1,'never bridge separate trips');
assert.equal(M.summarize({trips:[],route:r.trips[0].points}).pointCount,0,'explicit empty trips override legacy route');
const bad=M.summarize({trips:[trip('bad',[pt(60,24),pt(NaN,24),pt(61,25),pt(91,25),pt(62,26)])]});assert.equal(bad.distanceMeters,0);assert.equal(bad.segments.length,3);assert.equal(bad.invalidPointCount,2);
assert.equal(M.summarize({route:[pt(60,24,{tripId:'a'}),pt(60.001,24,{tripId:'a'}),pt(70,30,{tripId:'b'})]}).segments.length,2);
assert.equal(M.summarize({trips:[trip('x',[pt(60,24,{segmentId:0}),pt(70,30,{segmentId:1})])]}).distanceMeters,0);
assert.equal(M.bearing(pt(0,0),pt(0,1)),90);assert.equal(M.bearing(pt(0,0),pt(1,0)),0);assert.equal(M.arrows([pt(0,0),pt(0,0)]).length,0);
assert.equal(M.valid(pt(1,Infinity)),false);assert.equal(M.valid(pt(1,181)),false);
assert.equal(M.representative([r]).record,r,'reference is observed record, not averaged route');
const sparse=Array.from({length:28},(_,i)=>i<4?r:{period:'Day '+i,trips:[]});const sparseRef=M.representative(sparse);assert.equal(sparseRef.mappedDayCount,4);assert.equal(sparseRef.observedDayCount,28);assert.equal(sparseRef.referenceSlotCount,28);assert.equal(M.representative([...sparse,{missingPeriod:true}]).observedDayCount,28);
const blank=new Element();assert.equal(M.update(blank,{participant:{id:'real'},record:{}}).status,'no_data');assert.equal(mapCount,0);
const container=new Element(),p={id:'demo',synthetic:true,places:[pt(60,24,{name:'<img src=x onerror=alert(1)>'})]},payload={participant:p,record:r,baselineRecords:[r]};
let s=M.update(container,payload);assert.equal(mapCount,1);assert.ok(container.children[2].textContent.includes('1 mapped / 1 observed reference days'));assert.equal(tileCount,0,'file URLs must not request OSM tiles');assert.equal(s.status,'offline');assert.equal(s.map.hasLayer(s.streetLayer),true,'offline mode immediately shows bundled streets');assert.equal(s.groups.arrows.layers.size,2);assert.ok([...s.groups.places.layers].some(x=>x.tooltipOptions?.permanent&&x.tooltip.includes('&lt;img')),'permanent place labels escape names');const first=s.selectedLines[0],map=s.map;assert.ok([...s.groups.places.layers].some(x=>x.popup.includes('&lt;img')),'untrusted popup names escaped');
s=M.update(container,payload);assert.equal(s.map,map);assert.equal(s.selectedLines[0],first);assert.ok(first.updates);assert.ok(first.frontOrder>s.referenceLines[0].writeOrder,'selected lines brought above reference on each update');assert.equal(map.fits,1,'slider does not reset viewport');
s=M.update(container,{...payload,record:{period:'Day 50',trips:[]}});assert.equal(s.canvas.hidden,false);assert.equal(s.selectedLines.length,0);assert.ok(s.referenceLines.length);assert.ok(container.children[2].textContent.includes('No mapped walks this day'));
s=M.update(container,{...payload,record:{missingPeriod:true,trips:[]}});assert.ok(container.children[2].textContent.includes('No movement observation'));
s=M.update(container,{participant:{id:'real'},record:{},baselineRecords:[]});assert.equal(s.status,'no_data');assert.equal(s.canvas.hidden,true);assert.equal(s.referenceLines.length,0);assert.equal(s.groups.places.layers.size,0);
M.destroy(container);assert.equal(map.removed,true);
global.location.protocol='http:';s=M.update(container,payload);assert.equal(tileCount,1);s.tileLayer.handlers.tileerror();assert.equal(s.status,'error');s.tileLayer.handlers.loading();s.tileLayer.handlers.tileload();s.tileLayer.handlers.load();assert.equal(s.status,'ready','new loading cycle recovers errors');assert.equal(s.map.hasLayer(s.streetLayer),false,'online tiles replace fallback');s.tileLayer.handlers.tileerror();assert.equal(s.map.hasLayer(s.streetLayer),true,'tile failure restores local streets');
s=M.update(container,{participant:{id:'real'},record:{}});assert.equal(s.map.hasLayer(s.tileLayer),false,'no-GPS switch removes tile layer');assert.equal(s.map.hasLayer(s.streetLayer),false,'no-GPS switch removes fallback');M.destroy(container);global.location.search='?offline=1&story=demo';global.location.href='http://127.0.0.1:8766/package/index.html?offline=1&story=demo#movement';const priorTileCount=tileCount;s=M.update(container,payload);assert.equal(tileCount,priorTileCount);assert.equal(container.children[3].children[0].href,'http://127.0.0.1:8766/package/index.html?story=demo#movement','online detail preserves package origin/path/query/hash while removing offline flag');assert.equal(s.map.hasLayer(s.streetLayer),true,'explicit offline preview uses same no-network path');
global.MAP_STREETS.bbox=[24.945,60.166,24.953,60.169];s=M.update(container,payload);assert.equal(s.localCoverage,'none');assert.equal(s.map.hasLayer(s.streetLayer),false);assert.ok(container.children[2].textContent.includes('local street context is not bundled'));
console.log('Map regression suite passed: geometry gaps, trip segmentation, direction, reference selection, persistent updates, empty days, missing days, provenance escaping, offline policy and tile recovery.');

// A stale selection or wrong-person GPS record must not appear against this person's health.
const linkedRecord={...r,participantId:'person-a',subjectId:'person-a',date:'2026-03-10',dayKey:'person-a:2026-03-10',timeZone:'UTC',periodIndex:65};
const linkedPerson={id:'person-a',timeZone:'UTC',records:[linkedRecord],places:[]};
assert.equal(M.linkageIssue(linkedPerson,linkedRecord,0),null);
assert.equal(M.linkageIssue(linkedPerson,{...linkedRecord,participantId:'person-b'},0),'person_mismatch');
assert.equal(M.linkageIssue(linkedPerson,{...linkedRecord,subjectId:'person-b'},0),'person_mismatch');
assert.equal(M.linkageIssue(linkedPerson,{...linkedRecord,dayKey:'person-a:2026-03-09'},0),'day_key_mismatch');
assert.equal(M.linkageIssue(linkedPerson,{...linkedRecord,timeZone:'Europe/Helsinki'},0),'timezone_mismatch');
assert.equal(M.linkageIssue(linkedPerson,{...linkedRecord,date:'2026-03-09',dayKey:'person-a:2026-03-09'},0),'selected_day_mismatch');
assert.equal(M.linkageIssue(linkedPerson,linkedRecord,1),'selected_day_missing');
let linkedState=M.update(container,{participant:linkedPerson,record:linkedRecord,selectedIndex:0,baselineRecords:[linkedRecord,{...linkedRecord,participantId:'person-b'}]});assert.equal(linkedState.rejectedReferenceCount,1);assert.equal(linkedState.reference.mappedDayCount,1);assert(container.children[2].textContent.includes('1 reference records excluded'));
const oldLinkedMap=linkedState.map;linkedState=M.update(container,{participant:linkedPerson,record:{...linkedRecord,participantId:'person-b'},selectedIndex:0});assert.equal(linkedState.status,'linkage_error');assert.equal(oldLinkedMap.removed,true);assert.equal(linkedState.summary.pointCount,0);assert(container.textContent.includes('does not match'));
linkedState=M.update(container,{participant:linkedPerson,record:linkedRecord,selectedIndex:0,baselineRecords:[linkedRecord]});assert.notEqual(linkedState.status,'linkage_error');assert(linkedState.summary.pointCount>0);
console.log('PASS linked GPS guard: person, subject, selected day, day key and timezone mismatches reject routes; contaminated references are excluded; recovery clears stale geometry.');

// Separate regional bundles must not claim coverage between distant cities.
M.destroy(container);global.MAP_STREET_REGIONS=[{type:'FeatureCollection',bbox:[-72.31,43.68,-72.26,43.73],features:[]}];
const hanover={trips:[trip('gps',[pt(43.70,-72.29),pt(43.701,-72.29)])]};
s=M.update(container,{participant:{id:'studentlife-sample'},record:hanover,baselineRecords:[]});assert.equal(s.localCoverage,'full');assert.equal(s.map.hasLayer(s.streetLayer),true);
s=M.update(container,{participant:{id:'not-in-either-bundle'},record:{trips:[trip('outside',[pt(50,-20),pt(50.001,-20)])]},baselineRecords:[]});assert.equal(s.localCoverage,'none');assert.equal(s.map.hasLayer(s.streetLayer),false);
s=M.update(container,{participant:{id:'partially-covered'},record:{trips:[trip('mixed',[pt(43.70,-72.29),pt(43.75,-72.29)])]},baselineRecords:[]});assert.equal(s.localCoverage,'partial');
console.log('PASS regional offline context: Helsinki/Hanover bounds checked independently; no false coverage between distant regions.');

const repeatedFixes={trips:[trip('fixes',[pt(43.7,-72.29,{timestamp:'2013-03-30T10:00:00Z',accuracy:5}),pt(43.7,-72.29,{timestamp:'2013-03-30T10:05:00Z',accuracy:7})])]};
assert.equal(M.summarize(repeatedFixes).segments[0].points.length,2,'stationary fixes retain distinct observation times');
s=M.update(container,{participant:{id:'fixes'},record:repeatedFixes,baselineRecords:[]});assert.equal(s.groups.fixes.layers.size,2);assert([...s.groups.fixes.layers].every(x=>x.popup.includes('Reported accuracy:')));assert([...s.groups.fixes.layers].some(x=>x.popup.includes('10:05:00Z')));
s=M.update(container,{participant:{id:'real-empty'},record:{},baselineRecords:[]});assert.equal(s.groups.fixes.layers.size,0);
console.log('PASS recorded GPS inspection: timestamps/accuracy retained, stationary fixes distinct, old point overlays cleared.');

s=M.update(container,{participant:{id:'fix-labels'},record:repeatedFixes,baselineRecords:[]});assert.equal(s.fitButton.textContent,'Fit selected day');assert(s.legend.textContent.includes('recorded GPS'));assert(container.children[2].textContent.includes('not the exact travel path'));
console.log('PASS map terminology: genuine GPS dots/sample links are not labelled verified walks or two-route comparisons.');

container.clientWidth=800;s=M.update(container,{participant:{id:'responsive'},record:repeatedFixes,baselineRecords:[]});const fitsBefore=s.map.fits;container.clientWidth=345;s=M.update(container,{participant:{id:'responsive'},record:repeatedFixes,baselineRecords:[]});assert.equal(s.map.fits,fitsBefore+1,'fit the day after a responsive width change');M.update(container,{participant:{id:'responsive'},record:repeatedFixes,baselineRecords:[]});assert.equal(s.map.fits,fitsBefore+1,'ordinary day updates keep the viewport stable');
console.log('PASS responsive map: resized viewport fits the selected day; ordinary updates preserve manual view.');
