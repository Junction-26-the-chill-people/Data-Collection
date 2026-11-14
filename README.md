# WITHIN — data collection and routine-change demo

**Current release: `daily-linked/1.5.0` · analysis `routine-change/2.0.0` · presentation `within-ui/3.0.0` · export `1.2.0`.** Before integrating, fetch the repository and compare [release.json](relapse-demo/release.json) and the [changelog](relapse-demo/CHANGELOG.md). Agents must read [AGENTS.md](AGENTS.md) and update version notices, the changelog and verification together when behavior or data changes.

WITHIN is a hackathon prototype for noticing adverse changes in a person's usual activity, sleep, mood and movement. A selected known-good period is the frozen anchor; a bounded baseline can adapt slowly from earlier eligible days. A single harder day is **noted**, while repeated evidence or slow drift across domains can suggest a check-in. These are explainable demo heuristics, not a relapse probability, diagnosis or validated clinical alert.

## Open it

Clone or download this repository and open **[relapse-demo/index.html](relapse-demo/index.html)** in a browser. The viewer is static HTML/CSS/classic JavaScript, with bundled Leaflet, fonts and street geometry. It needs no npm, build step, API key or server. Do not open GitHub's source-code preview expecting the application to run.

For an optional loopback server:

```sh
python relapse-demo/scripts/preview_server.py --serve --port 8765
```

Then visit `http://127.0.0.1:8765/?offline=1` for bundled streets, or omit `?offline=1` for optional online map detail. On Windows, `relapse-demo/START-DEMO.cmd` is another launcher. No bulk tile downloads are used.

Click **Tour** for eleven steps, or inspect these stories:

| Story | Date | Expected result |
| --- | --- | --- |
| Sofia | 2026-03-10, then 2026-03-11 | One harder day is noted; the next day is steady |
| Noah | 2026-04-15 | Sustained change worth a check-in |
| Mila | 2026-04-14, Day 100 | Slow drift across activity and mood despite a daily signal of 0.23 |
| StudentLife | Source 10, 2013-03-30 | Recorded same-person GPS and check-ins, deliberately unscored |

Personal and Clinical views share the selected person/date/reference. Clinical adds engine persistence, drift statistics and anchor/effective baseline values. Each of the eleven generated people has a distinct Helsinki neighborhood. Only substantial changes appear in summaries; all measurements remain inspectable.

## What is included

| Folder | Contents |
| --- | --- |
| `relapse-demo/` | Complete viewer, portable engine, CLI, tests, preprocessing, documentation and release metadata |
| `relapse-demo/data/` | Ready-to-open viewer bundles, eleven generated stories, recorded research derivatives and offline OSM geometry |
| `datasets/` | Licensed research originals/selected members, decoded tables, publisher metadata, checksums and local audit records |
| `datasets/archives/` | Lossless gzip copies of the full normalized PSYCHE-D input and the large SYN-RoadGPS CSV |
| `scripts/bootstrap.py` | Restores those two files locally and verifies checksums; no network or third-party Python packages |
| `scripts/test_all.py` | Bootstraps prerequisites and runs every JavaScript and Python test |
| `scripts/verify_repository.py` | Verifies all files listed in the repository dataset manifest |

The viewer is ready immediately. Run bootstrap before data tooling or tests:

```sh
python scripts/bootstrap.py
python scripts/verify_repository.py
python scripts/test_all.py --node node
```

Tests require Python and Node.js, not npm. The handoff was tested with Node 24.22.1. The baseline release passed **16 JavaScript suites, 32 Python tests, 351 UI cases and 10,907 integration combinations**; see [verification](relapse-demo/docs/verification.md). A 400-series stable-noise fixture produced no flags; that is a software check, not clinical validation.

## Datasets and licenses

See [datasets/README.md](datasets/README.md), [repository manifest](datasets/repository-manifest.json) and [attribution](relapse-demo/ATTRIBUTION.md) for exact inventory, hashes and transformations.

