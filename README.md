# Iron Tangle Atlas - reader 0.3.0 candidate

**Status: implemented and locally tested; NOT committed or published.**

The live Netlify site remains on the preceding release. Two unreferenced GitHub blobs were accepted, but the stylesheet write was blocked by the tool's safety-status check before a release commit was created. This package preserves the work for review. It is not evidence of a successful deployment or a GitHub permission denial.

Tracked at: https://github.com/rwxford/iron-tangle-atlas/issues/9

## Review the new app

The new reader's source is in `web/`. Run the dependency-free build from this directory with Python 3.10+ and Node 22:

```sh
python3 scripts/build.py
```

The build runs structural and reader-logic checks and writes the compiled application to `dist/`. A static web server can serve `dist/` for local review. The app fetches `data.json`, so a file attachment preview is not an interactive web server.

**The root `index.html` is the legacy 0.2 standalone archive**, kept for existing data-parity tests. It is not the new reader entry point. The build stages `web/reader.html` as `dist/index.html`.

`netlify.toml` describes the intended build and publish configuration. No configuration in this bundle has been committed or activated by this release attempt. Resolve the blocked write through the normal authorized workflow before resuming publication.

## Main changes

- Reset view with Undo, retaining the reading point, selected crawler/report, notes and bookmarks.
- Separate confirmed restart from chapter 1 and viewport-only recenter.
- Map-first interface, global search above the map and one responsive details/results panel.
- Stable duplicate-number aliases, number-aware search and sound-alike matching for fulvis/fulvous and mendaro/mindaro.
- Beginning-versus-finished chapter controls, gated reference mode and compatibility with older shared links.
- No direction arrows on general network edges. Inferred number-order guides are off by default; a selected source-described movement may display a contextual arrow.
- Compact last-reported journey card, previous/next available reports, source details and reviewed public correction drafts.
- Canonical runtime `data.json`, build-time tests, release metadata and an evidence inventory with explicit unknown revelation fields.

## Validation and its limits

The local build passed 13 structural tests and 25 Node reader-logic tests. Another 34 Chromium DOM checks passed at desktop, phone and tablet viewport sizes. The browser checks use explicit in-memory data-fetch, storage and history fixtures because browser navigation is restricted in this environment. They are not live-host, real-storage persistence, Safari, real-touch-device or screen-reader tests.

Results are in `tests/build-run.log`, `tests/browser-results.json` and `tests/browser-run.log`. The screenshot previews are `tests/desktop-0.3.png` and `tests/mobile-0.3.png`.

## Evidence status

The factual dataset is unchanged: 39 location records, 23 edges and 44 crawler reports. Most records are secondary fan-index entries. Only the opening station context has primary-excerpt verification. No new station facts, trainyard affiliations, Katia drawing geometry or first-revelation scene offsets were invented.

The reader remains an incomplete research alpha, **not a definitive book map or a strictly spoiler-safe companion**. Primary-text verification and scene-level disclosure work remain open. The user does not need to purchase or transcribe another edition to review this UI work.

No full novel, book scans, credentials, personal notes, account system or application analytics are included.
