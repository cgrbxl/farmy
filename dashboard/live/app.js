'use strict';
const $ = s => document.querySelector(s);
const svgNS = 'http://www.w3.org/2000/svg';
let token = sessionStorage.getItem('farmyMonitorToken') || '';
const incoming = new URLSearchParams(location.hash.slice(1)).get('access');
if (incoming) { token = incoming; sessionStorage.setItem('farmyMonitorToken',token); history.replaceState(null,'',location.pathname); }
let state = null, selected = 'wallet.local', busy = false, timer, lastSuccess = 0;
const positions = {'wallet.local':[350,20], 'workflow.local':[690,20], 'connector.local':[35,160],
  'processing.local':[350,160], 'knowledge.local':[665,160], 'sensor.local':[35,310],
  'model.local':[350,310], 'assistance.local':[665,310]};
function el(tag,text,cls){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;}
function shape(tag,attrs,text){const e=document.createElementNS(svgNS,tag);for(const[k,v]of Object.entries(attrs))e.setAttribute(k,v);if(text)e.textContent=text;return e;}
function choose(id,scroll=false){selected=id;render();if(scroll)$('#detail').scrollIntoView({behavior:'smooth',block:'nearest'});}
function render(){
  if(!state)return;
  const focused=document.activeElement;
  const focusId=focused?.getAttribute('data-instance'),focusArea=focused?.closest('#network')?'#network':'#inventory';
  const nodes=state.nodes;
  $('#total').textContent=nodes.length;
  $('#available').textContent=nodes.filter(n=>n.status==='available').length;
  $('#degraded').textContent=nodes.filter(n=>n.status!=='available'||n.summaryStatus!=='available').length;
  $('#summaries').textContent=nodes.filter(n=>n.summaryStatus==='available').length;
  const svg=$('#network');svg.replaceChildren();
  const defs=shape('defs',{}),marker=shape('marker',{id:'arrow',viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:6,markerHeight:6,orient:'auto'});
  marker.append(shape('path',{d:'M0 0 10 5 0 10Z',fill:'#a9b99f'}));defs.append(marker);svg.append(defs);
  for(const node of nodes){for(const target of node.dependencies){
    const a=positions[node.instanceId],b=positions[target];if(!a||!b)continue;
    const ax=a[0]+105,ay=a[1]+35,bx=b[0]+105,by=b[1]+35,dx=bx-ax,dy=by-ay;
    const scale=1/Math.max(Math.abs(dx)/118,Math.abs(dy)/45);
    const endX=bx-dx*scale,endY=by-dy*scale;
    const path=Math.abs(dx)<1&&Math.abs(dy)>200?`M${ax} ${ay}H${a[0]-30}V${by}H${b[0]}`:`M${ax} ${ay}L${endX} ${endY}`;
    svg.append(shape('path',{d:path,class:'edge','marker-end':'url(#arrow)'}));
  }}
  for(const node of nodes){const pos=positions[node.instanceId];if(!pos)continue;
    const g=shape('g',{transform:`translate(${pos[0]},${pos[1]})`,class:`node ${node.status} ${selected===node.instanceId?'selected':''}`,tabindex:0,'data-instance':node.instanceId,role:'button','aria-label':`${node.name}: ${node.status}`,'aria-pressed':String(selected===node.instanceId)});
    g.append(shape('rect',{width:210,height:76,rx:10}),shape('circle',{cx:190,cy:18,r:5}),shape('text',{x:13,y:30},node.name),shape('text',{x:13,y:53,class:'sub'},node.instanceId));
    g.addEventListener('click',()=>choose(node.instanceId));g.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();choose(node.instanceId);}});svg.append(g);
  }
  const tbody=$('#inventory');tbody.replaceChildren();for(const node of nodes){const row=el('tr'),cell=el('td'),button=el('button',node.name);button.setAttribute('data-instance',node.instanceId);button.append(el('small',node.instanceId));button.addEventListener('click',()=>choose(node.instanceId,true));cell.append(button);row.append(cell,el('td',node.family),el('td',node.status),el('td',node.summaryStatus),el('td',node.version||'Unknown'));tbody.append(row);}
  if(focusId)document.querySelector(`${focusArea} [data-instance="${CSS.escape(focusId)}"]`)?.focus({preventScroll:true});
  const node=nodes.find(n=>n.instanceId===selected)||nodes[0],detail=$('#detail');detail.replaceChildren();
  detail.append(el('span',node.family.toUpperCase(),'eyebrow'),el('h2',node.name),el('p',`${node.status} · ${node.instanceId}`),el('p',node.endpoint),el('p',`Last checked: ${new Date(node.observedAt).toLocaleTimeString()}`));
  if(node.summaryStatus!=='available'){detail.append(el('h3','Contents unavailable'),el('p',`Summary access: ${node.summaryStatus}. No previous counts are shown.`));return;}
  const metrics=el('div',undefined,'metrics');for(const count of node.counts){const card=el('div',undefined,'metric');card.append(el('strong',count.value.toLocaleString()),el('span',count.label));metrics.append(card);}detail.append(metrics,el('h3','Recent activity'));
  const activity=el('ul',undefined,'activity');for(const event of node.activity){const row=el('li');row.append(el('time',new Date(event.at*1000).toLocaleTimeString()),el('b',event.event+' · '+event.outcome));activity.append(row);}if(!node.activity.length)activity.append(el('li','No recorded activity.'));detail.append(activity,el('p','Latest six recorded outcomes; monitoring is not a complete audit viewer.'));
}
function clear(message){state=null;document.body.classList.add('stale');$('#notice').hidden=false;$('#notice').textContent=message;for(const id of ['total','available','degraded','summaries'])$('#'+id).textContent='—';$('#network').replaceChildren();$('#inventory').replaceChildren();$('#detail').replaceChildren(el('h2','Snapshot unavailable'),el('p','Counts are hidden until an authorised refresh succeeds.'));}
async function refresh(){
  clearTimeout(timer);if(busy)return;if(!token){$('#login').hidden=false;return;}
  busy=true;$('#refresh').disabled=true;$('#freshness').textContent='Checking each service…';
  const controller=new AbortController(),deadline=setTimeout(()=>controller.abort(),12000);
  try{const response=await fetch('/api/snapshot',{headers:{Authorization:'Bearer '+token},cache:'no-store',signal:controller.signal});
    if(response.status===401){token='';sessionStorage.removeItem('farmyMonitorToken');$('#login').hidden=false;throw Error('Access key missing or expired. Reconnect using the runner’s link.');}
    if(!response.ok)throw Error('Monitoring bridge is unavailable. No current snapshot.');
    state=await response.json();lastSuccess=Date.now();document.body.classList.remove('stale');$('#notice').hidden=true;$('#login').hidden=true;$('#freshness').textContent='Checked '+new Date(state.observedAt).toLocaleTimeString();render();
  }catch(error){clear(error.name==='AbortError'?'Monitoring timed out. No current snapshot.':error.message);$('#freshness').textContent=lastSuccess?'Last successful refresh: '+new Date(lastSuccess).toLocaleTimeString():'No successful refresh.';}
  finally{clearTimeout(deadline);busy=false;$('#refresh').disabled=false;if($('#automatic').checked&&!document.hidden&&token)timer=setTimeout(refresh,10000);}
}
$('#login').addEventListener('submit',event=>{event.preventDefault();token=$('#key').value.trim();$('#key').value='';sessionStorage.setItem('farmyMonitorToken',token);refresh();});
$('#refresh').addEventListener('click',refresh);$('#automatic').addEventListener('change',()=>{clearTimeout(timer);if($('#automatic').checked)refresh();});
document.addEventListener('visibilitychange',()=>{clearTimeout(timer);if(!document.hidden&&$('#automatic').checked)refresh();});
setInterval(()=>{if(lastSuccess&&Date.now()-lastSuccess>30000&&!busy){document.body.classList.add('stale');$('#freshness').textContent='Stale snapshot · last success '+new Date(lastSuccess).toLocaleTimeString();}},5000);
refresh();
