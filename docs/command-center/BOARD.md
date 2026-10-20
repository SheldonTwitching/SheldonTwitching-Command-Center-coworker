> **Removed from Command Center at owner request, 2026-10-20.** The navigation entry, HTTP routes, runtime imports and background synchronization worker are removed. Existing local board JSON, screenshots and public connection configuration are retained. Prototype code is parked under extras/standalone-board for a separate application. GitHub Project contents and authorization are unchanged. Use [the separate-chat prompt](STANDALONE_BOARD_PROMPT.md). The guide below documents the former implementation, not an active streaming-app feature.

# Board and GitHub synchronization

Open Studio → Board, or /studio/board. Pop out board uses the existing resizable native editor window wrapper. Local board operations need no account and continue offline.

Private GitHub board created and grouped by the six Command Center Status columns: https://github.com/users/SheldonTwitching/projects/1. Four initial planning drafts are present. Full local cards will upload after owner sign-in and explicit Sync now.

## Local workflow

Create/edit cards; drag to a column or use its Move selector. Filter by area, priority, blocked flag, archive flag or text. Record acceptance criteria, expected/observed behavior, build/scene/source and evidence. Done requires all completion checks plus criteria/evidence. Archive is recoverable; no delete operation exists. Reload after a concurrent-window conflict; the draft stays open.

The versioned feature registry seeds next-step cards once. Owner roadmap ideas migrate once by stable area/idea ID and are preserved in Studio. Editing or removing the old idea does not erase its board card. Board data saves atomically as User Data/kanban.json with a previous-save backup. Damaged files are retained and writes refused rather than silently replacing them. JSON Export/Import is an additive merge; conflicting existing card versions cause an all-or-nothing refusal. Screenshot images live under User Data/board-attachments; include that folder in a full profile backup. JSON export carries references, not screenshot bytes or authentication.

## One-time GitHub setup

The owner selected Connect with GitHub. Register an OAuth application in the owner's GitHub settings, enable Device Flow and enter only the public Client ID in the board. Homepage can be the private Command Center repository; callback is not used by the device flow. No client secret or token is entered in the app/chat. The app requests Projects scope only, not repository scope. Approve the displayed one-time code at https://github.com/login/device. Credentials are session-only; reconnect after quitting Command Center.

Link an existing PRIVATE GitHub Project URL or explicitly create a private Command Center Project. The app refuses public projects before uploading cards. A custom single-select Command Center Status field contains the six columns. In GitHub, create/select a Board view and group it by that field; GitHub view layout is not configured by this adapter. Sync now explicitly starts sharing and enables subsequent polling about every minute. Privacy is rechecked each cycle. Failures back off up to 15 minutes; Sync now retries sooner. Existing repository issues/PRs are not converted by this draft-card adapter.

## Two-way behavior

Title, status, descriptions, priority, area, type, acceptance, evidence, completion checks and recoverable archive flag synchronize through draft content plus the status field. Additional card fields use readable Markdown sections in the draft body. The archive checkbox is a shared field in the body; it does not remove the GitHub item. Native GitHub removal/archiving creates a missing-item conflict and never deletes the local copy.

Stable item/content IDs and hidden local-card markers prevent normal duplicate creation after retries. Base snapshots distinguish local-only, remote-only and conflicting edits. Conflicts preserve both versions; choose Keep local or Use GitHub. If the local card changed after the conflict was recorded, resynchronize before deciding. Screenshots stay local; upload/link a shared reference separately if desired. No remote deletions are performed.

GitHub does not expose an atomic compare-and-swap draft mutation through this adapter. Snapshot conflict checks protect changes found during polling; simultaneous edits during a network write remain an acceptance risk. Use one editor at a time for a card during the first real rehearsal. This limitation must not be described as transactional synchronization.

## Verification and remaining acceptance

Automated tests cover restart, idea migration/idempotence, stale-window rejection, import conflicts, completion rules, screenshots, offline edits, bidirectional fixture sync, missing remote items and explicit conflicts. A live authorized GitHub edit rehearsal is still required. The owner's OAuth application Client ID and approval are external setup; no connection is silently configured.

Acceptance: create one card locally, sync, edit title/status in GitHub, pull, edit locally, push, create a conflict, resolve, disconnect/reconnect, test offline/retry, restore an archived remote item and verify no duplicates. Rehearse installed native board/pop-out and upgrade persistence before release-complete.

API references: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps#device-flow and https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects.
