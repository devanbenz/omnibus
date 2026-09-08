---
name: link
description: Bind the current Claude Code session to an Obsidian note so the conversation is mirrored into it live. Use when the user wants to log, mirror, or capture an ad-hoc session into the vault outside a /teach flow.
argument-hint: [note title]
disable-model-invocation: true
---

# Link this session to a note

Mirrors everything from here on into an Obsidian note — LaTeX, mermaid and
embedded SVGs all render there, and the session leaves an artifact behind.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/newsession.py" "<title>"
```

If no title was given, pick one from what the session is actually about — a
short natural-language phrase, not a slug.

The next time you finish a turn, the Stop hook claims the link and back-fills
the conversation so far. Tell the user the note path in one line, then carry on
with whatever they were doing.

To mirror into a note that already exists instead, write its vault-relative
path to `.learning/state/pending-link` and let the hook claim that.
