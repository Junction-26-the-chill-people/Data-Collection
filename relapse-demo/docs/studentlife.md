# Recorded GPS and same-participant health check-ins

**Available now:** 49 source participant IDs, 202,877 recorded GPS observations, 9,040 photographic affect(PAM) responses, 1,644 sleep self-reports and 84 pre/post PHQ questionnaire rows. The daily viewer has 2,116 days with both accepted GPS and same-participant check-ins. These are observed study records, separate from generated demo stories.

## Source and access

[Daniel Fryer's StudentLife R-format derivative](https://zenodo.org/records/3529253), DOI 10.5281/zenodo.3529253, version 1.0.0, explicitly declares **CC BY 4.0** in [official API metadata](https://zenodo.org/api/records/3529253). Original study citation: Wang et al.(2014), *StudentLife: Assessing Mental Health, Academic Performance and Behavioral Trends of College Students using Smartphones*, DOI 10.1145/2632048.2632054. Credit both the original study and the derivative creator when sharing these data. This is an attributable derivative hosted by the peer-reviewed tooling author, not a claim that Dartmouth's unavailable server was downloaded.

The archive is 230,469,489 bytes. We fetched only four members through HTTPS byte ranges: `sensing/gps.Rds`, `EMA/PAM.Rds`, `EMA/Sleep.Rds`, `survey/PHQ-9.Rds` (3,106,977 uncompressed member bytes). Each ZIP member CRC and local SHA256 was verified. Version, ETag, Last-Modified and exact URLs are retained in `datasets/location_sources/studentlife_zenodo/member-manifest.json`. **The whole archive's publisher MD5 was not verified**, because the whole archive was not downloaded. Directory listing and original repository metadata are retained alongside it.

An initial 49,784-byte tooling test fixture provided useful schema/codebook checks but only 38 GPS points across three IDs. It is not the viewer's GPS source. The viewer uses the separately licensed full derivative GPS table.

## Exact linkage and fields

- GPS: `uid,timestamp,provider,network_type,accuracy,latitude,longitude,altitude,bearing,speed,travelstate`.
- PAM: `uid,timestamp,picture_idx`.
- Sleep: `uid,timestamp,hour,location,rate,social`.
- PHQ: `uid,type,Q1..Q10`, where type is pre/post. Responses remain source strings; no numeric total or daily PHQ is generated.

All modalities join only within this study's `uid` namespace. Epoch-second timestamps are retained as UTC ISO strings; the viewer groups by UTC date of the source response timestamp as an analysis convention, not an inferred participant-local timezone. Shared day membership does not imply simultaneous observation. Sleep asks about the previous night; the response's day is not a verified sleep-episode date.

The derivative contains 49 GPS/PAM/sleep IDs although the original paper describes 48 students. We preserve and report the actual file contents rather than silently remove a person. 46 IDs have PHQ data; unavailable questionnaires stay missing. No cross-study identity join is made.

PAM picture indices 1..16 remain categorical image-selection codes: they are not a 1..5 mood scale. Sleep codes retain raw fields with labels from the author's `EMA_definition.json`: hour 1 means '<3 hours', 2 means 3.5 hours, through 19 meaning 12 hours; code 0 is unmapped. Quality codes 1..4 mean Very good/Fairly good/Fairly bad/Very bad. We display these labels only, without manufacturing an exact duration for a censored answer or treating self-report as a wearable measurement. The codebook/provenance is saved as `sleep-codebook.json`.

## GPS quality and viewer selection

All 202,877 GPS rows remain in decoded CSV. 8,501 fixes with accuracy above 100m are excluded from the map; no invalid coordinate bounds were found. 194,376 points pass quality checks. We split rendering segments after excluded fixes, gaps above 1,800 seconds, non-increasing time, or implied speed above 55m/s. These are broad visualization filters, not walking or clinical criteria. 99 high-speed jumps and 2,983 long gaps were found. Transport remains unknown; no home location is inferred.

The compact viewer retains at most 80 original accepted points per UTC day, sampled uniformly in timestamp order including endpoints. Original breaks remain, and any new sampled gap above 30 minutes creates another break.172,715 points are displayed; 21,661 accepted fixes omitted for display remain in CSV. Point coordinates and timestamps are never interpolated or moved onto streets. Singleton segments remain points. These connecting chords are not certified travelled routes.

There are 3,389 participant-days, 2,822 with accepted GPS, 2,298 with check-ins, and 2,116 with both. No-GPS days mean unavailable observations, not staying home. Default StudentLife 10/2013-03-30 was chosen for check-in availability and a visible Hanover-area spatial extent, not clinical severity or representative-sample claims. Bounds:[-72.2910206,43.701573,-72.2839311,43.7055085].

## Reproduce and integrate

- `python scripts/studentlife_fetch.py`: fetch/verify only selected source members using saved official metadata; no R runtime.
- `python scripts/studentlife_data.py`: decode with established `pyreadr==0.5.3` and pandas, write all source tables to `datasets/location_sources/studentlife_zenodo/decoded/`, and produce `data/studentlife-data.js/json` plus `docs/studentlife-audit.json`. Generated writes use atomic replacement.
- Pyreadr is an established [official package](https://pypi.org/project/pyreadr/0.5.3/), licensed AGPLv3, used only for offline conversion. The binary wheel is pinned; it needs no R execution. Version 0.5.3 avoids adding the newer release's extra dependency.

`window.STUDENTLIFE_DATA` contains participants with metrics:[], records with values:{}, raw checkins and GPS trips. The app must abstain from a behavior-risk score for this source. `participantId`, `subjectId` and `dayKey=participantId:date` make linkage explicit; raw source IDs remain in participant metadata. The two source IDs in different studies must never be equated.

Independent tests verify every displayed point against its same-UID source tuple, all daily counts, segment gaps/speeds, map linkage keys and unscored questionnaires. This validates conversion and display integrity, not depression diagnosis, relapse prediction or prevention.


## Response timestamps, repeated rows and conflicting reports

A follow-up source audit confirmed that the [tooling author's EMA conversion](https://github.com/frycast/studentlife/blob/master/R/SL_tbl_load.R) renames original JSON `resp_time` to `timestamp`; it does not invent our displayed timestamps. All 752 PAM and 126 Sleep response timestamps in the three-person raw JSON fixture match the derivative after the documented numeric UID conversion. The source UID is assigned from the original participant filename slot before missing files are removed, rather than assigning new sequential IDs after filtering.

The timestamp is therefore best labeled **source response timestamp (UTC)**. Its underlying client-event semantics are not independently validated here: a burst could reflect repeated responses, recording behavior or batching. We cannot establish that every second-separated record describes a distinct instantaneous emotional state, nor that it is an independently verified upload timestamp.

The complete derivative contains:

| Source | Duplicate UID/timestamp groups | Extra rows sharing UID/time | Exact duplicate extra rows | Groups with conflicting values |
|---|---:|---:|---:|---:|
|PAM|93|107|22|81|
|Sleep|7|7|6|1|

StudentLife 10 on 2013-03-30 has 21 PAM records and 4 sleep records. Several different answers occur between 02:07:42 and 02:07:49 UTC, including exact repeated PAM rows. This pattern exists in the source tables, not in our adapter. The sleep question is retrospective: four recorded answers do not imply four separate nights, and conflicting durations must not be averaged into a fabricated nightly estimate. UTC day boundaries can also place daytime and prior-evening local observations on the same displayed day.

We retain every source row and its original code/time. No deduplication, conflict resolution, symptom-change inference or separate-night counting has been applied. The report is at `datasets/location_sources/studentlife_zenodo/response-timestamp-audit.json`, including source-code hash and per-fixture match counts. The actual day linkage is a source-identifier/calendar-day association, not proof of simultaneous measurement or clinically independent observations.
