# Omnibus

A Claude Code plugin that teaches you things one-to-one, using Obsidian as the UI.

It measures what you actually understand, plans a path from there to your goal,
then walks it one reasoning step at a time — quizzing as it goes, and writing
the whole session into your vault with LaTeX, mermaid and diagrams rendered.

Adapted from [Eero Alvar — *How I Use AI to Learn Things*](https://youtu.be/kzcI5F4tGiU).

---

## Install

```bash
claude marketplace add https://github.com/devanbenz/omnibus
claude plugin install omnibus
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
| `/exercise [path \| url \| topic]` | One 10–15 minute open-response exercise, anchored to lines and passages |
| `/recall [topic]` | Spaced-repetition review of concepts that are due |
| `/link [title]` | Mirror any other session into a vault note |

The topic can be a thing as well as a subject: `/teach src/raft/` or
`/teach https://raft.github.io/raft.pdf` teaches *that* codebase or *that*
paper, with every claim pinned to the line or paragraph it comes from.

## The loop

**Probe** — multiple-choice questions binary-search the edge of your
understanding on every strand the topic depends on. Expect 12–25 of them, and
answer *I'm not sure* honestly — a guess corrupts the map. No teaching happens
here.

**Plan** — fact-checker subagents verify the material in parallel while the
path from your edge to the goal is reasoned out, then drawn as a mermaid graph
in your note.

**Teach** — one new idea per message, never more. A check after each step; miss
one and it backs up and re-teaches rather than pushing on. Diagrams are drawn
by a subagent that renders and *looks at* its own SVG before returning it.

## Two kinds of question

Multiple choice finds the edge fast, but picking the right option is not the
same as holding the idea. So the probe uses closed questions to bisect and
**open questions** to confirm, and the teach phase asks you to *produce* each
idea once it has been taught: predict what a change does, trace a request
through the code, debug a planted fault, sketch a design before seeing the
real one, or explain the idea back as if to a new colleague. The question is
posed and the message ends — no hints after it, no example answers. A wrong
prediction is the most useful thing you can give it.

The exercise shapes and the pause-for-input discipline are adapted from
Dr Cat Hicks's [learning-opportunities](https://github.com/DrCatHicks/learning-opportunities)
(CC-BY-4.0), which grounds them in the research on generation, pre-testing
and retrieval practice. `/exercise` runs one of them on its own — on a
codebase, a text, or whatever you just built.

## Anchored to the source

When the subject is a codebase, a paper, a post or a chapter, every claim
points at where it comes from and every question sends you somewhere to look:

- Code is quoted with a `path:line-line` caption, clickable in the terminal,
  plus a permalink to the commit, clickable in Obsidian.
- Texts are imported into `Sources/` in the vault and quoted with Obsidian
  block links — `[[Sources/Raft#^4f2a1c]]` previews the exact paragraph on
  hover. PDFs get one heading per page, so `[[Sources/Raft#Page 7]]` works too.
- Concept notes for source-bound ideas carry a *Where it lives* section, so
  the graph view connects ideas to the places they came from.

The anchoring is done by `scripts/anchor.py`; `pdftotext` (poppler) is optional
and only needed to import PDFs.

## Your vault

Created on first run, all plain markdown:

```
Sessions/      one note per session, written live as you go
Concepts/      atomic notes, one idea each — the durable layer
Sources/       imported papers, posts and chapters that lessons anchor into
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
Exercise shapes adapted from [learning-opportunities](https://github.com/DrCatHicks/learning-opportunities)
by Dr Cat Hicks, CC-BY-4.0.
