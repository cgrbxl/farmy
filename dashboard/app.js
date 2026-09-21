'use strict';
const $ = selector => document.querySelector(selector);
const statusLabels = {reference:'Reference slice', adapter:'Configuration adapter', planned:'Planned'};
const family = id => FARMY.families.find(item => item.id === id);
// Hosted dashboard-only copies link to rendered public documentation. A file://
// copy retains relative links to the adjacent local repository, including offline.
function hydrateRepoLinks(root = document) {
  if (location.protocol === 'file:') return;
  root.querySelectorAll('a[href^="../"]').forEach(link => {
    link.href = 'https://github.com/cgrbxl/farmy/blob/main/' + link.getAttribute('href').slice(3);
    link.target = '_blank'; link.rel = 'noopener noreferrer';
  });
}
$('#snapshot-date').textContent = FARMY.date;
$('#baseline-link').href = 'https://github.com/cgrbxl/farmy/commit/' + FARMY.revision;

function selectModule(id) {
  const item = family(id);
  document.querySelectorAll('.module-node').forEach(button => {
    const selected = button.dataset.family === id;
    button.classList.toggle('selected', selected);
    button.setAttribute('aria-pressed', String(selected));
  });
  $('#module-detail').innerHTML = `<span class="tag ${item.status}">${statusLabels[item.status]}</span>
    <div class="detail-symbol">${item.symbol}</div><h3>${item.name}</h3><p class="detail-subtitle">${item.subtitle}</p>
    <p>${item.does}</p><dl><dt>Owns</dt><dd>${item.owns}</dd><dt>Stays outside</dt><dd>${item.boundary}</dd>
    <dt>Implemented today</dt><dd>${item.now}</dd><dt>Still ahead</dt><dd>${item.next}</dd></dl>
    <a class="text-link" href="../${item.doc}">Open the family guide ↗</a>`;
  hydrateRepoLinks($('#module-detail'));
}
$('#module-grid').innerHTML = FARMY.families.map(item => `<button class="module-node ${item.status}" data-family="${item.id}" aria-pressed="false"><span class="node-top"><span class="node-symbol">${item.symbol}</span><span class="status-dot" aria-hidden="true"></span></span><strong>${item.name}</strong><small>${item.group}</small><span class="node-status">${statusLabels[item.status]}</span></button>`).join('');
$('#module-grid').addEventListener('click', event => {
  const button = event.target.closest('[data-family]');
  if (button) selectModule(button.dataset.family);
});
selectModule('wallet');

let flowId = 'UC-001', flowStep = 0;
$('#flow-tabs').innerHTML = FARMY.slices.map(slice => `<button data-flow="${slice.id}" aria-pressed="false"><small>${slice.id}</small>${slice.title}</button>`).join('');
function renderFlow() {
  const steps = FARMY.flows[flowId], step = steps[flowStep];
  document.querySelectorAll('[data-flow]').forEach(button => {
    const selected = button.dataset.flow === flowId;
    button.classList.toggle('selected', selected);
    button.setAttribute('aria-pressed', String(selected));
  });
  $('#flow-count').textContent = `${flowId} / STEP ${flowStep + 1} OF ${steps.length}`;
  $('#flow-title').textContent = step.title;
  $('#flow-text').textContent = step.text;
  $('#flow-check').textContent = step.check;
  $('#flow-actors').innerHTML = step.actors.map(id => {
    const item = family(id);
    return `<div class="actor"><span>${item.symbol}</span><div><strong>${item.name}</strong><small>${item.group}</small></div><i></i></div>`;
  }).join('');
  $('#step-dots').innerHTML = steps.map((item, index) => `<button data-step="${index}" aria-label="Step ${index + 1}: ${item.title}" aria-pressed="${index === flowStep}" class="${index === flowStep ? 'selected' : ''}"></button>`).join('');
  $('#flow-prev').disabled = flowStep === 0;
  $('#flow-next').disabled = flowStep === steps.length - 1;
}
$('#flow-tabs').addEventListener('click', event => {
  const button = event.target.closest('[data-flow]');
  if (button) { flowId = button.dataset.flow; flowStep = 0; renderFlow(); }
});
$('#flow-prev').addEventListener('click', () => { if (flowStep > 0) { flowStep--; renderFlow(); } });
$('#flow-next').addEventListener('click', () => { if (flowStep < FARMY.flows[flowId].length - 1) { flowStep++; renderFlow(); } });
$('#step-dots').addEventListener('click', event => {
  const button = event.target.closest('[data-step]');
  if (button) { flowStep = Number(button.dataset.step); renderFlow(); $('#step-dots').querySelector(`[data-step="${flowStep}"]`).focus(); }
});
renderFlow();

