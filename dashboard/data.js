/* Curated project snapshot. Update with every completed slice; exclude private feedback. */
const FARMY = {
  "date": "25 September 2026",
  "revision": "f4703c4",
  "families": [
    {
      "id": "wallet",
      "name": "Wallet",
      "symbol": "◈",
      "group": "Authority",
      "status": "reference",
      "subtitle": "Identity for information. Authority for access.",
      "owns": "Resource/source identities, versions, policies, provenance and future signed-claim/trust-policy references.",
      "does": "Records who owns information and who may access it. It separates logical identity from physical storage.",
      "boundary": "No parsers, provider SDKs, indexes or workflow execution.",
      "now": "Document/version grants and source/owner/consumer permissions. Additive state upgrades are tested. UC-009 adds explicit managed-copy admission, provenance and narrower item readers.",
      "next": "Owner and contributor claims, explicit issuer/holder/verifier trust policies and complementary credential adapters.",
      "slices": [
        "UC-001",
        "UC-002",
        "UC-003",
        "UC-004",
        "UC-005",
        "UC-006",
        "UC-008",
        "UC-009",
        "UC-010"
      ],
      "doc": "modules/wallet/README.md"
    },
    {
      "id": "registry",
      "name": "Registry",
      "symbol": "⌘",
      "group": "Composition",
      "status": "adapter",
      "subtitle": "Choose an implementation. Bind an instance.",
      "owns": "Selected instances, compatibility declarations and binding revisions.",
      "does": "Connects a capability to an explicitly chosen implementation and endpoint. Registration is not permission.",
      "boundary": "Does not grant access, install untrusted software or execute jobs.",
      "now": "Revisioned binding files plus authenticated local descriptor checks. UC-008 selects between two Knowledge instances.",
      "next": "Discovery and admission for remote environments; independently implemented transport.",
      "slices": [
        "UC-001",
        "UC-002",
        "UC-003",
        "UC-004",
        "UC-005",
        "UC-006",
        "UC-008",
        "UC-009",
        "UC-010"
      ],
      "doc": "modules/registry/README.md"
    },
    {
      "id": "workflow",
      "name": "Workflow",
      "symbol": "↗",
      "group": "Coordination",
      "status": "reference",
      "subtitle": "Remember the job, even when a step fails.",
      "owns": "Job phases, pinned inputs, step keys and recovery state.",
      "does": "Coordinates work across services through their public contracts.",
      "boundary": "No extraction rules or automatic expansion of permissions.",
      "now": "Durable extract/index jobs with optional Knowledge binding. Changed binding revisions cannot silently resume old job keys.",
      "next": "Additional reviewed workflows, scheduling and cancellation when needed.",
      "slices": [
        "UC-002",
        "UC-004",
        "UC-005",
        "UC-008"
      ],
      "doc": "modules/workflow/README.md"
    },
    {
      "id": "connectors",
      "name": "Connectors",
      "symbol": "⇄",
      "group": "Acquisition",
      "status": "reference",
      "subtitle": "Bring sources in without giving up control.",
      "owns": "Source access, provider credentials, snapshots and source membership.",
      "does": "Provides bytes or observations through an authenticated, authorised boundary. Different providers can have separate implementations.",
      "boundary": "Does not own general parsing, inference or export policy.",
      "now": "Local Folder and Synthetic Sensor are verified. An S3 implementation passes local HTTP-double checks; real provider evidence is pending. UC-009 separates collectively governed folders from immutable managed copies.",
      "next": "Finish Scaleway source validation; later admit AI-generated source mappings or isolated adapters.",
      "slices": [
        "UC-001",
        "UC-002",
        "UC-003",
        "UC-004",
        "UC-005",
        "UC-006",
        "UC-008",
        "UC-009",
        "UC-010"
      ],
      "doc": "modules/connectors/README.md"
    },
    {
      "id": "processing",
      "name": "Processing",
      "symbol": "✳",
      "group": "Interpretation",
      "status": "reference",
      "subtitle": "Turn permitted inputs into proposed results.",
      "owns": "Algorithm/configuration versions, attempts and result provenance.",
      "does": "Extracts, normalises, validates and computes through specialised implementations. A model is optional.",
      "boundary": "Cannot turn a parsed claim into an authoritative farm fact by itself.",
      "now": "A bounded text parser extracts crop from a synthetic report with exact quoted evidence.",
      "next": "More formats and specialised computations under explicit contracts.",
      "slices": [
        "UC-002",
        "UC-004",
        "UC-005",
        "UC-008"
      ],
      "doc": "modules/processing/README.md"
    },
    {
      "id": "knowledge",
      "name": "Knowledge",
      "symbol": "▤",
      "group": "Retrieval",
      "status": "reference",
      "subtitle": "Find evidence. Keep its source attached.",
      "owns": "Derived indexes, exact source mappings and retrieval state.",
      "does": "Returns evidence only after checking the consumer’s current permission.",
      "boundary": "Not a second resource authority; indexing permission is not reader permission.",
      "now": "Two exact-source evidence implementations with private stores. UC-008 proves an explicit public-API rebuild after replacement.",
      "next": "Richer retrieval, index removal/rebuild and independent alternatives.",
      "slices": [
        "UC-002",
        "UC-004",
        "UC-005",
        "UC-008"
      ],
      "doc": "modules/knowledge/README.md"
    },
    {
      "id": "model-access",
      "name": "Model access",
      "symbol": "◇",
      "group": "Inference",
      "status": "reference",
      "subtitle": "Choose where a model runs and what it receives.",
      "owns": "Model profiles, approved routes, endpoint references and invocation state.",
      "does": "Controls calls to independently supplied local or external models.",
      "boundary": "A routing service is not itself the model, and cannot bypass egress approval.",
      "now": "One pinned local Ollama model route, independently authorised evidence and a durable invocation journal.",
      "next": "Additional approved providers, richer model features and runtime isolation.",
      "slices": [
        "UC-004",
        "UC-005"
      ],
      "doc": "modules/model-access/README.md"
    },
    {
      "id": "assistance",
      "name": "Assistance",
      "symbol": "✧",
      "group": "Interaction",
      "status": "reference",
      "subtitle": "Help the farmer act on permitted evidence.",
      "owns": "Task/conversation state, evidence sets and constrained tool proposals.",
      "does": "Combines retrieval and approved model access into source-linked assistance.",
      "boundary": "Cannot expand grants or execute consequential actions without their own controls.",
      "now": "One crop question with a validated source citation; retained answers remain subject to current permissions.",
      "next": "Broader questions with explicit evidence and validation semantics.",
      "slices": [
        "UC-004",
        "UC-005"
      ],
      "doc": "modules/assistance/README.md"
    },
    {
      "id": "exchange",
      "name": "Exchange",
      "symbol": "↗",
      "group": "Disclosure",
      "status": "reference",
      "subtitle": "Approve the content, recipient and purpose.",
      "owns": "Disclosure manifests, delivery attempts and receipt uncertainty.",
      "does": "Prepares and delivers exact authorised disclosures across a boundary.",
      "boundary": "Not a generic computation engine or equipment controller. Delivered copies cannot reliably be recalled.",
      "now": "Exact-document preview, bound approval, permission-checked delivery and durable receipt recovery with a synthetic recipient.",
      "next": "Production recipient adapters, interactive approval, governed data-space exchange and credential presentations.",
      "slices": [
        "UC-006"
      ],
      "doc": "modules/exchange/README.md"
    }
  ],
  "slices": [
    {
      "id": "UC-001",
      "title": "Controlled memory",
      "label": "The foundation",
      "tests": 8,
      "families": [
        "wallet",
        "registry",
        "connectors"
      ],
      "path": "solutions/core/uc001/README.md",
      "command": ".venv/bin/python solutions/core/uc001/run.py demo",
      "outcome": "Register a document, read its exact version and retain identity through a move or update.",
      "proof": [
        "Immutable snapshots and explicit read grants",
        "Old versions remain identifiable",
        "Restart, revocation and unavailable-authority checks"
      ],
      "lesson": "Information identity belongs to Wallet; physical bytes belong to a Connector.",
      "services": "2 services",
      "scope": "Synthetic local documents",
      "access": "API-tested foundation"
    },
    {
      "id": "UC-002",
      "title": "Evidence with a source",
      "label": "Interpret & retrieve",
      "tests": 9,
      "families": [
        "wallet",
        "registry",
        "connectors",
        "processing",
        "knowledge",
        "workflow"
      ],
      "path": "solutions/document-path/uc002/README.md",
      "command": ".venv/bin/python solutions/document-path/uc002/run.py demo",
      "outcome": "Extract crop = wheat and retrieve it with its exact source version, digest and quoted byte range.",
      "proof": [
        "Distinct source, transfer, indexing and query grants",
        "Duplicate jobs converge on one derived entry",
        "Interrupted indexing resumes after Workflow restart"
      ],
      "lesson": "Processing, coordination and retrieval can be separate without losing provenance.",
      "services": "5 services",
      "scope": "One field in a synthetic text report",
      "access": "API-tested foundation"
    },
    {
      "id": "UC-003",
      "title": "Permission for a source",
      "label": "Beyond documents",
      "tests": 9,
      "families": [
        "wallet",
        "registry",
        "connectors"
      ],
      "path": "solutions/sensor-path/uc003/README.md",
      "command": ".venv/bin/python solutions/sensor-path/uc003/run.py demo",
      "outcome": "One source/owner/consumer permission covers existing and subsequently added observations.",
      "proof": [
        "Separate sources and consumers stay isolated",
        "Release records identify exact observations",
        "Revocation, restart and audit-storage failure checks"
      ],
      "lesson": "Observation identity supports traceability; it does not require an approval for every observation.",
      "services": "3 services*",
      "scope": "Synthetic temperature observations",
      "access": "API-tested foundation"
    },
    {
      "id": "UC-004",
      "title": "A cited model answer",
      "label": "Grounded assistance",
      "tests": 10,
      "families": [
        "wallet",
        "registry",
        "workflow",
        "connectors",
        "processing",
        "knowledge",
        "model-access",
        "assistance"
      ],
      "path": "solutions/assisted-answer/uc004/README.md",
      "command": ".venv/bin/python solutions/assisted-answer/uc004/run.py demo",
      "outcome": "Ask which crop is recorded; a selected local Qwen model returns a value and citation that Farmy checks against exact evidence.",
      "proof": [
        "Independent answer, evidence and invocation permissions",
        "Unapproved routes and fabricated citations rejected",
        "Restart replay and uncertain-call recovery checks"
      ],
      "lesson": "Model output remains untrusted until checked; reading evidence does not authorise every model destination.",
      "services": "7 services + Ollama",
      "scope": "One question · synthetic crop evidence · local Qwen",
      "access": "API-tested foundation"
    },
    {
      "id": "UC-005",
      "title": "The installation, in view",
      "label": "Live operations",
      "tests": 11,
      "families": [
        "wallet",
        "registry",
        "workflow",
        "connectors",
        "processing",
        "knowledge",
        "model-access",
        "assistance"
      ],
      "path": "solutions/operations/uc005/README.md",
      "command": ".venv/bin/python solutions/operations/uc005/run.py launch",
      "outcome": "Inspect eight running module instances, their declared dependencies, actual content counts and recent service outcomes.",
      "proof": [
        "Dedicated monitoring identity; no raw-content or write rights",
        "Unavailable and denied summaries never appear as fresh counts",
        "Closing the browser or bridge leaves independent modules running",
        "An occupied default port selects a free port without stopping other processes"
      ],
      "lesson": "Observability belongs at each service boundary. A client can compose the view without reading private databases.",
      "services": "8 services + UI bridge",
      "scope": "Read-only metadata · synthetic local installation",
      "access": "Read-only interface"
    },
    {
      "id": "UC-006",
      "title": "Approve what leaves",
      "label": "Controlled disclosure",
      "tests": 14,
      "families": [
        "wallet",
        "registry",
        "connectors",
        "exchange"
      ],
      "path": "solutions/disclosure/uc006/README.md",
      "command": ".venv/bin/python solutions/disclosure/uc006/run.py launch",
      "outcome": "Preview exact document bytes and recipient, approve a bound manifest and deliver with a durable receipt.",
      "proof": [
        "Changed recipient/content and missing export authority rejected",
        "Current read, approval and delivery grants checked separately",
        "Lost acknowledgements and restarts recover one accepted copy"
      ],
      "lesson": "Approval binds an exact disclosure; a failed response does not prove the recipient received nothing.",
      "services": "3 Farmy services + recipient fixture",
      "scope": "16 KiB exact-document export · synthetic local recipient",
      "access": "API-tested foundation"
    },
    {
      "id": "UC-008",
      "title": "Replace without sharing state",
      "label": "Knowledge replacement",
      "tests": 11,
      "families": [
        "wallet",
        "registry",
        "workflow",
        "connectors",
        "processing",
        "knowledge"
      ],
      "path": "solutions/replacement/uc008/README.md",
      "command": ".venv/bin/python solutions/replacement/uc008/run.py launch",
      "outcome": "Run two Knowledge instances, replace one domain implementation and rebuild through public APIs while the other stays available.",
      "proof": [
        "Separate audience grants; binding changes conflict with old jobs",
        "Fresh private store rebuilt from authorised Processing evidence",
        "Both providers deny revocation and authority outages"
      ],
      "lesson": "Replaceability requires explicit state recovery and permissions, not just matching API names.",
      "services": "6 services + UI bridge",
      "scope": "Exact crop evidence · shared optional transport SDK",
      "access": "API-tested foundation"
    },
    {
      "id": "UC-009",
      "title": "From source to managed item",
      "label": "Logical Wallet membership",
      "tests": 12,
      "families": [
        "wallet",
        "registry",
        "connectors"
      ],
      "path": "solutions/managed-items/uc009/README.md",
      "command": ".venv/bin/python solutions/managed-items/uc009/run.py launch",
      "outcome": "Read a connected folder collectively; admit one selected email as an immutable, individually governed copy.",
      "proof": [
        "Source and item grants cannot substitute for one another",
        "Provenance and inherited reader ceiling retained; owner can narrow access",
        "Original changes, revocation, concurrent retries and restart tested"
      ],
      "lesson": "Inside the Wallet describes individual governance, independent of where bytes are stored.",
      "services": "2 services + read-only UI bridge",
      "scope": "Synthetic email exports · owner-controlled folder · no real mailbox",
      "access": "API-tested foundation"
    },
    {
      "id": "UC-010",
      "title": "Use your Wallet",
      "label": "First interactive journey",
      "access": "Interactive interface",
      "tests": 12,
      "families": [
        "wallet",
        "registry",
        "connectors"
      ],
      "path": "solutions/interactive/uc010/README.md",
      "command": ".venv/bin/python solutions/interactive/uc010/run.py launch",
      "outcome": "Browse a source, admit a document, inspect its managed copy and grant or revoke a demo consumer’s real access.",
      "proof": [
        "Owner and consumer use separate browser credentials",
        "The consumer sees real denial, permitted content and denial after revocation",
        "Lost replies reconcile through durable requests without extra permissions"
      ],
      "lesson": "A usable client can expose existing capabilities without changing the module contracts.",
      "services": "2 services + interactive UI bridge",
      "scope": "One usable journey · synthetic documents · no real mailbox or production login"
    }
  ],
  "queue": [
    {
      "title": "UC-007 · A real S3 source",
      "families": [
        "connectors"
      ],
      "detail": "In progress: adapter and 11 local HTTP-double checks pass. Real Scaleway validation awaits an approved bucket/prefix and scoped credentials.",
      "number": "07",
      "status": "Provider evidence pending"
    },
    {
      "title": "Package each environment",
      "families": [],
      "detail": "Verify laptop and Kubernetes delivery one target at a time; Scaleway is first for cloud.",
      "number": "11",
      "status": "Next queued outcome"
    }
  ],
  "interactiveBacklog": [
    {
      "title": "Choose the AI",
      "detail": "Select an allowed model/provider, validate endpoint and secret references, and activate a versioned profile. Local first, then one external API."
    },
    {
      "title": "Issue a signed claim",
      "detail": "Add a document, preserve its exact version, preview the claim and sign as a named issuer. Uploading and issuing are separate actions."
    },
    {
      "title": "Present as holder",
      "detail": "Preview the recipient and disclosure; sign a presentation bound to that verifier, a fresh challenge and an expiry."
    },
    {
      "title": "Verify externally",
      "detail": "Use a separate verifier interface and a link or QR request. Show signature validity, issuer trust and credential status separately; the QR itself is not proof."
    },
    {
      "title": "Grow interaction across families",
      "detail": "Add signed third-party contributions, source setup, extraction previews, evidence search, job controls and binding management one tested use case at a time."
    }
  ],
  "flows": {
    "UC-001": [
      {
        "title": "Register the original",
        "actors": [
          "wallet",
          "connectors"
        ],
        "text": "The owner asks Wallet to register an approved local file. Connector captures its bytes; Wallet records a stable resource ID and immutable version.",
        "check": "Ownership and approved-root checks precede capture."
      },
      {
        "title": "Grant one exact read",
        "actors": [
          "wallet"
        ],
        "text": "The owner authorises an identified reader for one resource version. Knowing an endpoint or a grant ID alone gives no access.",
        "check": "The grant binds the subject and exact version."
      },
      {
        "title": "Check before serving",
        "actors": [
          "connectors",
          "wallet"
        ],
        "text": "The reader calls Connector. Connector checks current Wallet authority before returning the matching snapshot.",
        "check": "Unknown, expired, revoked and mis-scoped access is denied."
      },
      {
        "title": "Keep history through change",
        "actors": [
          "wallet",
          "connectors"
        ],
        "text": "Moving identical content preserves identity. Changed content becomes a new version while the old snapshot remains available.",
        "check": "No silent substitution of new bytes for an old version."
      }
    ],
    "UC-002": [
      {
        "title": "Authorise the path",
        "actors": [
          "wallet"
        ],
        "text": "The owner separately authorises source reading, proposal transfer, indexing and reader disclosure.",
        "check": "Permission to index is not permission to disclose to everyone."
      },
      {
        "title": "Start a durable job",
        "actors": [
          "workflow"
        ],
        "text": "Workflow records exact inputs and stable step keys. It remembers whether extraction or indexing has completed.",
        "check": "Changed inputs with the same job key conflict."
      },
      {
        "title": "Extract a proposed field",
        "actors": [
          "processing",
          "connectors",
          "wallet"
        ],
        "text": "Processing reads authorised source bytes through Connector and extracts crop = wheat with a quote, digest and exact source version.",
        "check": "Malformed or ambiguous reports fail without an accepted partial result."
      },
      {
        "title": "Accept derived evidence",
        "actors": [
          "workflow",
          "knowledge",
          "processing",
          "wallet"
        ],
        "text": "Knowledge fetches the proposal from authenticated Processing and accepts one derived entry. Workflow saves completion.",
        "check": "This is derived evidence, not an approved authoritative farm record."
      },
      {
        "title": "Retrieve under current permission",
        "actors": [
          "knowledge",
          "wallet"
        ],
        "text": "Knowledge checks the reader’s current query grant, including for retained evidence. Revocation blocks the next disclosure.",
        "check": "No Wallet connection means no new protected disclosure."
      }
    ],
    "UC-003": [
      {
        "title": "Identify distinct sources",
        "actors": [
          "wallet",
          "connectors"
        ],
        "text": "Wallet records a source, its owner and its serving Connector. Data requiring a different policy goes into a separate logical or physical source.",
        "check": "The synthetic Connector enforces stored source membership."
      },
      {
        "title": "Grant a consumer access",
        "actors": [
          "wallet"
        ],
        "text": "One grant covers the identified source, owner and consumer, including retained and future observations while active.",
        "check": "No individual approval is required for every observation."
      },
      {
        "title": "Append without relabelling",
        "actors": [
          "connectors",
          "wallet"
        ],
        "text": "The authorised owner adds immutable temperature observations. IDs and per-source sequence numbers support exact retrieval.",
        "check": "A request cannot move an existing observation into another source."
      },
      {
        "title": "Record the authorised release",
        "actors": [
          "connectors",
          "wallet"
        ],
        "text": "Connector checks permission and commits the consumer, source, grant and exact observation IDs/hashes before returning a page.",
        "check": "A release record is not proof of receipt or downstream use."
      },
      {
        "title": "Revoke subsequent access",
        "actors": [
          "wallet",
          "connectors"
        ],
        "text": "Revocation denies the next read. Observations remain stored and restart preserves the access decision.",
        "check": "Already delivered or authorised in-flight data cannot be recalled."
      }
    ],
    "UC-004": [
      {
        "title": "Prepare exact-source evidence",
        "actors": [
          "workflow",
          "processing",
          "connectors",
          "knowledge"
        ],
        "text": "Reuse the existing document path to extract and retain crop evidence with a source version, digest and quote.",
        "check": "Existing module implementations stay unchanged."
      },
      {
        "title": "Authorise four boundaries",
        "actors": [
          "wallet",
          "assistance",
          "model-access",
          "knowledge"
        ],
        "text": "Separate grants permit the reader’s answer, Assistance’s evidence read, model invocation and Model access’s own evidence read.",
        "check": "One permission never substitutes for another."
      },
      {
        "title": "Select the local model route",
        "actors": [
          "assistance",
          "model-access"
        ],
        "text": "Model access resolves its fixed bootstrap route and checks the installed model digest. It independently retrieves evidence; arbitrary prompts, URLs and tools are not accepted.",
        "check": "Unknown routes and non-loopback endpoints are denied before generation."
      },
      {
        "title": "Validate the model’s selection",
        "actors": [
          "model-access",
          "assistance",
          "knowledge"
        ],
        "text": "The local model returns a crop and citation ID. Farmy compares both with exact-source evidence and rejects malformed, fabricated or extra content.",
        "check": "A deterministic sentence is rendered only from a validated selection."
      },
      {
        "title": "Retain without bypassing authority",
        "actors": [
          "assistance",
          "model-access",
          "wallet"
        ],
        "text": "Replay rechecks permissions and returns a completed answer without another inference. An interrupted or uncertain model call requires an explicit new attempt.",
        "check": "Revocation blocks replay; already authorised in-flight prompts cannot be recalled."
      }
    ],
    "UC-005": [
      {
        "title": "Compose the installation",
        "actors": [
          "registry",
          "wallet",
          "connectors"
        ],
        "text": "Bootstrap explicit module instances and a dedicated monitoring certificate. Registry remains a binding-file adapter; Exchange is not deployed.",
        "check": "No automatic discovery or inferred permission."
      },
      {
        "title": "Inspect public service boundaries",
        "actors": [
          "wallet",
          "connectors",
          "processing",
          "workflow",
          "knowledge",
          "model-access",
          "assistance"
        ],
        "text": "Each receiver authenticates the monitor and checks its local summary allowlist. It reads only its own state and returns counts and six recent outcomes.",
        "check": "Ordinary readers and unconfigured monitors are denied."
      },
      {
        "title": "Visualise contents and connections",
        "actors": [
          "knowledge",
          "workflow",
          "model-access",
          "assistance"
        ],
        "text": "The browser bridge combines summaries, service versions and readiness checks. A selected module shows its actual counts, with no raw farm content.",
        "check": "Dependency arrows are declared connections, not measured traffic."
      },
      {
        "title": "Handle missing or stale information",
        "actors": [
          "wallet",
          "connectors"
        ],
        "text": "A stopped module loses its counts in the view. An unavailable bridge hides the snapshot. Old observations are marked stale rather than silently refreshed.",
        "check": "Unknown is never displayed as zero or healthy."
      }
    ],
    "UC-006": [
      {
        "title": "Preview the exact disclosure",
        "actors": [
          "wallet",
          "connectors",
          "exchange"
        ],
        "text": "Exchange reads one immutable document version under its own source grant and returns the bytes with a manifest binding recipient identity/certificate, purpose and content hash.",
        "check": "Source read is separate from export approval."
      },
      {
        "title": "Approve the bound manifest",
        "actors": [
          "wallet",
          "exchange"
        ],
        "text": "The owner approves the exact preview with a separate permission and short expiry. Changed recipient, version, content or purpose cannot reuse that approval.",
        "check": "Approval is stored authority, not a portable signed credential."
      },
      {
        "title": "Deliver and retain the receipt",
        "actors": [
          "wallet",
          "connectors",
          "exchange"
        ],
        "text": "Exchange rechecks current read, approval and delivery permissions, records an unconfirmed intent and sends to the pinned synthetic recipient. That separate process commits bytes and returns a stable receipt.",
        "check": "A lost reply leaves an uncertain outcome; it does not mean nothing was sent."
      },
      {
        "title": "Recover without another accepted copy",
        "actors": [
          "exchange"
        ],
        "text": "After a restart, an authorised retry sends the same disclosure ID and bytes. The recipient returns its existing receipt. Revoked grants block retries; they cannot recall copies already delivered.",
        "check": "Proven only against this explicit recipient deduplication contract."
      }
    ],
    "UC-008": [
      {
        "title": "Bind and authorise separately",
        "actors": [
          "registry",
          "wallet",
          "workflow"
        ],
        "text": "Select Knowledge A or B with a revisioned binding. Check the authenticated peer descriptor; issue separate transfer, index and query grants for each instance.",
        "check": "A binding selects a service; it does not grant access."
      },
      {
        "title": "Run two private indexes",
        "actors": [
          "workflow",
          "processing",
          "knowledge"
        ],
        "text": "Index the same accepted proposal into two Knowledge instances through public APIs. Their exact-source evidence agrees; neither reads the other’s store.",
        "check": "A query grant for A is rejected by B."
      },
      {
        "title": "Replace and rebuild deliberately",
        "actors": [
          "registry",
          "workflow",
          "processing",
          "knowledge"
        ],
        "text": "Keep A available. Stop B, retain its original store and start the journal implementation with empty private state. Advance the binding revision and start a new authorised rebuild job.",
        "check": "An old job key cannot silently continue against a changed binding."
      },
      {
        "title": "Verify the boundary again",
        "actors": [
          "knowledge",
          "wallet"
        ],
        "text": "Compare evidence after rebuild and restart. Revoke B’s query grant; A remains usable under its own grant. Both fail closed when Wallet is unavailable.",
        "check": "Local domain-provider substitution only; shared transport, no generic migration."
      }
    ],
    "UC-009": [
      {
        "title": "Connect a collectively governed source",
        "actors": [
          "wallet",
          "connectors"
        ],
        "text": "The folder can be on this laptop and still remain outside the Wallet. One source/owner/consumer grant covers both synthetic email exports.",
        "check": "A source grant covers the configured root, not the whole device."
      },
      {
        "title": "Admit an exact managed copy",
        "actors": [
          "wallet",
          "connectors"
        ],
        "text": "The owner selects one email and its digest. Connector stores immutable bytes; Wallet records individual identity, provenance, classification and a reader list within the inherited ceiling.",
        "check": "Admission is separate from signing a claim or issuing permission to read."
      },
      {
        "title": "Read under a separate item grant",
        "actors": [
          "wallet",
          "connectors"
        ],
        "text": "The item reader needs its own exact-version grant. A source grant cannot open the managed copy; an item grant cannot open the folder.",
        "check": "Physical location does not decide Wallet membership."
      },
      {
        "title": "Keep revocation boundaries explicit",
        "actors": [
          "wallet",
          "connectors"
        ],
        "text": "Source revocation stops future source reads and new admissions using that grant. The retained copy has its own revocation. Changing or deleting the original does not change the copy.",
        "check": "Previously delivered bytes cannot be recalled. Wallet outage blocks new reads."
      }
    ],
    "UC-010": [
      {
        "title": "Preview and keep one document",
        "actors": [
          "connectors",
          "wallet"
        ],
        "text": "In the owner interface, browse the synthetic connected folder. Preview a document, choose its permitted reader ceiling and add an immutable managed copy.",
        "check": "Real API calls. Adding to the Wallet does not grant the consumer access."
      },
      {
        "title": "Try the consumer view before granting",
        "actors": [
          "wallet",
          "connectors"
        ],
        "text": "Open the separate demo consumer view. Its generic test entry exposes no document metadata. Try opening it: Wallet denies the read.",
        "check": "The consumer token cannot invoke owner actions or browse the source."
      },
      {
        "title": "Grant and read the actual bytes",
        "actors": [
          "wallet",
          "connectors"
        ],
        "text": "The owner issues a consumer grant. Retrying the consumer read now returns the exact managed copy. The owner can separately inspect provenance and open that copy.",
        "check": "Private owner-only items reject consumer grants."
      },
      {
        "title": "Revoke, retry and observe denial",
        "actors": [
          "wallet",
          "connectors"
        ],
        "text": "Revoke in the owner view. The next consumer read is denied. Lost mutation replies offer the same request for reconciliation instead of issuing another permission.",
        "check": "Already delivered bytes cannot be recalled. The UI clears its read display before every new attempt."
      }
    ]
  },
  "method": [
    [
      "Frame",
      "One actor, one useful outcome, one synthetic fixture.",
      "Write an observable acceptance case."
    ],
    [
      "Map",
      "Assign capability ownership and predict which modules should change.",
      "Keep domain rules inside their responsible module."
    ],
    [
      "Specify",
      "Define only the contracts and permission semantics this case needs.",
      "Separate public interfaces from private storage."
    ],
    [
      "Build",
      "Connect the thin path across real service boundaries.",
      "Include authentication, state and failure handling."
    ],
    [
      "Challenge",
      "Exercise denial, duplication, failure, restart and prior slices.",
      "Passing the happy path alone is insufficient."
    ],
    [
      "Retain",
      "Keep the demo, regression tests and a reviewable revision.",
      "Update repository docs, dashboard, evidence and the next queue for every slice."
    ],
    [
      "Choose",
      "Select the smallest next outcome from what we learned.",
      "The queue can change; this is not a fixed schedule."
    ]
  ],
  "foundationTests": 19,
  "concepts": [
    {
      "id": "plasticity",
      "title": "AI-enabled plasticity",
      "subtitle": "Learn how to connect, not only what the data says.",
      "text": "AI can analyse contents, build embeddings and propose ontologies. It can also generate a source mapping or adapter. A module with a suitable extension mechanism can admit that interface while its host stays running.",
      "steps": [
        "Describe a permitted source",
        "Generate mapping or adapter",
        "Test and admit under policy",
        "Activate a versioned extension"
      ],
      "families": "Connectors · Processing · Assistance · Model access · Registry · Workflow · Wallet",
      "boundary": "No host redeployment where the runtime already supports the extension. Generated code still needs a version, bounded privileges and rollback; it cannot authorise itself.",
      "today": "Today: hand-written connectors and one checked local-model answer. Runtime-generated interfaces are not implemented."
    },
    {
      "id": "data-spaces",
      "title": "Source-governed data spaces",
      "subtitle": "Independent authority. Common participation rules.",
      "text": "Each source retains its own owner, consumer permissions and disclosure rules. Farmers, laboratories and other participants can cooperate under shared governance without centralising all data or all authority.",
      "steps": [
        "Source A keeps its policy",
        "Source B keeps its policy",
        "Common rules apply to participants",
        "Consumer meets every applicable rule"
      ],
      "families": "Wallet · Connectors · Exchange, with governance dependencies",
      "boundary": "Membership is not read permission. Combining sources requires authority from each and defined conditions for the result. After delivery, consumer accountability still matters.",
      "today": "Today: source/owner/consumer grants in one local authority. Federation between independent authorities is not implemented."
    },
    {
      "id": "trust-networks",
      "title": "Wallet-based trust networks",
      "subtitle": "Owners and contributors leave assessable evidence.",
      "text": "An owner signs a scoped declaration. A laboratory, reviewer or other contributor can sign its own certification, confirmation or marking. Holders present those claims; verifiers assess them and may issue further referenced statements.",
      "steps": [
        "Issuer signs a scoped claim",
        "Holder retains and presents it",
        "Verifier checks evidence and trust",
        "New claim can reference prior claims"
      ],
      "families": "Wallet + credential/key adapters · Exchange · Knowledge",
      "boundary": "A signature provides attribution and integrity, not automatic truth, conclusive ownership or access permission. Trust is assessed at each link; it is not automatically inherited.",
      "today": "Today: resource provenance and authenticated service access. Signed owner/contributor credentials and their trust networks are not implemented."
    }
  ]
};
