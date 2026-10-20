# Original cabinet artwork — arcade-overlay-v2

The default scene now renders the owner's supplied PNG layers and sprites. The earlier procedural CSS cabinet is still available under **Scene artwork → FX Lab**, with all 20 palettes and 12 styles. These options never recolor or replace source PNGs. The existing Streamlabs.com Tip Goal is untouched and remains a separate OBS source.

## Measured source geometry

- Reference `ArcadeCabinet_FINAL.png`: **2060 × 1220**. This is the original-mode browser-source canvas; it is not stretched to 1920 × 1080.
- Newly supplied `Cab/CABINET.png`: **1942 × 1220**, placed at **(59, 0)**. It differs from the older 2030-wide synced CABINET and the flattened reference; those are not identical exports.
- `FX.png`: **2030 × 1220**, placed at **(15, 0)**.
- Marquee: the top 270 pixels of the older synced CABINET, at **(15, 0)**. This preserves the exact existing logo/header absent from the newly supplied Cab/CABINET. The complete original PNG is retained; CSS clips the marquee region without raster editing.
- The largest fully transparent rectangular screen area through both new CABINET and FX layers is **1174 × 578 at (443, 374)**. It ends at x=1617, y=952, exclusive. Tests check every alpha value in this rectangle. Preserve your game source's own aspect ratio inside those bounds; do not stretch a 16:9 game into this wider opening. A centered 16:9 fit is approximately 1028 × 578 at (516, 374).
- `BUTTON_AREA.png` / older BUTTON sheet: **440 × 110 at (1113, 1049)**. Opaque pixels match the full reference exactly at this position.
- Eight main button top-left positions, in top-row then bottom-row order: **(1139,1053), (1219,1049), (1299,1049), (1379,1053), (1113,1093), (1193,1089), (1273,1089), (1353,1093)**.
- Neutral button: **78 × 66**; pressed button: **78 × 60**. The pressed state moves down six pixels so its bottom remains anchored. The separate ninth button at **(1475,1083)** is retained as decoration.
- Neutral joystick: **100 × 204 at (842,942)**, an exact opaque-pixel match to the full reference. All nine states anchor the shaft endpoint at **(891,1115)**. Unequal sprite sizes are not centered in a shared box.

Joystick source dimensions: NEUTRAL and FRONT 100×204; BACK 100×158; BACK_LEFT 124×140; BACK_RIGHT 124×138; LEFT/RIGHT 136×178; FRONT_LEFT/FRONT_RIGHT 126×168. Their measured shaft anchors are recorded in `arcade/assets/geometry.json` and `arcade/sprites.js`.

The supplied GIF `2019185_d1e5e.gif` is **400 × 214**, **13 frames × 100 ms = 1300 ms**, disposal mode 2. It shows blinking eyes and sparkles, not cabinet movement or controller states. It is not used as evidence for cabinet sprite timing. The joystick consists of nine input states, not nine frames of a timed animation.

## Editing and input

Open `/arcade/editor` from the EXE's Arcade Overlay V2 button. Drag numbered handles for the eight buttons and J for the shaft pivot; positions autosave and use the same renderer in preview and OBS. **Restore original sprites and positions** restores the measured layout.

Default input bindings are X, Y, RB, LB on the upper row and A, B, RT, LT on the lower row. Each can be remapped or learned. The XInput D-pad selects the nine joystick states; opposing directions cancel. All four arrow assets light for corresponding D-pad input. Normal input never sends game commands. The prior BACK+START modifier for optional cabinet commands remains opt-in.

Import per-button neutral/pressed PNGs, replace individual joystick-state PNGs, or import a sprite for the event currently selected in the event panel. Joystick replacements should use the corresponding original frame dimensions and pivot. Each image is limited to 400 KB; the existing local API also caps the total encoded request at 2.5 MB. Event sprite rules, targets, colors, duration and effects remain independent for donations, subscribers, followers, raids, bits, goals and songs. File-change/manual preview events do not imply a direct live Streamlabs donation connection.

Original-mode scanlines/reflections require **Apply optional scanlines and reflections to original art**. Default optional effects and widget content are off so the artwork starts clean. Existing saved widget selections are retained. Palettes/styles apply to the optional FX Lab cabinet, while native-art lighting and event effects can be configured separately. Tip Goal totals and its private URL are never imported.

OBS source URL: `http://127.0.0.1:47831/arcade/overlay`; original browser dimensions **2060 × 1220**. Place Game Capture underneath, retain its aspect ratio, and fit both sources together if the OBS output canvas differs. The screen hole itself remains transparent, including on reload. Do not independently stretch the cabinet to fill a 16:9 output.

## Verification status

Implemented and locally checked: source-pixel placement, PNG dimensions/alpha, nine-direction selection and shaft anchoring, face/D-pad separation with simulated input, validated saved positions and sprite overrides, legacy event migration, browser transparency, drag/save/reset, and switching between original and optional CSS scenes.

Automated checks: `python -m pytest tests -q`; `node tests/test_arcade_sprites.js`; existing renderer/Tip Goal script tests and JavaScript syntax checks. Browser tests require Playwright Chromium. CI installs it, tests the production editor/renderer, packages the Windows EXE with `arcade/**`, and runs `tests/smoke_windows_exe.py` against the compiled executable and all supplied sprite routes before uploading the artifact.

Native Windows bridge/packaging verification is reported separately from physical XInput and OBS acceptance. Physical button/D-pad learning, live game capture fit and OBS's embedded browser still require an owner session. No live OBS scene collection was edited. This branch is not marked release-complete on the strength of browser or CI checks alone.

Local Windows validation (2026-10-19): the PyInstaller EXE launched with a temporary configuration, served every one of the 18 required PNG routes and the native geometry, and reported a connected XInput controller. This confirms connection detection, not physical press/learning acceptance. Production Chromium tests also confirmed all nine sprite directions, both button states, transparent pixels, dragging/reset and scene-mode round trips. OBS Studio was installed but not running, so no OBS render or live collection verification is claimed.
