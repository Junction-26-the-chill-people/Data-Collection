# WITHIN — personal routine review

**Current demo release: `daily-linked/1.5.0` (presentation `within-ui/3.0.0`), 14 November 2026. Analysis model: `routine-change/2.0.0`. Display policy: `noteworthy-display/1.0.0`. Component contract: `component-signal/0.1.0`; combined preview `combined-preview/0.1.0`; export contract `1.2.0`.** Check this release identifier and CHANGELOG.md before integrating; the standalone package includes an asset manifest.

## Repository checkout

The repository root README describes dataset licenses, bootstrap and team boundaries. From the repository root, run `python scripts/bootstrap.py` before tests or rebuilding data. Then `python scripts/test_all.py --node node` runs all suites. Opening the viewer needs neither step.

## Open the demo

**Open `index.html` directly. Streets, buildings, parks and demo routes appear automatically, even without internet.** No launcher, npm, API key or server is needed for this view. The map uses bundled OpenStreetMap vector geometry, not cached map tiles.

Choose **Personal** for plain-language changes or **Clinical** for the measurement evidence. The same selected person, date, reference and index are retained when switching views. The default is the selected day; previous/next, a date picker and 7/14/28-day comparison buttons are available. Only noteworthy changes appear in the summary; Show all measurements reveals the complete record.

`locations.html` is a separate GPS-source explorer with 50 traces from a newly audited 10,000-trajectory synthetic corpus. It shows coordinates, timestamps and flagged discontinuities without claiming an unverified street alignment or a health linkage.

For optional detailed online street tiles, double-click `START-DEMO.cmd`; `STOP-DEMO.cmd` ends that loopback preview. The launcher uses the installed Python runtime. The automatic local map does not require Python.

## Recorded GPS linked to health

Choose **StudentLife ? GPS + check-ins** in Data view. This is a separate recorded research source: 49 source IDs, 3,389 calendar days, 202,877 original GPS observations, 9,040 PAM check-ins, 1,644 sleep submissions and 84 pre/post PHQ questionnaires. There are 2,116 days with quality-accepted GPS and same-person check-ins. The viewer retains up to 80 fixes per day (172,715 displayed); all source rows remain in decoded CSVs outside the viewer package.

The default is StudentLife 10 on **2013-03-30**, in Hanover/Dartmouth. Its offline street layout is bundled. Inspect a GPS dot for timestamp and reported accuracy. Daily joins use explicit UTC dates, not an inferred local timezone. Recorded point connections are not road-snapped journeys; transport and exact paths remain unknown. Raw PAM codes are not treated as an ordinal mood scale. Sleep answers use verified questionnaire labels; they concern the prior night and are grouped by submission date. This source remains unscored, with PHQ as pre/post context.

See docs/studentlife.md and docs/studentlife-audit.json for provenance, quality exclusions, sampling, license and limitations. The derivative has 49 observed IDs while the original paper describes 48 people; the discrepancy is retained.

## Presentation flow

Fastest path: click **✦ Demo tour** (or open `index.html?tour=1`). Eleven steps walk through the story; Back/Next drive the real controls, Esc closes.

Manual flow:

1. **Noah**, 15 Apr 2026, Personal view: a sustained pattern, a rose orb and a gentle check-in card. A high daily number alone no longer raises a flag.
2. Use previous/next in the day bar, the date picker, or 7 / 14 / 28-day comparisons. The timeline continues to plot daily signals; its lower band shows pattern states.
3. **Compared with your usual** opens the reference drawer. Choose a start and 7–90 days. The anchor stays frozen; daily adaptation is small, bounded and restricted to earlier eligible days.
4. **Clinical** shows the engine's high/observed day counts, drift versus the anchor and the anchor/used/next-day baseline values. Open Measurement evidence for the metric table.
5. **Mila**, 14 Apr 2026 (Day 100): slow drift across domains despite a daily signal around 0.23. Her story is deliberately generated to demonstrate this path.
6. **Sofia**, 10 Mar: a harder day, noted without a care card. On 11 Mar she is steady again. **Mara** and **Ada** never flag in their supplied stories. **Emil** retains illness context; drift can still flag because context does not erase anchor evidence.
7. The person picker keeps Stories, Students and Research archive separate. Each generated person now has their own neighbourhood and places; recorded StudentLife stays unscored.

