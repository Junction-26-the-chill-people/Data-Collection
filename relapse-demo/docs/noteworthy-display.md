# Noteworthy-only daily summaries

The default comparison is one selected calendar day. Longer 7/14/28-day windows remain available and use the existing median-based engine. A single difficult day can disappear in a longer median; the selected-day mode intentionally exposes it. This is not a clinical relapse label.

RoutineInsights.displayPolicy version `noteworthy-display/1.0.0` filters the visible summary only. Both minimums below must be met; a zero reference uses the absolute minimum alone. Changes in either direction may be shown. These are explicit demo display settings, not calibrated clinical cutoffs or statistical significance tests.

| Measure | Minimum absolute difference | Minimum relative difference |
|---|---:|---:|
| Steps | 1,000 steps | 20% |
| Sleep duration | 45 minutes | 10% |
| Sleep efficiency | 5 percentage points | None |
| Sleep onset | 1 hour | None |
| Resting heart rate | 5 bpm | 8% |
| Mood check-in | 0.5 source-scale points | None |
| Home time | 2 hours | 15% |
| Source-week short nights / active days | 2 nights / days | None |

`isNoteworthy(contributor)` returns a boolean; `noteworthyChange(contributor)` exposes the applied rule/reason. `summarize({..., noteworthyOnly:true})` filters narrative cards. Omit that option to retrieve all available narratives. Unknown metrics require an explicit rule. Missing/nonfinite values never become a change or a zero.

The scoring engine, source measurements and complete exports are unchanged by the filter. All measurements remain behind an explicit disclosure. If the composite engine flags a change but no individual measure crosses these display settings, the UI says a change needs a closer look, rather than saying no change occurred. Missing or unscored data has its own state. The display policy is included in exported assessments for reproducibility.

StudentLife raw check-ins are a separate unscored source. Questionnaire codes are not passed through these thresholds or interpreted as daily wearable metrics.
