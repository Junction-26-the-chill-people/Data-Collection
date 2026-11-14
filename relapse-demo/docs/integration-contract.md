# Component-signal contract (`component-signal/0.1.0`) and combined preview (`combined-preview/0.1.0`)

This repository owns the **routine & wearables** component (activity, sleep, resting heart rate, mood check-ins as a feature, time at home, GPS/movement). Other teams own **screen time / app use**, **social-feed analysis** and the **companion app** (reflections, images). This document defines how their outputs join ours. Implementation: `companion-signals.js` (dependency-free, browser global `CompanionSignals` and CommonJS). Tests: `node tests/companion-signals.test.cjs`.

Nothing in this repository computes screen-time, social-feed or reflection results. For **generated demo people only**, `CompanionSignals.demoSignals()` produces deterministic placeholder outputs so the combined view can be shown. They are marked `synthetic: true` and `provenance: "demo-generator:companion-signals.js"` in the UI (a "Demo" badge) and in exports. **Research participants (PSYCHE-D, StudentLife) never receive generated values**; their panels say "Not connected".

## One payload per component, per person-day

```json
{
  "contractVersion": "component-signal/0.1.0",
  "componentId": "screen_time",
  "componentVersion": "screen-usage/0.3.2",
  "participantRef": "app-user-7f3c",
  "dayKey": "app-user-7f3c:2026-04-01",
  "index": 0.42,
  "coverage": 0.9,
  "synthetic": false,
  "provenance": "android-usage-stats",
  "contributors": [
    {"id": "screen_minutes", "label": "Total screen time", "value": 312, "unit": "min", "reference": 180},
    {"id": "late_night_minutes", "label": "Use after midnight", "value": 55, "unit": "min", "reference": 12}
  ],
  "summary": "More screen time than usual"
}
```

| Field | Rule |
| --- | --- |
| `contractVersion` | Exactly `component-signal/0.1.0`; other versions are rejected. |
| `componentId` | One of `routine`, `companion_checkin`, `screen_time`, `social_feed`. |
| `componentVersion` | The producing model/algorithm version, so scores from different versions are not silently compared. |
| `participantRef` | The application's own user reference. Never a research source ID. Must equal the selected person, or the payload is rejected. |
| `dayKey` | `participantRef:YYYY-MM-DD` in the person's local day (the same convention as `record.dayKey`). Must equal the selected day, or the payload is rejected. Producers decide local-day boundaries before sending; sleep crossing midnight belongs to the day it ends unless stated otherwise in `contributors`. |
| `index` | Adverse-change index in [0, 1] **relative to that person's own reference**, or `null` when not scored. `0` means "no adverse change", not "missing". |
| `coverage` | Fraction in [0, 1] of the expected observation that was present. Below 0.6 the component is shown but excluded from the combined preview. |
| `synthetic` | Required boolean. `true` for any generated/demo value. |
| `provenance` | Required non-empty source description. |
| `contributors` | Optional explainable parts: value vs the person's reference, with units. Displayed in the Clinical view. |

`CompanionSignals.validate(payload, {participantRef, dayKey})` returns a list of error codes (`participant_mismatch`, `day_mismatch`, `index_out_of_range`, `coverage_out_of_range`, `synthetic_flag_required`, `provenance_required`, `unknown_component`, `unsupported_contract_version`). Rejected payloads are never displayed or fused. The routine component is converted with `CompanionSignals.routineSignal(participant, index, enginePoint)`.

## Combined preview

`CompanionSignals.fuse(payloads, expected)`:

- Accepts only valid payloads with a finite `index` and `coverage >= 0.6`.
- Abstains (`status: "insufficient_components"`, `index: null`) unless **at least two** components are accepted.
- Otherwise returns a weighted mean using fixed weights — routine 0.50, companion check-in 0.20, screen time 0.15, social feed 0.15 — renormalized over the accepted components.
- Reports `components` (with normalized weights), `rejected` (with reasons) and `includesSynthetic`.

The weights are a transparent placeholder for the hackathon, not learned or validated. The result is **not a relapse probability, diagnosis or emergency signal**. Correlated components (for example low mood reported in the companion app and low-mood content in a feed) can move together; agreement between them is not independent corroboration.

## Export

The viewer's assessment export (`contractVersion: "1.2.0"`, additive over 1.1.0) retains `componentSignals` and `combinedPreview`, and adds `alertState`, `persistence`, `drift` and `alerting` settings. The assessment also contains the frozen anchor, baseline used and next-day effective baseline. For daily inputs, consume alertState for pattern UI; score remains the selected-window change index. A single high day can have status no_change and alertState noted. The routine payload's componentVersion is supplied by the caller as routine-change/2.0.0; component validation and fusion semantics are unchanged. See engine.md for monthly compatibility and context behavior.

## Database integration

The shared schema lives at https://github.com/Junction-26-the-chill-people/DB-Data. Read that repository's `AGENTS.md` and check its schema version before mapping these payloads to tables. Authentication, consent and authorization are owned by the backend and must be explicit; source participant IDs from research datasets are not application users and must not be stored as `participantRef`.
