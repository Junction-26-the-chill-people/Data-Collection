
// Usage: node analyze.cjs input.json output.json [participant-id]
const fs=require('node:fs');
const E=require('./engine.js');
const [input,output,participantId]=process.argv.slice(2);
if(!input||!output){console.error('Usage: node analyze.cjs input.json output.json [participant-id]');process.exit(2);}
try{
 const data=JSON.parse(fs.readFileSync(input,'utf8').replace(/^\uFEFF/,''));
 const participant=data.participants?(participantId?data.participants.find(p=>String(p.id)===participantId):data.participants[0]):data;
 if(!participant)throw new Error('Participant not found');
 const options=Object.assign({windowSize:participant.defaultWindowSize??data.defaultWindowSize??2,granularity:participant.granularity||data.granularity||'observation'},data.options,participant.options,{metrics:participant.metrics||data.metrics,baselineIndices:participant.baselineIndices||data.baselineIndices||[],baselineLabel:participant.baselineLabel||data.baselineLabel||'Explicitly selected reference; wellness not established'});
 const result=E.analyze(participant.records,options);
 const latest=result.latest;
 const metricDefinitions=options.metrics.map(metric=>Object.assign({},metric,{weight:metric.weight===undefined?1:metric.weight}));
 const envelope={metricDefinitions,schema_version:'1.2.0',model_version:E.MODEL_VERSION,participant_id:participant.id??null,synthetic:participant.synthetic===true,source:participant.source||null,baseline_status:participant.baselineStatus||'unspecified',period_granularity:participant.granularity||data.granularity||'unspecified',analysis:result,integration:{module:'wearables',signal:latest?({no_change:'no_change',change_detected:'change_detected',review_suggested:'review_suggested'}[latest.status]||'insufficient_data'):'insufficient_data',data_coverage:latest?latest.coverage:0,confidence:null,evidence:{synthetic:participant.synthetic===true,source:participant.source||null,behavior_change_index:latest?latest.score:null,relapse_vector:latest?latest.relapseVector:null,anchored_score:latest?latest.anchoredScore:null,raw_score:latest?latest.rawScore:null,context_multiplier:latest?latest.contextMultiplier:1,contexts:latest?latest.contexts:[],adaptation:latest?latest.adaptation:null,alert_state:latest?.alertState??null,persistence:latest?.persistence??null,drift:latest?.drift??null,alerting:result.alerting,score_is_clinical_probability:false,baseline_label:result.baseline.label,baseline_indices:result.baseline.indices},required_before_database_insert:['verified user_id mapping','registered model_version_id UUID','valid measurement window timestamps','active analysis consent'],database_write_performed:false}};
 fs.writeFileSync(output,JSON.stringify(envelope,null,2));console.log('Wrote '+output);
}catch(e){console.error(e.message);process.exit(1);}
