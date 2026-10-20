# Art provenance and authoring continuity

Original CABINET/FX/balltop/button/arrow PNGs are owner-supplied assets. Do not regenerate these sprite silhouettes or infer pivots from apparent alpha bounds. Use `project-spec.json` and `sprites.js`.

Approved glacier/violet wordmark and existing room/fighter art are brought forward from this chat's arcade prototype. The wordmark retains its own outline and violet offset. The graffiti spray panel is runtime pixel geometry colored by saved palette values; it is not a replacement generated wordmark.

New bitmap briefs used during Command Center development:

- `arcade/world/assets/waterfront-v4.png`: detailed crisp pixel-art Bangor/Penobscot waterfront, bridge and industrial buildings; daylight base suitable for shared time/weather treatments; glacier-blue/violet accents, ST graffiti, no foreground fighters or UI. Generated through the built-in image generation tool, original result `exec-910ed49c-9ad7-48a3-bea5-cbbe76b23aea.png`.
- `assets/ST-Command-Center.png`: transparent ST app mark, angular glacier-blue letters with violet dimensional offset and pixel/graffiti character. Generated through the built-in tool, original result `exec-6eb93ef7-1549-4d92-8f94-e0e074b7032e.png`. The ICO is a packaging conversion with seven sizes.

These are retained authoring briefs, not a verbatim generation transcript. Future stage generations must follow the six entries in `stage-registry.json`: fixed camera, readable fight floor, no baked UI/fighters, consistent silhouettes across lighting variants, separate masks, and crisp pixels. Planned entries intentionally have no fabricated file path. Current cloud/weather loops are procedural; separate hand-drawn cloud sheets and detailed occluder masks are pending.

UI proof files are generated from the actual localhost app in an isolated test profile. They contain demo/fallback widgets, not evidence of connected Spotify/chat accounts or live OBS acceptance.

## Cabinet paint and marquee lettering · 2026-10-19

Created through the built-in image generation tool. Original owner source sprites remain unchanged. These are new style assets; they are not independently separated cabinet parts or completed stinger videos.

### Shared painted panel atlas

Output: `arcade/world/assets/cabinet1-paint-atlas-v1.png` (1672×941). Reference: `arcade/world/assets/arcade-room-v16.png`, the left cabinet's visual language. Runtime UV bands are declared in `arcade/cabinet-structure.json`; texture clipping is deterministic canvas composition.

Prompt:

> Generate one production pixel-art PAINT TEXTURE ATLAS for the cabinet on the LEFT in the supplied reference, not a picture of a cabinet. Crisp detailed arcade pixel art, chunky irregular electric cyan/glacier blue, violet and restrained magenta brush slashes, paint splatters, drips, chipped ink on very dark indigo lacquer. Cohesive hand-painted graffiti composition, not repeated tiny patterns or uniform confetti. No words, letters, logos, controls, hardware, frames, room or people. We will insert the approved SheldonTwitching wordmark separately, never draw a replacement logo. Landscape canvas divided into three equally high horizontal artwork bands with NO dividers or labels: TOP THIRD a wide marquee background with energetic broad asymmetrical splashes concentrated at left and right corners and a dark central clear space for the real logo, extending right to all edges; MIDDLE THIRD dense diagonal painted art for a sloping control deck, bold cyan/violet paint streaks and distressed dark negative space with clear depth from pixel clusters; BOTTOM THIRD coordinated side-panel artwork with larger diagonal slashes and scattered speckles. Flat front-facing texture artwork, no perspective on the texture sheet. Maintain the intricate pixel-art rendering language and cyan/violet painted-lacquer character of the reference left cabinet; no soft vector gradients, no smooth stock geometric pattern. This is an independent texture sheet, not an edit to the original room image.

### Rejected experiment · taller single-line wordmark

Generated experiment: `exec-2bdb00ad-1f9f-4581-8a2f-0d319f601016.png` in the chat generated-images folder. Not shipped or referenced by the app. Reference: approved `logo-glacier-violet.png`.

