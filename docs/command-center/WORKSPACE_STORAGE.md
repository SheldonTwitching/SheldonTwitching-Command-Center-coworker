# Local Command Center workspace

Owner-selected root: `C:/Twitch/SheldonTwitching 4.0/Codex Projects/Command Center`.

- `Project/`: working Git checkout, source artwork, docs, tests, generated proofs, local builds and downloaded installers. Existing build history and authoring files are retained.
- `References/`: copies of source PSD/PNG artwork, synced project references, earlier design/overlay work, conversation handoff/screenshots and available original generation outputs. These are local references, not runtime replacements or approved new artwork.
- `User Data/`: local settings, saved Studio project/roadmap ideas, controller bindings and other app-owned profile files. Keep this private and outside the Git checkout.
- `Local Inventory/`: copy manifest and verification results, including unavailable reference paths. Originals remain at their old locations.

The installed EXE remains under the normal per-user Programs directory. New app versions resolve saved data through `%APPDATA%/SheldonTwitchingLabels/storage-location.json`. `ST_LABELS_HOME` still overrides this for isolated tests. The pointer is machine-local, never committed. Original profile files are retained; an older running app continues to use its startup location until exited/restarted. Reinstall the new build and restart to use the relocated profile.

Do not commit private profile contents, tokens, old runtime directories or the full local reference archive. GitHub contains source/runtime artwork, roadmaps, tests and public-safe documentation. Imported external Streamlabels directories are not moved or silently rewritten.
