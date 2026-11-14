# Changelog

## Repository handoff - 2026-11-14

Published the 1.5.0 source tree, tests, licensed dataset originals/derivatives and OSM snapshots in Data-Collection. Added repository README/agent rules, checksum inventory and standard-library bootstrap/test commands. Large CSV and normalization input are stored as lossless gzip; no Git LFS is required. NFI originals and an unlicensed tooling fixture are excluded; Dryad remains metadata-only. Analysis, viewer code, health values and component semantics are unchanged.

## daily-linked/1.5.0 - 2026-11-14 · analysis routine-change/2.0.0

Presentation remains `within-ui/3.0.0`; export contract is additive `1.2.0`. Component contracts and fusion semantics are unchanged.

- Daily pattern layer: isolated harder days are noted; repeated high daily signals produce watch/sustained states; anchor-relative level plus Theil–Sen/Mann–Kendall trend across two domains detects slow drift. Missing/undercovered days abstain. The original selected-window score fields retain their meanings.
- Frozen robust anchor plus a small bounded EWMA, trained only on earlier eligible days. Exports expose persistence, drift, baseline used, next-day effective baseline and effective alert settings. Confirmed context can suppress non-mood Path A evidence; drift remains visible. Thresholds are demo heuristics, not validated clinical alerts.
- Personal orb and care cards now follow pattern states. Clinical evidence displays engine counts and drift rows; the timeline retains daily signals and adds a state band. An input-keyed analysis cache avoids recomputing trends when only the selected date/view changes.
- Leaflet host now has its own stacking context, keeping panes/controls below navigation and overlays. Vendored Leaflet is untouched.
- Eleven distinct Helsinki neighbourhoods with personal places and OSM-edge routes. Existing ten profiles' health, dates, phases, contexts and missingness are preserved by hashes. New Mila story reaches drift on Day 100 without an earlier sustained flag. Its tuned rates and seed are documented; it is generated demonstration data.
- All PSYCHE-D rows and StudentLife assets remain unchanged. Independent old/new engine comparison preserves all 41,891 monthly point results across 4,948 histories. See docs/verification.md and docs/v2-test-results.json for exact checks and limitations.

## daily-linked/1.4.0 - 2026-11-14 · presentation within-ui/3.0.0

Presentation redesign from scratch. Analysis model (`routine-change/1.1.0`), display policy (`noteworthy-display/1.0.0`), component contract (`component-signal/0.1.0`), export contract (`1.1.0`) and data are unchanged.

- **Calm, low-stimulus Personal view.** Warm apricot-blush palette with cocoa text and one dusty-mauve accent; muted sage/honey/rose replace alarm colours. A single slowly breathing colour orb shows the day (disabled under reduced motion), with one plain sentence and the 0–1 value in small type. A care card appears only when something changed; quiet days stay quiet.
- **Pinboard layout.** The map is the large pin; up to three noteworthy changes sit beside it as tinted tiles (sleep, activity, mood, home) with simple line icons. The timeline drops per-day dots in Personal view. Map tiles are desaturated and route colours softened.
- **"Your usual" drawer.** In Personal view the reference settings slide in from the side, opened from "Compared with your usual…" under the orb.
- **Clinical view keeps more on the table**: reference column, arc gauge, 14-day persistence, comparison cards, map with day details, multi-component signals, index breakdown and evidence, in the same palette. Labels are sentence case.
- **New person picker.** The header chip opens a sheet (bottom sheet on phones) with three sources: Stories, Students and Research archive. People appear as soft colour "pebbles" with a one-line description. Search filters suggestions as you type and only switches person on an exact ID/name or a single match; "no match" leaves the current person in place.
- Bundled fonts: Young Serif and Figtree (SIL OFL 1.1) under `vendor/fonts/`; the preview server now serves `.ttf`.
- Tour step 8 opens the Clinical view (the component panel is Clinical-only). Test expectations updated for the new labels; presentation test now covers the picker search.

## daily-linked/1.3.0 - 2026-11-14 · presentation within-ui/2.0.0

Analysis model unchanged (`routine-change/1.1.0`); display thresholds unchanged (`noteworthy-display/1.0.0`). Source data unchanged.

