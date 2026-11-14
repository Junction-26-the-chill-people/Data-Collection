# Demo integration guidance

Work within this repository's `relapse-demo/` directory and inherit `../AGENTS.md`. Run `python ../scripts/bootstrap.py` before tests or a full-cohort rebuild.

Read README.md, CHANGELOG.md and docs/engine.md before integrating. Keep analysis-model version separate from presentation changes. Any further behavioral/contract/data changes must update CHANGELOG.md and the current-version notice at the top of README.md, with meaningful verification recorded in docs/verification.md.

Preserve all real research rows and nulls. Never merge constructed records into a real participant's gaps. Keep `synthetic` and source fields in exports even when the presentation uses the concise 'Demo data' label. Do not claim the heuristic is a calibrated relapse probability or verified diagnosis.

The browser deliverable is static HTML/CSS/classic JavaScript: no npm or mandatory build step. Leaflet is pinned at 1.9.4 under vendor/. Keep its license and OpenStreetMap attribution. Do not use Google tiles through unofficial endpoints. OpenStreetMap street tiles require a valid web origin/referrer; direct file:// mode must not request them. Never bulk-prefetch tiles. Routes are separate trip segments; missing observations must not create connections.

START-DEMO uses a loopback-only Python standard-library server. Do not expose private workspace files or directory listings. Keep local runtime state and credentials in ignored paths. Google Maps keys, if added later, require website/API restrictions and must not be committed.

Default rebuild uses .tmp/all-records/demo-data.json; do not replace the full cohort with the smaller eligibility subset. Run the relevant engine, data, map and UI suites and perform browser checks for visual changes when available. Record blockers honestly rather than describing DOM mocks as visual certification.

Current daily-linked release adds a separate STUDENTLIFE_DATA source. Compare release.json, README.md and CHANGELOG.md before making changes; packaged asset-manifest.json hashes describe the exact distributed viewer. Update these release indicators and verification evidence together. StudentLife raw questionnaire codes are unscored; retain source response timestamps, duplicates/conflicts, UTC grouping and same-study IDs. Preserve explicit person:date day keys, unknown transport and missing GPS. Never attach unrelated GPS to measured health records. Display thresholds are versioned separately from the engine and must remain visible/exportable. Complete generated itineraries and partial recorded GPS must retain distinct coverage descriptions.

Release daily-linked/1.3.0 adds presentation within-ui/2.0.0 and companion-signals.js. Keep the component contract (component-signal/0.1.0), combined preview (combined-preview/0.1.0) and export contract versions separate from the analysis model. Generated component outputs exist only for synthetic demo people, must carry synthetic:true and demo provenance, and must never be produced for research participants. Reject component payloads whose participantRef or dayKey differ from the selected record. tour.js is presentation only and must use the public WithinApp selection API.
