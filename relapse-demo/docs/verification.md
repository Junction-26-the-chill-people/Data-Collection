# Repository handoff verification — 14 November 2026

The separate Data-Collection checkout was tested after copying the release without the original .tmp/.deps/work directories. The standard-library bootstrap restored and hash-verified the full normalized PSYCHE-D input and SYN-RoadGPS CSV from committed gzip archives. All 16 JavaScript suites and 32 Python tests passed, including 351 UI cases and 10,907 UI/engine combinations; exact output is in repository-tests.json.

The engine, viewer files, generated health bundle, StudentLife bundle and companion-signals.js are byte-identical to the verified 1.5.0 working release. New work is repository documentation, portable launch/bootstrap/test helpers, licensed source inventory and a regenerated 2.0.0 CLI example. The dataset manifest checks all shipped originals/derivatives/geometry; excluded or blocked sources are explicitly documented. A credential-pattern and local-artifact scan found no findings in the proposed commit. README relative links resolve. No new browser verification was needed for this handoff because viewer code/data are unchanged; the preceding release's actual desktop/mobile checks follow below.

The package builder also completes in the new checkout. Credentials, certificates, local runtimes, preview state, generated work artifacts and unlicensed raw NFI files are excluded. The working Git checkout is E:\Junction26\Data-Collection; the original E:\Junction26\relapse-demo directory is retained independently.

---

# Verification record - daily-linked/1.5.0 (analysis routine-change/2.0.0)

14 November 2026. Presentation remains within-ui/3.0.0. Export contract is additive 1.2.0; component-signal/0.1.0 and combined-preview/0.1.0 semantics are unchanged.

## Changed test expectations

- `tests/presentation.test.cjs`: Sofia 2026-03-10 now expects alertState noted and status no_change, without a care card; 11 March is steady. The old daily >=50 / seven-day <20 alert contrast is replaced by those state assertions. Noah's sustained tour assertion uses index 100; Mila's drift uses index 99. Persistence displays engine highDays/observedDays for seven calendar days instead of recomputing 14 legacy statuses. Export 1.1.0 becomes 1.2.0; routine component metadata becomes 2.0.0. Eleven stories replace ten. Daily numeric guide labels become signal 0.20/signal 0.50, retaining the same guide geometry.
- `tests/test-ui.cjs`: daily adaptation is now on by default. Date-only navigation reuses analysis (zero engine calls); changing the comparison window still recomputes. Coverage grows from 342 to 351 render cases because Mila adds nine. Assertions for all personal places remain intact; the view now lists every personal place instead of truncating at two.
- `tests/test_story_outcomes.cjs`: retained the original anchored-score scenario checks and added daily state outcomes: Noah/Jonas sustained, Sofia noted then steady, Mila drift, Mara/Ada never flagged, Lea disruption then recovery, Emil context-annotated drift then recovery.
- `tests/test_data_bundle.py`: eleven generated profiles replace ten; Sofia/Elias have their own home plus2–4 places instead of the former fixed six-place layout. Route-node/edge checks use each person's source extract instead of the shared Esplanadi graph. Added distinct-home, original-health/metadata hash, bounded-region and story-location checks; retained source/null preservation, endpoints, speed, timestamps and complete24-hour budgets.
- `tests/cohort.test.cjs`: now passes each participant's actual granularity into analyze so daily stories exercise2.0 alerting and monthly histories retain1.x behavior.
- Existing core/adaptive/adversarial engine expectations, map tests, StudentLife UI, release UI and UI-integration assertions were not weakened. UI-integration grows from 9,939 combinations/15 histories to 10,907/16 through the additional story. New tests/engine-alerting.test.cjs is additive.

## Automated checks

