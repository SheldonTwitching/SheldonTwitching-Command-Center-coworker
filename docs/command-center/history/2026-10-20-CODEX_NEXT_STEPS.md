> **Authoritative repository (2026-10-20):** [SheldonTwitching - Command Center](https://github.com/SheldonTwitching/SheldonTwitching-Command-Center) is the new **private** repository, with **main** as the primary branch, explicitly requested by the owner. Read [COMMAND_CENTER_README.md](COMMAND_CENTER_README.md) first. Earlier repository/branch/build references below are historical. The 2.1 installer series belongs to the new repository; the last verified installed baseline remains 2.0.28 until the new artifact is tested. Kanban implementation is pending; no board code was added during this migration.

> **Current build and directory (2026-10-20):** Installed2.0.28 verified, including a separate native preview;100 tests and downloaded-EXE checks passed. Use `C:/Twitch/SheldonTwitching 4.0/Codex Projects/Command Center/Project` from now on. All source/build files,314 verified reference copies and six profile files were organized under the new root; User Data routing is active. Old copies retained. Latest installer is under the root Installers folder.

> **Workspace and pop-outs (2026-10-20):** Owner root is `C:/Twitch/SheldonTwitching 4.0/Codex Projects/Command Center`; use its `Project` checkout after copying. Read `docs/command-center/WORKSPACE_STORAGE.md` and `PREVIEW_AND_FEEDBACK.md`. Private User Data is outside Git and selected by the machine-local storage pointer. Pop-outs are editor-only inspection windows, preserving native source dimensions.

> **All roadmap testing sheets published (2026-10-20):** `docs/command-center/roadmaps/README.md` links all 17 areas with current scope, test checks, planned work and owner note templates. Preserve local pinned ideas; application baseline remains2.0.27. These documentation updates do not require another installer.

> **Installed GUI now verified (2026-10-20):** Found installed2.0.24 after the repeated error report; updated the actual installation to2.0.27 and hash-matched it. Native desktop shows Saved locally and animated Starting Soon at47832; left open. Old Labels47831 remains active. The user had an older2.0.24 GitHub run open. See testing handoff for the correct build link.

> **Replacement build verified (2026-10-20):** 2.0.27, source `6340cd2`, CI run39371961064: 96 tests and packaged conflict checks passed. Downloaded EXE checksums, legacy-port recovery and repeated launch were also verified locally. See `docs/command-center/TESTING_AND_NEXT.md`; owner installed GUI/OBS acceptance remains pending.

> **Installed startup fix (2026-10-20):** Older Labels bridge on port47831 can return Studio JSON 404. Exclusive Windows bind and verified HTML/version reuse now select a nearby port with a visible notice. Tests include occupied legacy port and packaged repeated launch. Native cabinet scaling belongs to the owner in OBS; use supplied widget references and combined-chat/platform-icon roadmap.

> **Owner test handoff (2026-10-20):** Read `docs/command-center/TESTING_AND_NEXT.md`. Build 2.0.24 passed automated and downloaded-EXE checks; owner visual/OBS and upgrade acceptance are pending. The numbered nine-button reference is included; investigate any difference in the installed/saved layout before adding new cabinet shapes.

> **STRICT PIXEL ART:** Read `docs/command-center/PIXEL_ART_CONTRACT.md`. Source control pixels are authoritative; smooth procedural sphere shading is prohibited. Review enlarged control crops before accepting materials.

> **PSD source evidence (2026-10-19):** Read `docs/psd-reference/README.md` and `inventory.json` before changing source geometry or claiming parts are detached. Four documents/47 layer records,16 identical sprites and eight directional demo frames are verified. Beta offsets differ slightly from the approved app; do not silently resize/reposition its glass. Current-shape material acceptance comes before new shell concepts.

> **Cabinet construction update (2026-10-19):** Read `arcade/cabinet-structure.json` and the Cabinet Parts workbench at `/studio/cabinet`. Original artwork, Cabinet 1 paint/large lettering, protected-aperture frame variants and upright reflection are implemented. Baked part separation, shared room perspective rig and Stingers exports remain roadmap work; keep owner pinned ideas.

> **Command Center development update (2026-10-19):** Read [COMMAND_CENTER_README.md](COMMAND_CENTER_README.md), [COMMAND_CENTER_ROADMAP.md](COMMAND_CENTER_ROADMAP.md), `arcade/project-spec.json` and `arcade/stage-registry.json` first. The executable is now **SheldonTwitching - Command Center.exe**. The older sections below document the retained Labels components. Shipped source features and pending real-world acceptance are separated in the new roadmap.

# Codex handoff — SheldonTwitching Labels v0.9

Repo: **PRIVATE** SheldonTwitching/SheldonTwitching-Labels, branch main. This is the owner's personal stream app and arcade art system, not a generic streamer platform.

## Implemented in source (read before editing)

- Python localhost bridge + standalone Windows EXE packaging script and Actions build workflow.
- WYSIWYG controls + raw CSS, Streamlabels file monitoring and rotated labels.
- Spotify PKCE Now Playing metadata widget at `/now-playing` (user must locally connect account).
- Stream Costs through the owner's existing **Streamlabs.com Tip Goal** (NO .txt source), with custom HTML/CSS/JS exported from `streamlabs-tip-goal/` and app `/api/export-streamlabs-tip-theme`. `/tip-bar` is a backward-compatible local demo only.
- 32 playable SF6 character entries now have individual selectable concept art (12 prior PNGs, 20 newly generated transparent WebP); Tifa and Bosch remain marked upcoming.
- Four new scene Browser Source URLs under `/scenes/`: gameplay, starting, brb and ending; existing arcade-cabinet art, transparent game hole, live widget frames and responsive layout. Read `SCENE_SETUP.md` for source stacking details.

## Completion tasks, in priority order

1. **VERIFY BUILD**: Run `python -m pytest tests -q`, `node tests/test_renderer.js` and the JS syntax checks. Check the new GitHub Actions Windows build, download EXE and exercise all scene/widget routes, tray and startup on real Windows/OBS. Fix failures before calling complete.
2. **SCENE REALITY CHECK**: In OBS, position Game Capture beneath the transparent arcade frame, check scene fit at 1920×1080 and tweak camera area, Stream Costs, rotation and Spotify panel positions. The user's current reference screenshot is `docs/channel-brand-reference.png`; the ORIGINAL cabinet art is preserved in `scenes/arcade-frame.webp` with the gameplay hole.
3. **FINISH SPOTIFY**: User must authorize a local Spotify OAuth app (no client secret in Git). Verify current-track title, artist, artwork, pause/disconnect handling and account eligibility; do not broadcast music via the widget.
4. **FINISH TIP BAR**: Keep the actual Streamlabs Tip Goal Browser Source; test custom HTML/CSS/JS in its Streamlabs dashboard, verify `goalLoad`/`goalEvent`, currency and zero/overflow handling, and ensure the OBS gameplay scene does not embed duplicate local goal.
5. **ART QA**: Harmonize palette and faces across existing 12 concept-board crops and 20 new chibi sticker icons; verify recognition of each official playable SF6 character. Do not treat Tifa/Bosch as currently playable. Keep fan artwork personal-use.
6. **STREAM-WIDE POLISH**: Flesh out label presets, event alerts, scene switching, status screens and icons; preserve no-code editor controls AND custom CSS without overwriting the owner's own theme.
7. **TEST AND RELEASE**: Run automated tests and native Windows acceptance. Ship Windows EXE as GitHub Actions artifact or private release with accurate changelog, not fabricated claims.

## Owner-only inputs required before 100% acceptance

- Spotify developer-app Client ID, entered in the local editor, and user's OAuth approval (never ask user to paste tokens in chat).
- Owner preview/approval of Streamlabs.com Tip Goal custom code (no .txt source needed).
- Visual acceptance of complete scene composition (game capture location, camera position and art direction) on their OBS setup.

**Do not restart this project or overwrite the live OBS collection without permission.** Keep all GitHub content private. Work directly in this repo and keep a verifiable changelog of what's tested versus pending.

## Arcade v3 continuation

The `arcade-overlay-v2` branch now includes the v3 FX Lab. Read `ARCADE_V3_README.md` and inspect `arcade_studio.py` before changing controller code. Verify physical XInput D-pad learning and raw button presses using the Windows EXE, test all 20×12 theme combinations and 16:9 game-mask integrity, verify Streamlabels file-change events and authorized Spotify track updates, and keep Streamlabs.com Tip Goal external. The branch is experimental; do not merge without user acceptance. Run `python -m pytest tests -q`, `node --check arcade/editor.js`, and `node --check arcade/overlay.js`.

## Original PNG cabinet continuation

Read `ARCADE_ARTWORK_README.md`. The `arcade-overlay-v2` default now uses the supplied PNG cabinet/sprites at 2060×1220 with native screen coordinates, independent from the optional 1920×1080 FX Lab. All nine joystick PNGs and both button states are present. Do not restore the procedural cabinet as the default or enforce 1280×720 on the original-art aperture. Physical XInput and OBS acceptance remain separate from automated Windows/browser checks.
