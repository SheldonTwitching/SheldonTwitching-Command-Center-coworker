# Cabinet Structure & Marquee - testing and notes

Updated 2026-10-20. App baseline: **2.0.28**. Status: owner testing/notes pending.

## Current scope

Strict source-pixel palette recoloring replaces smooth ball shading and restores button contrast. Full trapezoidal marquee coverage and independent trim masks are defined. Native sprite geometry, protected glass and upright reflection remain. Owner visual acceptance pending.

## Test and review

- [ ] Compare Owner Original and Cabinet1 at native size and several owner-chosen OBS zoom levels. Preserve strict pixel clusters, dither, silhouettes and proportions.
- [ ] Count all nine controls (four upper, four lower, one right); press each, then check all eight joystick directions and neutral.
- [ ] Inspect full marquee-face coverage, unchanged stacked-logo proportions, blue trim without pink bleed and all painted surround planes.
- [ ] Check cap/rim accents, six-pixel pressed travel, joystick above arrows and editable layer order.
- [ ] Check faint upright stick reflection at the glass bottom with no buttons/arrows. Directional relighting remains pending pixel-preserving masks.

## Planned next work

- Preserve native PSD-like pixel-art proportions; owner scales and zooms the gameplay overlay in OBS as appropriate
- Review native and gameplay renders plus enlarged pixel-control crops before adding new shapes
- Author pixel-preserving directional light masks; smooth procedural spheres are prohibited
- Refine detached cap/rim masks against the original PSD
- Verify marquee face coverage and blue trim containment in OBS
- Replace legacy loading-room cabinet with shared perspective rig

## Owner notes

- Tested build/date:
- Scene/widget/source and OBS size/zoom:
- Preset/layer order (if relevant):
- Expected behavior:
- Observed behavior:
- Screenshot or recording reference:
- Requested changes/ideas:
- Priority and acceptance status:

The integrated Board is removed; use **Widget Roadmaps -> Add & pin idea** and this review sheet for now. Existing Board files remain local for a separate app. See [master index](../MASTER_INDEX.md) and [separate app brief](../STANDALONE_BOARD_PROMPT.md). Those notes stay in the local Studio profile; **Export Studio** includes them. This GitHub template can also be edited for repository review. Keep tokens, private widget URLs and account credentials out of notes.

[All roadmap test sheets](README.md) | [Main roadmap](../../../COMMAND_CENTER_ROADMAP.md) | [Current test build](https://github.com/SheldonTwitching/SheldonTwitching-Labels/actions/runs/39399815387)
