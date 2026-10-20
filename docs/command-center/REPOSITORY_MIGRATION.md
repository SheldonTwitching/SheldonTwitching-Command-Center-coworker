# New private Command Center repository

Owner request: 2026-10-20.

- Repository: https://github.com/SheldonTwitching/SheldonTwitching-Command-Center
- Product: SheldonTwitching - Command Center
- Primary branch: main
- Source baseline: 179c93c, with its existing commit ancestry preserved.
- Previous repository: SheldonTwitching/SheldonTwitching-Labels, retained unchanged.

The complete tracked project migrates: Python bridge and Windows wrapper, web editors, source art and approved runtime assets, cabinet/stage specifications, tests, installer workflow, all 17 feature roadmaps, and design/PSD evidence. This is a new repository, not a rename or a merge into the old repository's main branch. Existing GitHub issues, Actions artifacts and settings belong to the old repository and are not Git files; historical artifact links remain there.

Live installer links now target the new repository. The new workflow uses 2.1.<run number>, preventing the fresh counter from producing a version below the installed 2.0.28 baseline. Stable installer identity and User Data routing are preserved. New builds still require CI and packaged/native acceptance.

## Local files

Continue in C:/Twitch/SheldonTwitching 4.0/Codex Projects/Command Center/Project.

References, Installers, User Data and Local Inventory remain organized beside Project. Private profiles, account credentials, cached builds and the original reference archive are not blindly added to Git. Source-art provenance and PSD inspection evidence are tracked; original reference files remain available locally. User Data is still routed to the owner's chosen directory. Old local copies are retained.

## Next task

Resume the approved organization plan: a single feature/specification index, strengthened art do/do-not rules, a persistent in-app Kanban, preservation/migration of pinned ideas, and two-way GitHub Projects synchronization with explicit conflict handling. That board is not yet implemented. Update roadmaps and the master handoff as implementation proceeds. No new cabinet art was created during repository migration.
