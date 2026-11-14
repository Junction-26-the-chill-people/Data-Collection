# Data provenance and complete-cohort audit

Current release 1.5.0 has eleven daily stories and eleven personal Helsinki extracts. The synthetic-extension section below describes the original eight-story implementation; see paired-daily-data.md and maps.md for Sofia, Elias, Mila and the current location generator. Research-source transformations below are unchanged.

## Real PSYCHE-D data

The presentation now includes every one of the 4,948 de-identified participant IDs and all 35,694 source rows from PSYCHE-D v0.1 (Zenodo5085146; CC BY-NC4.0). The parquet has154columns. It is a monthly indexed aggregate feature matrix, not a continuous daily sensor stream. The publisher's4,036-person analytical sample is a derived subset and differs from all IDs in this downloaded matrix.

There are6,197 explicit intervening missing-month slots. Their measurements and labels remain null. No synthetic observations fill real people's gaps.928 participants have fewer than 3 observed records and cannot establish the default three-observation reference. Explicit shorter references expose low-evidence and unknown-variability warnings. The default first-three-observed reference is provisional; it does not establish happiness/remission. PHQ9 endpoint values are contextual labels only, excluded from scoring.

All210,501 finite mapped metric values across all35,694 source rows were compared against independent reconstruction of the source-column transformations. All participant/month identities are unique; timeline indices are contiguous after explicit null padding. Source ranges and dictionary text are recorded in `all-history-audit.json`. An additional nine-or-more-month eligible audit covers2,272participants,24,868actual rows and1,384gaps (`full-cohort-audit.json`).

| Normalized field | Source column | Mapping |
| --- | --- | --- |
| steps | steps_awake_mean | mean steps while awake |
| sleep_hours | sleep_asleep_mean_recent | minutes /60, source recent4-day mean |
| sleep_efficiency | sleep_ratio_asleep_in_bed_weekday_mean | ratio x100, weekday mean |
| bedtime_hour | sleep_main_start_hour_adj_median | adjusted hour,28 means04:00 next day |
| short_sleep_nights | sleep__hyposomnia_count_ | nights below5hours, source last7days |
| active_days | steps__active_day_count_ | days above10,000steps, source last7days |

The normalizer rounds finite raw numeric values to4decimal places before the above unit conversions and rounds converted outputs to4places. `featureCompleteness` describes available selected fields, not device wear-time coverage. No sensor completeness can be inferred from these aggregates. Missing PHQ9 start/end labels are not interpolated. Their source three-month windows differ from the feature windows.

Real PSYCHE-D has no HR, GPS, walking routes, home-dwell, daily mood or image observations. Those capabilities cannot be reconstructed for these study participants. No clinical training target or model-performance estimate was produced.

## Synthetic daily extension

Eight separately identified demo profiles each have 120 daily slots (960 total): Mara's stable rhythm, Noah's sustained withdrawal, Lea's recovery, Oskar's travel, Iris's device gaps, Emil's reported illness/recovery, Ada's intentional fitness change, and Jonas's sustained sleep-led disruption. Fixed seeds 20261114..20261121 reproduce identical data. Every person is marked `synthetic:true`, `datasetId:synthetic-daily`; records retain the same provenance. Narrative phase markers and a default selected day support presentation without changing the underlying data.

The first 28 days are generated as a stable reference, not observed clinical evidence. Correlated day-to-day noise, weekday/weekend differences, occasional walks and different feature-change timings avoid perfectly coupled trajectories. Sleep shifts before activity/mood in Jonas's case. Illness/recovery and intentional activity contexts are supplied explicitly with synthetic provenance; no real participant has invented context.

Street geometry is actual OpenStreetMap pedestrian/path/public-street data from one bounded Helsinki Esplanadi extract. Personal movement, visit times and the home-area association are generated. The home marker does not identify an actual participant residence. Shortest graph paths use only permitted mapped street/path edges; there are no geometric circular trajectories or straight connectors across absent movement. The source extract, its SHA-256 and ODbL attribution are retained (`data/map-source/helsinki-esplanadi.osm`, participant `mapGeometrySource`). ? OpenStreetMap contributors; https://www.openstreetmap.org/copyright.

