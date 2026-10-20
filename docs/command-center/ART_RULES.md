# Art rules: do and do not

Owner-mandated, applies to originals, reskins, new shells, scene art and exports. Read PIXEL_ART_CONTRACT.md before editing. Keep styling rules and physical structure as distinct specifications.

## Do

- Preserve authored pixel clusters, dither, hard alpha boundaries, source silhouettes and native proportions. Use nearest-neighbor sampling; evaluate native and enlarged crops.
- Recolor existing control tone ramps. Keep all nine controls: four upper, four lower, one right. Preserve cap/rim detail, 6-pixel pressed travel, shaft pixels, sprite pivots and all nine lever poses.
- Use the approved stacked logo uniformly scaled. The marquee's paint fills its face to the registered inner edge; surrounding composition makes the logo feel fitted.
- Register every shell face: marquee face and returns, overhang underside, shoulders, upper bridge, uprights, inner glass lip, sill, side faces, control deck/inlays, dividers, trim, seams, bevels and contact shadows.
- Give paint, base material and trim separate masks. Trim colors remain independent; blue edges exclude all residual pink shades. Add larger shoulder splashes and a complete designed screen surround.
- Replace obsolete panel print and matching decorative FX together. Keep structural seams and depth rather than painting them out.
- Define adjustable cap/rim colors, nine-button accent assignments, lever-light shape/color and layer order. Stick defaults above arrows. Label capabilities honestly where parts remain baked together.
- Keep the glass aperture protected. Native artwork is 2060×1220, glass 403/340/1254/646. Optional measured gameplay is 1920×1080, glass 197/38/1541/868. The owner chooses OBS scale/zoom.
- Reflect only a faint upright stick arc, clipped to the bottom glass (default 10 native pixels, 8% opacity). Reverse the vertical reflection pose mapping; preserve source orientation. No button/arrow reflections.
- Separate emission, receiver, occlusion and reflection masks. Overhang shade follows marquee depth; a selected light source affects nearby surfaces consistently. Audio drives light intensity, with smoothing and stale input settling to zero.
- Use 24/30/60 fps loops (default 30), fixed perspective and pixel density. Articulate sprite frame counts/timing and seam closure independently of renderer cadence.
- Use Bangor, Maine inspiration and shared stage geometry across Intro, Starting Soon, BRB, Outro and full-screen backgrounds. Provide at least one designated music focal item per scene. Auto weather/clock follow Bangor 04401 / America/New_York; independent manual overrides remain available.
- Use Consolas/monospace for operator screens; stage titles use the existing bitmap glyph renderer. Preserve widget font choices and raw CSS.

## Do not

- Never replace the balltop with a smooth procedural sphere or buttons with vector ellipses. Directional relighting remains disabled until authored pixel masks preserve source detail.
- Do not stretch/reletter the approved logo, squash controls, distort the cabinet for a particular OBS transform, or shrink the glass because edge pixels are translucent.
- Do not let graffiti bleed over trim, leave unpainted accidental gaps, or reuse decorative source stripes under replacement art.
- Do not flip a sprite to fake reflection, reflect buttons/arrows, or let red arrows cover the stick by default.
- Do not use a whole-scene flash as music lighting, or use Spotify metadata as a sound-level signal.
- Do not claim hand-drawn animation from a selected frame rate, completed masks from a flat background, or detached editable PSD pieces without evidence.
- Do not bake UI, fighters, lettering or new logos into stage artwork. Never overwrite the original PSD or supplied sprites.
- Do not generate new cabinet shapes before the current silhouette passes owner review. Every future form needs registered faces, boundaries, materials, masks, control clearance and protected aperture.

## Required review

Compare Original and Cabinet 1 at native scale, enlarged nearest-neighbor crops and owner OBS zooms. Count nine buttons; check pressed/unpressed state and nine stick poses. Inspect full marquee paint coverage, clean independent trim, shaded returns/overhang, source control detail, reflection clipping and transparent glass edge. Record screenshots and owner acceptance in the corresponding feature roadmap.


## Owner additions: paint containment and button mounting art (2026-10-20)

Graffiti belongs only to the registered panel face. Draw a clean dark separation gutter, physical seam and independent trim above the paint mask; preserve sharp inner/outer edges and exclude all paint from the control rim and structural outlines. Do not use a fuzzy shared painted outline as the cabinet edge.

Buttons must look deliberately mounted into the panel. Add a separate under-button mount group: contact shadow / recess, socket collar, deck-print ring or circuit motif, and optional emission mask. Keep the original physical rim and cap separate from these deck decorations. Options may include a precision recessed ring, segmented circuit collar, contained graffiti halo and stepped tournament collar. All use the same deck perspective and native button anchors. Decorations sit below controls and above panel paint; highlights and contact shadows follow the same light source. Keep the nine-button clearance and never hide controls. New concept images are references pending precise pixel masks and alignment; they are not silently applied to the live cabinet.
