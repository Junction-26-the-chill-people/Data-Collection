# Street movement map

Open `index.html` directly: the map automatically displays locally bundled OpenStreetMap roads, buildings and parks behind the demo routes. No internet, key, server or installation is required. Leaflet 1.9.4 is vendored locally.

Detailed online tiles are optional through START-DEMO.cmd or an existing web host. Direct file URLs do not fetch OSM tiles because those require a valid HTTP Referer. The offline fallback uses derived vector geometry, not downloaded tiles. `?offline=1` exercises the same offline map branch during browser QA.

## Data and interpretation

The current mapped stories are simulated movement on real public Helsinki street geometry. They are not GPS observations of a study participant. Public geometry attribution and extraction provenance are carried in the dataset. Real study records without coordinates display a no-route state; steps are never converted into an invented location.

The blue lines are selected-day trips. Dashed lines show one **actual reference record nearest the median mapped distance** among the chosen baseline records, rather than averaged coordinates. This is a representative mapped day, not an estimate of the most frequent street or a statistical movement baseline. Empty baseline days without coordinates are excluded from this representative-route selection. The caption explicitly gives the number of mapped reference days and observed reference days; returned metadata also includes the total supplied reference slots. Missing-period placeholders do not count as observed days. A selected day with explicit empty trips shows no mapped walks while preserving the reference route and known places. Missing-period records instead state that no movement observation is available.

Each trip and each segment is rendered separately. Invalid coordinates break a line, and trips are never joined across dwell time or missing points. Direction arrows describe geometric travel direction, not velocity. The distance summary is the sum of haversine segment lengths, excluding gaps and inter-trip jumps. Place markers in demo stories are story locations; they are not a real person's home address.

## Browser contract

Load `data/map-streets.js`, `data/hanover-streets.js`, and `data/neighborhood-01.js` through `data/neighborhood-11.js` before the map module, plus `vendor/leaflet/leaflet.css`, `movement-map.css`, `vendor/leaflet/leaflet.js`, and `movement-map.js`. Call:

```js
MovementMap.update(container, { participant, record, baselineRecords, selectedIndex });
MovementMap.resize(container); // after layout changes
MovementMap.destroy(container); // before removing the host
```

`update` reuses one Leaflet map and updates existing route polylines. It preserves the viewport during day playback, and fits on participant changes or the explicit Fit both routes button. Layer toggles independently control selected trips, reference trips, arrows and places. The return value includes `summary`, `reference`, `status`, `map`, `fit`, and `resize`. `MovementMap.summarize(record)` and `.representative(records)` are also available without a DOM.

Preferred records contain `trips: [{id, mode, startedAt, endedAt, points:[{lat,lon,timestamp,segmentId}]}]`. An explicit empty `trips` array is authoritative. Legacy `route` points are accepted and split by `tripId`; invalid coordinates and changing `segmentId` split further. Coordinates must be finite numbers in latitude/longitude bounds. Popups escape supplied labels, identifiers and timestamps.

## Tiles, privacy and availability

Only standard viewport tile requests are sent to `https://tile.openstreetmap.org/{z}/{x}/{y}.png`; participant files and route arrays are not uploaded. Tile requests nevertheless reveal the viewed geographic area and normal connection metadata such as IP address to the tile provider. Browser caching is retained; the application does not prefetch, bulk download, or offer offline OSM tile downloads. Visible OSM attribution is retained. Bundled local streets appear immediately while online tiles load, and remain available when tiles fail. A successful loading cycle replaces the fallback with detailed tiles. `?offline=1` explicitly selects the same local-only mode on HTTP for demonstrations or testing. The bounded fallback covers only the supplied Helsinki story areas and Hanover region; it is not a worldwide offline map. Its source, ODbL attribution, original-extract hash and reproducible extraction script are recorded with `data/map-streets.js` / `.geojson`.

The public OSM tile service has no availability guarantee and is intended for ordinary interactive viewing. For public production deployment or substantial traffic, configure an appropriate hosted tile service or self-hosting. A Google Maps provider is not implemented and no Google API key is needed or stored.

