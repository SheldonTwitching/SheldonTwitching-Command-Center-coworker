# Stream Chat - testing and notes

Updated 2026-10-20. App baseline: **2.0.28**. Status: owner testing/notes pending.

## Current scope

Editable combined/per-platform chat URLs and Twitch/Daigotron ingress implemented. YouTube, TikTok and Twitter/X account adapters are not implemented.

## Test and review

- [ ] Confirm the target design: one chronological feed combining all connected YouTube, Twitch, TikTok and Twitter/X accounts, with a recognizable platform icon per message.
- [ ] Test the current local/test-message widget and supported Twitch ingress; distinguish sample messages from a connected account.
- [ ] Record long messages, emotes, source icons, repeated messages, commands, account reconnect and scroll behavior for future adapter acceptance.
- [ ] YouTube, TikTok and Twitter/X account adapters and platform-icon rendering remain planned; textual platform labels are not icon acceptance. Use the owner widget reference.

## Planned next work

- Combine messages from all connected YouTube, Twitch, TikTok and Twitter/X accounts into one simple chronological feed
- Show a recognizable platform icon on every message so its source is clear
- Use owner-supplied OBS widget version as the design/behavior reference
- Verify Twitch ingress and implement supported account adapters for the other platforms
- Preserve editable styling, CSS and readable pixel-art animations

## Owner notes

- Tested build/date:
- Scene/widget/source and OBS size/zoom:
- Preset/layer order (if relevant):
- Expected behavior:
- Observed behavior:
- Screenshot or recording reference:
- Requested changes/ideas:
- Priority and acceptance status:

The integrated Board is removed; use **Widget Roadmaps -> Add & pin idea** and this review sheet for now. Existing Board files remain local for a separate app. See [master index](../MASTER_INDEX.md) and [separate app brief](../STANDALONE_BOARD_PROMPT.md). Those notes stay in the local Studio profile; **Export Studio** includes them. This GitHub template can also be edited for repository review. Keep tokens, private widget URLs and account credentials out of notes.

[All roadmap test sheets](README.md) | [Main roadmap](../../../COMMAND_CENTER_ROADMAP.md) | [Current test build](https://github.com/SheldonTwitching/SheldonTwitching-Labels/actions/runs/39399815387)
