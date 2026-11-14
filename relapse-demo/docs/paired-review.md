# Independent paired GPS and daily-view review

Review date: 14 November 2026. Reviewer: paired_review. This is code/data verification, not clinical validation or a browser visual inspection.

## Findings sent to the implementers

1. **P2 - flagged assessment can receive a no-change summary.** With the exact default UI reference settings (first 28 daily slots or first 3 monthly slots, excluding missing records) and a one-period comparison, 8 monthly observations score at least 20 while no contributor passes the display thresholds. Example: `psyche-924`, Month 12 (index 11), overall score 23; steps fall from 15,892.2857 to 12,805.5 (-3,086.8 / -19.4%), with anchored feature score 69.56. The strict 20% display threshold filters this out, and `app.js` initially displayed "No noteworthy changes" beside the changed assessment. Keep a clear engine-flag fallback or align the display rule for substantial deviations without admitting trivial differences. No such conflict was found in the 10 generated daily profiles.
2. **P2 - map guard result was not propagated to surrounding location details.** `MovementMap.update` rejects identity/date mismatches, but `app.js` initially ignored its returned status and separately called unguarded `summarize` / `representative` for the distance figures, visit frequencies and itinerary. A contaminated record would hide the map while leaving its rejected location details visible. Handle `linkage_error` consistently for the whole location section; do not present rejected location data as paired evidence. The current clean generated bundle did not contain such a mismatch.
3. **P3 - complete-day coverage copy needed to follow the selected profile.** For the two complete generated profiles, home hours are derived from the itinerary, yet the route footnote initially called home time a separate input and described all visit histories as incomplete. Use coverage-specific wording. Partial first-eight-story coverage should retain its existing limits.

## Verification performed

- `tests/insights.test.cjs`: passed. Tiny differences, absolute/relative thresholds, zero references, missing values, policy immutability and full measurement retention.
- `tests/map.test.cjs`: passed. Same-person/subject/day/timezone rejection, stale-map teardown, reference exclusion, gap segmentation, offline policy and map-layer recovery.
- `python -m unittest tests.test_data_bundle`: all 6 tests passed. Deterministic generated data, exact original research record preservation, geometry, physical/time budgets and linkage fields.
- `tests/test-ui.cjs`: passed 342 render cases and interaction assertions.
- `tests/ui-release.test.cjs`: passed edge cases including invalid dates, missing observations, unavailable summary helper, storage denial and single-record histories.
- Independent audit of all 240 complete generated days: every walking leg starts/ends at its declared place, stay coordinates match the place, no itinerary teleports, and event times exactly reference the corresponding trip. Sofia visits four distinct destinations; Elias visits five.
- Isolated-day scenario: `sim-09` March 10 / Day 065 / index 64 returns index 0.72 with a one-day comparison and 0.00 with 7- or 28-day medians. Adjacent days return 0.00 in daily mode. This illustrates temporal aggregation, not diagnosed relapse or prediction accuracy.
- Across the initial one-period cohort audit, 22,850 observations had scores. The 8 noted display/flag conflicts were reproduced with exact UI reference selection as well.

## Limits

Generated health, location and context remain separate from real research participants. A complete generated itinerary is not measured 24-hour GPS. The index and display thresholds are uncalibrated demonstration heuristics. This review did not execute untrusted serialized datasets, alter research originals, access Supabase or certify visual appearance. Follow-up fixes must be rechecked before treating the findings as resolved.


## Follow-up: real StudentLife paired source

The additional StudentLife derivative was reviewed against the decoded source CSVs, without using its adapter in the independent tests. Repository metadata declares CC BY 4.0 for DOI `10.5281/zenodo.3529253`. The download manifest accurately says only selected ZIP members were retrieved; ZIP CRC and local SHA-256 were checked, not the complete archive MD5. Original RDS members remain preserved.

Independent checks in `tests/test_studentlife_review.py` passed all six tests:

- 49 source identities, 3,389 contiguous participant-day slots; 202,877 original location rows, 9,040 PAM responses, 1,644 Sleep submissions and 84 contextual PHQ questionnaires.
- All participant/day GPS counts and raw questionnaire fields match their same-UID CSV rows and UTC grouping. No cross-study identity joins. No displayed points fall outside their assigned UTC date.
- All 172,715 displayed location points match an unchanged source tuple of UID, timestamp, latitude, longitude and accuracy. Every displayed accuracy is within 0-100 metres; 194,376 original points pass the location-quality filter before display sampling.
- 9,575 displayed segments retain 1,900 singleton observations. Segments never cross excluded-point gaps, original discontinuities or gaps above 1,800 seconds. The largest retained connection speed is approximately 54.847 m/s, below the declared 55 m/s limit. This threshold is a plausibility screen, not evidence of walking; transport mode stays unknown.
- Health `values` and scored `metrics` remain empty. PAM codes are not converted into an invented mood score. PHQ pre/post text is preserved at participant level and never copied to daily labels or scored features. Sleep submission dates are not treated as verified sleep-night dates.

All PAM records contain a picture choice. Of 1,644 Sleep submissions, 254 contain entirely blank answers, preserved as missing fields. No day counted as paired GPS/check-ins has only blank health responses.

An initial adapter bug set `dayKey` to the date alone, causing every route to fail the shared identity guard. It was corrected to `participantId:date`; every rebuilt record now passes the guard. The initial default was a roughly 20-metre stationary location cloud. It was replaced with `studentlife-10`, 2013-03-30, selected for paired observations and usable map extent rather than clinical severity.

The first persisted test run collided with a live CSV rewrite and detected a truncated intermediate file. The adapter now writes generated CSV/JSON assets through atomic replacements. The stable rerun passes. This was an output-publication race, not a missing source-data claim.

## Final regression review

The two P2 findings are resolved. The final `ui-release.test.cjs` reproduces the actual `psyche-924` conflict and verifies the explicit "A change needs a closer look" summary. The final `studentlife-ui.test.cjs` verifies that rejected identity/date linkage suppresses the map's surrounding GPS details and removes GPS fields and places from exports. Clinical scoring is never invoked for the unnormalized StudentLife reports; the exported index and model version remain null and baseline status is unavailable.

Final independent rerun:

- `python -m unittest tests.test_studentlife_review`: **6 passed**, including a lookup against the preserved original Sleep questionnaire options. Defined duration/quality labels match the codebook; code 0 remains unmapped. Raw answer codes are retained, and the submission date is not asserted to be the sleep-night date.
- `node tests/studentlife-ui.test.cjs`: passed real-source selection, daily navigation, raw-code scoring abstention, same-person map selection, exports, rejection redaction and missing diary days.
- `node tests/ui-release.test.cjs`: passed including the flagged-but-filtered real research regression.
- `node tests/test-ui.cjs`: **342 render cases passed**, with interaction/export/playback and missing-data assertions.

The complete generated profiles now describe home time as derived from their timelines. A minor residual generic visit-frequency footnote was sent to the UI agent for coverage-specific wording; it does not affect data or calculations. No remaining functional blocker was found in this review. Browser visual review remains the main agent's responsibility.