Sources: [OSM tile usage policy](https://operations.osmfoundation.org/policies/tiles/), [Leaflet 1.9.4 release](https://github.com/Leaflet/Leaflet/releases/tag/v1.9.4), [Leaflet license](https://github.com/Leaflet/Leaflet/blob/v1.9.4/LICENSE), [OSM attribution and licensing](https://www.openstreetmap.org/copyright). Vendored asset hashes and retrieval URLs are in `vendor/leaflet/vendor-manifest.json`.

## Verification

Run `node tests/map.test.cjs`. Deterministic Leaflet and DOM stubs verify trip separation, gaps, coordinate validation, arrows, representative selection, escaped popups, persistent rendering, no-walk and missing observations, real-data switching, file URL tile suppression and error recovery. Tests never download map tiles. Actual street rendering should additionally be viewed through the loopback launcher in a browser.

Troubleshooting: if no map appears, keep the entire demo folder together, including `vendor/leaflet`, `data/map-streets.js`, and the map JS/CSS. Real study participants have no GPS observations and intentionally show no map. The optional online preview link needs START-DEMO running on its default port 8765; a custom launcher port must be opened using the URL printed by the launcher. No browser page attempts to launch a local process.

Offline cartography uses separate land and street panes, with public buildings and parks beneath routes when available in the bounded bundle. Story place names remain visible as permanent labels; supplied labels are escaped. The adapter reports `localCoverage` (`full`, `partial`, `none`) based on route/reference/place coordinates versus bundle bounds. Out-of-area routes retain geometry but explicitly state that local street context is not bundled, rather than implying worldwide offline coverage.


## Linked daily research update

`data/hanover-streets.js` adds a second independently bounded region through `window.MAP_STREET_REGIONS`. Load it after the Helsinki bundle and before movement-map.js. It contains 866 public roads/path sections, 360 buildings and 32 parks. `scripts/hanover_streets.py` preserves the source extract/hash and rebuilds it. These are current OSM surroundings beneath historical 2013 StudentLife observations, not historical cartography. Routes outside either region still render with an explicit missing-local-context message; coverage is never inferred from one huge box spanning the two cities.

Recorded GPS dots retain their timestamp, coordinate and reported accuracy. The GPS observations layer can be toggled. Stationary fixes with distinct times are retained. Lines are chords between accepted samples, not proof of the exact road traveled. No transport mode or home location is inferred for StudentLife.

`linkageIssue(participant, record, selectedIndex)` checks supplied subject/participant identity, dayKey, selected date/period and timezone. A mismatch causes update() to clear stale geometry and return status linkage_error. Reference records with inconsistent keys are excluded. Callers must also suppress their surrounding movement summaries/exports. These are data-integrity checks, not access control or consent enforcement.


## Per-person Helsinki neighborhoods (daily-linked/1.5.0)

Each generated person now has a different home anchor and four personal-place roles in its own bounded Helsinki extract. Place labels such as park, cafe, grocery and library are **fictional scenario roles at public network nodes**, not claims that a verified amenity or a real person's residence is at that exact coordinate. Only the underlying street/path geometry is sourced from OpenStreetMap.

| Person | Neighborhood | Bundled file |
| --- | --- | --- |
| Mara | Kallio | `data/neighborhood-01.js` |
| Noah | Toolo | `data/neighborhood-02.js` |
| Lea | Punavuori | `data/neighborhood-03.js` |
| Oskar | Kamppi | `data/neighborhood-04.js` |
| Iris | Sornainen | `data/neighborhood-05.js` |
| Emil | Hakaniemi | `data/neighborhood-06.js` |
| Ada | Kaivopuisto | `data/neighborhood-07.js` |
| Jonas | Hietaniemi | `data/neighborhood-08.js` |
| Sofia | Kaisaniemi | `data/neighborhood-09.js` |
| Elias | Eira | `data/neighborhood-10.js` |
| Mila | Kruununhaka | `data/neighborhood-11.js` |

The 11 derived region files total about 3.65 MB; each is below 0.51 MB (the 2 MB per-region budget). Each contains its exact request URL, bounding box, source SHA-256 and ODbL attribution. Raw sources remain in `data/map-source/neighborhood-01.osm` through `neighborhood-11.osm`. `python scripts/personal_places.py` regenerates the derived files from those snapshots; it downloads a bounded OSM API extract only when that particular source snapshot is missing. It never downloads map tiles.

The route graph admits public footways, pedestrian ways, living streets, residential/service roads, paths, steps, unclassified roads, and secondary/tertiary roads unless access or foot access is explicitly prohibited; closed area polygons are excluded. This is a plausible demonstration graph, not a pedestrian navigation safety guarantee. Nodes and every route edge stay inside the person's own extract; routes follow actual source-node adjacency, with no invented straight connectors. Oskar's travel phase uses unfamiliar cafe/library roles; the decline stories use fewer, closer destinations later.

Location generation is a separate seeded pass. Original ten profiles' health values, dates, contexts, phases, missingness, coverage descriptions and identity metadata are protected by pre-change SHA-256 fixtures in `tests/fixtures/pre-1.5-health-hashes.json`. The original Esplanadi generator remains solely to reproduce its old RNG consumption and route-dependent health values. Those old routes are replaced before the bundle is written. Sofia and Elias keep complete generated 24-hour itineraries fitted to the preserved home-hour budgets; the other nine stories retain partial walking coverage. Recorded research data is untouched.

The map's existing participant-switch fit uses that person's places and selected/reference routes. Fit both routes includes selected and representative anchor geometry. Region bounding boxes are considered individually, so the offline coverage indicator does not infer coverage between neighborhoods.
