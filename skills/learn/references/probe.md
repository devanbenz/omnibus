# Phase 1 — Probe

**Goal:** a detailed map of where this mind's understanding ends, on every
strand the lesson will depend on. Not a vibe. A map.

**Your bisection tool is `AskUserQuestion`.** It renders a real picker — up
to 4 questions per call, 2–4 options each, plus a free-text "Other". Never
write "A) B) C) D)" as prose in a message; that is not a quiz, it is a wall of
text.

**Your confirmation tool is the open question** (`questions.md`): once you
think you have found a strand's edge, ask one short open question there —
predict, locate, or explain — and end the message. Recognising the right
option is much easier than producing it, so an all-closed probe overestimates
the user. One or two open questions per strand, at the edge, is enough; do not
open-question your way down a whole ladder.

## Method: binary-search the edge, strand by strand

1. **Enumerate the strands.** Before asking anything, privately list every
   prerequisite thread the goal rests on. For "differential forms" that is
   vector calculus, linear algebra/duality, integration, manifolds, and the
   physics motivation. Each is a strand.
2. **Open broad on each strand.** One question that sits in the middle of that
   strand's difficulty range.
3. **Bisect.** Correct → jump harder on that strand. Wrong or unsure → drop
   easier. Repeat until you have bracketed the edge: the hardest thing they
   hold and the first thing they don't.
4. **Probe the strands in parallel**, batching up to 4 questions per call so
   the user answers in one pass. Interleave strands; do not march down one
   thread for fifteen questions.
5. **Stop** when every strand is bracketed. That usually takes 12–25 questions.
   Stopping early means teaching blind; asking past the edge is wasted effort.

## Rules

- **Do not teach during the probe.** After each answer you may reveal the
  correct option in one line — never a paragraph, never a tangent. The teaching
  happens in phase 3, with a plan behind it.
- **Always offer an honest exit.** Include an explicit "I'm not sure" option on
  every question. A guess corrupts the map far worse than an admitted gap.
  Tell the user this once, up front.
- **Probe understanding, not recall.** Bad: "What is the definition of a
  1-form?" Good: give a concrete field and a curve, ask what the line integral
  computes. You are looking for whether they can *use* the idea.
- **Make wrong options genuinely tempting.** Every distractor should be the
  answer a specific plausible misconception produces. That is what turns a
  question into a measurement — the wrong answer tells you which model they are
  running.
- **Chase surprises.** An unexpected correct answer means a strand runs deeper
  than you assumed; an unexpected miss means a hidden gap upstream. Re-bisect
  rather than continuing your original ladder.
- **Take free text seriously.** If the user types their reasoning into "Other",
  that is higher-resolution data than any option click. Read it closely.
- **Source-bound topics probe by location.** For a codebase or a text, the
  sharpest probe is "where": *which function would you change to make X
  happen?* or *which paragraph of the paper does this line implement?* Ask it
  as an open question, then anchor the real answer with `anchor.py` so the
  note holds it (`sources.md`).

## Closing the phase

Write the map into the session note under `## Probe`, as a table:

```markdown
| Strand | Holds solidly | Edge | First gap |
|---|---|---|---|
| Vector calculus | line/surface integrals, Stokes in $\mathbb{R}^3$ | flux as a $2$-form | orientation |
```

Then set `phase: plan` in the note frontmatter and move on. Tell the user in
one sentence what you found — they earned it, and it calibrates them too.
