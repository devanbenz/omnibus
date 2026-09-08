# Omnibus

A Claude Code plugin that teaches you things one-to-one, using Obsidian as the UI.

It measures what you actually understand, plans a path from there to your goal,
then walks it one reasoning step at a time — quizzing as it goes, and writing
the whole session into your vault with LaTeX, mermaid and diagrams rendered.

Adapted from [Eero Alvar — *How I Use AI to Learn Things*](https://youtu.be/kzcI5F4tGiU).

---

## Install

```bash
claude marketplace add https://github.com/devandbenz/omnibus
claude plugin install omnibus@omnibus
```

Optional, so diagrams can be visually self-checked before you see them:

```bash
sudo apt install librsvg2-bin      # or: brew install librsvg
```

## Use

Any folder can be a vault. Open one in Claude Code and Obsidian side by side:

```bash
mkdir ~/vault && cd ~/vault && claude
```

```
/teach differential forms
```

Approve the hook when prompted. The folder structure is created on first run,
and a session note appears in `Sessions/` — keep it open in Obsidian and watch
it fill in as you go.

| Command | What it does |
|---|---|
| `/teach <topic>` | The full loop: probe → plan → teach |
| `/recall [topic]` | Spaced-repetition review of concepts that are due |
| `/link [title]` | Mirror any other session into a vault note |

## The loop

**Probe** — multiple-choice questions binary-search the edge of your
understanding on every strand the topic depends on. Expect 12–25 of them, and
answer *I'm not sure* honestly — a guess corrupts the map. No teaching happens
here.

**Plan** — fact-checker subagents verify the material in parallel while the
path from your edge to the goal is reasoned out, then drawn as a mermaid graph
in your note.

**Teach** — one new idea per message, never more. A quiz after each step; miss
one and it backs up and re-teaches rather than pushing on. Diagrams are drawn
by a subagent that renders and *looks at* its own SVG before returning it.

## Your vault

Created on first run, all plain markdown:

```
Sessions/      one note per session, written live as you go
Concepts/      atomic notes, one idea each — the durable layer
Attachments/   diagrams
Reviews/       review logs
.learning/philosophy.md    ← yours
```

**`.learning/philosophy.md` is the file that matters.** Probing and planning
are mechanical; teaching should be personal. It's seeded with a starting
philosophy — one step at a time, derive rather than decree, concrete before
abstract — and overrides the plugin's defaults wherever they disagree. It lives
in your vault, so updates never overwrite it. Rewrite it as you learn how you
learn.

## Why one teacher

Learning is normally many-to-many: every resource is built for many learners,
and every learner juggles many resources. A resource built for everyone is
optimal for no one — optimal teaching depends entirely on *your* current
understanding. And juggling sources costs more than context-switching: with an
unfamiliar source your brain hedges, refusing to commit to a fact until the
source has proven itself.

One teacher doesn't reduce the number of sources — it aggregates them behind a
single interface that has actually measured you. Trust isn't built over time
with an AI teacher; it's engineered in, which is what the fact-checking is for.

So: maximise struggle in the material, and eliminate it everywhere else.
Difficulty in the ideas is the point. Difficulty in logistics is waste.

## Local development

```bash
git clone https://github.com/devandbenz/omnibus
claude marketplace add ./omnibus
claude plugin install omnibus@omnibus
claude plugin validate ./omnibus
```

MIT. Method credit: [Eero Alvar](https://www.youtube.com/@EeroAlvar).
