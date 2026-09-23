/* Optional explanation layer. The phone remains a self-contained simulation. */
(() => {
  'use strict';
  const families = {
    assistance: {name:'Assistance', role:'The farmer-facing conversation', example:'“What needs my attention this week?” brings findings together, explains uncertainty and offers possible next steps. The phone is a replaceable client, not the owner of all Farmy capabilities.', partners:'Knowledge supplies evidence; Model access handles model calls; Workflow coordinates an approved task.', today:'UC-004 demonstrates one narrowly checked crop answer. This multi-topic copilot and its suggested actions are simulated.'},
    knowledge: {name:'Knowledge', role:'Find evidence and keep its origin', example:'An answer links a leak hypothesis to sensor history, a controller manual and a maintenance message. Citations should preserve the exact source/version rather than turn a generated answer into an authoritative record.', partners:'Processing produces derived evidence. Wallet authority is checked before evidence is disclosed.', today:'UC-002 provides exact-source crop evidence; UC-008 demonstrates two Knowledge instances and a deliberate provider rebuild. Broad retrieval across this farm is simulated.'},
    processing: {name:'Processing', role:'Turn permitted inputs into useful findings', example:'Parse documents, align meter and pump histories, calculate unusual night flow and prepare a permitted pseudonymised view. These are specialised processing capabilities, not responsibilities of Wallet.', partners:'Connectors supply permitted inputs; Knowledge retains derived evidence; Workflow coordinates the steps.', today:'A deterministic crop-field extractor is demonstrated. Leak diagnosis, cross-source analysis and robust pseudonymisation here are simulated; replacing names does not guarantee anonymity.'},
    'model-access': {name:'Model access', role:'Choose how AI is invoked', example:'The model selector represents an approved local or external route. A real implementation must check the route, credentials, permitted context and egress before sending anything.', partners:'Registry binds the provider instance; Wallet constrains access; Assistance requests inference and checks the result.', today:'UC-004 demonstrates one fixed local Qwen route with checked output. This selector makes no real model calls and configures no API keys.'},
    wallet: {name:'Wallet', role:'Authority, provenance and future trust evidence', example:'“Who may see which source” represents source/owner/consumer policy. A certificate in Drive is a document first; its issuer, signature, status and trust would need separate checks. A signed claim is not automatic truth or permission.', partners:'Every serving module enforces current authority. Exchange applies explicit disclosure approval. Credential/key adapters would support issuer, holder and verifier roles.', today:'Resource/version and source-scoped grants are demonstrated in UC-001–003. Signed credentials and trust chains are future work. All permissions in this public mock govern fictional browser data only.'},
    connectors: {name:'Connectors', role:'Reach sources without owning their policy', example:'Folders, message exports, sensors, weather and tractor telemetry are different source interfaces. The hub is a deployment location that may host several modules, not a tenth module family.', partners:'Wallet controls access; Processing interprets inputs. Source filters bound what a connector ingests; a binding alone never permits reading it.', today:'Local Folder and synthetic Sensor connectors are demonstrated. S3 has local fixture evidence; live Scaleway validation is pending. This mock uses no GPS, mailbox, tractor, weather service or real sensors.'},
    workflow: {name:'Workflow', role:'Coordinate work and remember its state', example:'Investigate a suspected leak, prepare a draft, ask the farmer to approve and then track the outcome. A proposed device change needs its own bounded execution and safety contract.', partners:'Processing calculates; Assistance explains; Wallet authorises; Exchange handles approved outward disclosure. Device execution would require a specialised adapter.', today:'Durable extraction/indexing jobs and binding-pinned recovery are demonstrated. Scheduling, device actuation and the mock’s undo controls are simulated, not validated real equipment controls.'},
    exchange: {name:'Exchange', role:'Make outward disclosure deliberate', example:'Preview what would leave, who would receive it and under what purpose and conditions. A prepared letter is not sent; permission to read a source is not permission to export it.', partners:'Wallet supplies authority; Connectors/Knowledge supply permitted exact content; Workflow may coordinate approval and delivery.', today:'UC-006 demonstrates exact-document approval and receipt recovery with a synthetic recipient. This mock sends nothing. Downstream contracts are obligations, not a way to recall data or technically prevent every reuse.'},
    registry: {name:'Registry', role:'Bind compatible module instances', example:'Behind this simple phone experience, a composition chooses which Connector, Knowledge or Model access instance serves each need. Instances can be replaced only with compatible contracts, explicit state handling and appropriate trust.', partners:'Provides selection and compatibility metadata to consumers. It neither executes work nor issues Wallet grants.', today:'Revisioned binding files and local descriptor checks are demonstrated, including UC-008 replacement. Automatic discovery, a visual configuration catalogue and mixed laptop/cloud deployment remain future work.'}
  };
  const contexts = [
    ['#view-copilot', 'Behind the copilot', ['assistance','knowledge','processing','model-access','workflow']],
    ['#view-drive .pad', 'Behind the farm drive', ['connectors','wallet','knowledge']],
    ['#view-hub .pad', 'Behind the hub', ['connectors','processing','workflow']],
    ['#view-control .pad', 'Behind access and sharing', ['wallet','exchange','registry']]
  ];
  const makeButton = (id) => {
    const button = document.createElement('button');
    button.type = 'button'; button.className = 'farmy-info-tag';
    button.textContent = 'ⓘ ' + families[id].name;
    button.setAttribute('aria-label', 'Explain ' + families[id].name + ' in this solution');
    button.addEventListener('click', () => explain(id));
    return button;
  };
  const toolbar = document.createElement('div');
  toolbar.className = 'farmy-explain-toolbar';
  toolbar.innerHTML = '<button type="button" id="farmy-explain-toggle" aria-pressed="true">ⓘ How Farmy works · on</button><button type="button" id="farmy-all-modules">All 9 families</button><span>Architecture notes · every interaction is simulated</span>';
  document.querySelector('main').prepend(toolbar);
  contexts.forEach(([selector, label, ids]) => {
    const row = document.createElement('aside'); row.className = 'farmy-explain-tags';
    row.setAttribute('aria-label', label);
    const title = document.createElement('span'); title.textContent = label; row.append(title);
    ids.forEach(id => row.append(makeButton(id)));
    document.querySelector(selector).prepend(row);
  });
  const modal = document.createElement('dialog'); modal.className = 'farmy-explain-dialog';
  modal.setAttribute('aria-labelledby', 'farmy-explain-title');
  modal.innerHTML = '<div class="farmy-explain-head"><span>FARMY / SOLUTION ARCHITECTURE</span><button type="button" aria-label="Close architecture explanation">✕</button></div><div id="farmy-explain-content"></div>';
  document.body.append(modal);
  modal.querySelector('button').onclick = () => modal.close();
  modal.addEventListener('click', e => { if (e.target === modal) { const r = modal.getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) modal.close(); } });
  function showContent(content) {
    const container = modal.querySelector('#farmy-explain-content'); container.replaceChildren(content);
    if (!modal.open) modal.showModal();
    modal.querySelector('button').focus();
  }
  function explain(id) {
    const item = families[id]; const content = document.createElement('div');
    content.innerHTML = `<h2 id="farmy-explain-title">${item.name}</h2><p class="farmy-explain-role">${item.role}</p><h3>In Las Tres Encinas</h3><p>${item.example}</p><h3>Works with</h3><p>${item.partners}</p><div class="farmy-explain-status"><h3>Implemented today / illustrated here</h3><p>${item.today}</p></div><a href="https://github.com/cgrbxl/farmy/blob/main/modules/${id}/README.md" target="_blank" rel="noopener noreferrer">Read the family guide ↗</a>`;
    showContent(content);
  }
  document.querySelector('#farmy-all-modules').onclick = () => {
    const content = document.createElement('div');
    content.innerHTML = '<h2 id="farmy-explain-title">One solution, nine families</h2><p>The four phone tabs are views, not four backend modules. A family can have several implementations and instances, running together on a hub or across permitted environments.</p><p class="farmy-explain-flow">Sources → Connectors → Processing → Knowledge → Assistance ↔ Model access</p><p>Wallet controls authority. Registry selects instances. Workflow coordinates tasks. Exchange handles separately approved outward disclosures.</p>';
    const grid = document.createElement('div'); grid.className = 'farmy-explain-grid';
    Object.keys(families).forEach(id => grid.append(makeButton(id))); content.append(grid);
    const limits = document.createElement('p'); limits.className = 'farmy-explain-status';
    limits.textContent = 'This is an illustrative future solution, not a completed production release. One simulated hub does not prove federated data spaces. Hash-linked audit entries are not signed credentials or independently witnessed proof. AI-generated source interfaces remain future work. No real model calls, equipment actions or messages occur.';
    content.append(limits); showContent(content);
  };
  document.querySelector('#farmy-explain-toggle').onclick = function () {
    const enabled = this.getAttribute('aria-pressed') !== 'true';
    this.setAttribute('aria-pressed', String(enabled));
    this.textContent = 'ⓘ How Farmy works · ' + (enabled ? 'on' : 'off');
    document.querySelectorAll('.farmy-explain-tags').forEach(row => { row.hidden = !enabled; });
  };
})();
