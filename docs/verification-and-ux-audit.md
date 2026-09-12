# Verification and reader UX audit

Date: 2026-09-12. Scope: the Book 3 reader companion, not an official or complete Iron Tangle map.

## Baseline

Audited `index.html` blob: `cf8be03320691f1bc4671ee29347c5f585c4e4c3`.
Audited `data.json` blob: `f4b01721907635ea512d172e764f783c28d170c0`.

The current dataset contains 39 location records, 29 route/service roster entries, 23 edges, one special-access relation, and 44 crawler checkpoint reports. Only one location record is tagged primary-checked. These are database counts, not a claim about the complete number of locations in the novel.

## Evidence findings and next sources

| Claim or lead | Source and locator | Disposition |
| --- | --- | --- |
| The opening party is aboard the Red Line, car 20, approaching Sirin station 81. | [Author's authorized preview](https://mattdinniman.com/books/the-dungeon-anarchists-cookbook/), audio-transcript opening. | Primary-source checked. Do not place the party on the station platform. Car 20 is a potential enrichment; no new app data was published in this audit. |
| Katia's explanation of the network's shape has a specific primary-text retrieval lead. | [Fan chapter index](https://www.dccdatabase.com/wiki/dungeon_anarchist's_cookbook_(book)/), chapter 30; chapter 31 is a follow-on topology lead. | Secondary locator only. Retrieve the actual passages before modeling their topology or first-reveal boundaries. This does not establish when every earlier drawing was made. |
| Nightmare Express has a source-listed five-stop circuit with repeated numbers. | [Fan service entry](https://www.dccdatabase.com/wiki/nightmare_express/), citing chapter 14. | Preserve distinct physical IDs and existing editorial aliases; do not promote to primary-verified until checked in the novel. |
| A trainyard can be reported, observed through a portal, or physically visited. | [Fan yard entry](https://www.dccdatabase.com/wiki/train_yard/), chapter references. | These are separate evidence states. Do not infer presence, transfers, or a common physical station from the number 10. |

For every new factual claim, record: claim ID; physical station/service IDs; relation; book edition, chapter and scene; optional edition-specific page or audio time; first reader revelation; event time; evidence tier; uncertainty; and integration status. Diagram coordinates are presentation choices, not geographical evidence.

Do not publish novel scans, full text, access tokens, or private reading notes in this public repository. Use paraphrases and source locators.

## Accuracy guardrail

Eleven current edges have `kind: sequence`, meaning inferred number order. The current renderer nevertheless draws direction chevrons on qualifying segments regardless of edge kind, and the detail panel places these edges under 'Where this service goes'. This can imply operational direction that the evidence does not establish.

Issue #2 separates membership, adjacency, circuit order, observed journeys, and operating direction. Unknown links must stay unknown. This audit has not changed the rendering or asserted new topology.

## UX measurements

A local Playwright inspection used the exact production-source HTML blob above:

- 1600 x 1050 desktop: 18 visible HTML buttons in the default state, excluding selects and SVG station targets.
- 390 x 844 mobile: map top approximately 486 CSS pixels; search field top approximately 1221 CSS pixels, below the map and initial viewport.
- Fit changes the viewport but leaves a typed search and selected route active.
- The 83(b) alias remains searchable and distinct.
- No horizontal mobile overflow or uncaught browser exceptions was observed during this limited inspection.

Nine targeted audit assertions passed. They establish these observed behaviors, not exhaustive UX quality or literary accuracy.

## Prioritized work

1. #2: stop presenting inferred numerical sequences as verified train directions.
2. #3: one-click Reset view, preserving reading position, selected crawler, and notes. Start from chapter 1 is a separate confirmed action.
3. #4 and #5: map-first layout, global search, progressive disclosure, and a mobile bottom sheet.
4. #1 and #6: primary-text claim ledger and scene-aware first-revelation/spoiler boundaries; these can proceed alongside UX work.
5. #7: a contextual crawler/train journey card, displaying the next documented point rather than guessing the next stop.
6. #8: canonical-data workflow, structural/browser regression checks, durable sharing, and reviewed reader corrections.

The eight issues are implementation work items, not completed UI features.

## Comparable product patterns

- [Google Maps layers and transit details](https://support.google.com/maps/answer/3092439?hl=en&co=GENIE.Platform%3DDesktop): group optional overlays and reveal details after a selection.
- [ArcGIS Experience Builder map widget](https://doc.arcgis.com/en/experience-builder/latest/configure-widgets/map-widget.htm): distinguish Home, Locate, and extent history; adapt tools/pop-ups to small screens.
- [Citymapper GO](https://citymapper.com/news/517/go-your-personal-trip-assistant): show contextual journey information for the current step. The atlas must not imply live position, ETA, or guaranteed operational routing.
- [WCAG 2.2 target size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html): test target size and spacing. A 44 x 44 CSS-pixel primary-control goal is a product choice, not a blanket AA requirement.

## Structural tooling implemented

`scripts/validate_data.py` checks record IDs, references, chapter types, coordinate pairs, source tiers, event-location conflicts, four published duplicate-alias contracts, and equality of `data.json` with the JSON embedded in `index.html`.

`tests/test_validate_data.py` supplies 13 unit tests. All 13 passed locally against the audited data. The validator reported no structural errors and explicitly warned that primary verification is incomplete and inferred sequences are not verified directions.

Run with Python 3.10 or later, from the repository root:

```sh
python scripts/validate_data.py
python -m unittest discover -s tests -v
```

These checks are available to run; a CI deployment gate is not configured by these files. Neither passing unit tests nor consistent JSON establishes book accuracy or spoiler safety. The live map UI and factual dataset are unchanged by these tooling/documentation additions.
