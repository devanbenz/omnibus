---
name: vault-conventions
description: Conventions for notes in this learning vault - folder layout, frontmatter fields, concept-note shape, linking, LaTeX and mermaid rendering, attachments. Use whenever writing or editing any note in this vault.
---

# Vault conventions

    Sessions/     one note per learning session, written live by the Stop hook
    Concepts/     atomic notes, one idea each - the durable layer
    Sources/      imported texts (papers, posts, chapters) that lessons anchor into
    Attachments/  SVGs and images, embedded with ![[...]]
    Reviews/      spaced-repetition logs
    .learning/    machine state - never edit by hand

## Rendering

This vault is read in Obsidian. That constrains syntax:

- Maths is `$inline$` and `$$display$$`. **Never** `\(...\)` or `\[...\]`.
- Diagrams are fenced ```mermaid blocks. Mermaid does not render LaTeX — use
  plain unicode inside node labels.
- Images and SVGs embed as `![[Attachments/name.svg]]`, not markdown image
  syntax.
- Callouts (`> [!note]`, `> [!question]`, `> [!warning]`) render natively and
  are worth using for quizzes, warnings, and asides. Fixed meanings:
  `> [!question] Your turn` is an open question the user answers in prose;
  `> [!example]` is a code anchor; `> [!quote]` is a text anchor;
  `> [!success]- Answer` is a collapsed model answer.
- Block links `[[Sources/Note#^id]]` and heading links `[[Sources/Note#Page 7]]`
  point into a source; hovering previews the block. `anchor.py` assigns the
  ids — do not hand-write `^id` markers.

## Concept notes

One idea per note. The filename *is* the idea, in natural language
(`Concepts/Wedge product.md`), so `[[Wedge product]]` reads as a sentence.

```markdown
---
type: concept
topic: differential forms
learned: 2026-08-20
next_review: 2026-08-23
interval: 3
ease: 2.5
tags: [concept, math/differential-forms]
---

# Wedge product

**In one sentence.** The wedge product turns two covectors into the machine
that measures oriented area on the plane they span.

## Why it has to exist
...

## The idea
...

## A concrete case
$\alpha = 3\,dx - 2\,dy$, ... (actual numbers, worked through)

## Prerequisites
[[Covector]] · [[Bilinearity]]

## Leads to
[[k-form]] · [[Exterior derivative]]

## Where it lives
(source-bound ideas only) `[[Sources/Raft#^4f2a1c]]` · `src/raft/log.py:88-104`

## Check yourself
A question whose answer requires *using* the idea, with the answer folded into
a `> [!success]- Answer` collapsible callout.
```

Rules:

- **Atomic.** If the note needs "and" in its title, split it.
- **Written for the future reader**, who has forgotten the session. Never
  "as we saw above" or "the thing from earlier".
- **Always a concrete worked instance.** A concept note with no numbers in it
  is a definition, and definitions do not survive.
- **Link generously.** `[[Prerequisite]]` links upward and `[[Leads to]]` links
  downward are what make the graph view worth looking at. A link to a note that
  does not exist yet is fine — it marks the next thing worth writing.

## Source notes

One note per imported text, written by `anchor.py import` into `Sources/`:
frontmatter `type: source`, `title`, `kind` (article, paper, chapter, docs),
`origin` (URL or path), `imported`. The body is the text itself, headings
preserved, one paragraph per block, so that `anchor.py quote` can attach a
`^id` to any paragraph. Treat the body as read-only apart from those ids.
Code is not imported — it is anchored in place by path and permalink.

## Session notes

Frontmatter: `topic`, `date`, `type: learning-session`, `phase`
(`probe` → `plan` → `teach` → `complete`/`paused`), `tags`.

The conversation body is appended automatically by
the `mdlog.py` Stop hook on every turn. Do not paste your own messages in.
Do write the structured artifacts by hand: the probe map table, the mermaid
DAG, progress ticks, and the closing `## Where we got to`.

## Spaced repetition

`next_review`, `interval` (days) and `ease` on concept notes drive `/recall`.
Nothing else maintains them — leave them alone unless running that skill.