- Baseline before edits: all 15 JavaScript suites and all 30 Python tests passed, including 342 UI cases and9,939 integration combinations.
- Final complete run: all 16 JavaScript suites and all 32 Python tests passed. This includes351 UI cases,10,907 UI/engine combinations,3,960 generated component payloads and all 4,959 cohort histories/43,211 calendar slots. Exact command output is retained in docs/v2-test-results.json.
- New alerting suite: isolated noted day,5 of 7 sustained,3 of 7 watch, sparse/missing calendar slots, independent daily evidence under longer display windows, two-domain drift, one-domain sleep exclusion, confirmed-context/mood protection, bounded EWMA updates/freezes,50 future-prefix perturbations, immutable inputs, explicit unit conversion, known Theil–Sen/Mann–Kendall values and nested configuration validation. It rejects settings that could turn one day into a pattern.
- Stable-noise fixture:0/400 seeded120-day series flagged. Mann–Kendall was nonsignificant in 387/400 independent noise samples. These are software-fixture checks, not an estimated clinical false-positive rate.
- Independent old/new engine comparison:4,948 monthly histories and41,891 monthly points preserve baseline statistics, status, score, anchoredScore, rawScore, contributors, coverage and windowIndices exactly. See docs/v2-monthly-preservation.json.
- SHA256 checks preserve companion-signals.js, both StudentLife derivative assets and the full original research input. Hashes in tests/fixtures/pre-1.5-health-hashes.json preserve all ten original profiles' health arrays, dates, phases, contexts, missingness and identity metadata. Research rows/nulls compare exactly to the original full cohort.
- Eleven distinct homes and per-person OSM route nodes/edges/bounds pass. Deteriorating profiles visit fewer/closer destinations; Oskar's travel visits differ from his anchor. Sofia/Elias retain240 complete24-hour itineraries and exact home budgets. Missing days have no trips or visits. The eleven bundled region scripts total3,649,224 bytes; each is below 504 KB. Raw source snapshots are excluded from the viewer package.

## Story outcomes and deliberate choices

- Sofia, index 64 / 10 March: noted, score0.72; index 65 / 11 March: steady, score0.00. No single-day care card.
- Noah has flag_sustained at index 100 / 15 April; Jonas reaches sustained in his later phase. Their earlier multi-domain changes can meet the higher-priority drift path first.
- Mila first flags via drift at index 99 / 14 April / Day 100 with day signal 0.23 and activity+mood domains; no sustained flag occurs in her120 days. The generated seed20261125 and means were tuned to this demonstrative outcome: steps decline3%/week and mood0.13 points/week. The suggested2% steps rate could not reliably meet the unchanged25% drift minimum by Day 100. This tuning is disclosed in docs/paired-daily-data.md and is not model validation.
- The separate1.5%-per-week test uses220 days; first drift occurs at index 152. Its longer horizon follows the specified minimum change rather than weakening thresholds.
- Mara and Ada never flag. Lea returns to steady after disruption. Emil can trigger drift during confirmed illness because Path B is deliberately not suppressed; context remains visible and he later returns to steady. These rules cannot determine the cause of a change.
- Persistence uses calendar slots, with periodIndex gaps respected, while drift uses observed values. Fewer than four observed days abstains even if the few observed values are high. Independent daySignal prevents overlapping display windows from manufacturing persistence.
- Confirmed illness/intentional context can suppress non-mood Path A counts while retaining unsuppressedAlertState, anchored/raw scores and unadjustedHighDays. This resolves the conflicting requirements to suppress illness-only sustained flags and retain anchored evidence. Drift and mood evidence are never suppressed.

## Browser verification

Actual Chromium browser, loopback server at 127.0.0.1:8765 with ?offline=1. The existing loopback server was reused and left running.

- Desktop1280 px and phone375 px: Personal/Clinical views, Noah sustained, Sofia noted then steady, Mila drift. Clinical shows0/7 high days alongside2 drift domains for Mila, with anchor/recent/trend/p values matching the engine.
- All eleven guided-tour steps completed and landed on their intended stories/states, including unscored StudentLife. Different selected stories visibly show Toolo, Kaisaniemi and Kruununhaka geometry/places.
- Map host computed position relative, z-index 0 and isolation isolate. Scrolling the map to the sticky-bar boundary leaves top/day controls above it. Reference drawer, picker and tour cover the map; toast remains visible at z-index 90. Desktop and phone overlays were exercised; no Leaflet vendor CSS changes.
- No document horizontal overflow at 375 px, including expanded clinical evidence and the picker/drawer. Desktop and phone screenshots retained with the release handoff. No browser warnings/errors were captured.
- Not re-tested: physical phones, external file:// browser behavior or live online tiles. Offline-vector rendering was exercised through loopback using the same offline branch; no tile prefetching is introduced.

## Limits

These are uncalibrated patterns worth a check-in, never a relapse probability, diagnosis or validated clinical alert. Correlation, autocorrelation, multiple comparisons, reference selection and sensor gaps limit inference. The chosen generated story is illustrative; the existing research sources provide no validation of these thresholds. See docs/engine.md for every default and the full adaptation/context rules.

---


# Verification record - daily-linked/1.4.0 (presentation within-ui/3.0.0)

14 November 2026. Presentation-only release on top of 1.3.0; analysis, display policy, contracts and data unchanged.

