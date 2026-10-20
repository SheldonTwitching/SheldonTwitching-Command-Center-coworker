# Weather & Clock - testing and notes

Updated 2026-10-20. App baseline: **2.0.28**. Status: owner testing/notes pending.

## Current scope

Bangor weather, network clock, independent manual overrides and shared stage weather/time rendering implemented. 24/30/60 fps is selectable.

## Test and review

- [ ] Compare automatic Bangor weather and America/New_York time with expected local conditions.
- [ ] Override weather and clock independently; reload/reconnect and restore automatic mode.
- [ ] Check day/dusk/night transitions, weather intensity, DST/offline recovery and 24/30/60 fps loops. Separate current effects from planned authored masks/cloud sheets.

## Planned next work

- Create distinct day/dusk/night art and shadow masks per stage
- Author seamless looping cloud layers and seasonal sprites
- Verify DST, long offline recovery and weather transitions

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
