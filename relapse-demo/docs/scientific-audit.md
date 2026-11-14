# Full-cohort scientific audit findings

Run `tests/audit_full_cohort.py` for reproducible source, mapping, missingness and baseline checks. It reads published TSV definitions directly and does not fit a model or infer participant diagnoses. Machine-readable reports are `full-cohort-audit.json` (2,272long histories) and `all-history-audit.json` (all4,948histories).

Passed: all35,694real records retained exactly once;210,501finite metric mappings checked; all6,197padded month slots remain null; no duplicate participant/month IDs; six mapped metrics have no values outside broad logical bounds. Sleep_recent source range0..1200minutes, efficiency ratio.088608..1, bedtime adjusted hours12..35, step mean49.29..52048.93. Missing source values: steps20, recent sleep583, weekday efficiency1571, bedtime1489. Count metrics have no missing values, but absence of reported count missingness does not establish device completeness.

Important source limitations and counterexamples are documented in `data-notes.md`. Baselines with existing elevated symptom context, zero recorded sleep, correlated feature weighting and floor-dominated scale estimation prevent interpreting the index as relapse probability or absence of danger. Generated stable/withdrawal/travel/recovery stories validate software behavior only; their visual plausibility is not evidence of clinical accuracy.

The three bundle tests exercise many values across720synthetic days and all35,694real rows, rather than only UI smoke checks. They verify fixed-seed reproducibility, explicit provenance, sensor-gap nulls, physical bounds, fictional-route closure and unique source-row preservation. These are software/data checks and do not replace independent prospective clinical evaluation.
