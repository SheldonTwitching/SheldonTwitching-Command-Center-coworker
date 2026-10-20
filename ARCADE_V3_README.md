# SheldonTwitching Arcade v3 — XInput Mapper & Visual FX Lab

**Status:** development branch `arcade-overlay-v2`. The approved `main` overlay remains untouched. This is for Sheldon's personal stream.

## Launch in the EXE

- Open `http://127.0.0.1:47831/arcade/editor` or click **Arcade Overlay v2** in the existing Labels editor. The in-EXE web editor is a separate page within the same local app.
- Add `http://127.0.0.1:47831/arcade/overlay` to OBS at **1920×1080**. Place OBS Game Capture **underneath**; place its visible picture inside the editor's green 16:9 safe rectangle (default X 320, Y 138, width 1280, height 720).
- The gameplay transparency is intentionally protected and locked to 16:9. The app cannot move OBS Game Capture itself.

## More visual variation

- **20 palettes** × **12 complete cabinet looks**, plus per-property mixing, random combinations, and independently colored arcade buttons.
- 7 materials, 8 button finishes, 3 frame shapes, 4 scanline patterns, 6 idle light animations, 4 neon-zone patterns, configurable reflections, scanline opacity and glow power.
- 8 distinct button base colors AND 8 independent pressed colors, with press glow strength, afterglow duration, physical bounce / burst / spark / shockwave, and rainbow/accent/original press color modes.
- All visual effects default outside the transparent game opening. "Scanlines over game" must be deliberately enabled; accessibility-reduced-motion styles disable animation.

## XInput D-pad press-to-map

1. Choose the XInput controller slot (0–3). Typical XInput controls are A/B/X/Y, LB/RB, BACK/START, D-pad Up/Down/Left/Right, left/right stick click and LT/RT analog triggers above 50.
2. For any of the **eight visible arcade buttons** hit **Learn**, release all buttons, then press the desired physical input. The editor displays the recognized input and automatically swaps an input already assigned elsewhere.
3. Assign each button its base color, active/pressed color, and optional action separately. Controller presses illuminate visual buttons automatically, even when the editor window is hidden and only the bridge is running.
4. Commands are **disabled by default** to prevent pressing fighting-game inputs from changing your streaming scene. Only enable them knowingly; hold **BACK + START** and press a mapped input. Using the visual Test button bypasses this chord by design.
5. Press-to-map times out after 15 seconds or can be canceled. If your stick is detected as DirectInput/HID rather than XInput, the mapper cannot capture it until a separate DirectInput adapter is implemented.

## Stream event celebrations

Per-event controls: follower, subscriber, donation, raid, bits, goal and song. Each has its own label, color, motion (burst/chase/ripple/pulse/flash/off), duration and which arcade buttons illuminate. **Test event** simulates effects without sending tips or changing your real stream.

Optional real **file-change** triggers: connect your existing Streamlabels export folder in the main Labels editor, then select an actual `.txt` file for each event inside the FX Lab. The first reading is treated as the baseline. Subsequent changes cause a celebration. File-change alerts reflect **a changed label**, not a guaranteed unique tip/follow event (Streamlabels may rewrite an unchanged file, repeat usernames, or omit events). For `song`, if no file is assigned and Spotify is locally connected and playing, new tracks can also trigger music effects. No cloud calls are used for label event detection.

**Stream Costs remains the original private Streamlabs.com Tip Goal widget in its OWN separate OBS Browser Source.** We do not read its amount/goal as a `.txt` and do not collect Streamlabs credentials or a private widget URL. Direct donation/goal alerts from Streamlabs would require a separate supported integration. Use the optional Streamlabels recent-donor file for approximate donation-triggered lighting or the test button.

## Quality and release

- Local: Python validation / mapping tests, JS syntax checks.
- GitHub Actions: Python tests, Streamlabs JS test, Arcade JS checks, PyInstaller Windows build and downloadable executable. A green CI build is not evidence of the owner's physical controller/OBS test.
- Final verification: mouse/keyboard usability in EXE, USB XInput D-pad identification, safe rectangle gameplay visibility, transparent OBS source, performance at 60fps, Streamlabels events, Spotify events, and real Streamlabs Tip Goal overlay alignment.