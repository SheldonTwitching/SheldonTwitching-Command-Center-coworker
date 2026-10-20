# SheldonTwitching Arcade Overlay v2 — design branch

**Branch:** `arcade-overlay-v2` in the owner's private SheldonTwitching-Labels GitHub repository. This is an additive prototype and does not overwrite the original `main` overlay or its Streamlabs Tip Goal.

## What is new

- Arcade Overlay Studio inside the existing SheldonTwitching Labels Windows EXE at **`http://127.0.0.1:47831/arcade/editor`**.
- OBS Browser Source at **`http://127.0.0.1:47831/arcade/overlay`**, width **1920**, height **1080**.
- Completely redrawn CSS neon cabinet with original SheldonTwitching branding cues: angled rails, lit marquee, simulated joystick, eight colored buttons, reactive arcade lighting, scanlines, button designs and rounded/angular borders.
- Six configurable cabinet color channels, five preset themes, individual color for each of eight buttons, animation sliders, optional scanlines **not over the game by default**, and a protected 16:9 gameplay opening.
- Default gameplay safe area: **x=320, y=138, width=1280, height=720**, including the 16:9 ratio. The editor allows 1024–1440 width; positions are clamped to keep a usable game opening and control deck. The actual game source is a separate OBS Game Capture positioned/scaled behind this transparent region.
- Eight on-screen test buttons with per-button actions. A compatible Windows XInput controller (controller slot 1–4) can light the panel in real time without the editor open, because the local bridge polls XInput directly. No third-party drivers or network service are needed.
- Optional modifier-protected controller shortcuts: **BACK + START + mapped button**, enabled explicitly; off by default to prevent game inputs changing the stream. The app does not send game inputs.
- Reuses the existing `/overlay` for follower/subscriber/donor label rotation and `/now-playing` for Spotify. Stream Costs remains the owner's private **Streamlabs.com Tip Goal Browser Source**, layered separately in OBS; no donation total is fabricated or mirrored by the app.
- Separate local settings file `%APPDATA%/SheldonTwitchingLabels/arcade-overlay.json`, backup independent of main editor project.

## OBS setup (do not replace working scene yet)

1. Clone or download the `arcade-overlay-v2` branch, run the editor locally, or compile the EXE using `Build-Windows-EXE.bat` / the branch GitHub Actions artifact.
2. Open Arcade Studio from the main app toolbar and choose a preset, colors, button mappings and effects.
3. In a **new test scene**, create a Browser Source pointing to `http://127.0.0.1:47831/arcade/overlay`, exactly 1920×1080, and place it **above Game Capture**.
4. Place/resize your Game Capture to the displayed 16:9 safe region. The default bounds are **(320, 138) to (1600, 858)**; if you change the window size or position in Studio, update Game Capture's OBS transform to match. The game itself stays 16:9 and readable; we do not stretch it.
5. Keep the existing Streamlabs Tip Goal browser source with its original private widget URL in OBS, **above** the arcade overlay, and position it in your desired marquee/rail slot. Do not embed its URL in GitHub or the local project.
6. The bridge must remain running while streaming (it can be in the Windows notification tray). This is a local-only utility.
7. Only replace your current stream scenes after you have tested the game, controller, tip source, Spotify, window scaling, and overall composition.

## Controller behavior & caveats

**Reactive lights** use Microsoft's XInput API on Windows, so they can respond while the app's designer is hidden in the tray. XInput supports Xbox-style controllers and some arcade sticks, but many fight sticks present as DirectInput-only or keyboard HID devices. Those **will not be detected by this first integration**. The eight virtual buttons in the editor work independently and are always available for testing. We need your fight-stick model/Windows controller mode to implement the correct HID mapping if necessary.

OBS Browser Source should not interact with game inputs. Its controller lights arrive through the companion localhost bridge.

## Remaining before release

- Native Windows and OBS verification, ideally during SF6 training mode.
- Confirm the actual hardware button mapping with your arcade/fight-stick controller; XInput is a supported first pass, not proof of universal controller support.
- Refine positions and effects around the exact canvas and capture/card dimensions of your current OBS scene collection.
- Confirm Spotify account connection and Streamlabs Tip Goal theme inside their own dashboards.
- Audit accessibility/reduced-motion and any custom fonts you want to reuse.