Prompt:

> Create a wide SINGLE-LINE arcade marquee wordmark variant of the supplied approved logo. Exact text: SheldonTwitching. Both words on ONE horizontal baseline, no stacking. Preserve its recognizable aggressive hand-lettered angular glacier-blue / cyan graffiti lettering, strong violet offset depth, icy white pixel highlights, very dark keyline. This is for a long low physical arcade marquee: lettering should naturally span a very wide roughly 7:1 horizontal footprint so it can fill nearly the whole sign without squashing or stretching. Give letters a tall substantial face within that wide wordmark. Transparent background everywhere outside the lettering and its tight keyline. No panel, no frame, no room, no extra icons, no skull, no slogan, no repeated decorative slashes, no paint background; separate painted artwork already exists. Detailed crisp pixel-art shading matching the source, sharp pixel clusters and restrained dither, not smooth generic vector text. The complete exact name must remain legible and uncut. Compose as one cohesive energetic hand-lettered name, not two separated logos.

### Rejected experiment · low-profile ribbon wordmark

Generated experiment: `exec-8efdecaf-19eb-40f4-9dc5-136523b448b9.png` in the chat generated-images folder. User explicitly rejected its squashed proportions. Not shipped or referenced by the app. The approved stacked master is restored; all active compositions preserve its glyph proportions. Prompt retained only for provenance and to prevent repeating the mistake.

Prompt:

> Edit this exact SheldonTwitching wordmark into an EXTREMELY WIDE, VERY LOW ribbon wordmark for a long arcade marquee, exact lettering SheldonTwitching, ONE baseline. Keep its cyan white and violet pixel art and angular graffiti identity. CRITICAL: the nontransparent INK BOUNDING BOX must have a width-to-height ratio of about 8 to 1, not 3:1 or 4:1. Letter strokes need much shorter vertical extent and more horizontal energy to form an ultra-wide low panoramic sign. Preserve complete text and do not crop any letter. Place this extremely wide low 8:1 wordmark centered horizontally on the transparent canvas with lots of transparent space above and below if necessary. No panel or backdrop, no extra marks. This is a deliberately relettered low-profile marquee variant to naturally fit the full width of a long sign without runtime stretching. Height of all lettering together must be no more than one eighth of its total width.

Rendered cabinet proofs in this folder are actual browser screenshots of the runtime's Original/Cabinet 1 compositions, not generated mockups. The native controller art, cap/rim depth, source sprite pivots and transparent game aperture are retained. Baked detail limitations remain explicit in the construction manifest and workbench.

User-approved correction: retain the approved stacked logo, keep current original-shaped Cabinet 1 styling, remove button/arrow reflections, lower the upright stick reflection to a faint bottom-edge arc, and cover both upper shoulder corners with broad paint splashes. These splashes reuse the generated atlas through registered panel masks; they are not newly fabricated cabinet sprites. The rejected stretched wordmarks are not packaged.

2026-10-19 panel correction: the existing atlas is now sampled onto opaque replacement inlay faces and four registered screen-surround planes. Vertical upright sampling turns 90 degrees with the panel. Source face stripes and corresponding interior FX are excluded together, while edge bevels/seams and control sprites are retained. No new generated lettering or raster edits were used; this is deterministic runtime surface composition. Per-lever direction tint uses the original arrow alpha mask.

Original owner PSD inspected read-only (see `docs/psd-reference`). Four PSD/PSB documents were parsed,16 runtime sprites were confirmed pixel-identical, and eight directional authoring frames were recovered. The approved current logo and painted atlas remain unchanged. New button/ball materials are deterministic runtime shading of source-alpha regions, not detached PSD layers or AI-regenerated source sprites. No original PSD was overwritten.

## Pixel-style correction, 2026-10-19

Analytic sphere shading was rejected by the owner. Controls now recolor source pixel tones without synthesizing spatial highlights. Native PSD/PNG assets are unchanged. Directional relighting awaits authored pixel masks. See PIXEL_ART_CONTRACT.md.
