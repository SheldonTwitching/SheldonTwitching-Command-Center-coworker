> **Authoritative repository (2026-10-20):** [SheldonTwitching - Command Center](https://github.com/SheldonTwitching/SheldonTwitching-Command-Center) is the new **private** repository, with **main** as the primary branch, explicitly requested by the owner. Read [COMMAND_CENTER_README.md](COMMAND_CENTER_README.md) first. Earlier repository/branch/build references below are historical. The 2.1 installer series belongs to the new repository; the last verified installed baseline remains 2.0.28 until the new artifact is tested. Kanban implementation is pending; no board code was added during this migration.

> **Current Command Center testing (2026-10-20):** [All 17 roadmap test sheets and note templates](docs/command-center/roadmaps/README.md). Use the verified 2.0.27 build linked there. Older Labels milestones below are retained history.

> **Cabinet construction update (2026-10-19):** Read `arcade/cabinet-structure.json` and the Cabinet Parts workbench at `/studio/cabinet`. Original artwork, Cabinet 1 paint/large lettering, protected-aperture frame variants and upright reflection are implemented. Baked part separation, shared room perspective rig and Stingers exports remain roadmap work; keep owner pinned ideas.

> **Command Center development update (2026-10-19):** Read [COMMAND_CENTER_README.md](COMMAND_CENTER_README.md), [COMMAND_CENTER_ROADMAP.md](COMMAND_CENTER_ROADMAP.md), `arcade/project-spec.json` and `arcade/stage-registry.json` first. The executable is now **SheldonTwitching - Command Center.exe**. The older sections below document the retained Labels components. Shipped source features and pending real-world acceptance are separated in the new roadmap.

# SheldonTwitching Labels — Personal Stream Project

**Owner:** SheldonTwitching | **Repository:** private `SheldonTwitching/SheldonTwitching-Labels` | **Updated:** 2026-10-18

## Product definition

An arcade-themed Windows editor that creates live OBS browser-source widgets for the owner's own stream. It must be easy to configure by sliders, selectors, drag/resize and templates but allow raw CSS for fine tuning. Stream data is local-first.

## Existing working code (not a claim of final Windows acceptance)

- `app.py`: local HTTP bridge, validation, project save/backup, editable labels, rotation sources, Streamlabels file reader, tip bar data API.
- `web/editor.*`, `web/renderer.js`, `web/overlay.*`: WYSIWYG and raw CSS controls, existing labels source.
- `spotify_bridge.py`, `web/now-playing.*`: Spotify PKCE flow, locally stored token, current-track reader, Spotify-themed Now Playing OBS URL.
- **Corrected:** Stream Costs is the owner's existing Streamlabs.com Tip Goal. `streamlabs-tip-goal/` supplies exported custom HTML/CSS/JS from the app, live funds remain at Streamlabs.com; `web/tip-bar.*` is legacy only.
- `web/roster.json`, `assets/sf6/`: character-picker schema and 12 cropped concepts plus 20 newly drawn transparent WebP individual character portraits, all selectable; visual consistency and official status review still pending.
- Windows EXE build script and GitHub Actions workflow. No verified real-Windows/OBS acceptance test yet.

## New v0.9 assets and stream-wide scene package

- Gameplay / Starting / BRB / Ending OBS Browser Sources at `/scenes/*.html` use the original arcade cabinet art, with an alpha hole for gameplay capture.
- All 32 verified playable SF6 fighters have individual concept assets; Tifa and Bosch remain upcoming.
- The new art is **concept-ready, not final art-directed or OBS-approved**. The existing 12 and new 20 need visual consistency review.
- Updated PyInstaller workflow embeds scenes and the roster images.
- Remaining acceptance: GitHub Actions after v0.9 push, real Streamlabels mappings, Spotify OAuth, Windows and OBS layout verification.

## Work order for Codex

### P0 — Build and confirm the Windows executable

- Run GitHub Actions `windows-build.yml`, repair build failures, upload EXE artifact, verify dependency bundling (`spotify_bridge.py`, `web`, `assets`, WebView2 and tray).
- Test on Windows: launch, choose Streamlabels folder, close to tray, reopen, quit, update OBS with window closed, restart/login startup behavior.
- Confirm no secrets or paths shipped into the EXE or repository.

### P1 — Finish Spotify Now Playing widget

- In editor, add polished Spotify connection flow with clear Client ID instructions, connection status, playback states, reconnect/disconnect and fallback UI.
- Smooth track-change transitions, artwork, title, artist and a recognizable Spotify logo or brand-compliant treatment.
- Validate Spotify Web API behavior, scopes, playback eligibility, rate limits and loopback callback requirements against current official documentation.
- Never commit authorization credentials or user music listening history. Test with mocked API before connecting to the owner's Spotify account.
- OBS URL: `http://127.0.0.1:47831/now-playing`.

### P1 — Streamlabs.com Tip Goal theme and existing goal retention

- **Implemented:** the editor exports custom HTML/CSS/JS with arcade colors, title-size slider, animations, and advanced custom CSS.
- **Implemented:** the gameplay scene no longer embeds a duplicate local tip bar. The existing Streamlabs Tip Goal Browser Source is layered above the scene in OBS.
- **Pending user verification:** paste exported files into Streamlabs Custom HTML/CSS/JS and test live `goalLoad`/`goalEvent` data, visual fit, currency formatting, and actual goal progress. Backup prior customization first.
- **No Streamlabels .txt mapping is needed** for Stream Costs. Keep the existing Streamlabs widget URL private.

### P2 — Complete the SF6 roster icons

- Verify roster against the official current Street Fighter 6 playable roster (not rumors, planned guests or world-tour-only names).
- Supply a consistent **individual transparent PNG/WebP icon per verified playable character** with a matching style to the approved neon-chibi concept sheet. Existing twelve crops are prototypes, not finished isolated transparent character badges.
- Update `web/roster.json` and search/category/preview picker. Include per-widget character assignment, glow, sizing and accessible fallback states.
- Do not pretend a catalog entry without a file is a finished icon.

### P2 — More arcade designs and animations

- Expand themed preset library (Character Select, VS, Training, Rank Up, Retro Arcade) and reusable animation types (KO burst, combo counter, character-select flash, arcade coin, glitch, scanline, stamp, energy pulse) using GPU-friendly CSS where possible.
- Support animation preview and reduced-motion, keep WYSIWYG and raw CSS fully interoperable.

### P3 — Stream artwork redesign conversation

- The owner wants to discuss a broader rethink of stream art (cabinet border, scene framing, typography, song request area, overlay alignment). This is a separate design-review track, not permission to replace everything automatically. Use the existing screenshot as evidence and propose coherent options for owner approval.

## Owner inputs before final acceptance

- Spotify developer app Client ID registered with correct local redirect URI, owner authorization (do not ask for tokens or secret keys in chat).
- Sample `Streamlabels` amount/goal `.txt` values or exact filenames for accurate tip source mapping.
- Confirmation of any art style change after reviewing original stream assets.

## Acceptance checklist

- [ ] GitHub Windows build succeeds and release EXE artifact is downloadable.
- [ ] EXE launches on owner's Windows PC; editor/tray lifecycle verified.
- [ ] All three browser-source URLs render in OBS correctly and keep live updates.
- [ ] Spotify connects through safe local PKCE and handles pause/no track/rate limits.
- [x] Project no longer treats Stream Costs as a local Streamlabels text-file goal.
- [ ] Owner tests generated HTML/CSS/JS in actual Streamlabs Tip Goal preview and OBS.
- [x] Every verified playable SF6 character has an individual concept art asset (32/32).
- [ ] All 32 assets pass a final visual consistency/character-recognition review.
- [ ] New animations and designs work across editor preview and OBS.
- [ ] Full automated test suite green.
