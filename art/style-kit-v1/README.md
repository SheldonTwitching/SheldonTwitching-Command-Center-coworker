# Copilot / PSD sprite reference kit v1

Start with ARTSTYLE.md and attach only the reference images relevant to the current asset. Original controls are pixel-identical copies with hashes in CONTROL_SPRITES.json. New candidate atlases are examples, not replacements for the approved sprites.

- references/: cabinet composition, source paint, rooftop materials and 15 original control PNGs.
- candidates/: new prop, button-mount and weather/ambient style studies.
- ARTSTYLE.md: full PSD layer hierarchy, Bangor stage brief, weather looping and export rules.
- psd/rooftop-layers.json: machine-readable authoring blueprint; no actual multi-layer PSD is claimed.
- prompts/COPILOT_PROMPTS.md: individual generation requests and variations.
- manifest.json: file dimensions, hashes, alpha and provenance.

Generated images may need cleanup, exact layer separation, anchor registration and loop verification before runtime use. The current cabinet trim bleed must NOT be copied. Button mounts belong below original cap/rim sprites and inside crisp deck boundaries.

Both original brand marks are in references/brand. Each stage requires at least one music-reactive asset; see music-focal-asset.json and ARTSTYLE.md section 11.
