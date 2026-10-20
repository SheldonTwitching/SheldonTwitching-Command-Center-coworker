# SheldonTwitching - Command Center

Private, local-first Windows command center for OBS scenes, pixel-art arcade overlays, widgets and stream asset packages.

- [Master feature index and work order](docs/command-center/MASTER_INDEX.md)
- [Separate Board app handoff](docs/command-center/STANDALONE_BOARD_PROMPT.md)
- [Art do / do not rules](docs/command-center/ART_RULES.md)
- [Copilot sprite kit and PSD layer contract](art/style-kit-v1/ARTSTYLE.md)
- [All feature roadmaps and owner review sheets](docs/command-center/roadmaps/README.md)
- [Application guide](COMMAND_CENTER_README.md)
- [Reusable task brief and handoff](docs/command-center/HANDOFF.md)

## Use the app

Download the Windows installer from this private repository's Actions artifacts. Open **SheldonTwitching - Command Center.exe**. The desktop opens Studio. Preview windows can pop out. The integrated Kanban and its GitHub sync have been removed at owner request; its saved local data is preserved for a separate application. Use Setup & Sources for the actual OBS URLs and dimensions. Keep the local bridge running during broadcast.

Existing installed baseline: 2.0.28. New repository builds use 2.1.x. A successful CI build does not establish owner visual/OBS acceptance. Read the testing handoff before selecting an installer.

## Local project

Working checkout: C:/Twitch/SheldonTwitching 4.0/Codex Projects/Command Center/Project.
References, User Data, Installers and Local Inventory stay in sibling folders. Private account settings and local board screenshots stay outside Git. The original PSD remains immutable.

Developer launch: `python app.py`. Build: `Build-Windows-EXE.bat`. Tests: `python -m pytest tests -q`, `node tests/test_renderer.js`, plus JavaScript syntax checks listed in AGENTS.md. Existing custom CSS and the external Streamlabs Tip Goal remain authoritative.

Historical README and handoff material is preserved under docs/command-center/history; current instructions above supersede stale branch/version/status claims there.
