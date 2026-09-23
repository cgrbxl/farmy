# Farmy visual project guide

An interactive explanation of Farmy's purpose, nine module families, capabilities, security boundaries, data flows and incremental delivery method. The progress view maps the seven runnable slices to the wider architecture and distinguishes demonstrated behaviour from planned work.

## Open it

Open [index.html](index.html) in a modern browser from your local checkout. No installation, build or running Farmy services are required. All illustrations, styles and scripts are included locally.

Alternatively, from the repository root:

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory dashboard
```

Then visit <http://127.0.0.1:8765>. On Windows, `py` can replace `python3` if that is your Python launcher.

When served over HTTP, documentation links open the public GitHub repository. When opened as a local file, they point into the adjacent checkout. GitHub's file viewer displays HTML source; this change does not configure a public website or GitHub Pages.

## Content and maintenance

This is a curated documentation snapshot, not an operational control panel or live monitoring system. It calls no Farmy services and includes no external libraries, analytics or remotely loaded assets.

The current evidence baseline is the UC-008 implementation revision linked in the dashboard: seven synthetic macOS slices, 19 foundation tests and 72 runtime acceptance tests. UC-004 also has a real local Qwen/Ollama demonstration. Passing slices do not imply that a whole family is complete, that production deployment is ready, or that other operating systems have been verified.

After accepting another slice:

1. Update the slice, family participation, walkthrough and delivery queue in [data.js](data.js).
2. Update the snapshot date and evidence revision in that file.
3. Counts and test legends derive from [data.js](data.js). Reconcile narrative and deployment statements in [index.html](index.html), and update both architectural SVG diagrams when a route changes.
4. Keep the root README and delivery backlog consistent. Use public repository evidence; private feedback is not dashboard content.
5. Check module selection, flow navigation, method stages, command copying and mobile navigation in a browser. Check both wide and narrow layouts and documentation links.

The initial dashboard was visually checked at desktop and mobile widths, with its interactive controls exercised. Its original SVG illustrations are in [assets](assets/), and its layout is defined in [styles.css](styles.css).

All dashboard files use the repository's [Apache-2.0 licence](../LICENSE).

## Live operational view

The separate [UC-005 dashboard](../solutions/operations/uc005/README.md) is a real read-only installation monitor. Its files are under `dashboard/live/` and must be served by their authenticated local bridge. It is not a standalone static HTML guide. Launch it using the documented runner and its printed access link; it prefers port 8766 and automatically chooses a free port if that port is occupied. Always use the printed access link.

The Core concepts section explains [AI-enabled plasticity, source-governed data spaces and wallet trust networks](../docs/core-concepts.md). Its interactive cards and diagram describe accepted direction, explicitly separated from the seven implemented slices and their recorded test baseline.

The progress section also shows a separate [future interactive backlog](../docs/interactive-modules.md): AI profile configuration, signed issuance, holder presentation, external verification and later family interactions. These cards do not change delivered slice/test counts or the next queued outcome.

[UC-006 launch](../solutions/disclosure/uc006/README.md) reuses the live monitor for the three-service disclosure composition. Inventory positions and undeployed family labels derive from the active snapshot; the recipient is listed as a dependency outside the monitored inventory. The project guide includes the UC-006 flow and exact disclosure diagram.

UC-007 appears separately as in progress: its 11 local HTTP-double checks and runnable preview are not included in the seven completed slice cards or their 91-test baseline. Real Scaleway validation is required before promotion. Use the optional verification flag documented in the S3 solution to run the combined 102 checks.

[UC-008 launch](../solutions/replacement/uc008/README.md) shows six module instances, including two separate Knowledge nodes and the replacement implementation. The static guide includes a replacement/rebuild diagram and walkthrough. Its seven delivered slices are UC-001–006 and UC-008; pending UC-007 is not counted.

## Phone solution mockup

The **Phone solution** section embeds [Las Tres Encinas](mock/index.html), a fictional future experience with optional module tags. All nine family explanations distinguish today's tested scope from simulated behavior. The original supplied HTML is retained under `docs/mock/`; regenerate the annotated copy with `python3 scripts/build_phone_mock.py`. See the [mapping and design observations](../docs/mock/README.md). Mockup work does not increase the delivered slice/test counts.

Public phone preview: [Las Tres Encinas](https://farmy-las-tres-encinas.cgrbxl.chatgpt.site). The dashboard embeds its local copy so a checkout remains self-contained.
