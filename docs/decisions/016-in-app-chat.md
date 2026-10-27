# 016 The in-app chat runs on the owner's subscription

- Date: 2026-10-26 (grilling rounds 4-8), ranked fifth after milestone 1 (round 25)
- Decided by: owner; the speech technique by Claude (round 8)
- Status: accepted, not started
- Scope: the chat box in the app

## Context
Until the chat exists, the owner teaches in the Claude Code chat in VS Code, by voice. `claude -p "<prompt>"` runs on
the owner's subscription login without an API key as long as ANTHROPIC_API_KEY is unset; it shares the plan's usage
limits, offers JSON output, and runs the working folder's hooks (Claude Code docs, read 2026-10-26).

## Decision
- A chat box for the owner only: plain-words explanations, questions, what-ifs, and telling the app that some mods are
  unobtainable for him.
- It runs on the owner's Claude subscription (`claude -p`), never an API key, from a controlled working folder.
- Speech-to-text through a microphone button using the browser's speech recognition (Chrome sends the audio to Google
  to transcribe); typed text works too. Windows voice typing (Win+H) works in any text box meanwhile.

## Consequences
- Anything other people could trigger would need an API key instead (the subscription terms assume individual use).
