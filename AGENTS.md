# Codex instructions — SheldonTwitching - Command Center

You are contributing to **SheldonTwitching - Command Center**, a PERSONAL, local-first Windows OBS Browser Source editor for one streamer. This is not a commercial or multi-user product. Keep this repository private.

## Authoritative repository

Owner request, 2026-10-20: the new private repository is `SheldonTwitching/SheldonTwitching-Command-Center`, and its primary branch is `main`. The old Labels repository is retained unchanged as historical reference. All earlier instructions to keep this project only on `arcade-overlay-v2` describe the old repository and are superseded by this explicit request. Preserve implementation/verification/owner-acceptance distinctions; publishing main does not establish visual acceptance.

## Current specification authority

Read `docs/command-center/MASTER_INDEX.md`, `docs/command-center/HANDOFF.md`, `docs/command-center/ART_RULES.md` and `arcade/feature-registry.json`. The registry supplies all shipped feature status and next actions; do not reintroduce duplicate status dictionaries. The owner removed the integrated Kanban on 2026-10-20. Do not restore it. Preserve its existing local JSON/screenshots; extraction code lives in extras/standalone-board for a separate EXE/chat. Preserve roadmap ideas. Read art/style-kit-v1/ARTSTYLE.md for Copilot/PSD art production. Treat older feature counts/branding below as retained component history, not current product scope.

## Project goals

- WYSIWYG label editing **and** custom/raw CSS, preserving the same visual output in the OBS render and the editor preview.
- Read Streamlabs Streamlabels `.txt` files from a user-chosen local directory, with safe parsing and no hardcoded assumptions about file naming beyond the user's actual data.
- Four OBS scenes under `/scenes/{gameplay,starting,brb,ending}.html` and three widgets under a single local bridge:
- The local bridge hosts `/overlay` (rotating labels) and `/now-playing` (Spotify), and an **offline/sample-only** `/streamlabs-tip-preview`. **Stream Costs is the user's existing Streamlabs.com Tip Goal Browser Source**, not `/tip-bar` nor any .txt file. The old `/tip-bar` endpoint is legacy compatibility only.
- Retain the user's purple, red and hot-pink neon arcade cabinet identity shown in `docs/channel-brand-reference.png`; SF6 chibi references are in `docs/sf6-concept-board.png`.
- Individual SF6 portraits in `assets/sf6/`, with metadata in `web/roster.json`; **32 playable characters now have individual concept icons**: 12 concept-board PNG crops and 20 newly illustrated transparent WebP stickers. Treat these as draft fan-art pending final visual approval, not as polished or official Capcom assets.
- One Windows `.exe`, using PyInstaller and the existing GitHub Actions Windows workflow. Verify compiled Windows behavior and OBS Studio rendering before calling it release-complete.

## Rules

1. Begin by reading `CODEX_NEXT_STEPS.md`, `README.md`, and `PROJECT_ROADMAP.md`. Inspect existing code before changing anything; do not restart from scratch.
2. Never commit Spotify access/refresh tokens, Client ID settings from the user's machine, actual Streamlabels directories, project.json, private keys, or other secrets. Spotify auth currently uses OAuth PKCE with tokens held in `%APPDATA%/SheldonTwitchingLabels` (or `ST_LABELS_HOME`).
3. Work within the current Python local bridge (`app.py`, `spotify_bridge.py`), static browser widgets (`web/`), and native desktop-wrapper approach unless a substantial migration is agreed upon.
4. Honor accessibility and browser-source constraints: OBS sources should render on transparent backgrounds, survive reloads, and not require the editor to stay visible. Keep private APIs bound to 127.0.0.1 and validate writes.
5. Preserve the visual editor's custom CSS cascade and add no silent style overwrites. Avoid cosmetic-only changes in place of functional delivery.
6. Roster metadata needs verification against official current SF6 roster data. Treat names/statuses in the current manifest as draft until confirmed; do not turn unverified planned characters into playable assets.
7. Keep all progress accurately separated into implemented, tested, and still pending. Do not represent a GitHub Actions artifact as locally Windows-tested without evidence.

## Verification

Run:

```bash
python -m pytest tests -q
node tests/test_renderer.js
node --check web/editor.js
node --check web/renderer.js
node --check web/now-playing.js
node --check web/tip-bar.js
```

Windows EXE workflow: `.github/workflows/windows-build.yml`; the local script is `Build-Windows-EXE.bat`.

## Streamlabs Tip Goal rule

Never request or commit the owner's private Streamlabs widget URL, do not mirror totals through a local bar, and do not recreate the goal. Edit only the exported custom HTML/CSS/JS appearance. The dashboard remains authoritative and OBS keeps the existing Streamlabs browser source. See `STREAMLABS_TIP_GOAL_SETUP.md`.

## Mandatory pixel-art contract

Read `docs/command-center/ART_RULES.md` and `docs/command-center/PIXEL_ART_CONTRACT.md` before cabinet/material/scene changes. Source pixel clusters, dithering, control silhouettes and nearest-neighbor rendering are mandatory. Smooth procedural sphere shading must never replace the original control artwork.