- All 15 JavaScript test files and all 30 Python tests passed. Two expectation updates: the StudentLife test now expects the sentence-case label "Recorded GPS and daily check-ins"; the presentation test expects the orb/arc markup, warm status colours, the pebble picker, quiet days without a care card, and new picker-search rules (partial query filters without switching person; exact ID opens; no match keeps the current person).
- Browser (Chromium preview pane, loopback server): Personal and Clinical at 1280 px; phone at 375 px with no horizontal overflow and the picker as a bottom sheet; reference drawer open/close; Stories/Students/Archive tabs and archive search; 10-step tour forwards and backwards with every focus target visible; both bundled fonts reported loaded; no console warnings or errors.
- Sensory choices checked by inspection: one non-user-triggered animation (orb, 7 s cycle, scale 0.97–1.02) removed under prefers-reduced-motion; no flashing; no saturated red; map tiles desaturated.
- Not re-run for this release: direct file:// opening in an external browser and a physical phone. The offline map path is unchanged from 1.3.0.

---

# Verification record - daily-linked/1.3.0 (presentation within-ui/2.0.0)

14 November 2026. Analysis model unchanged (routine-change/1.1.0); display policy unchanged (noteworthy-display/1.0.0); source data unchanged. New: presentation within-ui/2.0.0, component contract component-signal/0.1.0, combined preview combined-preview/0.1.0, export contract 1.1.0. The previous 1.2.0 record follows below and still describes the data, map and linkage evidence.

## Automated checks

- All 15 JavaScript test files passed: the 13 existing files unchanged (including 342 stratified UI render cases and 9,939 UI/engine combinations against the redesigned markup) plus two new files.
- `tests/companion-signals.test.cjs`: 3,600 generated demo component payloads (10 profiles x 120 days x 3 components) validate against the contract and carry `synthetic:true` and demo provenance; research participants receive none; unobserved demo days (missingPeriod) receive no scored phone/feed values and no combined value; demo references follow the user-selected reference; identity, day, range, provenance, version and missing day-key rejection; monthly research periods have distinct keys; fusion abstains below two components and below 0.6 coverage, and weights renormalize.
- `tests/presentation.test.cjs`: gauge colour, status and Personal care-card tone agree with the engine status; 14-day persistence is counted from the same engine points; timeline contains flag levels, reference/comparison shading and phase bands; story strip marks exactly one person; tour selection API applies person/day/window/view and `reset`; Sofia 2026-03-10 is flagged daily (0.72) and absorbed by a 7-day median (<0.20); exports contain component signals with correct person/day keys and synthetic flags; research exports contain only the routine component and an abstaining combined preview; demo-only actions are announced.
- All 30 Python tests passed, including loopback-server isolation with the new `Cache-Control: no-cache` header and the two new public files.

## Independent review

A separate reviewer agent read the new code cold (diffed against the pre-redesign copies) and ran the suites. It found no runtime errors, no unescaped data in innerHTML/SVG, no generated values for research participants, no timeline gap bridging, and unchanged rejected-linkage redaction. It reported seven lower-severity issues; all were fixed and covered by the regressions above: (1) demo phone/feed values generated on unobserved days, (2) demo reference ignoring the selected reference, (3) null day keys for monthly records accepted, (4) tour steps inheriting changed reference/adaptation settings and keyboard input while the tour was open, (5) Play hidden on phones, (6) this record not yet updated, (7) "days" wording for monthly participants and demo action buttons on research participants.

## Actual browser checks (Chromium preview pane, loopback server)

- Desktop ~1280-1366 px: Personal and Clinical views for Noah 2026-04-01 (0.75), sticky day navigator, gauge, care card, noteworthy cards, timeline, map with day ribbon and place frequency, signals panel. No console warnings or errors.
- Phone 375 px: no horizontal overflow (scrollWidth 375) in Personal, Clinical and StudentLife; date picker overlays the selected date; Play visible; hero, care card and cards stack correctly.
- Demo tour: all 10 steps forward and all steps backward land on the intended dataset/person/day/view and scores (0.00, 0.40, 0.75, 0.72, 0.00, StudentLife unscored).
- StudentLife switch: research badge, unscored state, "Not connected" for all components, UTC ribbon of recorded GPS segments, Hanover streets.
- `?offline=1` (same local-vector branch as opening index.html from disk): zero OpenStreetMap tile requests; Helsinki and Hanover vector street layers render.
- Not separately re-run for this release: direct `file://` opening in an external browser and a physical phone. The 1.2.0 checks below cover those code paths, which this release does not change.

## Limitations that still apply

