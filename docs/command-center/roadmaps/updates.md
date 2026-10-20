# Installers & Updates - testing and notes

Updated 2026-10-20. App baseline: **2.0.28**. Status: owner testing/notes pending.

## Current scope

Exact Command Center EXE name, ST icon, per-user installer definition and private Windows pipeline implemented; refreshed build acceptance pending.

Installed startup was verified on 2026-10-20 after updating the actual installation from 2.0.24 to 2.0.28. The native desktop showed Saved locally and the animated Starting Soon scene. Full OBS and profile-preserving upgrade acceptance remain pending.

## Test and review

- [ ] Launch the installed app from its normal shortcut and confirm the full Studio opens. Build2.0.28 was verified on this machine.
- [ ] With an older Labels bridge still running, confirm the notice and new-port source URLs; the old bridge should remain available.
- [ ] Check repeat launch, tray hide/reopen, restart and upgrade preservation of local projects, palettes, bindings, CSS and pinned ideas.

## Planned next work

- Verify launch with an older Labels bridge already running: clear notice, free local port and working Studio HTML
- Build and verify the latest Windows EXE and installer
- Test upgrade preserves local projects and presets
- Add signed releases and private authenticated update discovery

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
