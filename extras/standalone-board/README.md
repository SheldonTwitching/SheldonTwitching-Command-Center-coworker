# Standalone Board extraction reference

Owner decision 2026-10-20: remove the Board from Command Center and develop a separate Windows EXE in a different chat. This folder preserves the prior implementation for extraction; it is not served or imported by Command Center, and arcade/ is outside the packaged runtime assets.

Contains local persistence, GitHub device sign-in / Projects draft sync, UI assets and prior tests. These are reusable components, not an already completed independent app. The browser integration test describes the former embedding and requires adaptation. Unit checks: python -m pytest extras/standalone-board/tests/test_kanban.py -q.

Do not copy account credentials or silently reuse the streaming app profile. Preserve existing User Data/kanban.json, kanban.json.bak, board-attachments/ and github-project.json. Future migration must copy/verify them with owner choice, retain originals and avoid different-profile overwrites. Session credentials cannot be migrated.

Read docs/command-center/STANDALONE_BOARD_PROMPT.md for the separate-chat brief. Do not re-add this feature to Command Center unless requested.
