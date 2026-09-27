'use strict';
const $=s=>document.querySelector(s);
const incoming=new URLSearchParams(location.hash.slice(1)).get('access');
if(incoming){sessionStorage.setItem('farmy-workbench-access',incoming);history.replaceState(null,'',location.pathname);}
const token=sessionStorage.getItem('farmy-workbench-access');
let state=null,preview=null,busy=false,activeView='copilot';
function message(text,error=false){$('#message').textContent=text;$('#message').classList.toggle('error',error);}
const displayName=entry=>(state?.catalogue?.find(item=>item.entry===entry)?.path||entry).replace(/-[a-f0-9]{64}(?=\.[^.]+$)/,'');
const errors={unsupported:'Choose a UTF-8 .txt, .md, .csv or .eml file of at most 16 KiB, without binary control characters. The source also has a 100-file limit.',denied:'Wallet denied this action. Permission is missing, revoked or outside this item’s permitted readers.',unauthenticated:'This private link is missing or expired. Run “farmy open” for the owner workspace; open the consumer from the owner’s current consumer link.',conflict:'The source or permission changed, or another action needs retrying. Refresh before continuing.',unavailable:'A service is unavailable. No new access has been allowed. Retry when it returns.',expired:'This permission or request expired. Restart the demo for fresh development grants.',invalid_request:'This request could not be accepted.',not_found:'This item is not available in this session.'};
async function api(path,body){const response=await fetch(path,{method:body?'POST':'GET',headers:{Authorization:'Bearer '+(token||''),...(body?{'Content-Type':'application/json'}:{})},body:body?JSON.stringify(body):undefined,cache:'no-store'});const result=await response.json();if(!response.ok){const error=new Error(errors[result.error]||'The request failed.');error.code=result.error;throw error;}return result;}
function node(tag,text,cls){const n=document.createElement(tag);if(text)n.textContent=text;if(cls)n.className=cls;return n;}
function button(text,action,disabled=false){const b=node('button',text);b.disabled=disabled;b.addEventListener('click',action);return b;}
function clearResult(){$('#result').hidden=true;$('#content').textContent='';$('#content').hidden=true;}
function render(){const owner=state.role==='owner';if(state.persistent){$('#lifecycle-note').textContent='This local workspace retains managed copies and permissions when stopped. It uses separate owner and test-consumer identities; your selected source stays read-only.';$('#grant-lifetime').textContent='Consumer grants last up to one hour. Owner source access is maintained by this local installation.';$('#project-guide').hidden=true;}$('#role').textContent=owner?'Owner view':'Demo consumer view';$('#heading').textContent=owner?'Your Wallet, in your hands.':'See what the consumer can read.';$('#intro').textContent=owner?'Choose one document, keep a governed copy, then test its access.':'Every attempt asks the real Wallet for a current decision.';$('#owner-view').hidden=!owner;$('#consumer-view').hidden=owner;$('#consumer-link').hidden=!owner;
if(owner){$('#upload-section').hidden=!state.uploads;$('#upload-button').disabled=!$('#upload-file').files.length||!!state.pending;if(state.uploads){$('#iteration-label').textContent='UPLOAD AND CONTROL A DOCUMENT · UC-011';$('#data-scope').textContent='Sample documents and your selected local uploads use the real Wallet and Connector.';}$('#consumer-link').href=(state.consumerOrigin||'')+'/#access='+encodeURIComponent(state.consumerToken);$('#recovery').hidden=!state.pending;$('#source-search').hidden=!state.directory;const filter=state.directory?$('#source-filter').value.toLowerCase():'';const visibleEntries=state.entries.filter(entry=>displayName(entry).toLowerCase().includes(filter));$('#source-count').textContent=`${visibleEntries.length} of ${state.entries.length} files`;if(state.directory){$('#iteration-label').textContent=state.persistent?'PERSISTENT LOCAL WORKSPACE · '+state.runtimeVersion:'CONNECTED DIRECTORY · UC-012';$('#data-scope').textContent='The selected directory is read-only. Only selected files become managed copies.';}$('#sources').replaceChildren();for(const entry of visibleEntries){const info=state.catalogue?.find(item=>item.entry===entry);const card=node('article',null,'card');card.append(node('h3',displayName(entry)),node('p',info?`${info.size.toLocaleString()} bytes · ${info.reason||'Text preview available; encoding checked on read'}`:'Source file · not automatically in your Wallet'),button('Preview '+displayName(entry),()=>showPreview(entry),!!info?.reason));$('#sources').append(card);}
$('#items').replaceChildren();if(!state.items.length)$('#items').append(node('p','No managed copies yet. Preview a source document, then retain it here.'));
for(const item of state.items){const card=node('article',null,'card'),details=node('details'),dl=node('dl');card.append(node('h3',displayName(item.title)),node('span',item.sharing==='Not granted'?'No consumer access':item.sharing,'status'),node('p',item.classification==='private'?'Private · owner only':'Eligible readers: owner and demo consumer'));for(const [label,value] of [['Source',item.entry],['Source identity',item.sourceId],['Resource',item.resource.resourceId],['Version',item.resource.versionId],['SHA-256',item.resource.sha256],['Admitted',item.importedAt],['Mode','Immutable managed copy']])dl.append(node('dt',label),node('dd',value));details.append(node('summary','Inspect provenance and exact version'),dl);card.append(details,button('Open managed copy',()=>read(item.id)));
const granted=item.sharing.startsWith('Granted');card.append(button('Grant consumer access',()=>mutate('grant',{id:item.id}),item.classification==='private'||granted||!!state.pending),button('Revoke access',()=>mutate('revoke',{id:item.id}),!granted||!!state.pending));if(state.persistent){card.append(button(item.classification==='private'?'Allow paired consumer':'Make private',()=>mutate('policy',{id:item.id,policy:item.classification==='private'?'restricted':'private'}),!!state.pending),node('p','Recipient: '+(state.identities?.reader.name||'demo consumer')+' · key '+(state.identities?.reader.fingerprint.slice(0,16)||'development identity')),node('p',item.classification==='private'?'Only the owner can read this copy. Allow the paired consumer before granting access.':'Policy edits revoke existing consumer grants. Granting access is a separate action.'));}$('#items').append(card);}
}else{$('#consumer-items').replaceChildren();if(!state.items.length)$('#consumer-items').append(node('p',state.independentConsumer?'No grant receipts yet. Ask the owner to grant access, then refresh.':'No demo entries yet. Add a document in the owner view, then refresh here.'));for(const item of state.items){const card=node('article',null,'card');card.append(node('h3',displayName(item.title)),node('p','Generic test entry; no document metadata is disclosed before the read succeeds.'),button('Try to open '+item.title,()=>read(item.id)));$('#consumer-items').append(card);}}
renderWorkspace();
}
async function refresh(){clearResult();$('#workspace-answer').hidden=true;try{state=await api('/api/state');render();}catch(error){message(error.message,true);state=null;preview=null;$('#workspace-nav').hidden=true;for(const view of ['owner','copilot','connect','wallet'])$('#'+view+'-view').hidden=true;$('#preview').hidden=true;$('#sources').replaceChildren();$('#items').replaceChildren();$('#consumer-items').replaceChildren();throw error;}}
async function task(action){if(busy)return;busy=true;document.querySelectorAll('button').forEach(b=>b.disabled=true);try{await action();}catch(error){message(error.message,true);}finally{busy=false;if(state)render();$('#refresh').disabled=false;$('#admit').disabled=!preview||!!state?.pending;$('#cancel').disabled=false;$('#retry').disabled=false;}}
async function showPreview(entry){await task(async()=>{preview=await api('/api/action',{action:'preview',payload:{entry}});$('#preview-title').textContent=displayName(entry);$('#preview-body').textContent=preview.text;$('#preview').hidden=false;$('#policy').value=state.directory?'private':'restricted';message('Review the source bytes, then choose the copy’s permitted readers.');$('#preview').scrollIntoView({behavior:'smooth',block:'center'});});}
async function submit(action,payload){try{const receipt=await api('/api/action',{action,payload});await refresh();if(action==='admit'){$('#preview').hidden=true;preview=null;}if(action==='upload'){preview=await api('/api/action',{action:'preview',payload:{entry:receipt.entry}});$('#preview-title').textContent=displayName(receipt.entry);$('#preview-body').textContent=preview.text;$('#preview').hidden=false;$('#policy').value='private';$('#preview').scrollIntoView({behavior:'smooth',block:'center'});$('#upload-file').value='';$('#upload-selection').textContent='Upload complete.';}message(receipt.deliveryPending?'Grant recorded, but delivery to the consumer needs retrying. Press Refresh to retry delivery.':action==='policy'?'Policy updated. Previous consumer grants are revoked; no new access was granted.':action==='upload'?'Uploaded to the local source. Review it below, then retain a managed copy.':action==='admit'?'Managed copy retained. Consumer access is not granted yet.':action==='grant'?'Grant recorded. Try opening the document in the demo consumer view.':'Access revoked. A new consumer read will be denied.');return receipt;}catch(error){try{await refresh();}catch{}throw error;}}
async function mutate(action,payload){await task(()=>submit(action,{...payload,key:crypto.randomUUID()}));}
async function read(id){await task(async()=>{clearResult();$('#decision').textContent='Checking access…';$('#decision-detail').textContent='';$('#result').hidden=false;try{const result=await api('/api/action',{action:'read',payload:{id}});$('#decision').textContent='Access allowed';$('#decision-detail').textContent=(state.role==='owner'?'The owner':'The consumer')+' read these bytes through the Connector after Wallet authorisation.';$('#content').textContent=result.text;$('#content').hidden=false;$('#result').className='allowed';message('Live read succeeded.');}catch(error){$('#decision').textContent=error.code==='denied'?'Access denied':'Read unavailable';$('#decision-detail').textContent=error.message;$('#result').className='denied';message(error.message,true);}$('#result').scrollIntoView({behavior:'smooth',block:'center'});});}
$('#refresh').addEventListener('click',()=>task(async()=>{await refresh();message('Refreshed from the running services.');}));
$('#admit').addEventListener('click',()=>{if(preview)mutate('admit',{entry:preview.entry,sha256:preview.sha256,policy:$('#policy').value});});
$('#cancel').addEventListener('click',()=>{$('#preview').hidden=true;preview=null;});
$('#retry').addEventListener('click',()=>{if(state?.pending)task(()=>submit(state.pending.action,state.pending.payload));});
document.addEventListener('visibilitychange',()=>{if(document.hidden)clearResult();});
task(async()=>{await refresh();message(state.role==='owner'?state.persistent?'Use Copilot for workspace questions, or Library to browse your information.':'Start with a source preview on the left.':'Try a read before and after the owner grants access.');});

