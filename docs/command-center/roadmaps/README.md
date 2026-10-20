# All roadmaps - owner testing and notes

Updated 2026-10-20. All 17 application roadmap areas are listed below. Each sheet contains current scope, manual checks, planned work and a notes template. Unchecked items are not claimed as accepted.

## New authoritative repository

[SheldonTwitching - Command Center](https://github.com/SheldonTwitching/SheldonTwitching-Command-Center) is private and uses `main`. All 17 roadmap sheets migrated with the complete tracked source, assets and Git history. Earlier build artifact links intentionally point to the old repository where those artifacts were produced. Local pinned ideas and account settings stay in User Data; two-way Kanban sync remains pending.

## Build to use

**2.0.28** is the verified application baseline. [Download its private GitHub Actions artifact](https://github.com/SheldonTwitching/SheldonTwitching-Labels/actions/runs/39399815387). The installed copy on this machine has been updated and its native desktop startup checked. Do not use the older 2.0.24 run 39361816840.

100 automated tests and the downloaded-EXE conflict/normal-route checks passed. The actual installed GUI opened at 47832 alongside the older Labels bridge at 47831. Full visual, controller, audio, account and OBS acceptance remain separate.

## Test sheets

- [Social Media Packages](social.md)
- [Widget Animation Library](animations.md)
- [Installers & Updates](updates.md)
- [Rotating Labels](labels.md)
- [Spotify Now Playing](spotify.md)
- [Stream Chat](chat.md)
- [Streamlabs Tip Goal](tipGoal.md)
- [Notifications & Event Lights](events.md)
- [Weather & Clock](weather.md)
- [Scene & Stage Library](scenes.md)
- [Preview & OBS Sources](preview.md)
- [Audio & Scene Lighting](audio.md)
- [Text Reader & Parsing](text.md)
- [Cabinet Structure & Marquee](cabinet.md)
- [Stingers & Transition Packages](stingers.md)
- [Source PSD & Asset Pipeline](sourceArt.md)
- [Cabinet Shape Concepts](cabinetShapes.md)

## Current organization

The integrated Kanban and GitHub sync have been removed at owner request. Saved board data is retained for a separate EXE/chat. Use these roadmap sheets and the app's lightweight pinned ideas for streaming work. See [separate app prompt](../STANDALONE_BOARD_PROMPT.md) and [Copilot / PSD art contract](../../../art/style-kit-v1/ARTSTYLE.md).

## How to make notes

In Command Center, open **Widget Roadmaps**, add an idea to its area and pin it. **Export Studio** saves the local roadmap ideas with the rest of the Studio project. Personal profile contents are not automatically pushed to GitHub. For GitHub review, fill in the matching sheet above with build, source/scene, expected/observed behavior and a screenshot reference.

The owner scales the native PSD-like gameplay overlay in OBS. Use owner-provided widget versions for styling work. Combined chat means one feed from all connected accounts with platform icons; unsupported account adapters remain planned. Tip-bar styling is a collaboration using the existing Streamlabs goal.

[Main roadmap](../../../COMMAND_CENTER_ROADMAP.md) | [Testing handoff](../TESTING_AND_NEXT.md) | [Strict pixel-art contract](../PIXEL_ART_CONTRACT.md)
