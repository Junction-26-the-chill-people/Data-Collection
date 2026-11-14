> UPDATE: A licensed accessible StudentLife derivative has now been decoded:202,877 recorded GPS points and same-participant mood/sleep check-ins. See [StudentLife source and integration](studentlife.md). Earlier unavailable-source conclusions below are retained as dated research history and are superseded by this result.

# Follow-up: location and health linkage evidence

Audit date: 14 November 2026. This extends `location-dataset-audit.md`; it does not change the demo UI, clinical bundle or synthetic GPS explorer.

## Recommendation

**Corona Health is the strongest newly verified open source for same-study regional location plus repeated mental-health questionnaires. It is not a source for walking routes.** Its coordinate precision and collection frequency make home/street/routine reconstruction inappropriate. Keep the generated Helsinki street trajectories for the hackathon narrative, and keep external synthetic GPS trajectories in their independent evidence lab.

For future longitudinal movement-feature research, GLOBEM is a credible access-controlled option. For real detailed GPS with pre/post PHQ, StudentLife remains a plausible candidate, but the official site remains unreachable here and its dataset-specific redistribution terms have not been verified. None of these sources should be joined to PSYCHE-D people, or used to claim a validated relapse detector from the current prototype.

## Newly verified: Corona Health v2

Primary sources:

