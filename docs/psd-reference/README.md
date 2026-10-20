# Original overlay PSD findings

Source: `ArcadeCabinet_FINAL - Beta.psd`, inspected read-only on 2026-10-19. The SHA-256 in `inventory.json` was checked before and after inspection; the original file is unchanged. This is a structural reference, not a rollback of the approved Glacier Graffiti branding.

## What is actually in the file

- Main canvas: **2060 × 1220, RGB, 8 bits/channel**. Five root groups: BG, CABINET, ARROWS, BALL, BUTTON.
- Three embedded PSBs were inspected recursively: **2445×1067**, **2445×948**, **2445×920**. In total, four documents contain **47 layer records**, including groups. The nested artwork contains raster logo components, masks and Color Overlay effects. There are no editable text layers in the inspected tree; no font name should be invented from it.
- **16 supplied PNGs match their PSD layers byte-for-byte as decoded RGBA pixels**: FX, four arrows, nine joystick poses, neutral button and pressed button. This confirms the current native sprite artwork, including transparency, rather than requiring guessed redraws.
- Every joystick pose's PSD bounds agrees with its current source dimensions and the shared **891,1115** shaft pivot. BALL contains whole rendered poses; it does not contain detached sphere, shaft or lighting layers.
- Neutral button: **78×66 at 1113,1093**. Pressed: **78×60 at 1113,1099**. The bottom stays at1159, confirming **6px physical travel**, not a vertically stretched pressed image. Cap and rim are still baked together within each sprite. The other eight button images are combined in BUTTON_AREA; this is not nine independently layered cap/rim assemblies.
- Direction lights are individual layers. UP/LEFT/RIGHT are **44×42**; DOWN is **44×46**. Runtime must preserve the taller original DOWN silhouette. New procedural shapes may have their own declared dimensions.
- LOGO has separate LIGHT and LIGHT_2 pixel layers using **Hard Light**, opacity179/255 (~70.2%, visible) and51/255 (20%, hidden). The old logo also contains nested masked/color-overlay construction. Use this separation as an emission/receiver reference; the old orange/red pixels are not spatially interchangeable with the approved blue logo.
- Document global-light defaults are **90° angle /30° altitude**. Those settings do not establish the baked sphere's light vector: the ball layers have no corresponding live lighting effect or normal map.

## Recovered animation

The Photoshop animation descriptor contains eight frame IDs. Replaying its visibility deltas gives:

1. FRONT + DOWN light
2. FRONT_LEFT + DOWN/LEFT lights
3. LEFT + LEFT light
4. BACK_LEFT + UP/LEFT lights
5. BACK + UP light
6. BACK_RIGHT + UP/RIGHT lights
7. RIGHT + RIGHT light
8. FRONT_RIGHT + DOWN/RIGHT lights

The selected frame is index6 (the seventh frame), and replayed visibility agrees with the saved document state. Neutral exists as a separate pose but is not one of these eight directional demo frames. No per-frame delay appears in the recovered FrIn descriptors; **FrGA=90 is a global light angle, not90fps or a frame delay**. Exact original GIF timing needs Photoshop/GIF verification before it is claimed.

## Version differences to preserve explicitly

The Beta CABINET layer is **1942×1224**, positioned at **60,0**. The supplied PNG is its identical top1220 rows, and the app's approved placement is **59,0**. FX is pixel-identical, but its PSD origin is16,0 versus the current15,0. Preserve these version differences in the manifest; do not silently shift approved geometry.

Beta arrow positions are UP870,1056; DOWN870,1132; LEFT814,1090; RIGHT926,1090. The app uses calibrated positions with small offsets. Compare them visually before migrating positions. SCREEN content plates have different bounds from one another; **neither is authority to resize the owner-measured game hole**.

## Consequences for the roadmap

1. Keep source sprite alpha, original dimensions and pivot coordinates; replace estimated metadata with PSD evidence where it agrees.
2. Respect the6px pressed travel and44×46 down arrow. Reconcile Beta origin/arrow-placement deltas separately from the measured aperture.
3. Add explicit cap/rim material masks and a sphere-lighting model because these are not detached in this PSD. Do not claim the PSD already separates them.
4. Keep trim/receiver/paint/shadow masks distinct. Body trim, panel print and screen bevel shading are flattened into CABINET and still need registered masks or newly authored source layers.
5. Drive the approved logo's own emission mask from actual selected audio; use the PSD's separate glow construction as a reference, not as replacement branding.
6. Reuse current painted panels and approved logo for banners/stingers. Design alternate cabinet silhouettes only after acceptance of this current shape.

`original-merged-preview.png` is the Photoshop-saved composite. `original-logo-smart-object-preview.png` and `logo-light-raw.png` are extracted reference views, not regenerated art. Raw LIGHT extraction does not apply its layer opacity or Hard Light blend; those values remain in the inventory.

## Repeat the inspection

Use the optional `requirements-psd-inspection.txt` dependency and run `tools/inspect_cabinet_psd.py SOURCE --out OUTPUT`. The tool reads embedded PSD/PSB documents without executing smart-object contents and never writes the source. The desktop app does not depend on psd-tools.
