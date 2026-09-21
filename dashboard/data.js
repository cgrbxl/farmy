/* Curated project snapshot. Update with every completed slice; exclude private feedback. */
const FARMY = {
  "date": "21 September 2026",
  "revision": "47ff0f2",
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
      "now": "Document/version grants and source/owner/consumer permissions. Additive state upgrades are tested.",
      "next": "Owner and contributor claims, explicit issuer/holder/verifier trust policies and complementary credential adapters.",
      "slices": [
        "UC-001",
        "UC-002",
        "UC-003",
        "UC-004",
        "UC-005"
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
      "now": "A revisioned binding-file adapter supports explicit local composition. No catalogue server.",
      "next": "Discovery, richer admission checks and demonstrated provider substitution.",
      "slices": [
        "UC-001",
        "UC-002",
        "UC-003",
        "UC-004",
        "UC-005"
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
      "now": "A fixed extract/index workflow survives restart and resumes on owner retry.",
      "next": "Additional reviewed workflows, scheduling and cancellation when needed.",
      "slices": [
        "UC-002",
        "UC-004",
        "UC-005"
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
      "now": "Local Folder snapshots and a separate Synthetic Sensor implementation.",
      "next": "Real providers and admitted AI-generated source mappings or isolated adapters, without host redeployment where supported.",
      "slices": [
        "UC-001",
        "UC-002",
        "UC-003",
        "UC-004",
        "UC-005"
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
        "UC-005"
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
      "now": "One derived crop-field entry per exact source version; online checks gate cached evidence.",
      "next": "Richer retrieval, index removal/rebuild and independent alternatives.",
      "slices": [
        "UC-002",
        "UC-004",
        "UC-005"
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
      "status": "planned",
      "subtitle": "Approve the content, recipient and purpose.",
      "owns": "Disclosure manifests, delivery attempts and receipt uncertainty.",
      "does": "Prepares and delivers exact authorised disclosures across a boundary.",
      "boundary": "Not a generic computation engine or equipment controller. Delivered copies cannot reliably be recalled.",
      "now": "Family boundary and requirements documented; no implementation.",
      "next": "Exact-content disclosure first; later governed data-space exchange and authorised credential presentations.",
      "slices": [],
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
      "scope": "Synthetic local documents"
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
      "scope": "One field in a synthetic text report"
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
      "scope": "Synthetic temperature observations"
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
      "scope": "One question · synthetic crop evidence · local Qwen"
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
      "scope": "Read-only metadata · synthetic local installation"
    }
  ],
  "queue": [
    {
      "title": "Controlled disclosure",
      "families": [
        "exchange"
      ],
      "detail": "Preview exact content and recipient; require separate export authority."
    },
    {
      "title": "A real S3 source",
      "families": [
        "connectors"
      ],
      "detail": "Reuse the working path and test actual provider semantics."
    },
    {
      "title": "Prove replacement",
      "families": [
        "knowledge",
        "processing",
        "registry"
      ],
      "detail": "Run multiple instances and an independent alternative, with declared migration."
    },
    {
      "title": "Package each environment",
      "families": [],
      "detail": "Verify laptop and Kubernetes delivery one target at a time; Scaleway is first for cloud."
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
