# Mandatory pixel-art contract

Owner requirement, 2026-10-19. Applies to every cabinet style and animated pixel-art scene.

- Preserve native balltop, shaft and button pixel clusters, dither, silhouettes, highlight shapes, contact shadows and alpha in every pose/state.
- Recolor existing source tones. Do not replace their spatial detail with smooth analytic sphere lighting, gradients, blurred highlights or vector ellipses.
- Use nearest-neighbor sampling. Preserve control proportions and pressed travel. Glow is a separate emission layer and must not erase the crisp base artwork.
- Directional sphere relighting requires authored pixel masks/ramps before reactivation. Keep saved light settings for that work; expose the limitation in the editor.
- Graffiti fills each registered panel face through its inner edge. Independently colored trim excludes paint and all old pink/magenta trim tones, including dark shades.
- Keep the approved stacked logo uniformly scaled; no stretched lettering. Keep the measured glass aperture unchanged.

Acceptance: compare source and recolored control crops at native size and enlarged nearest-neighbor size; test all nine poses and both button states; verify equal source-color clusters remain equal after recoloring, source alpha/shaft unchanged, full marquee-face coverage, blue trim without pink residuals, and native/projected output in the browser. Owner OBS acceptance remains separate.

Regression corrected: the materials pass replaced original ball shading with an analytic Lambert/specular sphere and flattened button contrast. That approach is prohibited. Current palette remapping keeps the authored spatial pixel pattern. Precise detached cap/rim and directional-light masks remain roadmap work.

Owner clarification (2026-10-20): the original native pixel-art size and PSD-like proportions are intentional. The owner will resize/zoom the Gameplay overlay in OBS at multiple scales. Do not rebuild or distort artwork to force one OBS transform. Keep native output available alongside optional measured output.


## Owner additions: paint containment and button mounting art (2026-10-20)

Graffiti belongs only to the registered panel face. Draw a clean dark separation gutter, physical seam and independent trim above the paint mask; preserve sharp inner/outer edges and exclude all paint from the control rim and structural outlines. Do not use a fuzzy shared painted outline as the cabinet edge.

Buttons must look deliberately mounted into the panel. Add a separate under-button mount group: contact shadow / recess, socket collar, deck-print ring or circuit motif, and optional emission mask. Keep the original physical rim and cap separate from these deck decorations. Options may include a precision recessed ring, segmented circuit collar, contained graffiti halo and stepped tournament collar. All use the same deck perspective and native button anchors. Decorations sit below controls and above panel paint; highlights and contact shadows follow the same light source. Keep the nine-button clearance and never hide controls. New concept images are references pending precise pixel masks and alignment; they are not silently applied to the live cabinet.
