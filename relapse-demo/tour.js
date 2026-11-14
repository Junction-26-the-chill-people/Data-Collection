/* Guided presentation tour. Presentation only: drives the same public selection API the user controls. */
(function(){
'use strict';
const $=id=>document.getElementById(id);
const S=window.STUDENTLIFE_DATA;
const steps=[
 {kicker:'1 · The idea',title:'Learn someone’s usual — then notice change',body:'Meet Noah (a demo person). He picked four weeks when he felt reasonably well. That period, the soft lilac band on the timeline, becomes his personal reference. Nothing is compared with other people.',go:{dataset:'synthetic',participantId:'sim-02',index:14,window:1,view:'personal'},focus:'trajectory'},
 {kicker:'2 · Early signs',title:'Small shifts start to show',body:'Five weeks later, walks are shorter and sleep is drifting. The engine sees an emerging pattern across several days. In the Personal view the message stays gentle: notice, don’t alarm.',go:{dataset:'synthetic',participantId:'sim-02',index:64,window:1,view:'personal'},focus:'overview'},
 {kicker:'3 · Sustained change',title:'Several routines have shifted together',body:'Less sleep, far fewer steps, lower mood check-ins and more time at home. Only noteworthy changes are summarised; everything else stays one click away. It suggests a check-in — it never diagnoses.',go:{dataset:'synthetic',participantId:'sim-02',index:100,window:1,view:'personal'},focus:'overview'},
 {kicker:'4 · Same person, same day',title:'Where the day actually went',body:'Blue trips are this day; the dashed route is a typical reference day. The 24-hour ribbon shows stays and walks. Gaps stay gaps: missing GPS is never drawn as a trip or read as “stayed home”.',go:{dataset:'synthetic',participantId:'sim-02',index:100,window:1,view:'personal'},focus:'route-panel'},
 {kicker:'5 · Clinical view',title:'Same assessment, more evidence',body:'Clinicians get persistence (high daily signals in the last seven calendar days), slow drift against the frozen anchor, how many signals moved, the anchored index, data availability and per-measurement evidence — without changing the underlying result.',go:{dataset:'synthetic',participantId:'sim-02',index:100,window:1,view:'clinical'},focus:'overview'},
 {kicker:'6 · Slow drift',title:'Small changes can add up over weeks',body:'Mila has no dramatic day. Movement, sleep and mood gradually fade. The slow-drift path checks recent medians and robust trends against her original anchor across different domains, even while the effective baseline learns slowly.',go:{dataset:'synthetic',participantId:'sim-11',index:99,window:1,view:'clinical'},focus:'overview'},
 {kicker:'7 · One hard day',title:'A difficult day is seen — not over-read',body:'Sofia has one rough day after weeks of steady routine. Her day signal shows it clearly, but it is noted, not flagged. One unusual day does not establish a pattern.',go:{dataset:'synthetic',participantId:'sim-09',index:64,window:1,view:'clinical'},focus:'trajectory'},
 {kicker:'8 · Recovery',title:'The next day, she’s back to her rhythm',body:'One day later every signal is back within her usual range. A single bad day doesn’t become a trend, and nothing sticks once the routine returns.',go:{dataset:'synthetic',participantId:'sim-09',index:65,window:1,view:'personal'},focus:'overview'},
 {kicker:'9 · Built to combine',title:'The bigger picture, one contract',body:'Our teammates’ screen-time, social-feed and companion-app detectors plug in through one versioned contract. Payloads for the wrong person or day are rejected. Demo values here are clearly labelled synthetic.',go:{dataset:'synthetic',participantId:'sim-02',index:100,window:1,view:'clinical'},focus:'companion-panel'},
 {kicker:'10 · Real data',title:'Recorded GPS and check-ins, linked correctly',body:'StudentLife: 49 real students, 2,116 days with same-person GPS and check-ins. Click any GPS dot for its time and accuracy. Raw questionnaire codes stay unscored rather than being turned into invented mood scores.',go:S&&S.participants&&S.participants.length?{dataset:'studentlife',participantId:S.defaultParticipantId,view:'personal'}:null,focus:'route-panel'},
 {kicker:'Thanks',title:'Within — notice change early, gently',body:'Personal for the person, Clinical for the care team, portable engine for the app. An experimental behaviour-change index, not a diagnosis. Close the tour to explore freely.',go:{dataset:'synthetic',participantId:'sim-02',index:100,window:1,view:'personal'},focus:'overview'}
];
let i=0,focused=null;
function show(k){
 i=Math.max(0,Math.min(steps.length-1,k));const s=steps[i];
 if(s.go&&window.WithinApp)window.WithinApp.go(Object.assign({reset:true},s.go));
 $('tour-kicker').textContent=s.kicker;$('tour-title').textContent=s.title;$('tour-body').textContent=s.body;
 $('tour-progress').innerHTML=steps.map((_,n)=>`<i class="${n<=i?'on':''}"></i>`).join('');
 $('tour-back').disabled=i===0;$('tour-next').textContent=i===steps.length-1?'Finish':'Next';
 if(focused)focused.classList.remove('tour-focus');focused=$(s.focus);
 if(focused){focused.classList.add('tour-focus');const top=focused.getBoundingClientRect().top+window.scrollY-130;window.scrollTo({top:Math.max(0,top),behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});}
}
function open(){$('tour').hidden=false;show(0);$('tour-next').focus({preventScroll:true});}
function close(){$('tour').hidden=true;if(focused)focused.classList.remove('tour-focus');focused=null;$('tour-start').focus({preventScroll:true});}
if(!$('tour')||!$('tour-start'))return;
$('tour-start').addEventListener('click',()=>$('tour').hidden?open():close());
$('tour-next').addEventListener('click',()=>i===steps.length-1?close():show(i+1));
$('tour-back').addEventListener('click',()=>show(i-1));
$('tour-close').addEventListener('click',close);
document.addEventListener('keydown',e=>{if($('tour').hidden)return;if(e.key==='Escape')close();});
if(/[?&]tour=1\b/.test(location.search))setTimeout(open,300);
})();
