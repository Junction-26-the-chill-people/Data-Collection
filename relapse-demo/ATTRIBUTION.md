# Data attribution and transformation notice

## PSYCHE-D (real data)

Mariko Makhmutova, Raghu Kainkaryam, Marta Ferreira, Jae Min, Martin Jaggi, and Ieuan Clay. **PSYCHE-D: predicting change in depression severity using person-generated health data (DATASET)**, v0.1, 2021. DOI: https://doi.org/10.5281/zenodo.5085146

Source: https://zenodo.org/records/5085146
License: Creative Commons Attribution-NonCommercial 4.0 International, https://creativecommons.org/licenses/by-nc/4.0/ . Publisher license retained at `docs/PSYCHE-D-LICENSE.pdf`.

Changes in this demo: six numeric features selected and normalized (minutes to hours, ratio to percentage), participant IDs namespaced, chronological monthly records sorted, missing month placeholders added without imputing measurements, endpoint survey values retained as context, and experimental heuristic scores computed. Original raw files remain untouched. These changes and the demo are not endorsed by the dataset authors. Real data use remains subject to the noncommercial license.

## NFI FARED digital traces (real trace audit)

Conor McCarthy, Jan Peter van Zandwijk, Marcel Worring, and Zeno Geradts. **Forensic Activity Classification Using Digital Traces from iPhones: A Machine Learning-based Approach**, 2025, https://arxiv.org/abs/2512.03786 .

Source: https://huggingface.co/datasets/NetherlandsForensicInstitute/NFI_FARED_Digital_Traces , pinned revision `5d528bd3fe38bc33067015496045ed1f155f005c`.

All seven pickle files were checksum-verified and examined using a non-executing symbolic opcode parser plus primitive buffer decoding. No pickle constructors/reducers were executed. The audit contains 111,121 overlapping trace rows, not 111,121 independent people. Fifteen distinct subject strings appear in the files while the card describes 14 participants; this discrepancy is disclosed rather than silently reconciled. No latitude/longitude fields were found. There is no depression label or real map in this source. The card did not specify a clear reuse license: confirm terms before redistributing source data or using it commercially. Only derived audit summaries are included with this demo.

## Dryad

Yuning Wang and coauthors. **Loneliness and well-being in Finnish immigrants: A multimodal dataset from wearables and passive data collection**. https://doi.org/10.5061/dryad.qz612jmrn . Latest selected version 2025-11-28, version 410377. Metadata declares CC0-1.0. Source metadata reviewed, data files unavailable because public download returns 403 and API download requires authentication 401. No Dryad participant observations are claimed in this demo.

## Demo stories

Participant IDs prefixed `sim-` are generated locally with fixed seeds. All personal measurements, contexts, visit choices and trip times for those IDs are constructed. They demonstrate software mechanics, not model accuracy or observed clinical outcomes. They are never inserted into real participants' missing histories. The interface uses a concise Demo data badge; structured exports retain explicit synthetic provenance.

## Street geometry and map display

? OpenStreetMap contributors. Public street/path geometry is distributed under the Open Database License (ODbL), https://www.openstreetmap.org/copyright . The bounded source extract is retained at `data/map-source/helsinki-esplanadi.osm`; its exact URL and SHA-256 are embedded in each demo profile's `mapGeometrySource`. The generated walking trips follow that network. Locations labeled Home area are scenario anchors, not actual participant homes.

The daily-linked/1.5.0 generated profiles use eleven additional bounded OpenStreetMap API extracts for Kallio, Toolo, Punavuori, Kamppi, Sornainen, Hakaniemi, Kaivopuisto, Hietaniemi, Kaisaniemi, Eira and Kruununhaka. Source snapshots are `data/map-source/neighborhood-01.osm` through `neighborhood-11.osm`; the corresponding `data/neighborhood-*.js` files embed each exact API URL, bbox, source SHA-256 and ODbL attribution. `scripts/personal_places.py` selects public streets/path edges, buildings and parks for display and creates fictional timed routines on that graph. Place-role labels are generated, not verified amenity labels or personal addresses. The original Esplanadi source remains for reproducibility of the unchanged ten health scenarios. No source geometry implies that a real person made these trips.

Street tiles come directly from https://tile.openstreetmap.org/ under the OpenStreetMap Foundation tile usage policy, https://operations.osmfoundation.org/policies/tiles/ . Visible attribution remains on the map. Tiles are requested only for a visible interactive map over HTTP/HTTPS; no bulk tile downloads or prefetching are performed. Tile requests disclose the viewed map region to the provider, but the app does not upload participant records or health measurements.

Leaflet 1.9.4 is vendored locally under `vendor/leaflet/`. Retain the bundled license and distribution provenance when sharing this demo. Google map tiles are not used through unofficial endpoints.

## SYN-RoadGps location explorer

Smile1120, SYN-RoadGps, https://huggingface.co/datasets/Smile1120/SYN-RoadGps . Publisher-declared CC BY 4.0, https://creativecommons.org/licenses/by/4.0/ . Pinned revision `482d9f29bbee8282626e5136f16924366bcf5f6e`. Changes: source tuples normalized into explicit coordinate/time fields, fifty original-order traces selected for the viewer, anomalous edges split without deleting or smoothing points, distances and quality summaries computed. Full-corpus audit and source hashes are in docs/location-dataset-audit.md/.json. No author endorsement is implied. Unknown coordinate datum and mismatched road identifiers remain disclosed; no health linkage is created.

## StudentLife recorded GPS and health reports

Rui Wang and coauthors, StudentLife (UbiComp2014), DOI10.1145/2632048.2632054; Daniel Fryer, StudentLife data in RData format,v1.0.0, https://zenodo.org/records/3529253 , DOI10.5281/zenodo.3529253. The derivative repository declares CC BY4.0. Changes: four selected tables decoded to CSV, namespaced participant IDs, UTC calendar grouping, original questionnaire codes retained with verified sleep display labels, quality-based GPS segment breaks, and up to80original accepted fixes perday selected for the viewer. No scores or outcomes inferred. No endorsement implied. See docs/studentlife.md for licenses, exact source/member integrity and repeated-response caveats.

The additional Hanover/Dartmouth offline street extract is OpenStreetMap data under ODbL1.0. Its source URL and SHA256 are embedded in data/hanover-streets.js; raw extract is retained in data/map-source/hanover.osm. It is current street context, not a2013historical map. Recorded StudentLife fixes are not moved onto the road network.

## Fonts

- Young Serif (Bastien Sozeau / Noirblancrouge) and Figtree (Erik Kennedy), both SIL Open Font License 1.1, bundled unmodified from the google/fonts repository under `vendor/fonts/` with their OFL texts. Used for the presentation only.