$('#test-bars').innerHTML = [{n:FARMY.foundationTests,cls:'foundation'}, ...FARMY.slices.map((s,i) => ({n:s.tests,cls:`uc${i+1}`}))].map(item => `<span class="${item.cls}" style="flex:${item.n}">${item.n}</span>`).join('');
$('#slice-cards').innerHTML = FARMY.slices.map((slice, index) => `<article class="slice-card"><div class="slice-top"><span>${slice.id}</span><span class="tag reference">Verified slice</span></div><div class="slice-number">0${index+1}<span>↗</span></div><small class="eyebrow">${slice.label}</small><h3>${slice.title}</h3><p>${slice.outcome}</p><ul>${slice.proof.map(point => `<li>${point}</li>`).join('')}</ul><div class="slice-lesson"><b>What it proves</b><p>${slice.lesson}</p></div><div class="slice-meta"><span>${slice.tests} acceptance tests</span><span>${slice.services}</span></div><p class="slice-scope">${slice.scope}</p><div class="slice-actions"><a href="../${slice.path}">Run & inspect ↗</a><button class="copy-button" data-copy="${slice.command}" aria-label="Copy ${slice.id} demo command">Copy command</button></div></article>`).join('');
$('#coverage-table').innerHTML += `<thead><tr><th scope="col">Delivered slice</th>${FARMY.families.map(item => `<th scope="col">${item.name}</th>`).join('')}</tr></thead><tbody>${FARMY.slices.map(slice => `<tr><th scope="row">${slice.id}<small>${slice.title}</small></th>${FARMY.families.map(item => {
  const present = slice.families.includes(item.id), adapter = present && item.status === 'adapter';
  return `<td class="${present ? 'covered' : 'uncovered'}" aria-label="${item.name}: ${adapter ? 'binding-file adapter' : present ? 'reference behaviour exercised' : 'outside this slice'}">${adapter ? '◐' : present ? '●' : '—'}</td>`;
}).join('')}</tr>`).join('')}</tbody>`;
$('#next-queue').innerHTML = FARMY.queue.map((item,index) => `<article><span class="queue-number">${String(index+FARMY.slices.length+1).padStart(2,'0')}</span><div><span class="tag planned">${index === 0 ? 'Next queued outcome' : 'Queued'}</span><h4>${item.title}</h4><p>${item.detail}</p></div></article>`).join('');

$('#method-steps').innerHTML = FARMY.method.map((step,index) => `<button data-method="${index}" aria-pressed="false"><span>${String(index+1).padStart(2,'0')}</span>${step[0]}<b>↗</b></button>`).join('');
function selectMethod(index) {
  const step = FARMY.method[index];
  document.querySelectorAll('[data-method]').forEach(button => {
    const selected = Number(button.dataset.method) === index;
    button.classList.toggle('selected', selected);
    button.setAttribute('aria-pressed', String(selected));
  });
  $('#method-detail').innerHTML = `<span class="method-big">${String(index+1).padStart(2,'0')}</span><span class="eyebrow">ONE INCREMENT, END TO END</span><h3>${step[0]}</h3><p>${step[1]}</p><div class="method-check">${step[2]}</div><div class="method-loop" aria-label="Repeat the seven-stage delivery loop">Frame → Map → Specify → Build → Challenge → Retain → Choose <span>↺</span></div>`;
}
$('#method-steps').addEventListener('click', event => {
  const button = event.target.closest('[data-method]');
  if (button) selectMethod(Number(button.dataset.method));
});
selectMethod(0);

