# Portable routine-change engine

**Current model: routine-change/2.1.0.** See [Ongoing patterns (2.1.0)](#ongoing-patterns-210) for independent episode hysteresis. The [Alerting (2.0.0)](#alerting-200) section defines current daily states and adaptation defaults. The numerical scoring foundation below remains shared; the old 20/50 status labels and opt-in adaptation defaults apply only to monthly or unspecified-cadence data. The versioned 1.x sections are historical compatibility notes.

`engine.js` has no dependencies, DOM, network, dates, randomness or storage. It exports `RoutineEngine` as a browser global and CommonJS for Node. Open the demo directly from disk, or run `node analyze.cjs data/demo-data.json output.json [participant-id]` with an installed Node runtime; npm is not needed. Check the actual data filename before running. Tests: `node tests/engine.test.cjs`.

## Input

Call `RoutineEngine.analyze(records, options)`. Each ordered record has `{period, values:{metricId:number|null}}`. Supply metrics `{id,label,unit,direction,floor,weight?}`, explicit `baselineIndices`, `baselineLabel`, and integer `windowSize`. Options default to at least 3 baseline observations (7 when granularity is day), 2 comparable metrics and 60% observation coverage. Explicit minBaseline=1 allows a single-point exploratory reference with variabilityKnown=false and a low-evidence warning. `direction` is lower/higher/both. A floor is a strictly positive scale in that metric's own units; its choice is a heuristic modeling assumption, not a validated clinical threshold.

Inputs must be ordered in actual observation time and use equally comparable observation periods. Monthly aggregates remain monthly; three monthly samples cannot establish a daily routine. Irregular intervals require preprocessing rather than pretending array positions represent equal elapsed time. Bedtime requires circular normalization before scoring; raw clock hour must not be treated linearly across midnight. Use source-defined units and exclude outcome/PHQ labels from scored features.

## Reference and rolling window

The baseline is explicitly selected, not inferred from the absence of measurements. Store whether it was user-confirmed well or only a provisional historical reference. Three observations is a demonstration minimum, not a claim of adequate clinical calibration. The anchored baseline median and median absolute deviation (MAD) remain frozen. Optional slow reference adaptation is described below and preserves the anchor. Scale = max(1.4826 * MAD, configured metric floor), preventing a flat reference from creating division by zero.

A monitoring window contains the most recent N observations strictly after the final baseline index. Earlier unselected observations are not scored. An incomplete window returns collecting_window. Missing/nonfinite values are excluded, never converted to zero. Each metric needs sufficient baseline count and coverage plus adequate window coverage. Coverage describes populated observations in this supplied matrix, not raw sensor wear-time or truthfulness of the measurements. Input missingness flags from providers must be honored during preprocessing.

Current level is the monitoring-window median. Directional deviation is max(0, adverse-direction difference / baseline scale). Per-feature index is 100 * clamp((deviation - 1) / 3, 0, 1). The total is the weighted mean over eligible features. Undercovered windows return a null score. Available-feature composition can change across windows; inspect contributor/coverage changes before interpreting score differences. Correlated features can double count behavior; choose weights/domains deliberately. These constants and feature choices are unvalidated hackathon heuristics.

Outputs: baseline centers/scales; per-record status, null or 0-100 behavior-change index, observation coverage, window indices, contributors (current/reference/delta/relative change/deviation/index) and explanation. Labels: no_change <20; change_detected 20-49; review_suggested >=50. None is a diagnosis, calibrated relapse probability, emergency assessment or automatic nudge command. `no_change` only describes measured features and cannot establish wellness.

## Integration

`analyze.cjs` reads normalized JSON, selects one participant, and emits the analysis plus a `wb_assessments`-compatible semantic envelope. It does not fabricate application UUIDs or absolute timestamps from study-relative months. A server must establish user identity, register the model UUID, map valid window timestamps, check consent, and supply these required fields before inserting. `confidence` remains null because a clinical probability is not estimated. `data_coverage` is explicitly observation completeness. Source participant IDs must remain separate from real app users.

## Android

The exact dependency-free engine can run offline inside an Android WebView, with the native layer supplying normalized JSON and receiving JSON results. A Kotlin port needs median, MAD, coverage filtering and the documented arithmetic only. Keep the test vectors and constants identical; use nullable doubles and reject nonfinite values. Android collection permissions, Health Connect/watch integrations, persistent storage and consent controls are separate application work.

## Verification

The test suite covers stable flat baselines; sustained directional change; missing/NaN/infinite samples; insufficient metrics; incomplete windows; improvement in a one-sided metric; resistance to one outlier in a three-observation window; preventing future baseline leakage; invalid configuration; partial coverage; and input immutability. Validation of depressive relapse prediction requires a separately designed participant-held-out, temporal evaluation and clinical review. This implementation does not make that claim.

Indexed-period safeguard: if every monitoring record supplies numeric `periodIndex`, indices must advance consecutively by one; a gap returns insufficient_data. Without period indices, windows explicitly count observations and the caller must ensure comparability. A completely missing latest observation also forces abstention even if earlier window values are present.


## Adversarial review, model 1.0.1

The seeded regression suite (`tests/engine-adversarial.test.cjs`, seed `0x713A2`) exercises malformed inputs, duplicate/out-of-order/mixed period indices, empty/future reference selections, prototype-like metric names, stale individual features and extreme arithmetic. Four hundred generated scenarios check unit conversion invariance (values and floors scaled together), temporal-prefix invariance, independence from outcome labels, input immutability and bounded finite results under missingness. Uniform stronger adverse movement is checked for monotonic score behavior.

Concrete corrections: periodIndex is now all-or-none and strictly increasing safe integers; records/values and metric definitions are validated; measurement magnitudes beyond safe arithmetic are rejected; metadata keys cannot alter object prototypes; an individual feature must have a valid current observation to contribute (previous periods cannot fill an absent current signal). Optional metric min/max bounds reject physically invalid values when configured. These bounds express data validity, not clinical thresholds. Caller-supplied raw zero remains a real zero: upstream missing-value sentinels must be normalized to null.

The CLI now honors dataset default window size, participant-specific metrics and cadence, and exports explicit synthetic provenance. Daily synthetic profiles are illustrative scenario tests, not additional clinical training evidence. Each cadence needs a matching ordinal periodIndex and chosen window size; raw date-string sorting, source alignment and physical unit normalization belong in the adapter.

Correlated features can still double-count a common cause (e.g. sleep duration and short-night counts). No universal correlation correction was fitted from these data; weights and feature composition remain explicit heuristic assumptions. Scores from differently configured metric sets should not be ranked as comparable clinical danger. A selected baseline can also be inappropriate despite satisfying numeric checks; its provenance must remain visible.


## Adaptive reference and context, model 1.1.0

`score` stays 0-100 for compatibility. `normalizedIndex` and `relapseVector` are scalar aliases `score/100`, bounded 0-1, not a calibrated clinical probability or a mathematical multi-axis vector. Feature-level directional contributions remain available. Higher steps or mood do not increase one-sided lower-direction concern; return toward the reference lowers concern. Metrics with direction both intentionally flag either side (such as unusually short/long sleep); context still needs interpretation.

Enable adaptation explicitly with `adaptive:true`. Defaults: `adaptiveWeight=.15`, `adaptiveAlpha=.1`; the blend weight is capped at .25 so the original anchor remains dominant. For each monitoring window, only observations after the reference end and strictly BEFORE the monitoring-window start are eligible to train an EWMA. No current/future measurement trains its own reference. The effective reference is `(1-weight)*anchor + weight*EWMA`; scale remains the anchored MAD/floor. Missing measurements, confirmed-context observations, and observations with an adverse anchored standardized deviation greater than one are skipped. This gate freezes strong adverse shifts above one anchored scale; small sub-threshold shifts may enter the low-weight reference, so it does not establish that adaptation is clinically safe. A durable intentional change can require an explicit reviewed reference reselection; the engine does not silently normalize it.

`point.adaptation` exposes enabled/weight/alpha, per-feature anchor/EWMA/effective references and every accepted/frozen candidate with index, reason and before/after values. `anchoredScore` is the fixed-reference score. `rawScore` is the adaptive-reference score before contextual adjustment. These are always available alongside the final index when data suffices.

Context input is `record.contexts=[{type:'illness'|'recovery'|'intentional_activity_change',confirmed:true,source:'user_report'|'synthetic'}]`. Unconfirmed/source-less context is ignored. No illness is inferred from steps, sleep, heart rate or weight. Confirmed context always freezes adaptation for those observations. Context attenuation is neutral by default (all weights 1). An explicit exploratory caller configuration may use illness .5, recovery .75 and intentional_activity_change .5. Context is metric-scoped and proportional to overlap. Illness/recovery apply only to steps, sleep_hours, sleep_efficiency, bedtime_hour, heart_rate and home_hours. Intentional activity change applies only to steps, home_hours and heart_rate. Mood is never attenuated. For each feature and each observation with a valid feature value, take the lowest explicit weight among applicable confirmed contexts (strongest attenuation, applied once); observations without applicable context use 1. Average those factors over the full comparison-window length, multiply that feature score by the result, then compute the usual weighted aggregate. Thus one illness day in a seven-day window with weight .5 produces a feature factor 1 - .5/7, not .5. This remains a heuristic, not a causal explanation. The effective aggregate ratio is exported as point.contextMultiplier; per-feature contextMultiplier, adjustedScore and appliedContexts are retained. Status uses max(anchoredScore, rawScore), never the context-adjusted aggregate. These values are visible heuristic settings, not evidence that illness explains a person's changes. All weights=1 disables score attenuation while preserving the freeze. Status and its explanation use the larger of raw/anchored scores, never the context-attenuated value: context cannot downgrade an observed change into no_change. `point.index` remains the ordinal record index for backward compatibility. Raw/anchored scores and complete context provenance must stay visible in the UI/export so adjustment cannot conceal the original change.

`referenceEndIndex` optionally marks the end of an explicit selected reference span, including trailing missing calendar slots. It must be at/after the final selected baseline record. Monitoring begins after that end. `baseline.quality`, `warning` and `variabilityKnown` must be shown: a one-point reference estimates no variability, so the configured scale floor drives its numerical result. It is exploratory and must not be presented with the same evidential strength as a longer reference.

Adaptive regression tests cover current-window exclusion, no future leakage, long sustained-change freeze, confirmed-context freeze, fixed versus adaptive score preservation on adverse shifts, confirmed/unconfirmed/source-less context handling, disabled attenuation, directional improvement/recovery, short-reference caution and trailing missing reference boundaries. The selected heuristic parameters have not been optimized or clinically validated.


## Alerting (2.0.0)

Model `routine-change/2.0.0` adds a chronological pattern layer for **daily** records. Its flags mean *patterns worth a check-in*, not relapse probabilities, diagnoses or validated clinical alerts. The original robust anchor, feature-score arithmetic, metric floors, nullable scores, coverage, contributor meanings and chosen comparison-window medians remain in use. Monthly and unspecified-cadence inputs retain the 1.x numerical/status behavior; their additive `alertState` maps legacy no_change/change_detected/review_suggested to steady/watch/flag_sustained. `result.alerting.enabled` and effective config.enabled are false for those cadences. StudentLife's raw unscored path remains outside this engine.

### Entry point, fields and chronology

`analyze(records, options)` remains the sole analysis entry point. `ALERT_DEFAULTS` is exported and recursively frozen. An optional `options.alerting` object overrides its documented defaults; `enabled:false` selects legacy behavior. Configuration is copied and validated, never mutated. Invalid nested objects, duplicate metric/domain assignments, invalid probabilities or inconsistent/unbounded windows throw.

The existing numeric point computation is retained as `computePoint`. A second strictly chronological pass computes independent one-day evidence, selected-window scores using a reference trained strictly before that window, adaptation and alert states. This resolves an ambiguity in the specification: **seven overlapping multi-day display windows are not seven independent abnormal days**. Persistence always counts `daySignal`, while existing `score`, `contributors`, `coverage` and `windowIndices` retain the selected-window meaning. The daily timeline may plot `daySignal.score`; the numeric selected-window index remains available. `daySignal` contains score, normalizedIndex, anchoredScore, rawScore, coverage, observed and contributors.

Each daily point adds:

- `alertState`, `alertReason` (single_day, emerging, k_of_m, drift, or null).
- `persistence`: window, observedDays, highDays, flaggedDays (alias), threshold, k, and unadjustedHighDays.
- `drift`: triggered, distinct qualifying domains, and per-metric anchorMedian, recentMedian, change, zAnchor, slopePerDay, mkP, adverse, qualifies, domain and observedValues. Compatibility aliases z and slope are also present. `qualifies`, not merely the slope sign, controls a clinical-table checkmark.
- `anchorBaseline`: immutable selected-reference medians.
- `baselineUsed`: blended effective reference used for this selected window. `adaptation.metrics[id].effective` remains the same used value.
- `effectiveBaseline`: effective reference after processing this day, eligible to score future days, never this day itself. `adaptation.nextUpdate` describes that day's update/freeze; existing adaptation.updates contains only candidates strictly before the displayed window start.
- `unsuppressedAlertState`, plus contextSuppressed/contextNote where applicable.

`result.alerting` contains version, enabled, the effective configuration, firstFlagIndex and firstFlagState. Effective alpha/weight/enabled are reported under its adapt config as well as the original result.config. The CLI passes these fields through in analysis and integration evidence (schema_version1.3.0, including ongoing_pattern in 2.1.0).

### Default configuration and rationale

| Setting | Default | Interpretation |
|---|---:|---|
| Daily alerting | enabled | Monthly behavior is unchanged |
| Tolerance | directional z <=1.0 | Only nearby observations may train the reference |
| adaptiveAlpha | .05 for daily alerting | Small EWMA step; explicit existing options override it |
| adaptiveWeight | .15 | Existing blend against the frozen anchor |
| Maximum blend | .25 | Validation retains anchor dominance |
| Drift cap | max(.5 * anchor scale, .10 * abs(anchor median)) | Bounds raw EWMA displacement on either side of the anchor |
| Noted | index >=.35 | A single harder day, without a pattern flag |
| Sustained | >=5 high days in7 calendar slots | Repeated evidence |
| Minimum observed | 4 of7 calendar slots | Conservative abstention with sparse observations |
| Watch | >=3 high days in7 calendar slots | An emerging pattern |
| Drift recent window | 14 observed values per metric | Robust recent level versus the frozen anchor |
| Trend window | 28 observed values per metric | Short longitudinal trend estimate |
| Drift deviation | anchored directional z >=2 | Change beyond the reference's robust scale |
| Trend significance | two-sided MK p <.05 | Heuristic monotonic-trend evidence |
| Required drift domains | 2 | Correlated sleep measures count once |

The sustained and watch windows must have the same length. Configuration cannot reduce sustained/watch counts or minimum observed days below two, preserving the rule that one day cannot create a pattern state. Values come from calendar slots t-m+1..t after the reference end, not the last m available readings. When periodIndex is supplied, the lower bound is current periodIndex-m+1, so omitted calendar rows cannot be counted as adjacent days. Without periodIndex, callers must supply a complete daily grid with explicit missing rows. Missing days neither increase highDays nor count as normal days. Fewer than four observed days yields insufficient_data, even when the few available values are high. This conservatively resolves the prompt's conflicting priority list versus explicit sparse-data test. A current missing/undercovered observation never yields a fresh pattern flag.

The configured relativeMin map uses **steps as a fraction of the anchor median** (.25); every other entry uses an **absolute difference in that metric's native units**: sleep_hours1h, sleep_efficiency5 percentage points, bedtime_hour1h, heart_rate5bpm, mood.8 scale points, home_hours2h, active_days2 and short_sleep_nights2. Callers converting units must convert absolute minima as well as values/floors; scaling floors alone cannot preserve a threshold explicitly expressed in hours or mood points. Unknown metrics have no default drift domain and cannot count toward a multidomain flag until assigned one. If a configured domain contains an unknown metric without a relativeMin entry, its absolute minimum defaults to zero; integrators should always supply a meaningful minimum in the metric's units as well as its domain.

Domains are sleep (sleep_hours, sleep_efficiency, bedtime_hour, short_sleep_nights), activity (steps, active_days), mood (mood), physiology (heart_rate), and place (home_hours). Default drift needs two domains. With a stricter configured minMetrics, mood plus another domain remains an alternative as requested. A single domain can never trigger drift.

### Adaptation safeguards

The anchor statistics never change: median, MAD and scale=max(1.4826*MAD, floor). Daily adaptation defaults on; an explicit adaptive:false disables updates without disabling pattern analysis. The raw EWMA starts at the anchor. It updates only when the day is observed with sufficient comparable feature coverage, all available eligible metrics are within the directional tolerance band versus the effective reference, no confirmed illness/recovery/intentional context covers that day, and neither the previous nor current state is watch/flag. Missing, context, alert and out-of-band days freeze it. A hard day never trains itself into normality.

For an accepted value, EWMA=(1-alpha)*EWMA+alpha*value. Following the literal requested pseudocode, raw EWMA is clamped to anchor +/-cap, then the existing adaptiveWeight blend is applied: effective=anchor*(1-weight)+EWMA*weight. Thus effective movement is at most weight*cap; a final cap is retained defensively. Favourable drift is bounded too. Metrics with direction both use absolute deviation for tolerance. Effective values used to score a day/window contain no observations from that day/window or any future time.

### Persistence, context and drift

High-day evidence uses the larger anchored/unadjusted daily signal, protecting it from numeric context attenuation. State precedence is current abstention/reference/collecting conditions, then drift, sustained, watch, noted, steady. `steady` and `noted` map to status no_change; watch maps to change_detected; both flags map to review_suggested. Existing non-assessment statuses keep their names. A displayed comparison that is still collecting remains collecting_window even though independent daily evidence is available.

When confirmed illness or intentional_activity_change covers at least half the last7 calendar slots, Path A recounts high days using only mood-domain feature evidence at or above35/100. Mood is never suppressed. If an otherwise sustained pattern drops below that state, contextSuppressed=true and the original evidence stays visible through unadjustedHighDays, unsuppressedAlertState, anchoredScore and rawScore. This explicitly reconciles two conflicting requirements: the requested illness/no-mood test requires suppressing a Path A flag, while the instruction to retain the stronger anchored/unadjusted signal forbids hiding the underlying evidence. Numeric context attenuation never erases that evidence. A suppressed behavioral pattern is not evidence of lower clinical relapse risk.

Drift is never suppressed by context. Each eligible metric uses its most recent14 observed values after the anchor, and a Theil-Sen median pairwise slope from up to28 observed values. Record periodIndex is used as x where supplied, preserving elapsed gaps. The two-sided Mann-Kendall test uses tie-corrected variance and continuity correction; fewer than10 values yields p=1. A metric qualifies only if its current measurement is available, recent anchored z and absolute/fractional minimum pass, the slope is adverse, and p<.05. For direction both, slope must point away from the anchor on the side of the recent median. Current missing features cannot become fresh drift evidence from old readings.

### Verification and limitations

`tests/engine-alerting.test.cjs` covers an isolated noted day,5of7 sustained,3of7 watch, missing days, slow drift, one-domain sleep rejection, context/mood protection, capped adaptation and freezes,50 future-prefix perturbations, frozen inputs, explicit unit conversion, known Theil-Sen/MK values, configuration validation and legacy status mapping. The deterministic stable-noise experiment uses400 series; the initial run produced0/400 flagged series. This is a test-fixture result, not an estimated clinical false-positive rate or external validation. The slower1.5%-per-week steps/.1-point mood test needs a longer220-day series; its first drift flag occurs around index152 because the explicit25% steps threshold cannot be reached by day100 at that rate.

Autocorrelation, multiple comparisons, changing sensor availability, arbitrary reference selection and overlapping trend windows violate simple inferential assumptions. MK p is heuristic evidence, not a calibrated clinical significance claim. Fixed floors, domain grouping, change minima and state thresholds require calibration against independent outcomes and participant-held-out temporal evaluation. Early warnings are not guaranteed; persistent flat deterioration may later move from drift to sustained when the monotonic trend fades. Confirmed illness can still trigger Path B, intentionally, so context must remain visible. No outcome labels train these rules.

## Ongoing patterns (2.1.0)

The daily score, alertState, persistence, drift, context rules, baseline adaptation and legacy status mapping are unchanged. An independent chronological episode layer prevents a previously flagged pattern from disappearing after one calmer observation. It never feeds back into those computations. One harder day or watch alone cannot start an episode.

Let H_t = max(daySignal.anchoredScore, daySignal.rawScore) / 100. A daily flag_sustained or flag_drift starts/continues the episode and resets its calmer-day count to zero. While active, an observed, non-flagged day increments the count only if H_t < 0.20 and drift.triggered is false; any other observed day resets it. The third qualifying observed day clears the episode. Missing or undercovered observations pause the count and retain the prior episode; they do not imply recovery. This means consecutive *observed* days, potentially separated by gaps. A long gap leaves a stale earlier pattern visible alongside current insufficient_data, not a fresh alert.

`ALERT_DEFAULTS.hysteresis = {clearBelow: 0.20, observedDays: 3}`. The lower clearing threshold provides hysteresis relative to the 0.35 noted/sustained threshold. clearBelow must be finite, positive and strictly below both configured entry thresholds; observedDays must be an integer from 2 to 366. Three calmer observations is a demo continuity heuristic, not evidence of clinical recovery. Persistent moderate deviation or a flat adverse state can keep an episode active even after the trend test ceases to flag; this is intentional. There is no automatic expiry and no clinical calibration.

Each daily point adds `ongoingPattern`: active, startedIndex, lastFlagIndex, lastFlagState, recoveryDays, clearedIndex, clearAfter, clearBelow and observed. Indices refer to the current analysis record array. Before any flag the indices/state are null; after clearing the most recent episode metadata and completed count are retained. A subsequent flag starts a new episode. Snapshot objects are independent; no future observations mutate earlier points. Anchor points have inactive snapshots; monthly or disabled alerting has null. Changing the displayed comparison window does not change this daily episode history, including while that window is still collecting. Changing the selected anchor reanalyzes the history.

The viewer shows an earlier-pattern notice in both views while active, with the observed calmer-day count or an explicit missing-data pause. Today's status, orb and care card still follow the daily alertState. Export 1.3.0 adds the episode object; component-signal/0.1.0 and combined-preview/0.1.0 semantics remain unchanged.
