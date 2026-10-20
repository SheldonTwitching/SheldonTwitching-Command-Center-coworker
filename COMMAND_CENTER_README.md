# SheldonTwitching - Command Center

A local Windows control app for broadcast scenes, widgets, stage art and live arcade parts. The authoritative private repository is [SheldonTwitching-Command-Center](https://github.com/SheldonTwitching/SheldonTwitching-Command-Center), with `main` as its primary branch, established by owner request on 2026-10-20. The earlier Labels repository remains intact as historical reference. Feature acceptance is still separate from branch publication.

## Organization and separate Board application

See [master index](docs/command-center/MASTER_INDEX.md), [art rules](docs/command-center/ART_RULES.md), [Board setup](docs/command-center/BOARD.md) and [master handoff](docs/command-center/HANDOFF.md). The Board and GitHub sync have been removed from the streaming application. Source is retained under extras/standalone-board, saved data is preserved, and the owner has a separate-chat brief for a standalone EXE.

## Open and preview

The desktop executable opens `/studio`. Top navigation provides Preview, Scenes, Widgets & Chat, Weather & Clock, Cabinet & Layers, Controller, Events, Audio & Lighting, Spotify & Music, Setup & Sources, and Widget Roadmaps. The existing labels editor remains at `/editor`.

Preview selects any published scene, widget or live cabinet part. Setup & Sources lists separate OBS URLs and their dimensions. Active-scene `/studio/scene` follows Studio; `?scene=gameplay` pins a scene. Format may be landscape or vertical. Add Game Capture under the overlay. Transparency is real alpha; editor checkerboards do not appear in OBS. Source editing does not modify the existing OBS collection.

## Authoritative definitions

- `arcade/project-spec.json`: product style, fonts, native cabinet parts, measured gameplay aperture, input/layer rules, scene capabilities and source catalog. Runtime layout and cabinet parts consume this file.
- `arcade/cabinet-structure.json`: physical part registry, baked/sprite/region/overlay capability, protected glass, shape/profile bounds, paint atlas bands, lighting roles, reflection pose rules and original/Cabinet 1 presets. The workbench, backend validation and shared rig consume it.
- `arcade/stage-registry.json`: six opening-game stage slots, asset readiness, art briefs, sprite layers, cloud/weather/time rules and lighting masks. Three existing backgrounds are usable; Downtown Neon Alley, Bridge Underpass and Mill District are planned, without invented assets.
- `COMMAND_CENTER_ROADMAP.md`: shipped feature status and next work. The app adds locally saved pinned ideas. New shipped roadmap status refreshes while those ideas survive.

Native cabinet space stays 2060 × 1220. The owner's OBS composition is a separate 1920 × 1080 space with glass **x197/y38/w1541/h868**, margins left197/right182/top38/bottom174. Cabinet panels use a documented piecewise projection; joystick/buttons retain uniform sprite scale and native pivots. The thin gameplay header stays within the top38px and preserves the approved wordmark aspect. The full native marquee is separately available. The painted loading-room cabinet remains a legacy perspective asset pending shared-rig replacement; do not assert it already matches this rig.

## Shared animation and lighting

Opening fights, BRB, ending, chatting and full-screen backgrounds use `arcade/stages.js`, the same stage selection, weather/time and registered art. Choose 24/30/60 fps; default30. Pixel sampling stays nearest-neighbor. Continuous procedural cloud, river, vent and weather loops are implemented; newly drawn cloud sheets, expanded fighter frames and full day/night shadow masks remain art work.

Each scene has a defined music focal item: opening wall ST/brand, gameplay cabinet trim, or the stage ST fixture. Emission/receiver/reflection/shadow layers should be authored separately. Current local fixture backing shadow and light pools are approximate; detailed artwork occluders are pending. Never replace this with a whole-frame music flash. Prefer cached art and small masks, bounded particles, fast attack/slow release, and profile the full OBS stack before claiming60fps performance.

Audio & Lighting selects an audio input, shared desktop/tab audio, or an OBS WebSocket source. Permission is requested only on Start. The capture/OBS connection lives in the open Command Center page and must remain open. No recording/playback occurs. Gain and source settings persist, but capture permission, stream handles and OBS password do not. OBS exposes amplitude, not a frequency spectrum. Captured inputs provide coarse bass/treble bands. Only the selected mode is accepted; stale data becomes zero in one second. Sources subscribe to the shared levels, not separate microphone capture sessions.

## Independent sources and chat

`/overlay`, `/now-playing`, `/studio/chat`, `/studio/text`, and `/studio/parts/{all,cabinet,marquee,buttons,joystick,arrows,lighting,reflection}` are clean separate sources. Cabinet parts all use1920×1080 coordinates: stack at0,0 without individually cropping or resizing. The full native `/arcade/overlay` and `/arcade/overlay?part=marquee` use2060×1220. Do not stack `all` plus its parts, which would duplicate them.

Individual labels have `/overlay?label={id}` URLs, populated from the current project in the source catalog. Chat can be combined or separated with `/studio/chat?platform=twitch` (also youtube/tiktok/twitter). The individual URLs use the same source bindings and styling as their parent editor.

All nine controls are independently XInput mapped. Joystick defaults above arrows and reflection; saved layer order is editable. Only a faint upright joystick arc is reflected at the lower glass edge; buttons and arrows are excluded. Original files are retained. Graffiti marquees reuse the approved logo and existing cabinet color fields. Built-in palettes plus saved named five-color presets persist/export with the cabinet.

Widgets & Chat shows connected Streamlabels feeds and an independent .txt reader (64KB maximum): raw, counts, sum, and text before/after a delimiter. It has its own OBS URL and live reload. Multi-reader collections and richer visual editing remain planned. Chat ingress accepts platform-tagged messages for Twitch/YouTube/TikTok/Twitter; Twitch has the Daigotron adapter. Other native account adapters are pending, not silently simulated. Tests are marked. Real funds stay in the external Streamlabs Tip Goal; only its styling is exported.

## Build and acceptance

`Build-Windows-EXE.bat` builds **SheldonTwitching - Command Center.exe** with the ST icon. Private Actions builds a uniquely versioned per-user installer on each development push. Stable installer ID preserves the existing `%APPDATA%/SheldonTwitchingLabels` profile. The app links to private Actions for updates; authenticated automatic updates/signing remain planned.

Run the Python suite, renderer parser, motion-library, tip-goal and sprite tests. `tests/smoke_windows_exe.py` exercises the actual packaged Windows bridge in a private temporary profile. Separate acceptance remains: physical controller press/learn, actual OBS capture/reflection/layer alignment, real music source, account/chat adapters, Spotify authorization and installer upgrade.

## Cabinet parts workbench and reusable branding

Cabinet & Layers opens `/studio/cabinet`. Owner Original reconstructs the supplied cabinet and original marquee first; Cabinet 1 applies the shared Glacier Graffiti atlas and approved stacked logo over its physical shading. Preview native 2060×1220 or measured Gameplay 1920×1080, then save to apply to live part sources. Per-part capabilities explicitly distinguish baked details from independent controls. The controller/legacy FX editor remains linked, with all nine bindings and custom sprites intact.

Alternate square/chamfered frames support edge profile/width and outward-growing bezel width. The original raster silhouette stays untouched in Original shape; its baked edge widths cannot be independently resized. These are constructed frame variants, not newly authored full cabinet sprites. The rectangular inner game hole is protected in every variant. Actual OBJ/3D geometry, free-form silhouette authoring and separated button-rim masks are not implemented.

The marquee uses the approved `logo-glacier-violet.png` stacked master. Only uniform contain-fitting is permitted. Its surrounding paint fills the long face; the glyphs are never flattened, stretched or relettered. A rejected wide ribbon experiment is not shipped. Native full-face preview is `/studio/parts/all?view=native`; query `design=original` or `design=cabinet1` previews without changing a saved preset. The top38px Gameplay band necessarily limits logo height; changing that band would require a new owner-approved aperture/layout, not silent crop changes.

Joystick reflection selects BACK↔FRONT for vertical movement, keeps neutral upright and leaves side/diagonal poses unchanged. Buttons and arrows are excluded from the reflection. Only a faint top arc of the ball is admitted at the lower glass edge: default 10 native pixels and 8% opacity, both adjustable. It does not flip the sprite. Real stick behavior remains unchanged. Layer order is editable, including the arrow/stick overlap.

The Stingers roadmap in Widget Roadmaps reuses this paint/wordmark family. Stinger timelines, transparent video export and OBS transition playback remain planned; no fake video files or completed transitions are claimed.

## Mandatory surface-detail logic

`cabinet-structure.json.surfaceDetailRules` defines the construction and acceptance rules for every future cabinet style: base material and return-face depth, outward bevel/recess/inner lip, panel-bound paint, visible seams/miters/contact detail above paint, bounded emitters and preserved dark-side shading. Painted variants include large registered shoulder splashes beneath both marquee corners. Original artwork remains unchanged in the Original preset. Do not call a flat fill plus outline a finished cabinet or reletter/stretch the approved logo to fit a sign.

## Reskinned deck and full frame paint

Cabinet 1 replaces the inlay faces of the left and button panels with opaque new laminate and painted pixel art. Source stripe print is not blended back over the replacement; matching original interior stripe FX is masked out too. Panel perimeter bevels/dividers, recessed edge seams and control contact depth remain. Owner Original keeps its source artwork and FX.

`cabinet-structure.json.panelSurfaces` registers both inlays and the four painted screen-surround planes: upper bridge, left/right uprights and lower sill. Paint sampling turns with vertical uprights and uses uniform cover-fitting. The inner glass lip and measured game hole remain excluded. The manifest's surface rules require future skins to replace obsolete printed artwork and matching FX together.

Cabinet & Layers includes a **Lever direction lights** color picker. The same setting is available under Physical part → Lever directional lights, with opacity and glow. It saves as `cabinetParts.arrows.color`, independent of button colors and shell trim, and applies to both aligned part URLs and the retained native overlay. Original arrow silhouettes and input mapping stay intact; neutral input turns all direction lights off.

## PSD-backed authoring evidence and material controls

Read `docs/psd-reference/README.md` and `inventory.json` before changing sprite bounds, pivots, press travel, arrow sizes or source-layer claims. The source PSD is unchanged. Its eight recovered directional frames are authoring evidence; their original timing is not established. SCREEN layer bounds do not replace the measured capture aperture.

The shared `/studio/parts/` rig now adds source-alpha button cap/rim regions, nine palette roles and per-button neutral/pressed overrides, source-pixel ball palette remapping (directional relighting awaits authored pixel masks), independent trim/inner-return colors, paint exclusion gutters and marquee overhang shadow strength/reach. These are runtime material masks, not proof that the source PSD separates these parts. All styles preserve source control pixel clusters and dither; see `docs/command-center/PIXEL_ART_CONTRACT.md`. The original preset and custom sprite overrides retain supplied artwork. Original DOWN indicators keep44×46 dimensions; pressed buttons travel6px and keep their60px height.

Cabinet & Layers exposes these controls. Logo bloom follows the shared selected audio envelope and is confined to logo ink/halo instead of flashing the painted face. Source PSD and Shape Concepts each have their own roadmap with pinned ideas; new shape production follows acceptance of the current silhouette. The retained native legacy overlay keeps original control rendering except already supported direction tint and corrected original arrow height; advanced material masks are in the shared rig used by Studio and Gameplay.

## Preview windows and local workspace

See [pop-out previews and screenshot feedback](docs/command-center/PREVIEW_AND_FEEDBACK.md) and [owner-selected local file organization](docs/command-center/WORKSPACE_STORAGE.md). New preview windows preserve native source sizes and follow saved edits. Private User Data and local reference archives stay outside the Git checkout.