$('#upload-file').addEventListener('change',()=>{const file=$('#upload-file').files[0];$('#upload-selection').textContent=file?`${file.name} · ${file.size} bytes`:'No file selected.';$('#upload-button').disabled=!file||busy||!!state?.pending;});
$('#upload-button').addEventListener('click',()=>task(async()=>{const file=$('#upload-file').files[0];if(!file)return;if(file.size>16384||!(/\.(txt|md|csv|eml)$/i).test(file.name))throw new Error(errors.unsupported);const bytes=new Uint8Array(await file.arrayBuffer());try{new TextDecoder('utf-8',{fatal:true}).decode(bytes);}catch{throw new Error('This file is not UTF-8 text. Save it as UTF-8 or choose another document.');}await submit('upload',{name:file.name,contentBase64:btoa(String.fromCharCode(...bytes)),key:crypto.randomUUID()});}));

$('#source-filter').addEventListener('input',()=>{if(state&&!busy)render();});
// Reopening an owner link in an existing tab may only change the URL fragment.
window.addEventListener('hashchange',()=>{if(new URLSearchParams(location.hash.slice(1)).has('access'))location.reload();});

const viewCopy={library:['Your information, under your control.','Browse a source, keep an exact copy, and decide who may read it.'],copilot:['Questions with a visible basis.','Start with workspace records. Document reasoning is the next integration.'],connect:['See what is connected.','A local composition with explicit responsibilities.'],wallet:['Your workspace. Your authority.','Inspect the current access rules and deployment boundaries.']};
function renderWorkspace(){
 if(state?.independentConsumer&&state.role==='consumer'){
  $('#iteration-label').textContent='PAIRED LOCAL CONSUMER · '+state.runtimeVersion;$('#role').textContent='Paired consumer';
  $('#lifecycle-note').textContent='This consumer keeps its own grant receipts. It runs locally with a separate key; the Wallet checks every read.';
  $('#grant-lifetime').textContent='Consumer grants last up to one hour. Old receipts do not establish current access.';
  $('#heading').textContent='Paired demo consumer';$('#intro').textContent='This separate local application proves its identity with its own key for every service connection.';
  $('#consumer-explanation').textContent='This consumer stores its own grant receipts. Only a live Wallet permission check can release document bytes. It cannot browse the source.';
  $('#consumer-identity').hidden=false;$('#consumer-identity').textContent='Public-key fingerprint (SHA-256): '+state.identity.fingerprint;
 }
 const enabled=state?.persistent&&state.role==='owner';$('#workspace-nav').hidden=!enabled;
 for(const view of ['copilot','wallet','connect'])$('#'+view+'-view').hidden=!enabled||activeView!==view;
 if(!enabled)return;
 if(state.consumerDeliveryPending)message('A grant receipt could not reach the paired consumer. Refresh retries delivery; no additional grant is created.',true);
 $('#owner-view').hidden=activeView!=='library';
 $('#heading').textContent=viewCopy[activeView][0];$('#intro').textContent=viewCopy[activeView][1];
 document.querySelectorAll('[data-view]').forEach(b=>{b.disabled=false;if(b.dataset.view===activeView)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');});
 document.querySelectorAll('[data-question]').forEach(b=>b.disabled=false);
 const components=$('#hub-components');components.replaceChildren();
 for(const [title,description] of [['Read-only directory','Lists the selected read-only folder and holds admitted immutable copies.'],['Paired consumer','Separate local process, browser origin, private key and grant-receipt store. Reads authenticate over mutual TLS.'],['Model providers','None connected to this persistent composition. Provider selection and AI-assisted connection setup are planned.']]){
  const card=node('article',null,'card');card.append(node('h3',title),node('p',description));components.append(card);
 }
 const controls=$('#workspace-controls');controls.replaceChildren();const dl=node('dl');
 for(const identity of Object.values(state.identities||{}))dl.append(node('dt',identity.name),node('dd','P-256 · SHA-256 public-key fingerprint: '+identity.fingerprint));
 for(const [label,value] of [['Runtime',state.runtimeVersion],['Wallet rules','Private copies permit only the owner. Other copies may permit the owner and demo consumer; consumer access still needs a separate grant.'],['Consumer lifetime','Up to one hour. Revocation blocks future reads, not bytes already received.'],['Model destination','None connected in this composition.'],['Cloud dependency','None required by this composition.'],['Authentication','Locally paired persistent P-256 keys; separate consumer process and browser origin. Browser links remain bearer credentials. Both applications run under the same Mac user; pairing does not verify a legal identity.']])dl.append(node('dt',label),node('dd',value));
 controls.append(dl);
 const grants=$('#wallet-items');grants.replaceChildren();
 if(!state.items.length)grants.append(node('p','No managed copies yet. Open Library to retain a source document.'));
 for(const item of state.items){
  const card=node('article',null,'card'),granted=item.sharing.startsWith('Granted');
  card.append(node('h3',displayName(item.title)),node('p',item.classification==='private'?'Private · owner only':'Eligible recipient: '+(state.identities?.reader.name||'demo consumer')),node('span',item.sharing==='Not granted'?'No consumer access':item.sharing,'status'),
   button(item.classification==='private'?'Allow paired consumer':'Make private',()=>mutate('policy',{id:item.id,policy:item.classification==='private'?'restricted':'private'}),!!state.pending),
   button('Grant consumer access',()=>mutate('grant',{id:item.id}),item.classification==='private'||granted||!!state.pending),
   button('Revoke access',()=>mutate('revoke',{id:item.id}),!granted||!!state.pending));grants.append(card);
 }

}
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{if(busy)return;activeView=b.dataset.view;clearResult();$('#preview').hidden=true;preview=null;message('');render();}));
document.querySelectorAll('[data-question]').forEach(b=>b.addEventListener('click',()=>task(async()=>{
 await refresh();if(state.role!=='owner'||!state.persistent)return;
 const answer=$('#workspace-answer');answer.replaceChildren();answer.hidden=false;
 answer.append(node('h3',b.textContent),node('p','Checked '+new Date().toLocaleString()+'. Local record summary; no model used.','help'));
 if(b.dataset.question==='inventory'){
  const previewable=state.catalogue.filter(item=>!item.reason).length;
  answer.append(node('p',`${state.entries.length} source files are listed. ${previewable} are eligible for a bounded text preview; encoding is checked when opened. Your Library contains ${state.items.length} managed copies.`));
  answer.append(node('p','Basis: the current directory listing and the Wallet’s current item records. A source file and its managed copy are separate objects.'));
 }else{
  const shared=state.items.filter(item=>item.sharing.startsWith('Granted'));
  answer.append(node('p',`${shared.length} managed copies have an unrevoked grant recorded by this client. Grants may have expired. A read still checks the Wallet and Connector; this summary is not an access decision.`));
  if(!shared.length)answer.append(node('p','No unrevoked consumer grants are recorded.'));
  for(const item of shared){const card=node('article',null,'card');card.append(node('h3',displayName(item.title)),node('p',item.sharing),node('p','Exact version: '+item.resource.versionId),node('p','SHA-256: '+item.resource.sha256));answer.append(card);}
  answer.append(node('p','Basis: the client’s grant receipts and current Wallet item records. Use Wallet or Library and the separate consumer view to test a live read.'));
 }
 message('Answered from refreshed workspace records.');
})));
