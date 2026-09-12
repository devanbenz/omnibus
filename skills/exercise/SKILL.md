---
name: exercise
description: Run one short (10–15 minute) open-response learning exercise on a codebase, a text, or work just done - predict, trace, debug, generate-then-compare, or teach it back - anchored to exact lines and passages and mirrored into the vault. Use when the user wants to test or deepen their understanding of specific code or a specific reference without a full /teach session, or after finishing architectural work.
argument-hint: [path | url | topic | "recent"]
---

# Exercise

A single deliberate-practice exercise. Not a lesson, not a probe of every
strand — one concrete piece of understanding, produced by the user in their
own words, checked against the real thing.

This is the omnibus port of Dr Cat Hicks's
[learning-opportunities](https://github.com/DrCatHicks/learning-opportunities)
(CC-BY-4.0): the same exercise shapes and the same pause-for-input discipline,
with two additions — every question points at an exact line or passage, and
the exchange lands in the Obsidian vault.

## 0. Bind and scope

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/newsession.py" "exercise: <subject>"
```

Tell the user the note path in one line.

Then decide the subject from the argument:

- **A path, repo area, URL or file** → source-bound. Read
  `${CLAUDE_PLUGIN_ROOT}/skills/teach/references/sources.md` and ingest first.
- **`recent`, or no argument during a coding session** → the work just done in
  this session: new files, schema changes, a refactor, an unfamiliar pattern.
  Pick the decision with the most *why* in it.
- **A topic** → find the concept notes and sessions in the vault on it; the
  exercise is on applying one of them to something new.

Say in one sentence what the exercise will cover and roughly how long it
takes. If the user did not ask for it directly, ask whether they want to
do it — one sentence, no pitch. Do not start until they say yes.

## 1. Choose the shape

Read `${CLAUDE_PLUGIN_ROOT}/skills/teach/references/questions.md`. Pick one
exercise type by what the subject is:

| Subject | First choice | Second |
|---|---|---|
| Control or data flow through code | Trace the path | Predict → observe |
| A design decision or refactor | Generate → compare | Debug this |
| A constraint, invariant, or hypothesis | Debug this | Predict → observe |
| A section of a paper or chapter | Predict from the text | Teach it back |
| A whole component or idea | Teach it back | Locate → explain |
| Returning to earlier work | Retrieval check-in | — |

One exercise, three to five pause points, done. Do not chain exercises unless
asked.

## 2. Run it

Every question follows the open-question protocol in `questions.md`: a
`> [!question] Your turn` callout, then **stop**. No hints, no examples, no
second question. Wait for the answer.

Every reveal is anchored. Code gets `anchor.py code path:start-end`; texts get
`anchor.py quote`. The reveal *is* the anchor plus one or two sentences — let
the excerpt do the work.

Feedback is direct. Right, partly right, or wrong, in those words. Credit
exactly what they produced. A wrong prediction is the most valuable moment in
the exercise: name the model that produced it, then show the excerpt that
refutes it.

Scaffold the setup, never the answer. If they are stuck, ask a more specific
question ("open this file, around line 90") rather than hinting.

Close with one transfer question: *where else does this apply?* or *what is
the general principle?* Then one line on what they can now do.

## 3. Leave something behind

- If the exercise locked in an idea that has no concept note, write one, per
  the `vault-conventions` skill, with a `## Where it lives` section holding
  the anchors and the exercise's question folded into `## Check yourself`.
- If it exercised an idea that already has a note, grade it so the schedule
  learns from it:

  ```bash
  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/due.py" --grade "Concepts/<Idea>.md" <again|hard|good|easy>
  ```

- Set `phase: complete` in the session note and add a two-line
  `## Where we got to`.

## Rules

- **Ask once, then respect the answer.** If they decline, no more offers this
  session. If they have done two exercises this session, do not offer a third.
- **Ten to fifteen minutes.** If they want to go deeper, that is `/teach`.
- **No teaching before the first question.** The pre-test is the point: an
  attempt before the explanation, even a wrong one, is what makes the
  explanation stick.
- **Everything you assert about the source has an anchor.** If you cannot
  point at it, do not claim it.
