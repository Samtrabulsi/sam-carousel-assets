# Instagram skill data

Shared memory for the `ig-*` skills (from Jakeschincariol/instagram-agent-skill, MIT).

- `voice.md`: Sam's voice. Every skill reads it. Fill in the TODOs.
- `swipe.md`: written by `/ig-viral`; hooks to shoot from.
- `plan.md`: written by `/ig-plan`.
- `log.md`: what was posted and who was engaged; written by `/ig-reel`, `/ig-comment` and others.

Cloud sessions are wiped, so **commit these files after a skill updates them**.

Client accounts: keep a separate folder per client, `.claude/instagram/clients/<slug>/voice.md` etc.,
and tell Claude which client you're working on so it reads that folder instead.
