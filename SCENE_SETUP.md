# SheldonTwitching — Arcade stream scenes (working first layout)

These optional OBS Browser Source scene skins use your **actual uploaded `ArcadeCabinet_FINAL.png` artwork**, not a replacement logo. The inner cabinet screen has been made transparent so an OBS Game Capture can show through it. They are independent of the labels editor and do not overwrite the existing OBS scene collection.

## OBS setup (1920 × 1080)

1. In your current OBS **Gameplay** scene, add your existing Game Capture source first (below the cabinet).
2. Add a new **Browser Source** called `Arcade Cabinet — Scene Skin`, enable **Local file**, choose `scenes/gameplay.html`, set Width `1920`, Height `1080` and keep **Shutdown source when not visible** off.
3. Match your Game Capture to the transparent inner screen: approximately **X = 399, Y = 324, W = 1122, H = 510** at 1920 × 1080. The original cabinet art screen isn't exactly 16:9; consider **Fit to Screen** inside the hole (letterboxing) to prevent distorting gameplay.
4. The gameplay skin hosts rotating labels and Spotify through the local bridge, but leaves Stream Costs empty for the existing **Streamlabs.com Tip Goal Browser Source** as a separate OBS layer ABOVE this scene. Keep `SheldonTwitching Labels.exe` bridge running.
5. Keep your webcam as a separate OBS source (usually in the lower-right corner); the scene skin deliberately does not embed any camera feed.
6. For extra scene transitions, create separate OBS scenes and load `scenes/starting.html`, `scenes/brb.html` and `scenes/ending.html` at 1920 × 1080. All three render without the local bridge, using the same cabinet artwork. They can be used for Starting Soon, Be Right Back and Stream Ending.
7. Edit `scenes/scene.js` to change on-screen text, and `scenes/scene.css` to change positions, colors and motion. No recompilation necessary.

**Important:** This is the first implementation of a complete scene *layout family*, not a guaranteed pixel-perfect replacement for your live OBS collection. Review the screen hole alignment, camera position, letterbox fit and text in your actual OBS before switching. The browser files have no audio and do not rebroadcast Spotify music.

## Repo assets

- `scenes/arcade-frame.webp`: optimized owned cabinet illustration with a conservative alpha hole for gameplay
- `scenes/*.html`: four OBS scene browser sources, each using the same CSS and JavaScript
- `assets/sf6/*.webp`: individual transparent chibi-inspired fighter icons; `web/roster.json` is the authoritative manifest

## Widgets

- `http://127.0.0.1:47831/overlay` — follower/sub/donor rotation
- Stream Costs: **your existing private Streamlabs.com Tip Goal URL** in its own OBS Browser Source (do not publish the URL)
- `http://127.0.0.1:47831/streamlabs-tip-preview` — local theme sample preview (NOT live amounts)
- `http://127.0.0.1:47831/now-playing` — Spotify metadata (requires local account authorization)

In OBS, don't use the artwork as a single opaque image without the supplied alpha hole, or gameplay will be obscured. If the local widget bridge is offline, hide the gameplay scene skin and restart SheldonTwitching Labels.
## Important: Stream Costs is managed by Streamlabs.com

The local demo `/tip-bar` must **not** be used for actual Stream Costs. Keep your current Streamlabs.com Tip Goal Browser Source in OBS with its existing private URL. The gameplay cabinet scene provides an empty placement at approximately **x=576, y=205; width=760, height=108** on a 1920×1080 canvas; put your real Streamlabs browser source over it.

To redesign the bar, use SheldonTwitching Labels → Stream Costs · Streamlabs Tip Goal → Export Streamlabs HTML/CSS/JS, then paste the code in your Streamlabs dashboard's Tip Goal custom code controls. See `STREAMLABS_TIP_GOAL_SETUP.md`.
