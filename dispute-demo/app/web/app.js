'use strict';
const $ = id => document.getElementById(id);
const names = {provisional_credit:'Provisional credit',request_evidence:'Request evidence',decline:'Decline',human_review:'Human review'};
let config, selected=localStorage.getItem('dispute-ui-selected'), busy=false, generation=0, polling;
const make = (tag, text, cls) => {const x=document.createElement(tag); if(text!==undefined)x.textContent=String(text); if(cls)x.className=cls; return x;};
const clear = id => {$(id).replaceChildren(); $(id).classList.remove('empty'); return $(id);};
const human = value => String(value ?? 'Unavailable').replaceAll('_',' ');
const money = (amount,currency) => amount===null || amount===undefined ? 'No credit effect' : `${currency} ${(BigInt(amount)/100n).toString()}.${(BigInt(amount)%100n).toString().padStart(2,'0')}`;
const notice = (text,error=false) => {$('notice').textContent=text; $('notice').hidden=!text; $('notice').className=error?'error':'';};
const button = (label,fn) => {const x=make('button',label,'secondary small');x.addEventListener('click',fn);x.disabled=busy;return x;};
async function api(path,body){const r=await fetch(path,{cache:'no-store',headers:body?{'Content-Type':'application/json','X-Analyst-Token':config.token}:{},method:body?'POST':'GET',body:body?JSON.stringify(body):undefined});const data=await r.json();if(!r.ok)throw new Error(human(data.error));return data;}
function setBusy(value){busy=value;$('running').hidden=!value;$('investigate').disabled=value||!selected;document.querySelectorAll('#recoveries button').forEach(b=>b.disabled=value);}
function table(parent,caption,heads,rows){const wrap=make('div',undefined,'table-wrap'),t=make('table');if(caption)t.append(make('caption',caption));const thead=make('thead'),tr=make('tr');heads.forEach(h=>tr.append(make('th',h)));thead.append(tr);t.append(thead);const body=make('tbody');rows.forEach(row=>{const tr=make('tr');row.forEach(v=>{const td=make('td');if(v instanceof Node)td.append(v);else td.textContent=String(v??'—');tr.append(td);});body.append(tr);});t.append(body);wrap.append(t);parent.append(wrap);}
function field(parent,label,value){const f=make('div');f.append(make('span',label,'field-label'),make('span',value,'field-value'));parent.append(f);}
function renderContext(c,label='Current source snapshot'){
  const d=c.dispute,ref=c.reference;const summary=clear('case-summary');summary.append(make('h2',d.dispute_id),make('span',human(d.reason_code),'badge'),make('p',`Claim ${money(d.claimed_amount_minor,d.currency)} · Source status: ${d.dispute_status}`));
  $('source-stamp').textContent=`${label} · revision ${ref.source_revision}`;
  const facts=clear('facts'),grid=make('div',undefined,'facts-grid');field(grid,'Primary transaction',d.transaction_id);field(grid,'Opened',d.opened_at);field(grid,'Snapshot cutoff',ref.evaluation_at);field(grid,'Source / policy',`${c.source_channel} / ${ref.policy_version}`);facts.append(grid,make('div',d.customer_statement,'statement'));
  table(facts,'Transactions',['ID / customer','Amount','Status'],c.transactions.map(t=>[`${t.transaction_id} / ${t.customer_id}`,money(t.amount_minor,t.currency),t.transaction_status]));
  table(facts,'Merchant settlement movements',['Source ID','Movement','Amount','Status'],c.settlements.map(s=>[s.settlement_id,human(s.movement_type),money(s.amount_minor,s.currency),s.settlement_status]));
  if(c.data_issues.length)facts.append(make('p',`Source issues: ${c.data_issues.map(human).join('; ')}`,'muted'));
  facts.append(make('p',`Snapshot ${ref.snapshot_id}. Merchant refunds/reversals are distinct from a new simulated credit.`,'muted'));
  const evidence=clear('evidence');if(!c.evidence.length)evidence.append(make('p','No visible evidence at this cutoff.','empty'));
  c.evidence.forEach(e=>{const detail=make('details',undefined,'evidence-item');detail.id='evidence-'+e.evidence_id;detail.append(make('summary',`${e.evidence_id} · ${human(e.evidence_type)} · ${human(e.integrity_status)}`),make('p',`${e.source_type} · Available ${e.available_at}`,'muted'),make('pre',e.content??'Evidence text unavailable'));evidence.append(detail);});
}
function resetResult(){
  $('reviewer-verdict').textContent='Not reviewed';clear('collaboration').append(make('p','No role calls in this view.','empty'));
  $('outcome').textContent='Not investigated';$('amount').textContent='No new effect reported';$('verdict').textContent='Not evaluated';$('feedback').textContent='A proposal requires independent validation.';$('persistence').textContent='Not attempted';$('persist-detail').textContent='Queue membership is read from saved records.';$('policy-version').textContent='Not evaluated';clear('policy').append(make('p','Investigate to see the applied rules and investigator proposal.','empty'));clear('memory').append(make('p',config?.memory_mode==='no_memory'?'No-memory mode. Recall and summary storage are disabled.':'Not recalled for this view.','muted'));
}
function renderPolicy(p,proposal){
  const box=clear('policy');if(!p){box.append(make('p','No evaluated policy returned.','empty'));return;}
  $('policy-version').textContent=`Policy ${p.reference.policy_version}`;
  box.append(make('p',`Allowed: ${p.allowed_outcomes.map(v=>names[v]).join(', ')}. Other business outcomes are blocked.`,'muted'));
  p.rule_checks.forEach(r=>{const row=make('div',undefined,'rule'),head=make('div',undefined,'rule-head');head.append(make('strong',r.policy_rule_id),make('span',human(r.status),'pill '+r.status));row.append(head,make('p',r.explanation));r.evidence_ids.forEach(id=>{const a=make('a',id+' ');a.href='#evidence-'+id;row.append(a);});box.append(row);});
  const missing=proposal?.missing_evidence??p.missing_evidence;if(missing.length){const panel=make('div',undefined,'recommendation');panel.append(make('strong','Requested evidence'));missing.forEach(m=>panel.append(make('p',`${human(m.category)} — ${human(m.reason)} (${m.policy_rule_id})`)));box.append(panel);}
  if(p.data_issues.length)box.append(make('p','Policy issues: '+p.data_issues.map(human).join('; '),'muted'));
  if(proposal){const panel=make('div',undefined,'recommendation');panel.append(make('strong','Investigator recommendation: '+names[proposal.recommendation.outcome]),make('p',proposal.rationale),make('p','Rules: '+proposal.policy_rule_ids.join(', '),'muted'),make('p','Evidence: '+(proposal.evidence_ids.join(', ')||'None'),'muted'),make('p',`Proposal ${proposal.proposal_id} · correction ${proposal.revision}`,'muted'));box.append(panel);}
}
function renderMemory(result){
  const box=clear('memory');if(result.memory_mode==='no_memory'){box.append(make('p','No-memory mode. Recall and summary storage are disabled.','muted'));return;}
  const events=result.events??[], recall=events.filter(x=>x.kind==='memory_recall').at(-1), verified=events.filter(x=>x.kind==='memory_verified').at(-1), saved=events.filter(x=>x.kind==='memory_save').at(-1);
  box.append(make('p',recall?`Recall ${recall.status}.`:'Recall not performed for this operation.','muted'));
  if(verified){box.append(make('p',`${verified.distinct_cases} distinct prior case(s) verified. Partial recall; not a complete customer history.`,'muted'));verified.history.records.forEach(r=>{const item=make('div',undefined,'record');item.append(make('strong',r.original_reference.dispute_id+' · '+names[r.recommendation.outcome]),make('p',`Committed ${r.committed_at}`,'muted'),make('code',r.source_reference),make('p',`Verified at revision ${r.verified_reference.source_revision}; original policy ${r.original_reference.policy_version}.`,'muted'));box.append(item);});}
  const ignored=events.filter(x=>x.kind==='memory_ignored');if(ignored.length)box.append(make('p',`Ignored candidates: ${ignored.map(e=>human(e.code)).join('; ')}.`,'muted'));
  box.append(make('p',saved?`Summary storage: ${saved.status}. Decision persistence is unchanged.`:'No summary save reported.','muted'));
}
function renderCollaboration(result){
  const box=clear('collaboration'), events=result.events??[];
  const labels={investigator:'Investigator',critic:'Deterministic critic',reviewer:'Independent Reviewer',correction:'Correction handoff',final_gate:'Final acceptance gate',commit:'Restricted writer'};
  const rows=events.filter(e=>labels[e.kind]).map(e=>{
    const r=e.result??{}, proposal=r.proposal, feedback=r.feedback;
    let status=e.kind==='correction'?`Requested by ${human(e.source)}`:e.kind==='final_gate'?`Critic ${e.critic}; Reviewer ${e.reviewer}`:r.verdict??feedback?.verdict??r.status??e.status??'Recorded';
    const detail=e.kind==='reviewer'?feedback?.feedback??r.error??e.error??'No valid feedback':e.kind==='critic'?r.feedback:e.kind==='investigator'?proposal?names[proposal.recommendation.outcome]:r.message:e.kind==='correction'?'One shared correction token consumed':e.kind==='final_gate'?'Both accept this exact proposal before dispatch':r.message;
    const id=proposal?.proposal_id??r.proposal_id??e.proposal_id??'—';
    const info=make('div');info.append(make('strong',human(status)),make('p',detail??'','muted'));
    if(e.kind==='reviewer'&&feedback){info.append(make('p',`Issues: ${feedback.issue_codes.join(', ')||'None'} · Evidence: ${feedback.evidence_ids.join(', ')||'None'} · Rules: ${feedback.policy_rule_ids.join(', ')||'None'}`,'muted'));}
    if(r.requested_route)info.append(make('p',`Route: ${r.requested_route} · Returned model: ${r.response_model??'Unavailable'}`,'muted'));
    return [labels[e.kind],info,id];
  });
  if(rows.length)table(box,null,['Stage','Result / feedback','Proposal identity'],rows);
  else box.append(make('p','No model review in this operation. Exact saved-request recovery does not call either agent.','muted'));
  const reviewer=events.filter(e=>e.kind==='reviewer').at(-1)?.result;
  $('reviewer-verdict').textContent=reviewer?`Reviewer: ${human(reviewer.feedback?.verdict??reviewer.status)}`:'Not reviewed';
}
function renderJob(job){
  if(job.input.dispute_id!==selected)return;
  setBusy(job.status==='running');
  if(job.status==='running')return;
  if(job.error){notice(human(job.error)+(job.run_id?'. Use exact saved-request recovery below.':'. No action request is associated with this operation.'),true);$('persistence').textContent=job.run_id?'Unconfirmed':'Not dispatched';$('persist-detail').textContent=job.run_id?'A saved request exists. Recover it to establish persistence.':'No action was dispatched by this operation.';}
  const r=job.result;if(!r)return;
  if(r.mode==='memory_retry'){notice(`Memory ${r.memory_save.status}. Source receipt verified; no action called.`);return;}
  const last=kind=>(r.events??[]).filter(e=>e.kind===kind).at(-1), display=r.display??{};
  if(display.context)renderContext(display.context,'Investigation snapshot');
  const proposal=last('investigator')?.result.proposal??display.proposal,policy=last('policy')?.result??display.policy,critic=last('critic')?.result??display.critic,commit=r.state.commit_result;
  renderPolicy(policy,proposal);renderMemory(r);renderCollaboration(r);
  $('outcome').textContent=commit?.recommendation?names[commit.recommendation.outcome]:proposal?names[proposal.recommendation.outcome]+' (proposed)':'No outcome committed';
  $('amount').textContent=commit?.recommendation?money(commit.recommendation.amount_minor,commit.recommendation.currency):'No confirmed new effect';
  $('verdict').textContent=critic?human(critic.verdict):'Not evaluated';$('feedback').textContent=critic?'At validation: '+critic.feedback+(critic.failed_checks.length?' Checks: '+critic.failed_checks.map(human).join('; '):''):'No critic result returned.';
  $('persistence').textContent=commit?(commit.message.includes('unconfirmed')?'Unconfirmed':human(commit.status)):'Not persisted';
  $('persist-detail').textContent=r.persisted?`${commit.status==='reused'?'Existing result reused':'Decision committed'} · ${commit.decision_id}${commit.simulated_credit_id?' · Credit '+commit.simulated_credit_id:''}`:human(commit?.message??r.state.error??'No action dispatched');
  if(proposal?.recommendation.outcome==='human_review'&&!r.persisted)$('persist-detail').textContent+=' · Review recommended; not persisted. Check any unconfirmed request before restarting.';
  const investigation=last('investigator')?.result;
  if(investigation&&!proposal)$('policy').append(make('p',investigation.message,'muted'));
  $('policy').append(make('p',`Run ${r.state.run_id} · ${r.state.model_calls} model call(s), ${r.state.tool_calls} source read(s).`,'muted'));
  if(r.mode!=='live')notice(`Execution mode: ${r.mode}. This is not a live integration result.`,true);
  $('investigate').textContent='Investigate again →';
}
function renderSaved(snapshot,recoveries){
  const box=clear('decisions');if(!snapshot.decisions.decisions.length)box.append(make('p','No committed decisions returned by this source snapshot.','empty'));
  snapshot.decisions.decisions.forEach(d=>{const item=make('div',undefined,'record');item.append(make('strong',names[d.recommendation.outcome]),make('p',money(d.recommendation.amount_minor,d.recommendation.currency)),make('p',d.committed_at,'muted'),make('code',d.decision_id));box.append(item);});
  const recovery=clear('recoveries');if(!recoveries.length)recovery.append(make('p','No local saved request for this case.','empty'));
  recoveries.forEach(r=>{const row=make('div',undefined,'record');row.append(make('p','Saved execution: '+human(r.status),'muted'),make('code',r.run_id),button('Recover / reuse result',()=>submit('recover',r.run_id)));if(r.memory_retry_available&&config.memory_mode!=='no_memory')row.append(button('Retry memory only',()=>submit('memory',r.run_id)));recovery.append(row);});
}
async function refreshInventory(){
  try{const data=await api('/api/inventory');const select=$('case-select'),old=selected;select.replaceChildren();data.cases.forEach(c=>{const option=make('option',`${c.dispute_id} · ${human(c.reason_code)}`);option.value=c.dispute_id;select.append(option);});select.disabled=!data.cases.length;if(old&&data.cases.some(c=>c.dispute_id===old))select.value=old;
    $('queue-count').textContent=data.queue.length;$('queue-stamp').textContent=`Source revision ${data.source_revision} · ${data.captured_at}`;const q=clear('queue');if(!data.queue.length)q.append(make('p','No pending persisted reviews at this source revision.','empty'));else table(q,null,['Case','Queue lifecycle','Persisted decision'],data.queue.map(r=>[button(r.dispute_id,()=>{select.value=r.dispute_id;selectCase();location.hash='workspace';}),r.status,r.decision_id]));return true;
  }catch(e){$('queue-count').textContent='?';$('queue-stamp').textContent='Unavailable';clear('queue').append(make('p','Review queue unavailable. An empty queue cannot be inferred.','empty'));notice(e.message,true);return false;}
}
async function selectCase(){
  const version=++generation;selected=$('case-select').value;if(!selected)return;
  localStorage.setItem('dispute-ui-selected',selected);
  clearTimeout(polling);notice('');resetResult();setBusy(false);$('investigate').disabled=true;$('investigate').textContent='Investigate →';
  clear('case-summary').append(make('h2',selected));['facts','evidence','decisions','recoveries'].forEach(id=>clear(id).append(make('p','Loading this case…','empty')));$('source-stamp').textContent='Loading source';
  try{const data=await api('/api/case?id='+encodeURIComponent(selected));if(version!==generation)return;renderContext(data.snapshot.context);renderSaved(data.snapshot,data.recoveries);$('investigate').disabled=false;
    const last=localStorage.getItem('dispute-ui-last:'+selected);if(last){const job=await api('/api/job?id='+encodeURIComponent(last));if(version!==generation)return;renderJob(job);poll(job.operation_id,version);}
  }catch(e){if(version!==generation)return;notice(e.message,true);$('source-stamp').textContent='Source unavailable';}
}
async function poll(id,version){
  try{const job=await api('/api/job?id='+encodeURIComponent(id));if(version!==generation)return;renderJob(job);if(job.status==='running'){polling=setTimeout(()=>poll(id,version),1500);return;}
    await refreshInventory();if(version!==generation)return;const data=await api('/api/case?id='+encodeURIComponent(selected));if(version!==generation)return;renderSaved(data.snapshot,data.recoveries);
  }catch(e){if(version!==generation)return;notice('Result unavailable: '+e.message+'. Refresh the page to retrieve the same operation; do not start a replacement while its result is uncertain.',true);}
}
async function submit(kind,run_id=null){
  if(busy||!selected)return;if(kind==='investigate')resetResult();setBusy(true);notice('');const version=generation;
  const input={operation_id:crypto.randomUUID(),dispute_id:selected,kind,run_id};
  localStorage.setItem('dispute-ui-last:'+selected,input.operation_id);
  try{const job=await api('/api/job',input);localStorage.setItem('dispute-ui-last:'+input.dispute_id,job.operation_id);if(version!==generation)return;renderJob(job);poll(job.operation_id,version);}
  catch(e){if(version!==generation)return;notice('Operation response unavailable: '+e.message+'. Refresh to check the retained operation before starting again.',true);}
}
$('case-select').addEventListener('change',selectCase);$('investigate').addEventListener('click',()=>submit('investigate'));
$('refresh').addEventListener('click',async()=>{if(await refreshInventory())await selectCase();});
(async()=>{try{config=await api('/api/config');$('mode').textContent='LIVE INTEGRATIONS · SYNTHETIC ACTIONS';if(await refreshInventory())await selectCase();}catch(e){notice(e.message,true);}})();
