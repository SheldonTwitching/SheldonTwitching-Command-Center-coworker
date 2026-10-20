# Preview & OBS Sources - testing and notes

Updated 2026-10-20. App baseline: **2.0.28**. Status: owner testing/notes pending.

## Current scope

Built-in preview selector and source catalog implemented for scene outputs, widgets and aligned live cabinet parts.

## Test and review

- [ ] Open each scene, widget and independent cabinet-part URL from Setup & Sources and compare editor/OBS output.
- [ ] Use the current instance address shown by the app, especially when the old bridge occupies the normal port.
- [ ] Confirm sources stay live when the editor window is hidden. Record desired sizing/layout changes against owner-supplied widget versions.

## Planned next work

- Use owner-provided OBS widget versions before redesigning individual widgets
- Verify every source at its documented OBS dimensions
- Add per-widget sizing presets and saved monitor layouts
- Add a layered preview compositor for separate OBS parts

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

## Pop-out update

Separate preview/editor windows now support native size, fit, zoom, scrolling and background inspection. See [usage and feedback](../PREVIEW_AND_FEEDBACK.md). Test saved edits in both inline/pop-out previews, multiple sources together, resized windows and closing a preview without stopping the bridge.
