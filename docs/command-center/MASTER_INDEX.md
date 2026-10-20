# Master feature index

Authoritative private repository: https://github.com/SheldonTwitching/SheldonTwitching-Command-Center, main.
Updated 2026-10-20. This index replaces conflicting historical progress banners. The machine-readable feature registry supplies all 17 area descriptions, next actions and roadmap links to Studio.

The integrated Board has been removed at owner request. Its data and GitHub Project are retained; a separate EXE/chat is planned. See STANDALONE_BOARD_PROMPT.md.

## Order of work

1. Streaming usability: native cabinet scale, off-canvas source placement, consistent blue editors, pixel control layers and one OBS test scene. Keep the standalone Board project separate.
2. Acceptance: installed desktop and upgrades, preview pop-outs, all nine buttons, original pixel art, clean trim, correct reflection, controller and OBS scaling.
3. Live systems: real audio source / light routing, account connections, combined chat icons and supported adapters.
4. Stage production: six registered Bangor-inspired locations, layered sprites, seamless loops, weather/time variants and physically consistent light masks.
5. Creative packages: social exports, stingers, additional cabinet shapes after acceptance of the original silhouette.

## Definitions and authority

- Product / fonts / dimensions / clean source catalog: arcade/project-spec.json.
- Cabinet parts, panel bounds, trim, pivots and reflection: arcade/cabinet-structure.json.
- Stage art slots, required layers and missing assets: arcade/stage-registry.json. A usable base background is not a completed animated stage.
- Feature descriptions and initial work cards: arcade/feature-registry.json.
- Visual constraints: ART_RULES.md and PIXEL_ART_CONTRACT.md; approved original pixel art and PSD evidence take precedence over generated approximations.
- Source evidence: ART_PROVENANCE.md and docs/psd-reference/README.md.
- Separate Board app handoff: STANDALONE_BOARD_PROMPT.md. Former behavior: BOARD.md.
- Copilot and PSD production contract: ../../art/style-kit-v1/ARTSTYLE.md.
- Task and feedback prompts: PROMPT_TEMPLATES.md. Background art briefs: STAGE_PROMPTS.md.
- Current work handoff: HANDOFF.md. Historical claims: history/.

## Workflow and finish line

Inbox → Ready → In progress → Review → Owner testing → Done. Blocking is a flag with a reason; priorities P0–P3 are separate. P0: cannot launch / loss of saved work / broken live output. P1: owner-blocking defect or critical acceptance. P2: planned functional work. P3: optional polish / experiments.

Every card records expected vs observed behavior, feature/scene, build, references and evidence. Done requires acceptance criteria, evidence, implementation, verification and owner acceptance. Passing automated checks alone cannot supply that last check. New ideas migrate to Inbox; new shipped roadmap steps do not silently overwrite edited cards.

## Feature areas

- **Social Media Packages** — planned; Owner review pending. [Roadmap](roadmaps/social.md).
- **Widget Animation Library** — partial; Owner review pending. [Roadmap](roadmaps/animations.md).
- **Installers & Updates** — partial; Owner review pending. [Roadmap](roadmaps/updates.md).
- **Rotating Labels** — partial; Owner review pending. [Roadmap](roadmaps/labels.md).
- **Spotify Now Playing** — partial; Owner review pending. [Roadmap](roadmaps/spotify.md).
- **Stream Chat** — partial; Owner review pending. [Roadmap](roadmaps/chat.md).
- **Streamlabs Tip Goal** — partial; Owner review pending. [Roadmap](roadmaps/tipGoal.md).
- **Notifications & Event Lights** — partial; Owner review pending. [Roadmap](roadmaps/events.md).
- **Weather & Clock** — partial; Owner review pending. [Roadmap](roadmaps/weather.md).
- **Scene & Stage Library** — partial; Owner review pending. [Roadmap](roadmaps/scenes.md).
- **Preview & OBS Sources** — partial; Owner review pending. [Roadmap](roadmaps/preview.md).
- **Audio & Scene Lighting** — partial; Owner review pending. [Roadmap](roadmaps/audio.md).
- **Text Reader & Parsing** — partial; Owner review pending. [Roadmap](roadmaps/text.md).
- **Cabinet Structure & Marquee** — partial; Owner review pending. [Roadmap](roadmaps/cabinet.md).
- **Stingers & Transition Packages** — planned; Owner review pending. [Roadmap](roadmaps/stingers.md).
- **Source PSD & Asset Pipeline** — partial; Owner review pending. [Roadmap](roadmaps/sourceArt.md).
- **Cabinet Shape Concepts** — planned; Owner review pending. [Roadmap](roadmaps/cabinetShapes.md).

## Current verification

The embedded Board is retired. 101 Command Center tests pass, including a real bridge check that removed routes return 404 while saved board/profile bytes remain unchanged. Former Board screenshots/tests are historical extraction evidence only. Packaged/native and owner OBS acceptance remain separate.

## Copilot / PSD style kit

See [ARTSTYLE.md](../../art/style-kit-v1/ARTSTYLE.md): 14 PSD groups, 158 named stage layers plus a 12-part required music-sign subgroup, loop/export definitions, 32 individual Copilot sprite briefs and six stage briefs. The kit contains 15 unchanged control PNGs, two original brand marks and three generated candidate atlases. Generated art is not runtime-approved or claimed to be a complete layered PSD/animation.
