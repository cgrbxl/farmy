# UC-005 — Read-only operational dashboard

Status: done for synthetic macOS 26.6.2 arm64 / Python 3.14.6. Evidence revision: the commit implementing UC-005 (linked after verification).

Actor: the local installation operator wants to see which modules exist, what categories of state they hold and whether checks succeed. The owner explicitly bootstraps a dedicated monitoring identity; ordinary readers receive no metadata rights.

Outcome: one browser view of eight real service instances, a Registry adapter and undeployed Exchange, with declared dependencies, authenticated service checks, authorised counts, latest-six activity and honest stale/unavailable states. No file names, source values, model text or credentials are disclosed. Closing the browser or independently stopping its bridge does not stop modules.

Expected and actual module impact: all eight implementations gain their own metadata-summary method; shared optional transport supplies allowlisted GET dispatch and response validation, and a helper formats service-local queries. This is a deliberate cross-cutting observability addition, not justification for a central shared database. No domain operation, table schema or previous contract version changes. Two static non-service families remain labelled without invented checks. UC-004 bootstrap gains optional composition reuse.

Evidence: nine new acceptance tests, 55 prior tests and five demos, including the real local-model demo. Tests cover contents, access denial, no monitor mutations, browser-origin/token controls, no file traversal, outage recovery, summary-access removal, refreshed counts and independent bridge shutdown. The operational UI is inspected with real seeded source/evidence/answer state. Reproduction and limits are in the [solution README](../uc005/README.md).

The intended first view is metadata and counts, not raw-content browsing. Service dependency edges are declared, not observed packet flows; service readiness does not prove model-runtime availability. Retained grants are not active-grant counts. Cross-service counts are not an atomic snapshot. Windows, Linux and cloud packaging are not claimed.

Queue change: this slice precedes controlled export at the maintainer's request. The next outcome remains a synthetic disclosure bound to exact content and recipient with independent export permission. Every completed slice must continue updating the project dashboard, runtime instructions and affected contracts/documentation.