- **Redesigned viewer.** Calm health-product styling; warm Personal view, cooler/denser Clinical view. Sticky day navigator (previous/next, date picker, comparison window, play) is always visible. Demo-people strip for one-click story switching.
- **Index gauge and "what this means" card.** Semicircular 0–1 gauge with the 0.20/0.50 flag levels. Personal view adds a gentle, status-specific message (check-in suggestion for larger changes; "missing data isn't a bad sign" for unscored days). Action buttons are demo-only and announced as such.
- **Clinical persistence.** Same engine points summarised as "N of the last 14 days flagged", current flagged run, signals above usual range, anchored index and reference evidence, with a 14-cell strip.
- **Timeline.** Story-phase bands, dashed flag levels, gradient area, missing-observation ticks, recorded-context markers and a selected-value bubble. Gaps remain gaps.
- **24-hour day ribbon** beside the map: stays/walks (generated) or recorded GPS segments (StudentLife) against hatched "not observed" time, in the record's time zone.
- **Multi-component signals panel + contract.** New `companion-signals.js` defines `component-signal/0.1.0` (per person-day payloads, identity/day validation) and `combined-preview/0.1.0` (weighted mean, abstains below two components, coverage ≥ 0.6). Generated demo people get deterministic, clearly-labelled demo check-in/screen-time/feed outputs; research participants show "Not connected". See `docs/integration-contract.md`.
- Demo component outputs follow the user-selected reference and are never scored on unobserved days (no combined value there). Component payloads require a non-empty day key; monthly research records use `person:period`.
- **Export contract 1.1.0** (additive): `componentSignals` and `combinedPreview`, plus limitations for synthetic component values.
- **Guided demo tour** (`tour.js`, or open `index.html?tour=1`): 10 steps from reference to deterioration, map, clinical view, single difficult day vs 7-day median, components and StudentLife.
- Keyboard: ← → change day, P/C switch view. Preview server sends `Cache-Control: no-cache` so edits are never shown stale.
- New tests: `tests/companion-signals.test.cjs`, `tests/presentation.test.cjs`.

## daily-linked/1.2.0 - 2026-11-14

- Selected-day comparison is now the default; explicit daily navigation and longer window presets coexist.
- Summary cards show only meaningful differences. Complete measurements and exact display thresholds remain inspectable/exportable; flagged-but-filtered states never claim no change.
- Added a separate recorded StudentLife GPS + check-in source, linked by source identity and UTC submission day, with 49 IDs and 2,116 paired days. Raw questionnaire codes remain unscored.
- Bundled Hanover OSM streets alongside Helsinki. Recorded GPS dots expose time and accuracy; gaps remain split, transport unknown, and current streets are not claimed as a 2013 reconstruction.
- Ten generated 120-day profiles now include two complete 24-hour stay/walk timelines, one showing a single difficult day followed by recovery.
- Same-person/date guards reject mismatched routes and suppress their statistics/exports. Exports contain the selected linked observation and policy provenance.
- Source measurements and scoring model remain unchanged. See current verification and independent paired-data review.


## 2026-11-14 ? Personal / Clinical and automatic maps

- Personal explanations and Clinical evidence share one assessment and retain selected state. View preference persists for the browser session.
- Date picker, interactive keyboard-accessible timeline and 7/14/28-day comparison presets.
- Accurate mood-scale points, sleep-efficiency percentage points and bedtime duration changes; no inferred stress from heart rate.
- Direct HTML opening now automatically renders bundled OSM streets, buildings and parks. Internet tiles and launcher are optional.
- Audited 10,000 external synthetic GPS traces / 546,273 coordinates, with an independent 50-trace explorer, source provenance and implausible-jump segmentation.
- No clinical person joins or model changes. See the new location audit and updated verification record.


## 2026-11-14 — Street-map and story review

- Interactive OpenStreetMap streets through vendored Leaflet 1.9.4; independent selected/reference trip layers, direction arrows and place markers.
- One-click local launcher, no npm or package installation; offline file viewing remains available without street tiles.
- Eight 120-day profiles with daily variability, timestamped trips on actual public path geometry, two persistent deterioration stories and recovery/context counterexamples.
- Presentation starts with a deterioration story; phase shortcuts, day navigation and progressive disclosure replace dense controls and repeated source warnings.
- Source provenance remains in the discreet dataset badge, methodology, generated bundle and exports. Original research values are unchanged.
- Scoring model remains `routine-change/1.1.0`; this is a presentation/data-generation update, not clinical validation.

## 2026-11-14 — Full-cohort and adaptive reference

- All 4,948 PSYCHE-D histories and seven NFI trace files audited; Dryad download unavailable.
- User-selected reference start/duration, bounded slow adaptation, metric-scoped optional context weights and a normalized 0–1 index.
- Fixed context adjustment suppressing the original review flag, ordinal/index collision and stale-feature scoring.
