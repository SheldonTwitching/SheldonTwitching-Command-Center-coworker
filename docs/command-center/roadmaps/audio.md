# Audio & Scene Lighting - testing and notes

Updated 2026-10-20. App baseline: **2.0.28**. Status: owner testing/notes pending.

## Current scope

Input/desktop capture and selectable OBS source meters feed shared audio state; stale signals settle to zero. Local fixture, cabinet and room lighting implemented.

## Test and review

- [ ] Select the actual source intended to drive music-reactive effects; metadata alone is not an audio meter.
- [ ] Check reaction strength, smoothing, silence, mute and disconnect/reconnect across scenes.
- [ ] Record each scene reactive object and how light, shadow, receiver masks and occlusion should respond.
- [ ] Measure the complete OBS source stack at 24/30/60 fps; keep emission layers separate from crisp static pixel art.

## Planned next work

- Verify the owner music source and mute/reconnect in OBS
- Author precise emission, receiver, occlusion and reflection masks per stage
- Add saved per-scene gain and light routing
- Profile 24/30/60 fps on the full OBS stack

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
