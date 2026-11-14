# UI review

The presentation now starts with a named demo story and a selected deterioration day. The primary flow is person → story phase/day → changed measurements and street routes. Reference controls, raw calculation details and dataset inventory remain available through progressive disclosure.

The main view retains one concise Demo data badge; data and exports retain explicit provenance. Eight stories include stable, persistent-change, recovery, illness, travel, fitness and missing-device patterns. Real monthly research data is a separate searchable selection.

Map behavior: blue selected trips over a wider dashed reference underlay, trip direction arrows, place markers, layer toggles and explicit fit. Reference routes are sampled days nearest the median among mapped reference days, with mapped/observed denominators shown. Separate trips are never bridged. Empty mapped-walk days retain the reference; missing movement is unavailable; research records do not inherit routes.

Place cards compare distinct visited days in the selected reference and rolling window, excluding missing observations. Local trip times use the profile time zone; trip endpoints say Arrival/end. Home hours are a separate input and no-route does not imply staying home all day.

The root agent verified desktop and 390px phone-sized layouts in a browser, including live street tiles, visible attribution, route controls, phase navigation, missing-device handling and no-GPS cleanup. Corrected fixed-height clipping, small mobile chart labels, clipped phase buttons and selected routes hidden behind reference lines. Final phone document width equals client width (375px with scrollbar), with no page overflow.

`tests/test-ui.cjs` passes 324 representative renders plus interaction checks. `tests/ui-integration.test.cjs` passes 6,083 stratified cases. `tests/map.test.cjs` checks map lifecycle and geometry without requesting network tiles. See verification.md for exact coverage and limits; mocks do not establish pixel-perfect or screen-reader compliance.
