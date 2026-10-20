# SheldonTwitching — ARTSTYLE and PSD production contract

Version 1.0 • Owner direction, 2026-10-20 • Feed this Markdown file to Copilot alongside the named PNG references.

This is an art-production specification, not a claim that its PSD layers already exist. The source rooftop is a flattened 1672×941 illustration. It provides materials, composition and atmosphere; hidden surfaces and independent light/weather masks still have to be authored. The generated candidate atlases are style studies, not approved game-ready sprites or verified loops. Original control references are copied without pixel edits.

## 1. Identity and hierarchy of references

The style is detailed arcade pixel art: stepped silhouettes, deliberate clustered highlights, restrained dithering, physical material depth, weathered metal, old brick and painted graffiti. Preserve readable dark negative space. Avoid smooth procedural spheres, vector ellipses replacing source controls, photographic noise, painterly smears and blurred base artwork.

1. references/original-controls/*.png: exact control shape, authored pixels, shading and transparency.
2. references/graffiti-paint-reference.png: cyan/violet/magenta paint language, not permission for paint to cross material edges.
3. references/rooftop-material-reference.png: rooftop composition, weathered architecture, wet surfaces and lighting hierarchy. This imagined tall-city skyline is not a literal view of Bangor.
4. references/cabinet1-composite-reference.png: cabinet composition only. Its historical trim bleed is a defect, not a style feature to reproduce.
5. candidates/*.png: new image-generated examples to guide further work. They require pixel-scale, silhouette, alpha and registration review. Never override an original sprite with a candidate automatically.

Copilot uses these as visual context; attaching images does not train or permanently teach the model. Start each new generation conversation with this file and the relevant references.

## 2. Palette and pixel discipline

Core colors: shadow indigo #100d20, deepest navy #080e1c, slate blue #273650, glacier cyan #80d7ff, strong cyan #23c9ff, violet #9664ed, restrained magenta #ed36ce, pale highlight #e4efff. Environment accents may add rusty brown #8b4b35, brick #713c4a, lamp amber #ffb65c and sunset rose #f8629a. These are role anchors, not a claim that existing source PNGs use only those exact values.

Use a small authored ramp per material (usually 4–8 tones), consistent light direction and readable dark faces. Author at actual pixel resolution with a 1-pixel grid and deliberate clusters; stage detail may use 2–4-pixel clusters. Do not infer that a model output is exact 64×64 pixel art because the prompt requested it. Review actual pixels, then document the approved logical grid per asset. Do not repeatedly resize to fix mistakes. Integer enlargement and nearest-neighbor preview only. The original controls keep their own native grid.

Base art, emission, receiving light, occlusion, contact shadow and reflection are different layers. Soft additive light may be a separate optional runtime layer; it must never soften or replace the crisp underlying pixels. Keep unlit art complete and attractive with all FX disabled.

## 3. PSD master and coordinates

New stage master: ST_Bangor_Rooftop_Master_v001.psd, 1920×1080 px, RGB/8, sRGB. Origin is top-left; +X right, +Y down. This is a new production canvas, not the source image's native size. Import the 1672×941 reference only into a locked hidden guide group, uniformly contain-fitted; never stretch it or call the rescaled reference finished pixel art. Redraw/separate the approved composition on the chosen production grid.

Proposed production guides, to lock before individual layer generation: horizon Y=420; roof rear edge Y=736; usable fighting baseline Y=930; sun/moon nominal center (1140,320); clear central fight region X=300..1620 and Y=736..1000. These are new authoring anchors, not measured source coordinates. Review once, then freeze them for all exports and day/weather variants. No generated prop may move the fight baseline or obstruct central fighters.

All environmental layers export at the full 1920×1080 document size with transparent unused pixels. Isolated prop sprites may be tightly bounded only if an explicit full-stage anchor, pivot, width/height and placement are supplied in metadata. Keep export trimming OFF by default so PSD layers remain registered. Overscan/wrapping tiles have their own explicit dimensions. No hidden reference, notes, guides, checkerboard or comparison labels in an export.

Group names use NN_GROUP; children use lowercase stable IDs. PSD Layers panel is top-to-bottom front-to-back, so high-numbered groups sit above lower ones. The accompanying psd/rooftop-layers.json is listed back-to-front for rendering. Normal for opaque base art, Multiply for shadow previews, Screen for light previews. Export raw receiver/emission/occlusion masks separately; do not assume Photoshop blend appearance is itself a runtime mask.

## 4. Full rooftop PSD stack — back to front

### 00_REFERENCE_AND_GUIDES — hidden, locked, never exported

reference_original_flat; reference_graffiti_palette; reference_pixel_grid; guide_horizon; guide_roof_rear_edge; guide_fight_baseline; guide_safe_regions; guide_vanishing_point; notes_asset_ids. Keep scale/color annotations here, not painted into art.

### 10_SKY

sky_day_base; sky_dusk_base; sky_night_base; sky_dawn_base; sunset_warm_band; night_stars; sun_disc; sun_emission_mask; moon_disc; moon_emission_mask; sky_atmospheric_haze. Bases are mutually exclusive time variants. Use pixel-banded ramps. Stars stay behind clouds. The sun/moon can be occluded by cloud layers; no permanently baked sun halo over foreground objects.

### 20_FAR_CLOUDS

clouds_far_base; clouds_far_sunlit_edges; clouds_far_night_ramp; clouds_far_opacity_mask; clouds_far_wrap_tile. Draw billowing masses as pixel clusters, with clean alpha and no checkerboard. The tile wraps horizontally and has documented seam overlap. Weather changes coverage/opacity; time changes the lit-edge ramp. Geometry does not regenerate at each weather request.

### 30_DISTANT_LANDSCAPE_AND_CITY

maine_treeline_silhouette; distant_low_skyline; distant_mid_skyline; distant_tower_accents; rooftop_antennas; crane_silhouettes; skyline_contact_haze; skyline_window_emission; antenna_beacon_emission; skyline_light_occlusion. Separate dark building bodies from window pixels and beacon points. Keep left, center and right building clusters separate subgroups if they receive independent parallax or masks.

### 35_PENOBSCOT_RIVER_AND_BRIDGE

river_base_color; river_far_bank; river_directional_ripple_tile; river_sky_reflection; river_city_reflection; river_bridge_reflection; river_reflection_occlusion; bridge_rear_piers; bridge_deck; bridge_truss_or_girders; bridge_contact_shadows; bridge_light_emission. Match water reflections to actual object positions and river perspective. Reflection texture motion is separate from the reflected silhouettes. The rear river/bridge is distant scenery, never the walkable fight floor.

### 40_NEAR_CLOUDS_AND_DEPTH

clouds_near_wrap_tile; clouds_near_lit_edges; distance_fog; midground_mist; skyline_weather_occlusion. Place this depth band in front of distant scenery but behind rooftop hardware. Use restrained opacity; never place one global gray veil over everything regardless of distance.

### 50_ROOFTOP_REAR_STRUCTURE

rear_parapet_base; rear_parapet_top_faces; rear_parapet_cracks; rear_parapet_paint; rear_parapet_seams; rear_parapet_contact_shadow; fence_posts; fence_top_rail; fence_wire_mesh; fence_wire_highlights; fence_occlusion; rear_pipes_horizontal; pipe_elbows_and_clamps; rear_junction_boxes; pipe_contact_shadows; rooftop_edge_shadow. The fence mesh has real transparent holes. Paint stays inside parapet faces and does not recolor the rail, fixtures or edge caps.

### 60_LEFT_FOREGROUND_ASSEMBLY

left_steel_upright; left_cross_braces; left_overhead_beam; left_rivet_details; left_steel_edge_highlights; left_hanging_cables; left_vertical_conduit; left_lamp_mount; left_lamp_housing; left_lamp_glass_unlit; left_lamp_emission; left_lamp_receiver_wall; left_lamp_receiver_floor; left_lamp_occlusion; left_HVAC_body; left_HVAC_fan_grille; left_HVAC_vent_slats; left_HVAC_rust; left_HVAC_contact_shadow; left_graffiti_decal. Group all members under a fixed anchor so a weather/time variant cannot move the assembly.

### 65_RIGHT_FOREGROUND_ASSEMBLY

right_overhead_platform; right_platform_guardrail; right_upright; right_rivets; right_cable_loops; right_conduit; right_lamp_mount; right_lamp_housing; right_lamp_glass_unlit; right_lamp_emission; right_lamp_receiver_wall; right_lamp_receiver_floor; right_lamp_occlusion; right_HVAC_body; right_fan_grille; right_secondary_vent; right_HVAC_rust; right_pipework; right_equipment_contact_shadows. Do not mirror the left assembly wholesale: distinct silhouettes, same materials/light rules.

### 70_FIGHT_FLOOR

floor_base_tiles; floor_tile_variation; floor_cracks; floor_seam_recesses; floor_edge_chips; drainage_grates; grate_recess_shadows; bolts_and_fasteners; old_yellow_markings; floor_stains; puddle_coverage_mask; puddle_dark_base; puddle_sky_reflection; puddle_fixture_reflection; puddle_ripple_animation; floor_light_receiver; floor_snow_receive_mask; floor_precipitation_splash_mask. Keep walkable area visually readable and level. Crack/stain overlays must not masquerade as obstacles. The wet state changes material/reflection coverage without replacing the tile geometry.

### 75_LOCAL_AMBIENT_SPRITES

vent_steam_rear; vent_steam_front; loose_cable_idle; fan_rotation; tiny_airborne_dust; isolated_water_drips; drip_impact_ripples; distant_window_flicker; antenna_beacon_cycle. Each is independently enabled with anchors and timing; no full-background sprite-sheet regeneration for one rotating fan.

### 80_WEATHER_DEPTH_BANDS

rain_far; rain_mid; rain_near; rain_floor_splashes; snow_far; snow_mid; snow_near; snow_surface_accumulation; fog_far; fog_mid; fog_ground; storm_lightning_emission; storm_sky_receiver; storm_building_receiver; storm_occlusion. Rain/snow/fog are separate switchable effects, not textures baked into every art layer. Precipitation behind a foreground object is hidden by that object's occlusion mask. Near particles may overlap it when physically in front.

### 85_SCENE_LIGHT_RIG — control/mask groups

keylight_direction_guide; ambient_time_ramp; sunlight_receiver; sunlight_occlusion; moonlight_receiver; fixture_receiver_left; fixture_receiver_right; music_focal_emission; music_focal_receiver; music_focal_occlusion; music_focal_reflection; contact_shadow_receivers. For the first test, route music to ONE existing wall lamp or a new blank industrial light fixture. Do not generate a replacement ST logo; if an ST fixture is later used, place the approved mark as its own asset.

### 90_FINAL_PREVIEW — optional authoring-only

time_variant_selector; weather_variant_selector; FX_toggle_comparison; pixel_scale_comparison; export_preview_checkerboard. None is a baked runtime layer. UI labels, stream widgets and fighters stay outside the environment PSD.

Every named light receiver and mask is separately paintable. For major surfaces the receiving mask may be split into top/front/side faces. Keep one common source light direction; do not independently invent lighting for each prop.

## 5. Bangor, Maine stage definition

Stage ID stays rooftop, display name Rooftop Circuit; art direction subtitle: Penobscot Rooftop, Bangor-inspired. A fictional elevated industrial roof overlooks a river and bridge. Use low historic brick blocks, mill/warehouse silhouettes, steel infrastructure, a distant Maine treeline and a restrained imagined neon skyline. It is a stylized setting, not a surveyed city panorama. Avoid claiming identifiable buildings or geographic precision without additional verified reference.

Foreground: worn roof tiles, rusted HVAC equipment, conduit, chain-link rail, sturdy lamps, faded paint and puddles. Brightest static light is the sunset or selected lamp; brightest music accent is restricted to its designated fixture and receiving surfaces. Cyan/violet graffiti connects the stage to Cabinet 1, while rust/amber/brick keep it grounded.

Time states: dawn, day, dusk, night. Dawn/dusk warms sky-facing planes; daylight reduces visible lamp dominance; night strengthens fixture/window emission without erasing dark materials. Keep identical geometry, floor anchors and sprite pivots in every state. Live clock is America/New_York; weather location is Bangor, Maine USA 04401. Manual time/weather overrides are independent. This does not require changing Windows clock.

Other stage slots reuse this contract: waterfront (riverfront view), afterhours (late-night street/arcade), downtown (brick neon alley), bridge (underpass), mill (brick mill district). They get distinct silhouette, floor and focal fixture, not merely different color filters. Current flat bases and planned slots must stay labeled accurately in the runtime registry.

## 6. Looping weather and animation contract

Renderer cadence: choose 24, 30 or 60 fps; default 30. Frame holds are integer ticks at the selected cadence. Distinguish unique painted frames from playback ticks. A four-frame study sheet is not proof of a smooth finished loop.

Use one shared stage clock and seeded effect phases. Pause/resume and source reload must have defined behavior. Start/stop weather with an opacity/intensity transition rather than respawning all particles in one visible burst. Clock/time transitions must not jump shadows instantly; choose a separate transition duration from loop length.

Production targets:

- Far/near clouds: transparent, horizontally wrapping tile layers; proposed 128-second closed drift cycle. Endpoint phase equals start phase. Use independent speeds/depth multipliers, but keep the whole package's chosen common loop duration explicit.
- Rain: 4-second phase cycle, sparse/deep/dense layers and floor splashes. 96/120/240 playback ticks at 24/30/60 fps. Wrapping particle positions and a stable random seed make the seam exact; never duplicate the final frame as an extra hold.
- Snow: 8-second cycle with depth-specific flake size/velocity, wind drift and separate receive masks; 192/240/480 ticks. Accumulation is a weather-state layer, not an endlessly increasing loop.
- Fog: 8-second tile drift with a constant density envelope or periodic envelope; no fade-to-empty seam unless deliberately approved.
- Steam: 2-second cycle, proposed 8–16 authored frames at a fixed emitter; crossfade two offset puff instances if needed for a continuous plume.
- River shimmer and puddle ripples: 4-second phase, fixed material coverage and independently moving highlights. Example 6–12 authored ripple frames; do not move the puddle outline with each frame.
- Beacons/focal fixture: 1- or 2-second idle cycle; audio modulates a separate bounded emission layer, not frame order or the entire scene exposure.

8 seconds is a convenient common weather sub-loop, while a full composite including the proposed cloud motion repeats at 128 seconds. These are production targets to validate, not current exported animations. Runtime motion may scroll/reuse small tiles at the selected cadence instead of redrawing or storing hundreds of full-HD frames. Actual speed, seed, tile extent and duration must satisfy velocity × duration = an integer wrap distance. If they do not, the loop is not seamless.

Export animation as native-resolution PNG frames or a sprite sheet with frame rectangles, pivot, durations, loop=true, phase offset and mask role in JSON. Use zero-based frame indices. At time T the phase returns to 0; export frames 0..N-1 only. Test first/last transition, opacity, edges, anchors and occlusion at all supported frame rates.

Generated candidates/weather-fx-study-v1.png is only four example poses per effect. It still requires same-size frame registration, edge cleanup, timing and loop-seam review. Do not declare it a final weather animation.

## 7. Cabinet PSD companion and paint boundaries

Cabinet master remains 2060×1220 with protected glass x403/y340/w1254/h646. The owner scales/zooms the full cabinet in OBS. Do not flatten it to fit a particular scene preview. Keep Original and Glacier Graffiti as separate presets; never overwrite source art.

Suggested editable groups, behind to front: shell_base; side_returns; marquee_underside_shadow; panel_face_masks; panel_paint; panel_wear; seam_recesses; clean_dark_gutters; structural_trim; trim_highlights; marquee_background; approved_logo; logo_emission; glass_lip; protected_glass_alpha; deck_base; deck_face_masks; deck_paint; deck_dividers; control_contact_shadows; button_mounts; button_housings; button_caps; stick_shaft_and_ball_source; direction_lights; receiver_masks; emission_masks; faint_stick_reflection.

Clip graffiti ONLY to panel-face masks inset from the edge. Preserve a clean dark gutter and crisp independent trim drawn above paint. Match light/shadow to the panel's physical depth. Old pink trim shades must not remain when a blue edge preset is chosen. Source stripes and matching printed FX must be removed together when the panel is reskinned. Never use graffiti as a fuzzy substitute for a structural outline.

Button mount groups are independent from physical buttons. Each of nine mounts has: local contact-shadow/recess, socket collar, optional deck-print ring/circuit motif, wear, emission and receiver masks. All align to the original button anchor and deck perspective. Four candidate styles: recessed precision ring, segmented circuit collar, contained graffiti halo, stepped tournament collar. Keep the center opening and the physical cap/rim boundary clean; no paint crosses the collar's outline. Ring size/spacing must not obscure neighboring controls. Draw a receiving shadow so it reads as manufactured into the deck, not pasted on top.

Original button states: 78×66 neutral, 78×60 pressed, 6 px pressed travel. Produce future cap and rim masks on the same pixel grid and shared anchor. With recoloring and FX off, their composite must reproduce the original pixels exactly. Newly painted hidden surfaces are explicitly new art. Until those masks are authored and verified, do not claim the existing ellipse-based runtime mask is exact separation. CONTROL_SPRITES.json records all source sizes and hashes.

Stick source poses and shading remain authoritative. Never smooth or flip the balltop. Stick defaults above arrows; only its faint upright top arc reflects at the bottom glass, with no button/arrow reflections. New button collars do not change this rule.

## 8. Copilot prompt — generate one layer or sprite at a time

Read ARTSTYLE.md and inspect the attached approved reference PNGs. Generate [ASSET_ID] for [STAGE_ID / CABINET_PART]. This is a [base layer / isolated prop / loop frame sheet / grayscale mask / deck collar] with [CANVAS_SIZE] and [ANCHOR/PIVOT]. Match the reference camera, pixel density, palette, authored top-left keylight and stepped pixel clusters. Keep [LOCKED_GEOMETRY] unchanged.

For an environmental layer, preserve its position on the full 1920×1080 stage canvas and leave everything outside that layer genuinely transparent. For a sprite sheet, use [ROWS×COLUMNS], [FRAME_SIZE], [FRAME_COUNT] and [TIMING], with identical cell-local pivot and alpha padding. No labels, checkerboards, frame borders, UI, people, fighters or new logos.

Keep unlit material, paint, trim, contact shadow, emission, receiver and occlusion separate. Paint never crosses seams/gutters/trim or physical button outlines. Use only the requested weather/time state and do not move landmarks. Return the image and a plain-text description of dimensions, layer role, anchor, light direction and any unmet requirements. Do not claim a loop is seamless without first/last frame inspection.

## 9. Copilot prompt — new full stage concept

Using this contract and the approved rooftop/cabinet references, propose [BANGOR-INSPIRED LOCATION] in the same detailed pixel-art style. Keep a fixed fighting-game camera, horizon Y420, rear floor edge Y736 and fighter baseline Y930 on a 1920×1080 authoring canvas unless the owner approves different guides. Preserve a readable central fight region. Give the location a distinctive silhouette and at least one music-reactive asset / focal fixture. Show a composition draft first. Then generate one registered PSD layer at a time according to the group list. Do not offer one flattened image as a completed layered stage. Keep characters, HUD and the SheldonTwitching logo out of generated scene art.

## 10. Acceptance and export checklist

Inspect native pixels, enlarged nearest-neighbor preview, alpha gutters/holes, canvas bounds, anchors, fixed horizon/floor and palette ramps. Toggle each layer independently. Check shadows match light, foreground occludes weather correctly, and audio is confined to the chosen fixture/receivers. For the cabinet, count nine controls and inspect every paint/trim/collar edge. Compare Original versus new masks with FX disabled. Export only requested layers and include provenance (model/tool, prompt, reference hashes, dimensions and approval status).

A reference pack can guide Copilot, but does not guarantee pixel-exact or free outputs. Usage availability depends on the user's Copilot account; no quota bypass is part of this workflow. Keep rejected or unreviewed outputs separate from approved runtime assets.


## 11. ST mark, full logo and required music-reactive asset

Two existing brand assets are included unchanged:

- references/brand/ST-monogram-original.png: the existing compact ST mark used by Command Center. Use it for small wall signs, fixture badges, corner branding, equipment decals and music-reactive focal objects. Its source dimensions and alpha are recorded in manifest.json; do not assume the app icon is a freshly authored vector or a detachable layered logo.
- references/brand/SheldonTwitching-full-logo-original.png: the approved stacked glacier/violet full wordmark. Use it for marquee/hero panels, stage entrance signage, title treatments, outro focal graphics, social banners and stinger compositions where it is legible.

Insert the actual files as linked/embedded Smart Objects or separate transparent layers. Never ask Copilot to reletter, spell out, stretch, squash, flatten into a ribbon, or redraw either logo. Uniform contain-fitting for front-facing panels; adjust the surrounding paint/sign dimensions, not the glyph proportions. A perspective sign must project the entire registered sign plane consistently; no independent stretching of letters. Keep safe margins and sufficient dark contrast around the mark. Do not paint across transparent logo boundaries or alter the original file.

For a scene with small incidental branding, use ST. For a prominent hero sign with sufficient space, use the full stacked logo. Avoid repeating full logos on every prop. A sign's hardware, paint, surface wear and shadows can vary by location; the brand artwork remains the same. Use cyan/violet lacquer, clipped graffiti behind the logo and a clean independent trim edge around its panel. The original assets are approved source references; newly generated logo alternatives are not approved.

Every stage package MUST include at least one identifiable music-reactive ASSET, not merely a label saying the scene is interactive. First Rooftop Circuit production target: an ST wall/equipment sign near the left-side rooftop equipment, outside the central fighting safe region. A wall lamp can be used for the initial runtime test if the sign's hardware art is still pending; declare which asset is active. Other stages may use a waterfront sign, alley fixture, underpass light or mill vent/fixture, but each must have a documented asset ID, anchor and routing.

Required PSD subgroup 85_SCENE_LIGHT_RIG / music_ST_sign:

1. music_ST_sign_mount_and_contact_shadow.
2. music_ST_sign_unlit_housing.
3. music_ST_sign_clipped_paint_and_trim.
4. music_ST_sign_logo_original (Smart Object; choose the supplied ST or full logo).
5. music_ST_sign_logo_emission_mask.
6. music_ST_sign_panel_emission_mask.
7. music_ST_sign_receiver_wall.
8. music_ST_sign_receiver_equipment.
9. music_ST_sign_receiver_floor.
10. music_ST_sign_occlusion.
11. music_ST_sign_reflection (only where the material is wet/reflective).
12. music_ST_sign_idle_and_audio_controls (metadata; never baked into the image).

The unlit sign is complete with audio at zero. A selected actual audio source drives a smoothed level/envelope into only the registered emitters and receiving surfaces. Source silence, disconnect or stale input must settle to the defined idle state. Keep an adjustable gain, floor, ceiling, attack/release, color and idle brightness. Suggested starting design values: attack 40 ms, release 240 ms, idle emission 0.08, maximum emission 0.8; these are tuning targets, not claims of existing measured runtime behavior. Optional bass emphasis only when the audio source provides real spectral data; OBS amplitude-only meters must not pretend to supply bass bins. No whole-screen flashing, no changing base artwork color every beat, and no use of Spotify track metadata as a volume meter.

Deliver music-focal-asset.json with assetId, logo source, layer IDs, anchor, source routing, emission/receiver/occlusion/reflection masks, limits and stale behavior. At least one music-reactive asset is mandatory in all six new stage briefs and their Intro/Starting Soon/BRB/Outro/background uses. It may be the same registered asset reused across those scene modes.

Copilot brand request: Create the UNBRANDED [sign housing / lamp / fixture] around the attached ST/full-logo reference in the established pixel-art style. Leave a clearly defined empty panel for the exact supplied logo to be inserted separately. Produce the unlit housing and masks separately; do not generate replacement letters or a baked bloom. Include a plausible physical mount, contact shadow, clean trim/gutter and nearby light-receiving surfaces. This asset will react to music; its base must remain readable when all emission is disabled.
