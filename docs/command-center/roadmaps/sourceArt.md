# Source PSD & Asset Pipeline - testing and notes

Updated 2026-10-20. App baseline: **2.0.28**. Status: owner testing/notes pending.

## Current scope

Original Beta PSD inspected read-only: four PSD/PSB documents, 47 layer records, 16 pixel-identical runtime sprites and eight recovered directional demo frames. Evidence and source hash are stored in docs/psd-reference.

## Test and review

- [ ] Compare native exported poses and controls against the read-only original PSD; never modify that source as a runtime fix.
- [ ] Retain the recorded source hash, exact sprite bounds/alpha/pivots and strict pixel-art contract.
- [ ] Record masks still needed for cap/rim, trim and lighting. Recover animation timing from source evidence rather than guessing from light-angle metadata.

## Planned next work

- Enforce docs/command-center/PIXEL_ART_CONTRACT.md for every new sprite, reskin and animated scene
- Verify original GIF timing in Photoshop; do not infer fps from global light angle
- Reconcile Beta cabinet/FX origins and arrow placement with the approved app alignment
- Author explicit source masks for trim, return faces, button cap/rim and sphere materials
- Keep source PSD immutable and export versioned assets with native bounds, alpha and pivots

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