- [Dataset repository, DOI 10.23728/b2share.cgf63-kme28](https://b2share.eudat.eu/records/cgf63-kme28)
- [Official repository API metadata](https://b2share.eudat.eu/api/records/cgf63-kme28)
- [Original data descriptor](https://www.nature.com/articles/s41597-026-07015-7)

The descriptor documents GPS only at questionnaire submission, rounded to 0.1 degree for privacy, with a shared anonymous `user_id`. It describes mental-health instruments including PHQ-9 and Android app-use data. This supports regional/contextual research, not continuous path reconstruction. Approximate 0.1 degree latitude spacing is 11 km; longitude spacing depends on latitude. Do not plot these observations as precise streets or infer that a person stayed home between submissions.

The official API independently verifies **CC BY 4.0**, public file access, version v2, published 5 February 2026, record revision 4. Seven repository files total 28,784,937 bytes. We downloaded only four CSVs totaling **3,801,848 bytes**, verified every publisher MD5, and recorded local SHA-256. App-use CSVs and the XLSX codebook were not downloaded in this bounded audit. No additional dependencies or serialized object loading were used.

Saved evidence is under `E:/Junction26/datasets/location_sources/corona_health/`:

- `record.json`: exact official metadata, file links, rights and checksums.
- `download-manifest.json`: four file sizes, publisher hashes, local hashes and source URLs.
- `raw/`: four immutable downloaded CSVs.
- `schema-audit.json`: actual field names, row counts, missingness, coordinate checks and PHQ item-value counts.
- `linkage-audit.json`: measured same-person temporal offsets; no inferred timestamp correction applied.

### Actual files inspected

| File | Bytes | Rows | Unique user IDs | Observed usable fields |
|---|---:|---:|---:|---|
|GPS_Baseline.csv|131,304|4,243|2,704|user_id,sensordata_collected_at,sensordata_altitude,sensordata_longitude,sensordata_latitude|
|GPS_EMA.csv|370,616|11,541|1,488|Same five fields|
|Baseline.csv|966,914|2,704|2,704|user_id,collected_at,phq9_a..phq9_i plus other survey/context/device fields|
|EMA.csv|2,333,014|11,541|1,488|Same identity/time/PHQ item fields plus repeated survey/context/device fields|

Every GPS row's user ID appears in its corresponding survey file. This establishes study-internal identity linkage; it does **not** establish an unambiguous survey-instance join. PHQ raw items are 0, 1, 2, 3 or blank. All nine are present in 2,691 baseline and 11,479 EMA rows. We did not calculate or classify participant PHQ totals, check codebook wording, identify clinical episodes or estimate predictive performance.

### Important problems discovered in the actual CSVs

| Check | GPS baseline | GPS EMA |
|---|---:|---:|
|Finite in-range coordinate pairs|3,185|9,031|
|Rows with missing/nonparseable coordinate pairs|1,055|2,501|
|Rows with out-of-range coordinates|3|9|
|Users with at least one valid coordinate pair|1,979|1,190|
|Valid pairs lying on the 0.1 degree grid|3,185|9,031|
|Duplicate valid-coordinate(user_id,timestamp) rows|1,205|41|
|Exact(user_id,sensor time=survey time) row matches|0|0|

All finite accepted coordinates match the stated coarse grid. Twelve rows contain impossible latitude values, such as values less than -90 or greater than 90; these were counted and excluded from usable coordinates, never automatically swapped/corrected. Baseline GPS rows substantially exceed baseline questionnaire rows, including repeated valid identity/time keys. A one-row-per-person GPS join would duplicate or arbitrarily discard observations.

The actual CSV timestamp format is `DD.MM.YYYY HH:MM`, with **no timezone suffix**. For each timed GPS observation, we measured the nearest survey timestamp for the same user:

- Baseline: 2,315 offsets are exactly +120 minutes, 1,072 are +60 minutes, one is +3,033 minutes.
- EMA: 5,131 offsets are +120 minutes and 4,645 are +60 minutes; other offsets also occur.
- Median absolute nearest-survey offset is 120 minutes in both files.
- None of the valid coordinate observations match a survey within five minutes before any correction.

A UTC-versus-local/DST mismatch is a plausible **inference**, not a verified source convention. We did not shift times to force agreement. The EMA file happens to have the same user ID at each corresponding row position as GPS_EMA, but there is no explicit response-instance ID in these CSVs; positional order is not a durable join contract. Further integration needs timezone confirmation from documentation/code or the authors, deterministic duplicate handling, and verified participant/time matching. Do not simply join on `user_id` alone: repeated assessments would produce a many-to-many expansion.

This source can eventually support a region/mood/app-use research branch. It cannot measure walks, exact visited places, GPS-derived home dwell, or continuous daily travel. Its pandemic context also limits transfer to ordinary routines. Missing permission and missing coordinates must not become evidence of staying home.

## StudentLife official retry

We retried the official [dataset page](https://studentlife.cs.dartmouth.edu/dataset.html), [homepage](https://studentlife.cs.dartmouth.edu/) and [original paper](https://studentlife.cs.dartmouth.edu/studentlife.pdf) through the web tool. We separately retried HTTPS/HTTP dataset-page GET and archive HEAD using Python urllib with a 20 second timeout. Each direct request timed out. No archive or mirrored dataset was downloaded.

The [published StudentLife GPS/PHQ analysis](https://pmc.ncbi.nlm.nih.gov/articles/PMC5361882/) independently documents 48 students, approximately five-minute GPS sampling over 10 weeks, and PHQ-9 at baseline and follow-up. This is primary evidence for that analysis's same-person GPS/PHQ linkage, not a current source-file/schema audit. Importantly, it does **not** establish daily PHQ or clinically adjudicated relapse onsets.

Third-party R package metadata advertises a GPL license for its software; this is not evidence of the original dataset's license. Secondary mirrors and article CC licenses likewise cannot settle redistribution rights for original GPS files. We therefore leave exact released GPS column names, present download size, dataset-specific terms and live availability **unverified** rather than promote a mirror as authoritative.

## Other credible routes and their limits

| Source | Primary evidence verified | Actual availability conclusion |
|---|---|---|
|[GLOBEM1.1](https://physionet.org/content/globem/1.1/)|Same-study wearable/survey data and location-derived features such as home time,distance,radius of gyration and entropy. Credentialed Health Data License 1.5.0.|Potentially useful after credentialed access; public metadata does not establish a downloadable raw geographic route stream. No files downloaded.|
|[RADAR-MDD mobility study](https://mental.jmir.org/2022/3/e34898)|Phone location sampled about every 10 minutes, PHQ-8 every two weeks; coordinates obfuscated with a participant-specific reference.|Same-person longitudinal location/symptom evidence, but obfuscated coordinates cannot be placed on actual streets. No unrestricted dataset license or download established here; no files downloaded.|
|[Remote depression trials data descriptor](https://www.nature.com/articles/s41597-022-01633-7.pdf)|Raw GPS cannot be broadly shared; released intraday geospatial summaries support behavior/context analysis.|A feature-research candidate, not a raw street-route source. No files or access authorization claimed.|

## Next integration steps, if this source is selected

1. Keep a dedicated `corona-health` study namespace and immutable source hashes; do not attach records to existing demo or application identities.
2. Confirm timezones and response linkage before a temporal join; establish explicit duplicate/conflict policies and leave unresolved records unmatched.
3. Verify the questionnaire codebook before computing any totals; preserve missing items and source scales.
4. Treat coarse coordinates as uncertain regions at survey times. Never connect them into walks or substitute them for missing smartwatch/GPS streams.
5. Evaluate any predictive analysis on held-out participants and future time, with calibration, missing-data reporting and independently defined endpoints. Current ingestion checks are not clinical validation.

No UI bundle, demonstration score or clinical source was modified during this follow-up.


## Follow-up after the explicit same-person GPS + health requirement

The additional GPS-only download was stopped before adapter/UI integration when the requirement changed. The official [UCI Go!Track GPS Trajectories](https://archive.ics.uci.edu/dataset/354/gps+trajectories) archive is small and licensed CC BY 4.0. Its documented fields include latitude,longitude,track_id and time (GMT-3), but it describes car/bus journeys and traffic ratings, not health. A 220,824-byte ZIP and contained RAR were saved; archive membership was listed, but CSVs were not extracted or joined to any health records. HTTPS failed because the server certificate was expired; the public official HTTP URL worked. Local SHA256/ZIP CRC are recorded, but there is no verified publisher checksum or authenticated transport for this download. Treat it as an archived GPS-only candidate, not a newly approved clinical source.

Two additional primary-lab repositories were checked:

- [Human Rhythms, UVA](https://github.com/HAI-lab-UVA/Human-Rhythms-Dataset), repository tree revision `3fe83300ca9726a1ff6755d235347bc63a976022`: participant-keyed Fitbit and survey folders exist, but the documented cleaned raw AWARE folders do not include locations. The location directory is under `Processed_Data/Behavioral/Aware/Locations`; it is not evidence of released raw coordinate tracks. The README grants academic use and distinguishes external COVID/weather licenses; do not apply those external CC licenses to the entire participant dataset. No study data downloaded.
- [EmoPhone, KAIST](https://github.com/Kaist-ICLab/EmoPhone/blob/main/DATASHEET.md), repository tree revision `8152168ee9f62f5074676eefebb434fb796f834c`: its datasheet describes same-participant affect/sensor windows, explicitly says raw participant CSVs are not public, and documents participant-specific longitude offsets. It cannot support authentic street-aligned routes without an unsupported reversal of the masking. No study data downloaded.

No verified new freely usable full-coordinate + health stream was found in these additional primary sources. The immediately available full-coordinate/health pairing is the explicitly generated participant scenarios. Expanding those scenarios can honestly supply more varied, complete days: generate the location trips and health measurements together under the same fictional identity and time axis, preserve declared simulation provenance, and never relabel GPS-only research subjects as observed mental-health patients. Corona Health remains a separately namespaced real, coarse-coordinate/survey source with unresolved time conventions.
