# Dataset inventory for the repository handoff

This is the **committed inventory**, not a claim that every source archive was downloaded. Exact shipped file sizes and SHA256 values are in [repository-manifest.json](repository-manifest.json). Publisher checksums and pinned revisions remain in the original manifests. Some original audit records contain the source workstation's absolute paths; use the repository-relative paths below for current work.

| Source | Included here | License and limitations |
| --- | --- | --- |
| [PSYCHE-D v0.1](https://zenodo.org/records/5085146) | `psyche_d/raw/`: Parquet, feature dictionary, license; full normalized input in `archives/psyche-d-normalized.json.gz` | CC BY-NC 4.0. All 4,948 histories retained; monthly aggregates, no GPS |
| [StudentLife R-format derivative](https://zenodo.org/records/3529253) | `location_sources/studentlife_zenodo/`: four source RDS members, decoded GPS/PAM/Sleep/PHQ CSVs, codebook and audits | CC BY 4.0 derivative; credit Daniel Fryer and Wang et al. Original member hashes/CRCs verified; whole-archive MD5 not verified |
| [SYN-RoadGPS](https://huggingface.co/datasets/Smile1120/SYN-RoadGps) | Publisher README/attributes, road files and full 10,000-trajectory CSV (lossless gzip in archives) | CC BY 4.0. Synthetic GPS-only source; never linked to another dataset's health records |
| [Corona Health](https://b2share.eudat.eu/records/cgf63-kme28) | Four downloaded CSVs plus schema/linkage audits | CC BY 4.0. Partial source; rounded 0.1-degree GPS and uncertain timestamp offsets, no street-level routes |
| [UCI GPS trajectories](https://archive.ics.uci.edu/dataset/354/gps+trajectories) | Downloaded ZIP/RAR and manifest | CC BY 4.0. GPS-only, not integrated; source transport/checksum limitations retained in manifest |
| [NFI FARED](https://huggingface.co/datasets/NetherlandsForensicInstitute/NFI_FARED_Digital_Traces) | Pinned metadata, source card, file/checksum inventory; generated static summaries under relapse-demo/docs | Original raw pickles omitted: no clear redistribution license found. Local download is distinct from permission to republish |
| [Finnish immigrants / Dryad](https://datadryad.org/dataset/doi:10.5061/dryad.qz612jmrn) | Metadata and failed-download record only | Metadata declares CC0; raw 1.86 GB archive was blocked (403/401), not shipped |
| [OpenStreetMap](https://www.openstreetmap.org/copyright) | Source snapshots under `../relapse-demo/data/map-source/`, derived local geometry in the viewer | ODbL; attribution and exact source URLs/hashes retained |

The tiny StudentLife tooling test archive is omitted because its separate redistribution terms were not established. Its manifest and historical audit remain, and it is not the viewer's GPS source. The separately licensed Zenodo members and decoded tables used by the viewer are included.

## Restore and verify

From the repository root:

```sh
python scripts/bootstrap.py
python scripts/verify_repository.py
```

Bootstrap verifies the two gzip archives and restores byte-identical files to the paths expected by existing tools. It refuses to overwrite a different existing file. No network, R runtime, npm or third-party Python module is needed. The restored CSV and normalization cache are ignored by Git; their gzip sources are tracked as ordinary blobs, with no Git LFS dependency.

The original publisher `.gitattributes` in SYN-RoadGPS is retained byte-for-byte for provenance. Its LFS patterns apply only within that raw-source directory. Bundled gzip archives intentionally live outside it, and the restored large CSV is ignored.

For optional source acquisition, `scripts/download_datasets.py` retains the original NFI/PSYCHE-D/Dryad URLs and checksums. It also attempts the blocked Dryad files; do not run it merely to open the demo. `scripts/verify_datasets.py` checks that original download manifest and will report deliberately omitted NFI/Dryad files missing. Use `verify_repository.py` to verify what this repository actually ships.

## Provenance and integrity

See `dataset-registry.json`, `download-manifest.json`, per-source manifests and `archive-manifest.json`. The repository manifest contains hashes for shipped originals, decoded tables, ready-to-open viewer derivatives and OSM source/derived geometry. Do not alter original bytes or checksums. Update the repository manifest and release verification when intentionally changing derivatives.

All generated people remain explicitly synthetic. Research nulls are preserved. StudentLife joins only within its own same-person/date namespace and remains unscored. No source is treated as validated evidence that the prototype detects or prevents depression relapse. Retain source licenses and attribution when sharing derivatives; PSYCHE-D's noncommercial condition is not removed by committing it here.
