---
name: recall
description: Run a spaced-repetition review over concept notes that are due, quizzing on application rather than recall and rescheduling each note by how it went. Use when the user wants to review, revise, or test what they have learned.
argument-hint: [topic filter]
---

# Recall

Learning that is not retrieved decays. This closes the loop: the ideas locked
in during a teaching session come back on a schedule, and the schedule adapts
to how well they hold.

## 1. Find what is due

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/due.py"          # everything due
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/due.py" "linear algebra"
```

If nothing is due, say so and offer the soonest upcoming date. Do not invent a
review session out of notes that are not due — that is the schedule's job, and
overriding it wastes the user's effort.

Cap a session at about 15 notes. More than that and quality collapses.

## 2. Quiz

Read each due note, then quiz. Two instruments, per
`${CLAUDE_PLUGIN_ROOT}/skills/teach/references/questions.md`:

- `AskUserQuestion`, batched up to 4 at a time, for the bulk of the session.
- An open question — a `> [!question] Your turn` callout, then the message
  *ends* — for at least a third of the notes, and for every note that has
  failed before. Predict, debug, or teach it back. Recognition is not recall;
  a note the user can only pick out of a list is not held.

**Ask for application, never definition.** The note contains the definition; if
they can only recite it, they have learned the note rather than the idea. Give
a *new* instance — different numbers, different setting than the worked case in
the note — and ask what the idea does to it. Include an "I'm not sure" option
on closed questions and an explicit *skip* on open ones. A note with a
`## Check yourself` question is a starting point, not the question — vary it.

For notes with a `## Where it lives` section, the review can be a
locate-and-explain: send them to the file or passage and ask what it does
before anchoring the answer (`sources.md`).

Grade each answer as one of:

- **again** — wrong, or right for the wrong reason
- **hard** — right, but visibly reconstructed with effort or after a hint
- **good** — right, direct
- **easy** — right, immediate, and they extended it unprompted

When something is wrong, teach it again *right there*, briefly and from a
different angle than the note takes. Then re-quiz it later in the session.

## 3. Reschedule

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/due.py" --grade "Concepts/Wedge product.md" good
```

SM-2-style: `again` resets the interval to 1 day and drops ease; `hard` grows
it slightly; `good` multiplies by ease; `easy` multiplies harder and raises
ease. The script writes `next_review`, `interval` and `ease` back into the
note's frontmatter and appends a line to `Reviews/`.

## 4. Close

Report plainly: how many held, which ones did not, and what the misconception
was in each failure. If a note failed twice, say so and suggest a short
`/teach` session on it — a note that keeps failing usually means a gap in a
prerequisite, not a weak memory.
