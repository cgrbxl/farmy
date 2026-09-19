# Farmy visual project guide

An interactive explanation of Farmy's purpose, nine module families, capabilities, security boundaries, data flows and incremental delivery method. The progress view maps the three runnable slices to the wider architecture and distinguishes demonstrated behaviour from planned work.

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

The initial evidence baseline is commit `9cfa481`: three synthetic macOS slices, 19 foundation tests and 26 runtime acceptance tests. Passing slices do not imply that a whole family is complete, that production deployment is ready, or that other operating systems have been verified.

After accepting another slice:

1. Update the slice, family participation, walkthrough and delivery queue in [data.js](data.js).
2. Update the snapshot date and evidence revision in that file.
3. Reconcile summary counts, test labels and deployment statements in [index.html](index.html), and the foundation test count in [app.js](app.js).
4. Keep the root README and delivery backlog consistent. Use public repository evidence; private feedback is not dashboard content.
5. Check module selection, flow navigation, method stages, command copying and mobile navigation in a browser. Check both wide and narrow layouts and documentation links.

The initial dashboard was visually checked at desktop and mobile widths, with its interactive controls exercised. Its original SVG illustrations are in [assets](assets/), and its layout is defined in [styles.css](styles.css).

All dashboard files use the repository's [Apache-2.0 licence](../LICENSE).