Each record has separate `trips` with origin/destination IDs, walking mode, ISO timestamps, duration, distance and ordered OSM-node points. `visits` describe destination dwell intervals. The compatibility `route` array contains the same points with `tripId`/`segmentId`; renderers MUST split trip IDs rather than connect through dwell or unobserved periods. These are selected local walking trips, not all movement. Work/other away-time has no invented connecting line. `movementStatus` distinguishes a missing device, no selected walk, and observed-in-simulation walking segments. Route distance cannot exceed the day's generated step distance; trip/dwell time cannot exceed generated away-time.

Fictional calendar dates begin 2026-01-05. Timestamp strings are UTC, and `timeZone:Europe/Helsinki` identifies the intended display zone. A UI displaying local times must convert the UTC timestamps, including daylight-saving transitions. User measurements and routes remain synthetic even though the basemap streets are real. Sensor gaps remain null. No clinical relapse diagnosis or outcome truth labels are assigned.

`tests/test_data_bundle.py` checks deterministic generation, all real source-row retention, provenance separation, exact source street-node coordinates/edge adjacency, walking speeds, timestamps, per-day movement/away-time consistency and context episode boundaries. `tests/test_story_outcomes.cjs` checks generated behavioral contrasts against the scoring engine. Two sustained-change stories have late anchored means about 66?67 compared with approximately zero for the stable story; two recovery stories rise and return near reference. This verifies scripted software behavior, not clinical discrimination. Results and the engine version are saved in `docs/synthetic-story-checks.json`.

## Findings that limit interpretation

-1,922 source rows contain exactly zero recent recorded sleep hours. This might reflect sensing/preprocessing as well as behavior; it cannot establish that somebody did not sleep.
-1,241 participants have at least one observed PHQ9 endpoint>=10 within their initial reference selection;1,286have no endpoint there. Endpoint context is not a contemporaneous mood label, but makes a blanket known-good baseline claim untenable.
-Three-point reference medians/MADs are unstable. In the eligible cohort, configured scale floors dominate2,103/2,163 usable sleep-efficiency references and1,954/2,170bedtime references. The heuristic score is therefore strongly controlled by engineering floor choices.
-Measurements are correlated: full-source Spearman steps/active-days=.8838 and sleep-hours/short-sleep-nights=-.7828. Multiple changed tiles are not independent evidence. Four sleep fields carry62.5%of the original real-data metric weight. This weighting is a declared demo choice, not clinical calibration.
-A low directional-change index only means selected measurements did not deviate enough from the chosen reference. Persistent depression, deterioration in unmeasured domains or an already poor baseline can all yield a low index. It must not reassure users that relapse is absent.
-The full history display eliminates the initial eight-person demonstration subset restriction. It does not eliminate study recruitment bias, missingness, retrospective feature design or short-history exclusions from scoring. No held-out sensitivity, specificity or relapse probability is claimed.

## Reproduce without overwriting the demo

`python scripts/prepare_data.py --all --include-short-histories --output-dir .tmp/all-records`

`python tests/audit_full_cohort.py --input .tmp/all-records/demo-data.json --output docs/all-history-audit.json`

`python scripts/build_demo_bundle.py --real-input .tmp/all-records/demo-data.json`

`python -m unittest discover -s tests -p test_data_bundle.py`

Use `--all` without `--include-short-histories` for the nine-or-more-record eligibility subset. `--max-participants N` restricts deterministic numeric-ID selection. `--output-dir` keeps audit generation separate. pandas and established Apache Arrow pyarrow are required for preparation, but viewing needs only the shipped HTML/JS/CSS. The bundle keeps real and simulated participants separate and embeds source metadata; `bundle-manifest.json` records input/output hashes. Other dataset adapters may append separately labeled participants after this PSYCHE-D+simulation build; do not silently overwrite those extensions when rebuilding.

Run `node tests/test_story_outcomes.cjs` after regenerating scenarios or changing the engine. The generator now defaults to `.tmp/all-records/demo-data.json`, preserving all study participants instead of accidentally selecting only long histories.