- **PSYCHE-D:** original Parquet, feature dictionary and license; all 4,948 histories / 35,694 observed monthly rows retained. **CC BY-NC 4.0**; the noncommercial restriction continues to apply to source data and derivatives.
- **StudentLife:** four selected RDS members, decoded CSVs and daily viewer derivative. 49 source IDs, 202,877 original GPS observations, 3,389 participant-days. **CC BY 4.0** on the attributed Zenodo derivative; the whole 230 MB archive was not downloaded. Raw questionnaire codes remain unscored.
- **SYN-RoadGPS:** all five downloaded publisher files, with its 52.8 MB CSV stored losslessly in `datasets/archives/`. **CC BY 4.0**. GPS-only trajectories stay separate from health records.
- **Corona Health:** the four downloaded GPS/survey CSVs and audits, **CC BY 4.0**. Partial source only; coarse coordinates are unsuitable for street routes and are not attached to the viewer's health profiles.
- **UCI GPS trajectories:** downloaded archive and manifest, **CC BY 4.0**; not integrated with health data.
- **OpenStreetMap:** source extracts and derived street geometry, **ODbL**, with attribution retained.
- **NFI FARED:** source inventory, pinned URLs, static analysis summaries and download tooling. Raw pickles are omitted because a clear redistribution license was not found. Do not execute or deserialize untrusted pickles.
- **Dryad Finnish study:** metadata and download status only. The raw download was blocked; it is not represented as an available dataset.

Generated stories remain marked `synthetic:true`. No generated values fill research gaps, no unrelated GPS is attached to health data, and research source IDs are not application users. This repository has no blanket license that overrides the individual dataset/vendor terms. No new license is assigned to team-authored code by this handoff.

## Team integration boundaries

| Owner/module | Responsibility and interface |
| --- | --- |
| Routine / wearables / movement | `relapse-demo/engine.js`: `analyze(records, options)`; activity, sleep, physiology, self-reported mood and linked movement evidence |
| Screen-time / app-use team | Produce separate person-day `component-signal/0.1.0` outputs from real app-use data |
| Social-feed / algorithm team | Produce separate person-day signals from their own feed analysis |
| Companion app | Own reflections, images and check-ins; supply explicit observations/context and implement user-facing interactions |
| Backend / patient identity | Authentication, consent, user mapping, access control and storage; schema lives in [DB-Data](https://github.com/Junction-26-the-chill-people/DB-Data) |

A [current CLI export example](relapse-demo/data/analysis-example.json) shows the 1.2.0 envelope and routine-change/2.0.0 fields.

Read [the integration contract](relapse-demo/docs/integration-contract.md), [engine rules](relapse-demo/docs/engine.md) and [recorded GPS linkage](relapse-demo/docs/studentlife.md). The displayed phone/feed/check-in component outputs for generated people are placeholders, not integrated detectors. `companion-signals.js` validates identity/date/provenance and computes an explicitly unvalidated combined preview. It does not implement the other teams' analyses.

## Rebuild data and package

The shipped normalized input is sufficient to rebuild all demo stories without third-party Python packages:

```sh
python scripts/bootstrap.py
python relapse-demo/scripts/build_demo_bundle.py --verify-alerts --node node
python relapse-demo/scripts/package_viewer.py
```

The ZIP is written to `relapse-demo/work/WITHIN-demo.zip`. To reproduce the normalized PSYCHE-D input from Parquet or decode StudentLife from RDS, install [requirements-data.txt](requirements-data.txt) in a virtual environment first:

```sh
python -m pip install -r requirements-data.txt
python relapse-demo/scripts/prepare_data.py --all --include-short-histories --output-dir relapse-demo/.tmp/all-records
python relapse-demo/scripts/studentlife_data.py
```

Always use **both** `--all` and `--include-short-histories` for the research source. The preparation tool's small default subset must never replace the full cohort. Keep original files/checksums unchanged; place transformations in separate outputs. Read the relevant source documentation before rerunning download tools, since some sources remain blocked or deliberately excluded from redistribution.

## Updating and checking freshness

Run `git fetch origin` and `git status -sb` before editing; inspect `git log HEAD..origin/main --oneline` for newer commits. Preserve local changes and integrate deliberately. Release identifiers describe behavior/contracts; Git commits identify every documentation or packaging update.

For changes, update both README version notices, `relapse-demo/CHANGELOG.md`, `relapse-demo/release.json` and `relapse-demo/docs/verification.md` together. Version the analysis model separately from presentation and component contracts. Dataset changes also require source manifests, licenses, hashes and relevant preservation tests. Never commit credentials, preview-server state, local runtimes or generated work directories.
