# Reader 0.3.0 - implementation notes

## Publication status

Released from the public repository. GitHub issue #9 retains the original handoff and verification history.

## Issue work

| Issue | Candidate implementation | Still open |
| --- | --- | --- |
| #1 Primary evidence | Derived inventory of 106 node/edge/report records. Unknown first revelation explicitly remains null. | Primary text, Katia drawings, station and trainyard claim audit. |
| #2 Direction semantics | General network paths have no arrows. Inferred number-order guides are hidden by default. Only a selected recorded movement with a source-described segment can have an arrow. | Full evidence-level adjacency, direction and journey audit. |
| #3 Reset | Persistent Reset view, Undo, confirmed restart and separate recenter. Notes, bookmarks and reader position retained. | Production verification. |
| #4 Layout | Map-first desktop and one responsive mobile sheet. Search and reset above the map; secondary tools under More. | Real-device Safari, assistive-technology review and optional full-screen mode. |
| #5 Search | Global station/service/yard/report results; stable duplicate aliases, number-aware queries, keyboard selection and sound-alike spellings. | Production and broader search-corpus validation. |
| #6 Spoilers | Beginning/finished chapter control, filtered crawler choices, no automatic reference-mode restoration, gated shared views. | Per-claim first-revelation and scene cutoffs; no strict spoiler-safety claim. |
| #7 Journey card | Last report, vehicle/service, reported destination and next indexed report distinguished; previous/next permitted reports. | Primary-source presence/observation distinctions and journey continuity. |
| #8 Reliability | Runtime canonical data.json, test-gated static build, release metadata and explicit public correction drafts. | Legacy archive cleanup, full end-to-end CI and live browser tests, offline support. |

## Reader behavior

Reset view clears the search, selected route/station, open panels and optional guide layer, then refits the permitted map. It preserves chapter, beginning/finished phase, mode, crawler, selected report, notes and saved views. Undo restores the previous exploration state. Start from chapter 1 is separate and asks for confirmation. Recenter changes the viewport only.

Search accepts examples such as `83(b)`, `283(a)`, `yellow 83` and `yard E` without requiring a tab. `mendaro` and `fulvis` match the canonical spellings Mindaro and Fulvous. The corrections do not change factual source data.

The beginning-of-chapter option excludes same-chapter secondary entries, with the authorized opening excerpt retained. Selecting an earlier crawler report does not change the chapter disclosure cutoff; the card explicitly warns that this does not create within-chapter spoiler protection. Reference mode remains an explicit choice. Older 0.2 URLs preserve their original through-chapter semantics.

No general path arrow implies a timetable or normal operating direction. A reported reversal may have a purple movement arrow only when the selected recorded segment is represented by source-described network data. Inferred number-order guides are opt-in dotted lines, not known physical connections.

## Build and data

The new app fetches `data.json` directly. The root legacy `index.html` is not staged into production; it remains available for existing embedded-data parity tests. `scripts/build.py` stages `web/reader.html` as the new index, runs tests before staging and copies only runtime assets into `dist`.

`release.json` reads the commit from Netlify's `COMMIT_REF`. In this local package it says `local-development`, not a deployed commit. `evidence-ledger.json` is a derived audit inventory, not primary-source verification. It records unavailable first-revelation claims as null.

## Checks performed

- 13 structural tests passed.
- 25 Node reader-logic tests passed.
- 34 Chromium DOM integration checks passed, including reset/undo, note exclusion, duplicate aliases, reference gates, contextual reversal, keyboard selection and phone/tablet overflow.

Chromium could not navigate to a server in this environment. DOM checks therefore use the exact source assets in an in-memory document with explicit dataset-fetch, storage and URL-history fixtures. This is not live-host verification or proof of actual persistence, iOS Safari behavior, touch-device behavior or screen-reader accessibility.

## Release prerequisite

Primary-source auditing, strict spoiler verification and broader device/accessibility testing remain open.
