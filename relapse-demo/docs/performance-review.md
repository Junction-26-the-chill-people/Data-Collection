# Release robustness and performance review

Reviewed 2026-11-14 against routine-change/1.1.0 and the current 4,956-participant / 42,851-record demo bundle. This is an implementation review, not clinical validation.

## Assessment consistency

No stale-assessment defect was found in the current event flow. Only changing the personal/clinical presentation calls `render(true)` to reuse the analysis. Participant changes, search, reference span, monitoring window, adaptive settings, confirmed context, selected dates and playback recompute the result. The reuse condition requires literal `true`; browser event objects do not accidentally enable it. Mode changes deliberately preserve the analytical settings and values. Export reads the current participant and the assessment at the selected ordinal, with the active analysis configuration and baseline metadata.

The engine withholds a current assessment when current measurements are absent, keeps reference observations unscored, records per-metric window coverage, and separates contextual attenuation from the raw/anchored status. Availability percentages are not device wear time or confidence. The export includes that limitation. Research identifiers remain distinct from application users, and CLI integration explicitly requires a verified user mapping, registered model version, timestamps and consent before any database write.

The review identified that exported engine `config` omitted metric definitions. The CLI envelope now adds `metricDefinitions`, preserving participant-specific or shared definitions, including units, direction, floor, effective weight and configured domains. This additive field does not change engine configuration semantics or model behavior. Targeted tests verify participant precedence and shared-definition fallback. Original measurements and source provenance are still needed to rerun an analysis; an assessment export alone is not a complete reanalysis input. UI export parity is owned by the UI integration review.

## Measured engine performance

Environment: Windows, Node v24.22.1, AMD Ryzen 5 5600H. These are single local benchmark runs after one warm-up, not browser frame timings.

| Workload | Total | Median per analysis | 95th percentile |
| --- | ---: | ---: | ---: |
| Recompute all 120 points on each of 120 scrub positions, fixed reference | 215.61 ms | 1.49 ms | 2.45 ms |
| Same workload with slow adaptive reference enabled | 368.06 ms | 2.64 ms | 4.96 ms |
| All 4,956 participants, UI-equivalent default references/windows | 321.49 ms | — | — |

The full-cohort run produced 23,933 scored points and zero errors. Latest statuses: 3,085 below threshold, 748 changed, 955 still reference-only, 79 insufficient data, 89 larger changes. These counts are descriptive outputs of the demonstration heuristic and must not be interpreted as diagnoses or estimated prevalence.

The full-cohort harness clamps the reference duration to each short history exactly as the UI does. An initial exploratory harness omitted this clamp and was rejected by input validation; it was corrected before the reported cohort measurement.

The arithmetic is not a demonstrated high-frequency bottleneck at this data size. The UI currently also rebuilds chart SVG, metric cards, period buttons, JSON text, route markers and place markers on each render. Browser layout/paint and these DOM operations are plausible sources of visible scrub lag; their costs were not measured by this Node benchmark. The Leaflet map, street geometry and route polyline objects themselves are retained across updates. Avoid claiming a smooth-frame guarantee from engine timings alone.

## Map and startup checks

The actual local bundle contains 684 features: 609 roads/footpaths, 57 buildings and 18 parks/grass areas. All inspected vertices fall within the advertised Helsinki bounds. Land polygons render in a pane below streets, which sit below reference and selected routes. No network is needed for the local street context.

The map regression suite passed after the polygon bundle update. It covers empty selected days retaining reference geometry, missing observations, true no-GPS clearing of route/place layers, file-mode tile suppression, online failure/recovery, extent-aware local fallback and escaped permanent place labels. Out-of-area traces explicitly report geometry-only mode instead of claiming Helsinki street context. HTTP preview-server tests separately confirm required map assets are served and private paths, traversal and rebinding are rejected.

Actual browser visual checks remain the root reviewer's responsibility. No new clinical claims, new dependencies or speculative performance optimizations were introduced in this pass.