let toastTimer;
document.addEventListener('click', async event => {
  const button = event.target.closest('[data-copy]');
  if (!button) return;
  const text = button.dataset.copy;
  try {
    if (!navigator.clipboard) throw new Error('Clipboard unavailable');
    await navigator.clipboard.writeText(text);
    $('#copy-status').textContent = 'Command copied. Run it from the repository root.';
  } catch {
    const field = document.createElement('textarea');
    field.value = text; field.setAttribute('aria-label', 'Command to copy');
    field.style.position = 'fixed'; field.style.top = '0';
    document.body.appendChild(field); field.select();
    const copied = document.execCommand('copy');
    field.remove(); button.focus();
    $('#copy-status').textContent = copied ? 'Command copied. Run it from the repository root.' : `Copy this command: ${text}`;
  }
  $('#copy-status').classList.add('visible'); clearTimeout(toastTimer);
  toastTimer = setTimeout(() => $('#copy-status').classList.remove('visible'), 6000);
});
$('#menu-toggle').addEventListener('click', () => {
  const open = document.body.classList.toggle('menu-open');
  $('#menu-toggle').setAttribute('aria-expanded', String(open));
});
document.querySelectorAll('nav a').forEach(link => link.addEventListener('click', () => {
  document.body.classList.remove('menu-open'); $('#menu-toggle').setAttribute('aria-expanded', 'false');
}));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape') { document.body.classList.remove('menu-open'); $('#menu-toggle').setAttribute('aria-expanded', 'false'); }
});
const observer = new IntersectionObserver(entries => {
  for (const entry of entries) if (entry.isIntersecting) {
    document.querySelectorAll('nav a').forEach(link => {
      const active = link.hash === `#${entry.target.id}`;
      link.classList.toggle('active', active);
      if (active) link.setAttribute('aria-current', 'location'); else link.removeAttribute('aria-current');
    });
  }
}, {rootMargin:'-15% 0px -65% 0px', threshold:0});
document.querySelectorAll('main > section').forEach(section => observer.observe(section));

hydrateRepoLinks();
const compactNav = window.matchMedia('(max-width:980px)');
function syncNavAccess() {
  const hidden = compactNav.matches && !document.body.classList.contains('menu-open');
  $('#sidebar').inert = hidden;
  $('#sidebar').setAttribute('aria-hidden', String(hidden));
}
compactNav.addEventListener('change', syncNavAccess);
$('#menu-toggle').addEventListener('click', syncNavAccess);
document.querySelectorAll('nav a').forEach(link => link.addEventListener('click', syncNavAccess));
document.addEventListener('keydown', event => { if (event.key === 'Escape') syncNavAccess(); });
syncNavAccess();

const acceptanceCount = FARMY.slices.reduce((sum, slice) => sum + slice.tests, 0);
const totalTests = FARMY.foundationTests + acceptanceCount;
$('#slice-count').textContent = FARMY.slices.length;
$('#test-count').textContent = totalTests;
$('#delivered-count').textContent = `${FARMY.slices.length} slices delivered`;
$('#passing-count').textContent = `${totalTests} tests passing`;
$('#test-breakdown').textContent = `${FARMY.foundationTests} foundation + ${acceptanceCount} slice acceptance`;
$('#test-bars').setAttribute('aria-label', `${totalTests} tests: ${FARMY.foundationTests} foundation; ` + FARMY.slices.map(s => `${s.tests} ${s.id}`).join(', '));
$('#test-legend').innerHTML = `<span><i class="foundation"></i>Foundation ${FARMY.foundationTests}</span>` + FARMY.slices.map((s,i) => `<span><i class="uc${i+1}"></i>${s.id} ${s.tests}</span>`).join('');

$('#concept-tabs').innerHTML = FARMY.concepts.map((concept,index) => `<button data-concept="${concept.id}" aria-pressed="false"><small>0${index+1}</small><strong>${concept.title}</strong></button>`).join('');
function selectConcept(id) {
  const concept = FARMY.concepts.find(item => item.id === id);
  document.querySelectorAll('[data-concept]').forEach(button => {
    const active = button.dataset.concept === id;
    button.setAttribute('aria-pressed', String(active));
    button.classList.toggle('selected', active);
  });
  $('#concept-detail').innerHTML = `<span class="eyebrow">ACCEPTED DIRECTION · BROADER CAPABILITY NOT YET IMPLEMENTED</span><h3>${concept.subtitle}</h3><p>${concept.text}</p><ol class="concept-flow">${concept.steps.map(step => `<li>${step}</li>`).join('')}</ol><p class="concept-boundary">${concept.boundary}</p><p class="concept-today">${concept.today}</p><p class="concept-families"><b>Responsibility:</b> ${concept.families}</p>`;
}
$('#concept-tabs').addEventListener('click', event => {
  const button = event.target.closest('[data-concept]');
  if (button) selectConcept(button.dataset.concept);
});
selectConcept('plasticity');