The index is an experimental adverse-change heuristic with uncalibrated weights and thresholds, not a relapse probability or diagnosis. Combined-preview weights are placeholders. Screen-time, social-feed and companion-app outputs shown for demo people are generated from the same person's story and are not results of integrated components. Correlated features (sleep/activity; mood/feed tone) can move together and are not independent corroboration.

---

# Verification record - daily-linked/1.2.0

14 November 2026. Analysis model remains routine-change/1.1.0. Display policy is noteworthy-display/1.0.0. This release changes daily presentation, matched GPS/check-in data, map inspection and export metadata.

## Automated checks

- All 13 JavaScript test files passed, including core/adversarial/adaptive scoring, CLI, full cohort, maps, explanatory summaries, independent location explorer, daily UI, StudentLife UI and release regressions.
- All 30 Python tests passed, including exact preservation of original research rows, deterministic generated scenarios, six independently authored StudentLife source tests, GPS continuity, NFI inert parsing and loopback-server isolation.
- 342 stratified UI render cases and 9,939 UI/engine combinations across 15 selected histories passed. Both Personal/Clinical views preserve the same assessment and date.
- All 4,958 scored-demo/research histories and 43,091 calendar slots completed the cohort audit with zero failures. StudentLife remains a separate unscored source and is not counted as a validated scoring cohort.
- Every one of 172,715 displayed StudentLife coordinates matches its same-UID original timestamp/coordinate/accuracy tuple. All 3,389 daily identity/time joins match the decoded source CSVs; segments do not bridge excluded fixes, long gaps or flagged speed jumps.
- Generated profiles have 1,200 days. The two complete-location profiles cover 240 contiguous 24-hour itineraries with matching stay/trip endpoints and exact home/away budgets. Research records remain unchanged.
- Display-policy tests suppress 0.3% differences, retain meaningful changes and full measurements, and distinguish unscored/missing data. A real flagged-but-filtered research case (psyche-924) verifies that an index flag cannot accompany a misleading no-change headline.
- Linkage tests reject wrong participant/subject/date/dayKey/timezone GPS, clear stale geometry and suppress surrounding movement summaries and location-bearing export fields. Valid health answers remain inspectable.
- Map tests cover independent regional bounds, stationary GPS fixes, timestamp/accuracy popups, compact layer controls, responsive refitting, offline tile policy, gaps, singleton observations and invalid coordinates.

## Actual browser checks

Viewed local offline maps through HTTP with ?offline=1, using the same local-vector branch as file opening. Helsinki and Hanover streets, buildings and parks rendered without tile requests. The browser was exercised at 800px and 390px; the phone document measured 375px content/client width with no horizontal overflow.

Selected Sofia on2026-03-10: the daily index was0.72. A7day comparison retained that date and produced0.00 because the median suppresses the isolated day. Returning to Selectedday restored0.72. Switching Personal/Clinical preserved the date/window/index. Nextday,2026-03-11, displayed0.00 and No noteworthy changes for thisday, without tiny-change cards.

Selected StudentLife10 on2013-03-30, then navigated toMarch31. Check-in headings, GPS counts and map labels advanced together. A recorded GPS popup showed source time2013-03-30T21:24:45Z and accuracy30.6m. Verified sleep-duration/quality labels appeared alongside original codes. This source displayed no numerical score or reference controls. The source is grouped by UTC response time; shared dates do not imply simultaneous observation.

Browser testing caught author CSS overriding the hidden attribute, a stale reference-jump link on phones, and expanded map controls obstructing the phone map. These were fixed and rechecked. The final map refits when viewport width changes while preserving the view during ordinary day navigation. No console warnings or errors were returned in the final browser session.

Screenshots are saved with the delivered package in the task outputs folder. Browser tests use the HTTP offline branch rather than native file navigation; all package-local HTML dependencies and asset hashes are verified separately.

## Independent review and limits

See paired-review.md, studentlife.md, paired-daily-data.md and noteworthy-display.md. Independent review identified and verified fixes for flagged-but-filtered summaries and rejected GPS leaking into surrounding statistics/exports. A later source audit confirmed original repeated/conflicting response timestamps; these are preserved, not averaged or treated as distinct sleep nights.

The derivative has49 source IDs while its cited paper describes48students. Only four selected ZIP members were fetched: member CRCs/local SHA256 were verified, not the whole archive MD5. GPS lines join accepted samples; they are not verified travelled roads. Hanover cartography is current OSM context under historical observations. No actual home location or transport mode is inferred.

The experimental score is not a calibrated probability, diagnosis or demonstrated relapse-prevention system. StudentLife raw reports are deliberately unscored. Personal/Clinical changes presentation, not authorization. No research data was inserted into Supabase or joined to application users.
