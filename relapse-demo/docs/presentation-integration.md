# Presentation and integration contract

Personal and Clinical are presentation modes, not access-control roles. They use the same current assessment. A production companion app must authorize clinical access separately; this toggle must never bypass backend permissions.

`engine.js` exports the unchanged model `routine-change/1.1.0`. Its score is 0–100; `normalizedIndex` and `relapseVector` are 0–1 or null. Null means no estimate, never zero risk. `point.index` remains the record ordinal. See engine.md for the full input and adaptation contract.

`insights.js` exposes `RoutineInsights.summarize({assessment,records,baseline,windowSize,granularity})`. It describes recorded window medians against the selected historical reference. It does not infer stress from heart rate, percentages from arbitrary mood scales, or a diagnosis. Sleep efficiency uses percentage-point differences; bedtime uses duration differences. Source missingness and available-observation counts are retained. Never replace the explanation with a clinical probability claim.

`MovementMap.update(container,{participant,record,baselineRecords,selectedIndex})` accepts explicit trip segments and preserves gaps. `data/map-streets.js` is geographic context only; it contains no real participant movement. Its geographic extent is bounded and must not be presented as context for out-of-area traces.

`data/location-samples.js` sets LOCATION_DATA for the independent GPS explorer. It has synthetic source provenance, exact pinned revision/hash and `clinicalLink:null`. Source trajectory IDs are not users. Timestamps, coordinates and elapsed time do not establish a home, intent, mood or relapse. Never attach these traces to an existing clinical participant to make a more complete-looking profile. The main constructed stories are separately identified by `synthetic:true`.

Exports retain source IDs, model version, source provenance, selected reference, analysis configuration and metricDefinitions (including effective default weight 1). Reproduction still requires the original records; the assessment is not a standalone training dataset. Map exports retain quality flags and discontinuities. A production ingestion adapter must map actual app identities, consent, reliable timestamps and sensor coverage explicitly rather than treating research IDs or monthly observation ordinals as app identities/dates.

For future updates, change README's current release note and CHANGELOG; rerun affected suites and record verification scope. Data-preparation scripts should preserve source checksums and work from pinned copies. UI-only changes must not silently change model weights or reference definitions.
