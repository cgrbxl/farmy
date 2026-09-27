'use strict';
let messagingRevision=null,messagingPending=null;
try{messagingPending=JSON.parse(sessionStorage.getItem('farmy-messaging-pending')||'null');}catch{}
function saveMessagingPending(value){messagingPending=value;if(value)sessionStorage.setItem('farmy-messaging-pending',JSON.stringify(value));else sessionStorage.removeItem('farmy-messaging-pending');}
function currentChannel(){return state?.messaging?.channels.find(c=>c.id===$('#message-channel').value);}
function loadMessagingChannel(){const c=currentChannel();if(!c)return;messagingRevision=c.revision;$('#message-senders').value=c.senders.join('\n');$('#message-recipients').value=c.recipients.join('\n');$('#message-filter-result').textContent='';}
function renderMessaging(){
 const m=state?.messaging;$('#messaging-panel').hidden=!m;if(!m)return;
 if(messagingRevision===null)loadMessagingChannel();
 const selected=$('#message-target').value;$('#message-target').replaceChildren();
 for(const recipient of currentChannel().recipients){const option=node('option',recipient);option.value=recipient;$('#message-target').append(option);}if(currentChannel().recipients.includes(selected))$('#message-target').value=selected;
 for(const id of ['message-save','message-check','message-create'])$('#'+id).disabled=false;
 $('#message-create').disabled=!currentChannel().recipients.length;
 const rules=$('#message-rules');rules.replaceChildren();if(!m.rules.length)rules.append(node('p','No recurring draft rules.'));
 for(const rule of m.rules){const card=node('article',null,'card');card.append(node('h3',rule.topic),node('p',`${rule.channel} → ${rule.recipient} · ${rule.paused?'Paused':'Active · drafts only'}`),node('p',`Every ${rule.period/3600} hours · next due ${new Date(rule.next_due*1000).toLocaleString()}`),button(rule.paused?'Resume drafts':'Pause drafts',()=>messagingChange('rule.pause',{id:rule.id,revision:rule.revision,paused:!rule.paused})));rules.append(card);}
 const drafts=$('#message-drafts');drafts.replaceChildren();if(!m.drafts.length)drafts.append(node('p','No drafts created yet.'));
 for(const draft of m.drafts){const card=node('article',null,'card');card.append(node('h3',draft.topic),node('p',`${draft.channel} → ${draft.recipient} · NOT SENT · due ${new Date(draft.due*1000).toLocaleString()}`),node('pre',draft.content));drafts.append(card);}
 const audit=$('#message-audit');audit.replaceChildren();for(const event of m.audit)audit.append(node('p',new Date(event.time*1000).toLocaleString()+' · '+event.action+' · '+event.reference));
 $('#message-retry').hidden=!messagingPending;$('#message-retry').disabled=false;
 if(messagingPending)message('A messaging change needs retrying. Repeat the same action to retry its saved request; refresh alone does not apply it.',true);
}
async function messagingChange(action,payload){await task(async()=>{
 const logical=JSON.stringify([action,payload]);
 if(messagingPending&&messagingPending.logical!==logical)throw new Error('Retry the previous messaging change before starting a different one.');
 const request=messagingPending?.request||{action:'messaging.'+action,payload:{...payload,key:crypto.randomUUID()}};
 saveMessagingPending({logical,request});
 try{await api('/api/action',request);saveMessagingPending(null);await refresh();loadMessagingChannel();message('Saved locally. No external messages were sent.');}
 catch(error){if(['invalid_request','conflict','denied','unauthenticated'].includes(error.code))saveMessagingPending(null);if(error.code==='conflict'){await refresh();loadMessagingChannel();}throw error;}
});}
function initMessaging(){
 $('#message-retry').addEventListener('click',()=>{if(!messagingPending)return;const request=messagingPending.request,{key,...payload}=request.payload;messagingChange(request.action.replace('messaging.',''),payload);});
 $('#message-channel').addEventListener('change',()=>{loadMessagingChannel();if(state)renderMessaging();});
 $('#message-save').addEventListener('click',()=>messagingChange('channel.save',{channel:$('#message-channel').value,revision:messagingRevision,senders:$('#message-senders').value.split('\n').map(s=>s.trim()).filter(Boolean),recipients:$('#message-recipients').value.split('\n').map(s=>s.trim()).filter(Boolean)}));
 $('#message-check').addEventListener('click',()=>task(async()=>{const result=await api('/api/action',{action:'messaging.sender.check',payload:{channel:$('#message-channel').value,sender:$('#message-test-sender').value}});$('#message-filter-result').textContent=result.allowed?'Allowed by the saved sender list. No message body was received.':'Blocked by the saved sender list. No message body was received.';}));
 $('#message-create').addEventListener('click',()=>{const firstDue=Math.floor(new Date($('#message-first').value).getTime()/1000);if(!Number.isFinite(firstDue)||firstDue<Date.now()/1000-60){message('Choose a current or future first draft time.',true);return;}messagingChange('rule.create',{channel:$('#message-channel').value,recipient:$('#message-target').value,topic:$('#message-topic').value,content:$('#message-content').value,period:Number($('#message-period').value),firstDue});});
 const local=new Date(Date.now()+120000);local.setSeconds(0,0);local.setMinutes(local.getMinutes()-local.getTimezoneOffset());$('#message-first').value=local.toISOString().slice(0,16);
}
