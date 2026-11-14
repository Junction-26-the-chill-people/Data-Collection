# Location dataset audit - 14 November 2026

The original three requested studies do **not** provide usable geographic routes in the downloaded material. The Helsinki demo routes remain generated personal activity on actual OpenStreetMap pedestrian geometry. A new, separate **SYN-RoadGps coordinate explorer** uses an externally published synthetic mobility corpus; it is never joined to a clinical participant or used to validate depression detection.

## Evidence from the existing downloads

| Source | What was actually inspected | Geographic result | Health linkage and terms |
|---|---|---|---|
| [PSYCHE-D](https://zenodo.org/records/5085146) | Actual parquet schema: 154 columns, 35,694 monthly rows, 4,948 participants; source feature dictionary | No latitude, longitude, GPS or location fields. Steps/sleep monthly features cannot recover streets or visited places. | PHQ-related contextual labels exist; CC BY-NC 4.0. |
| [NFI FARED Digital Traces](https://huggingface.co/datasets/NetherlandsForensicInstitute/NFI_FARED_Digital_Traces) | All 7 pickle column schemas via non-executing static inspection and primitive numeric-buffer decoding; source README | Cache has ZALTITUDE,ZCOURSE,ZHORIZONTALACCURACY,ZSPEED,ZTIMESTAMP,ZVERTICALACCURACY, but **no latitude/longitude**. META_carrying_location is hand/pocket/rucksack placement. It cannot be plotted as a geographical route. | Activity labels, no depression outcomes; no clear redistribution license supplied. Originals were never unpickled. |
| [Finnish immigrants/Dryad](https://datadryad.org/dataset/doi:10.5061/dryad.qz612jmrn) | Official API metadata and local download registry; raw archive remains unavailable | Human-subjects statement explicitly says GPS was excluded. Do not describe this as a completed CSV audit. | 39 people, 28 days, wearable/EMA/survey data described; CC0; 1.86 GB expected archive, blocked download. |

Reproducible supporting files: `docs/nfi-data-audit.json`, `docs/all-history-audit.json`, `../datasets/dryad_metadata.json`, `../datasets/dataset-registry.json`. No inference of depression status, home address or mood is made from any unavailable location data.

## New downloaded synthetic corpus

[SYN-RoadGps by Smile1120](https://huggingface.co/datasets/Smile1120/SYN-RoadGps) declares [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Revision `482d9f29bbee8282626e5136f16924366bcf5f6e` is pinned. Its card describes generated road-constrained GPS sequences and says underlying real GPS records are not released. This is a publisher description, not independent validation or an endorsement of the source's scientific reliability. No publisher code or new software package was installed/executed.

Five originals, 63,171,951 bytes, are retained under `../datasets/location_sources/syn_roadgps/raw/`. Publisher LFS SHA-256 and Git blob SHA-1 were checked; local SHA-256 values, exact pinned URLs and sizes are in `../datasets/location_sources/syn_roadgps_download_manifest.json`. The CSV SHA-256 is `66e504de9fcbef38c7302ff3b0bc7ac7040ab6fbb91823d88fcbd5a05c27710e`.

Actual CSV columns are `gene_trace_road_id`, `gene_trace_datetime`, `gene_trace_rate`, `gps_list`. GPS tuples are longitude,latitude; timestamps are explicit UTC ISO strings. Decimal `np.int64(...)` wrappers in road IDs are narrowly stripped before Python `ast.literal_eval`; arbitrary expressions/calls are rejected. Within-segment ratios are validated in 0..1. No `eval`, pickle import or NumPy object loading is used.

The complete corpus - not just the viewer sample - contains:

- 10,000 trajectories and 546,273 points; 2 trajectories contain a single point.
- 536,273 consecutive point pairs; no non-increasing timestamps, repeated adjacent coordinates, invalid coordinate bounds or field-length mismatches.
- 1..83 second gaps, median 10 seconds; median 44 points/trajectory, range 1..328.
- 606 edges across 195 trajectories imply speeds above 55 m/s; maximum 222.91 m/s. Median 3.44 m/s does not support treating the corpus as walking-only.
- Longitude 116.517061..116.759364,latitude 39.732140..39.981072: southeast Beijing area. Publisher does not specify geodetic datum. Do not silently assume WGS84/GCJ02 or promise OSM alignment.
- Source roadmap has 60,681 IDs 0..60,680. Trace IDs extend to 142,502. 13,428 of 25,600 unique trace road IDs are absent from supplied geometry, affecting 272,951 points. Even numerically matching IDs are **not** verified as correct correspondences. No ID join or road map-match is exported.

Exact machine-readable results and thresholds are in `docs/location-dataset-audit.json`. These findings demonstrate ingestion/quality checks, not clinical validity. Road sampling chords may cut corners; retain that limitation even for apparently smooth traces.

## Viewer/export contract

`data/location-samples.js` sets `window.LOCATION_DATA` and has a JSON twin. It contains 50 trajectories: the first 50 parse-valid, multi-point source rows in original order, without ranking quality. This deterministic convenience sample is not representative of the corpus. 3,105 original coordinates/timestamps are preserved without smoothing or interpolation; the bundle is about 287 KB.

`source` contains title,url,license,revision,synthetic,clinicalLink:null and quality warnings. Each `trajectories[]` item contains id,sourceRow,synthetic:true,record{period,date,trips},summary{points,breaks,distanceMeters,durationSeconds},boundingBox. Each trip is an uninterrupted rendering segment with id,mode:`unknown`,points[{lat,lon,timestamp}]. Bounding boxes are[minLongitude,minLatitude,maxLongitude,maxLatitude].

Segments split at non-increasing timestamps, gaps above 300 seconds or implied speeds above 55 m/s. These are broad visualization-integrity thresholds, **not walking or medical thresholds**. Points are retained on both sides; never draw a connector across segments. Distance is the sum of drawn point-to-point chords excluding broken edges; duration spans first to last timestamp, including breaks. Single-point segments remain markers. `data/location-traces.json` retains per-point source road IDs/ratios and detailed break reasons. Its JS equivalent exposes `LOCATION_TRACES` for other integrations. Source `roadmap.geo`/`.rel` remain archived but are not included as trustworthy matched routes.

These are independent generated trajectories, not people with daily routines. There are no same-person mood, heart-rate, sleep, home/work labels or longitudinal relapse outcomes. The clinical demo dataset is unchanged. The separate explorer must default to coordinate view, with optional external-map use clearly described as datum-unverified.

Verify originals with `python scripts/location_download.py`; add `--download` only to restore missing pinned files (existing mismatches cause failure, never overwrite). Rebuild with `python scripts/location_dataset.py`; optional `--sample-count N`, `--output-dir PATH`, `--raw PATH`. Source CSV must match the pinned publisher hash. Run `python tests/test_location_dataset.py`. Tests verify all five original checksums, refusal to execute embedded calls, source point preservation, segmentation/recomputed counts, synthetic provenance and existing OSM polygon bounds. They do not validate real-world or clinical accuracy.

## Other official candidates assessed

| Candidate | Coordinates and clinical relevance | Access/license/size assessment | Decision |
|---|---|---|---|
| [Microsoft GeoLife](https://www.microsoft.com/en-us/download/details.aspx?id=52367) | Official page documents timestamped latitude/longitude/altitude,182 users, 17,621 routes; no mood/physiology linkage described. | 298.7 MB archive. Download page asks for citations; exact redistribution license not independently verified here. | Not downloaded: larger real-person alternative, user prefers synthetic. |
| [GLOBEM1.1](https://physionet.org/content/globem/1.1/) | Actual public feature description lists home time,distance,radius of gyration,location entropy and other derived features. It also describes wearable/survey data. This does not establish released raw latitude/longitude routes. | Credentialed access, PhysioNet Credentialed Health Data License 1.5.0. 497 unique participants across four studies; download size not verified. | Potential future feature/label research after access, not an open GPS route source. |
| [LifeSnaps original paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC9622868/) | Watch hardware has GPS, but documented EMA location is categorical(home/work/transit etc.). The paper alone does not establish released geographic trajectories. Wearable and mood/context self-reports coexist. | 71 participants, 71M data rows; article CC BY 4.0, dataset-specific download terms/size not independently checked in this audit. | Relevant physiology/EMA candidate; not selected as GPS evidence. |
| [StudentLife official dataset](https://studentlife.cs.dartmouth.edu/dataset.html) | Known candidate; official page timed out during this audit. | Exact current fields, release terms and size not verified from accessible primary source. | Not downloaded; no availability/license claims based on secondary copies. |
| [SynMob author project](https://yuanshao.me/SynMob/) / [repository](https://github.com/Yasoz/SynMob) | Synthetic urban mobility research; download documentation uses serialized data. No matched clinical outcomes established. | CC BY-NC-SA stated by project; exact version/individual artifact checksums not verified. | Not selected; no untrusted pickle execution. |
| [FreeGPSTrajectories100M](https://huggingface.co/datasets/ziadatalabs/FreeGPSTrajectories100M) | Publisher describes synthetic vehicle random walks with timestamp,latitude,longitude,speed and heading. No health labels or guaranteed street-constrained paths. | Card CC BY-NC 4.0,100Mpoints/about3.2GB; not downloaded. | Excess volume and weak pedestrian fit versus modest selected corpus. |

No cross-study person joins are valid. A future real routine/health study needs its own participant identity/time alignment, consent/access terms, coordinate quality and endpoint evaluation. More rows alone do not supply the missing linkage.

## Offline Helsinki cartography

`scripts/location_streets.py` uses only the already-downloaded OSM XML extract. `data/map-streets.js`/`.geojson` contain 609 road/footway lines, 57 completely bounded building polygons and 18 park/grass polygons, 184,250 bytes. Polygons are closed original ways fully inside [24.945,60.166,24.953,60.169]; multipolygons/incomplete features are omitted. Attribution and ODbL 1.0 source metadata stay embedded. This is genuine geographic context behind our explicitly generated demo movement; it must never be reused as Beijing context.
