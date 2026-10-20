> Current test build: **2.0.28**, including separate preview/editor windows and relocated app data. [Reinstall and screenshot feedback](docs/command-center/PREVIEW_AND_FEEDBACK.md) | [Workspace layout](docs/command-center/WORKSPACE_STORAGE.md).

# Command Center roadmaps

Updated 2026-10-20. Owner visual/OBS acceptance remains pending. The owner scales native pixel artwork in OBS and will provide widget references.

[Testing and notes for all 17 roadmaps](docs/command-center/roadmaps/README.md). Use build **2.0.27**; installed desktop startup is verified, while full owner OBS acceptance is pending.

## Social Media Packages

[Test checklist and owner notes](docs/command-center/roadmaps/social.md)

The approved Glacier Graffiti marquee and source PSD lighting structure define the visual direction. Social PNG export templates remain planned.

- Compose banner and offline-screen layouts using the approved logo and reusable panel paint
- Define export sizes and safe regions for each requested platform at implementation time
- Add palette-driven PNG package export with preview and source-asset provenance

## Widget Animation Library

[Test checklist and owner notes](docs/command-center/roadmaps/animations.md)

24 entrance/exit styles plus four idle icon loops implemented in the existing labels editor.

- Curate readable motion presets for each widget type
- Add reusable timeline and layered effect presets
- Test reduced motion and performance across the live scene stack

## Installers & Updates

[Test checklist and owner notes](docs/command-center/roadmaps/updates.md)

Exact Command Center EXE name, ST icon, per-user installer definition and private Windows pipeline implemented; refreshed build acceptance pending.

- Verify launch with an older Labels bridge already running: clear notice, free local port and working Studio HTML
- Build and verify the latest Windows EXE and installer
- Test upgrade preserves local projects and presets
- Add signed releases and private authenticated update discovery

## Rotating Labels

[Test checklist and owner notes](docs/command-center/roadmaps/labels.md)

Visual editor, source bindings, rotation, raw CSS, local persistence and individual label OBS URLs implemented.

- Connect and check the actual Streamlabels files
- Polish pixel-art presets and transitions
- Verify updates while the EXE stays in the tray

## Spotify Now Playing

[Test checklist and owner notes](docs/command-center/roadmaps/spotify.md)

PKCE authorization and playback widget implemented; owner account acceptance pending.

- Complete local owner authorization
- Verify artwork, pause and reconnect states
- Tune track-change effects with cabinet lighting

## Stream Chat

[Test checklist and owner notes](docs/command-center/roadmaps/chat.md)

Editable combined/per-platform chat URLs and Twitch/Daigotron ingress implemented. YouTube, TikTok and Twitter/X account adapters are not implemented.

- Combine messages from all connected YouTube, Twitch, TikTok and Twitter/X accounts into one simple chronological feed
- Show a recognizable platform icon on every message so its source is clear
- Use owner-supplied OBS widget version as the design/behavior reference
- Verify Twitch ingress and implement supported account adapters for the other platforms
- Preserve editable styling, CSS and readable pixel-art animations

## Streamlabs Tip Goal

[Test checklist and owner notes](docs/command-center/roadmaps/tipGoal.md)

Existing external goal stays authoritative; custom theme exporter implemented.

- Collaborate with owner on attractive tip-bar styling using their supplied reference; keep the existing Streamlabs goal authoritative
- Back up and test the theme in Streamlabs
- Verify live goalLoad/goalEvent formatting
- Fit the separate OBS source into each scene

## Notifications & Event Lights

[Test checklist and owner notes](docs/command-center/roadmaps/events.md)

Per-event styles, manual tests, priority queue and cooldown controls implemented.

- Verify supported real event sources
- Add reusable per-button effect presets
- Tune interruptions, sound and accessibility

## Weather & Clock

[Test checklist and owner notes](docs/command-center/roadmaps/weather.md)

Bangor weather, network clock, independent manual overrides and shared stage weather/time rendering implemented. 24/30/60 fps is selectable.

- Create distinct day/dusk/night art and shadow masks per stage
- Author seamless looping cloud layers and seasonal sprites
- Verify DST, long offline recovery and weather transitions

## Scene & Stage Library

[Test checklist and owner notes](docs/command-center/roadmaps/scenes.md)

