# Working method: use case to running increment

Status: draft for adoption. Builds on the accepted MVP approach and module families. UC-001, UC-002, UC-003 and UC-004 provide runnable synthetic macOS increments; broader deployment remains future work.

## Unit of delivery

Deliver one small, useful end-to-end outcome at a time. A vertical increment includes the necessary client interaction, module behaviour, public contracts, security checks, persistence, verification and a reproducible way to run it. It may touch several families; it does not complete any whole family before the others begin.

“In one go” means carrying an agreed slice through to a runnable demonstration within the same delivery cycle, not attempting the whole ecosystem in one pass. A working command-line interaction counts initially. Deployment here means running the increment on the chosen development target; it does not imply production readiness or support for every operating system.

Keep one active implementation slice and a short ordered queue. Split a slice when it introduces too many independent decisions, cannot produce a clear demonstration, or repeatedly stalls behind unrelated dependencies. Do not invent calendar commitments before the first completed slice gives us evidence of effort.

## The delivery loop

| Step | Work | Exit evidence |
| --- | --- | --- |
| 1. Frame | State the actor, outcome, synthetic example, limits and why this case matters. | Small use-case card with observable success, denial and recovery expectations |
| 2. Map | Map steps to existing capabilities/modules; identify missing semantics and actual trust/data boundaries. | Short interaction sketch and expected source/configuration changes; no full-system redesign |
| 3. Decide and specify | Resolve only decisions needed by this slice; define the narrow contract, fixture and acceptance checks. | Agreed assumptions, versioned contract draft and executable test plan; ADR only for a significant lasting decision |
| 4. Build vertically | Implement the thinnest real path, including required authentication/authorisation, persistence and errors. | Real modules communicating over the required boundary, not only mocks |
| 5. Run and challenge | Run from a clean setup; exercise success, denied access, restart/failure and previous completed cases. | Reproducible commands, actual results and known limitations |
| 6. Review and retain | Demonstrate the outcome, compare module impact with expectation, correct defects and update docs/recipes. | Reviewable commit or PR, evidence tied to a revision and a runnable development baseline |
| 7. Choose the next change | Record what was learned and select the smallest useful extension or correction. | Updated card/backlog; earlier working cases remain regression checks |

Design, tests and code can iterate within the loop. These are not approval gates requiring the maintainer to authorise every routine step. Continue autonomously within agreed scope; ask when a decision changes product intent, grants significant new access, incurs costs or accepts a material tradeoff. Present the concrete options and recommendation when input is needed.

## Use-case card

Keep each card in its solution directory, close to the composition it tests. It should contain:

- Identifier, actor, desired outcome, status and responsible person when assigned.
- Synthetic input and observable expected result; included and excluded behaviour.
- Families/instances involved, public contract changes, data movement and required authority.
- Success, denial, failure/restart and change-locality acceptance cases.
- Required decisions/dependencies and the simplest run/demo path.
- When completed: source revision, tested environment, exact commands/results, migration notes and next learning.

Use a small status set: proposed, ready, in progress, blocked, done. “Ready” means the slice is understood and execution can begin; it does not mean its code exists. Record a real blocker and a next action rather than leaving a stalled slice ambiguously active. The first implemented card is [UC-001](../solutions/core/use-cases/UC-001-controlled-memory.md).

## Definition of done for an increment

A slice is done only when its observable outcome runs against real components on the declared target, its acceptance checks pass, and another contributor can reproduce the result from documented prerequisites. Authentication and authorisation tests must exercise the receiver, not just a UI hiding a button or a fabricated success response.

Keep essential evidence proportionate:

- Exact source revision and tested OS/runtime versions; real startup, demo, test and shutdown commands.
- Declared configuration and credential bootstrap; no secrets or farm records committed.
- The happy path, relevant denied action and meaningful failure/recovery behaviour for the changed boundary.
- Owned state/migration behaviour and regression results for affected earlier cases.
- Updated contract/implementation/solution status and known unsupported features or environments.
- Updated [project dashboard](../dashboard/README.md): slice outcome, evidence baseline, counts, family coverage, data-flow diagrams and next queue. Dashboard and repository documentation updates are required for every completed slice, in the same delivery cycle.

Mocks can help development, but a mocked external dependency cannot establish real-provider compatibility. Synthetic data is appropriate for the MVP; it does not justify omitting access checks. Persistent development storage must state its protection and limits; do not advertise suitability for private data until the required key/storage controls are verified.

## Continuous modularity checks

Before coding, predict which implementation, contract, configuration and migration should change. Afterward, record what actually changed. Look for unnecessary changes to Wallet or Workflow when adding a provider, parser or algorithm.

Keep dependencies pinned sufficiently to show that unaffected modules still run unchanged. Add independent-provider substitution once the first relevant contract works; do not defer all replacement evidence until the full platform is built. The [change scenarios](module-architecture.md) guide these checks.

Common envelopes contain identity/version/provenance and execution semantics, not every domain field. Extend typed capability payloads explicitly. A new capability can legitimately change multiple consumers; report that honestly. Do not disguise new semantics as an arbitrary JSON parameter to preserve an illusion of compatibility.

Avoid speculative infrastructure: no universal plugin engine, marketplace, graphical workflow builder or support for every platform before a case requires it. Extract optional shared helpers after actual repeated needs appear; do not force all implementations to depend on one internal library.

## Continuity, releases and regression

Maintain a runnable development baseline once the first slice exists. Work in focused commits or a short-lived branch/PR; include contracts, implementation, tests and run instructions in the same coherent change. Do not merge a broken increment and call it complete. If the baseline breaks, restore it before starting another feature.

Each completed use case becomes a regression scenario. Run affected contract/security checks and the small end-to-end smoke suite on subsequent changes; broaden testing when a shared contract, migration or security boundary changes. Add automated repository checks with the first executable slice rather than building a complex CI system in advance.

Preserve data and source identities across supported upgrades. Breaking changes need explicit contract/version negotiation and migration or rebuild; early 0.x status is not permission to silently destroy state. Record unsupported downgrade paths. Tag a reproducible development milestone when useful, but do not describe it as a production or all-platform release.

Keep separate module, contract, solution and profile versions. Package additional targets after the path works: verify Windows, Linux and cloud profiles individually, and exercise a mixed-host topology. Do not conflate a local Mac demonstration with cloud, hardware or cross-platform validation. Scaleway remains the first cloud target when that work becomes justified.

## Collaboration rhythm

At slice start, state the outcome, scope and material assumptions. During work, report discoveries, failures and decisions rather than a stream of routine actions. At completion, show what runs, what was tested, remaining limits and the proposed next increment.

The maintainer steers priorities and product/security tradeoffs. Implementation work includes updating the small amount of documentation that changed; avoid producing another layer of architecture documents instead of a running slice. Review learning after each demo, with no mandatory ceremony or fixed sprint length.