The main presentation uses a discreet **Demo data** badge. Constructed people remain explicitly identified in the data, methodology and exports. Research observations are never filled with generated values. The 0–1 index is an experimental adverse-change index, not a calibrated probability or diagnosis.

## Integrating other components

Screen-time, social-feed and companion-app teams: emit one `component-signal/0.1.0` payload per person-day (index 0–1 vs the person's own reference, coverage, provenance, synthetic flag). See `docs/integration-contract.md` and `companion-signals.js` (`validate`, `fuse`). Payloads for the wrong person or day are rejected.

## Included data

| Source | Coverage | Available information |
| --- | --- | --- |
| PSYCHE-D v0.1 | 4,948 participant histories; 35,694 observed monthly rows; 6,197 explicit missing slots | Recorded activity/sleep features and PHQ-9 endpoint context |
| NFI FARED | Seven files; 111,121 overlapping trace rows inspected without executing pickle objects | Activity/context summaries; no usable GPS or depression labels |
| Demo stories | Eleven people × 120 days = 1,320 daily slots | Daily device-style measurements, mood, context, timestamped walking trips and story phases |
| StudentLife derivative | 49 IDs; 3,389 days; 2,116 paired GPS/check-in days | Recorded GPS, PAM and sleep responses; pre/post PHQ context; no assigned relapse scores |
| SYN-RoadGps | 10,000 trajectories / 546,273 coordinates audited; 50-trace explorer | Separate synthetic GPS source; gaps flagged; no health linkage |
| Dryad | Metadata reviewed; raw download returns 403/401 | Inventory only; no participant measurements claimed |

The walking geometry comes from a bounded OpenStreetMap extract, with attribution retained. Personal measurements, destinations and trip times in the stories are generated. PSYCHE-D has no GPS; StudentLife provides the separately namespaced recorded location/check-in view. No GPS-only source is attached to another study's health records. See `ATTRIBUTION.md`, `docs/data-notes.md`, `docs/maps.md` and `docs/location-dataset-audit.md` and `docs/location-followup.md`.

## Integration and checks

The scoring engine is dependency-free JavaScript, suitable for an Android WebView or later native port. Native device ingestion remains integration work. Keep study IDs separate from application users; the backend must establish user identity, valid dates, registered model IDs and consent. No research data was imported into Supabase.

```sh
node analyze.cjs data/demo-data.json analysis.json sim-02
node tests/engine.test.cjs
node tests/engine-alerting.test.cjs
node tests/engine-adversarial.test.cjs
node tests/engine-adaptive.test.cjs
node tests/cli.test.cjs
node tests/cohort.test.cjs
node tests/ui-integration.test.cjs
node tests/test-ui.cjs
node tests/ui-release.test.cjs
node tests/map.test.cjs
node tests/insights.test.cjs
node tests/location-explorer.test.cjs
node tests/companion-signals.test.cjs
node tests/presentation.test.cjs
python -m unittest discover -s tests -p 'test_*.py'
```

To rebuild, keep all original research downloads unchanged:

```sh
python scripts/prepare_data.py --all --include-short-histories --output-dir .tmp/all-records
python scripts/build_demo_bundle.py
```

Preparation uses pandas and Apache Arrow; viewing/scoring uses local JavaScript and vendored Leaflet 1.9.4. `.deps`, `.tmp` and credentials must not be committed. Original downloads remain under `E:\Junction26\datasets`.

See `docs/engine.md`, `docs/scientific-audit.md` and `docs/verification.md` for the contract, numerical evidence and limitations. Short references have limited variability evidence. Early research history does not establish remission. No prediction accuracy or relapse-prevention efficacy is claimed.

Daily linkage and summary rules: docs/paired-daily-data.md and docs/noteworthy-display.md. Update this release notice, CHANGELOG.md and verification evidence whenever the data, UI behavior or integration contract changes.