Seven broadcast modes, shared stage renderer, BRB/outro stage reuse and landscape/vertical layouts implemented. Opening-game registry defines six stage slots: three existing backgrounds and three planned.

- Draw Downtown Neon Alley, Bridge Underpass and Mill District stage art
- Create separate seamless cloud sheets and foreground loops for each stage
- Author time-of-day light and occlusion masks for all six stages
- Rehearse every scene, monitor layout and capture aperture in OBS

## Preview & OBS Sources

[Test checklist and owner notes](docs/command-center/roadmaps/preview.md)

Built-in preview selector and source catalog implemented for scene outputs, widgets and aligned live cabinet parts.

- Use owner-provided OBS widget versions before redesigning individual widgets
- Verify every source at its documented OBS dimensions
- Add per-widget sizing presets and saved monitor layouts
- Add a layered preview compositor for separate OBS parts

## Audio & Scene Lighting

[Test checklist and owner notes](docs/command-center/roadmaps/audio.md)

Input/desktop capture and selectable OBS source meters feed shared audio state; stale signals settle to zero. Local fixture, cabinet and room lighting implemented.

- Verify the owner music source and mute/reconnect in OBS
- Author precise emission, receiver, occlusion and reflection masks per stage
- Add saved per-scene gain and light routing
- Profile 24/30/60 fps on the full OBS stack

## Text Reader & Parsing

[Test checklist and owner notes](docs/command-center/roadmaps/text.md)

Independent bounded .txt reader with live raw text, line/word/character counts, text matches, numeric sum and delimiter extraction. Separate OBS URL implemented.

- Add named multiple readers and user friendly native file picker
- Add saved parser recipes and resettable counter sources
- Expand visual styling and animation controls

## Cabinet Structure & Marquee

[Test checklist and owner notes](docs/command-center/roadmaps/cabinet.md)

Strict source-pixel palette recoloring replaces smooth ball shading and restores button contrast. Full trapezoidal marquee coverage and independent trim masks are defined. Native sprite geometry, protected glass and upright reflection remain. Owner visual acceptance pending.

- Preserve native PSD-like pixel-art proportions; owner scales and zooms the gameplay overlay in OBS as appropriate
- Review native and gameplay renders plus enlarged pixel-control crops before adding new shapes
- Author pixel-preserving directional light masks; smooth procedural spheres are prohibited
- Refine detached cap/rim masks against the original PSD
- Verify marquee face coverage and blue trim containment in OBS
- Replace legacy loading-room cabinet with shared perspective rig

## Stingers & Transition Packages

[Test checklist and owner notes](docs/command-center/roadmaps/stingers.md)

Shared Glacier Graffiti paint atlas and approved stacked SheldonTwitching wordmark are available. Stinger playback and export are planned.

- Storyboard painted wipes, logo slams and cabinet-to-stage reveals using the shared panels
- Define 24/30/60 fps timelines, duration and exact covered-frame OBS cut points
- Add palette presets, logo safe margins and matching transition sound controls
- Export transparent WebM and compatible alpha masters with clean first/last frames
- Test alpha edges, OBS transition timing, interrupted transitions and audio in a full rehearsal

## Source PSD & Asset Pipeline

[Test checklist and owner notes](docs/command-center/roadmaps/sourceArt.md)

Original Beta PSD inspected read-only: four PSD/PSB documents, 47 layer records, 16 pixel-identical runtime sprites and eight recovered directional demo frames. Evidence and source hash are stored in docs/psd-reference.

- Enforce docs/command-center/PIXEL_ART_CONTRACT.md for every new sprite, reskin and animated scene
- Verify original GIF timing in Photoshop; do not infer fps from global light angle
- Reconcile Beta cabinet/FX origins and arrow placement with the approved app alignment
- Author explicit source masks for trim, return faces, button cap/rim and sphere materials
- Keep source PSD immutable and export versioned assets with native bounds, alpha and pivots

## Cabinet Shape Concepts

[Test checklist and owner notes](docs/command-center/roadmaps/cabinetShapes.md)

Current original silhouette remains the active acceptance target. Square/chamfered constructed prototypes exist; no new approved shape artwork is claimed.

- Accept paint containment, overhang shade, control materials and lighting on the current silhouette
- Explore wide tournament, tall narrow and rounded compact shell concepts
- Define panel thickness, trim paths, receiver planes and controller clearance for each shape
- Fit each shell around the protected game aperture; review native and projected views before production
