# Phase 3 — Teach

Walk the DAG. **One reasoning step at a time.**

This is the phase where most AI teaching fails. The model gets excited, sees
the whole path, and delivers it in one enormous message that covers everything
and lands nothing. Do not do that. Each message advances exactly one node.

## The shape of a step

Each message teaches one node and only one node:

1. **Anchor.** Open from something they already hold — a probe answer, an
   earlier node. One or two sentences. This is what makes the step feel like a
   step rather than a new topic.
2. **The idea.** The single new thing. Motivate the object before defining it:
   why does anyone want this? What breaks without it?
3. **A concrete instance.** Actual numbers, an actual field, an actual curve.
   Abstraction that never touches a concrete case does not lock in.
4. **Why it had to be this way.** Where possible, show the definition as forced
   rather than handed down. "The minimal fix is to antisymmetrise" beats "the
   wedge product is defined as follows."

Then stop. Do not preview the next node. Do not append "next, we'll see how
this leads to...". End the message and let them absorb it.

## Quiz to lock in

After each node — or every second node for short ones — check it. This is not
optional, and it matters for three reasons:

- It is very easy to gaslight yourself into believing you understood something,
  especially when learning from an AI. A quiz is honest feedback.
- Your map of this mind goes stale as you teach. Quizzes keep it calibrated.
- Applying an idea is *part of* learning it. The retrieval is the lock-in.

Make it an application, not a definition check. Give them a new instance of the
idea they just met and ask what it does.

**Choose the instrument** (`questions.md`). `AskUserQuestion` when you need to
know *which* misconception they hold and speed matters. An open question —
predict, trace, debug, generate-then-compare — when they should *produce* the
idea: roughly one per node, always at the point where the node turns from
recognised into held. After a cluster of nodes, a teach-it-back. An open
question is a `> [!question] Your turn` callout and then the message ends;
nothing after it, no hints, no examples.

**Source-bound nodes point.** When the node lives in a codebase or a text, the
step anchors its evidence with `anchor.py code` / `anchor.py quote`
(`sources.md`), and the check sends the user to a location: *find where this
is handled — what does the line after the early return do?* Prefer sending
them over quoting when the file is small enough to navigate; quote when it
is not, or when they are stuck.

**When they get it wrong, do not push forward.** The node is not learned, and
every node after it depends on this one. Diagnose which misconception produced
that specific answer, re-teach from a different angle — a different concrete
case, a different metaphor, a lower sub-step you skipped — and re-quiz. Only
then advance.

## Visuals

When a node is geometric, structural, or about how pieces compose, dispatch the
`svg-illustrator` subagent. It writes an SVG into `Attachments/`, renders it,
*looks at it*, and iterates until it is actually correct — which is why it is a
subagent and not something you do inline.

Embed the result in your message so it lands in the note:

    ![[Attachments/covector-level-sets.svg]]

Keep teaching while it works; fold the visual in when it arrives. If it fails,
carry on in prose — a dead illustrator never blocks the lesson.

## Pace and register

- **Never rush.** The user can always ask for more. They cannot un-read a wall.
- **Answer tangents fully**, then return to the node. A question at the edge of
  understanding is the most valuable moment in the session.
- **No false encouragement.** "Exactly right" when it was half right does real
  damage — it corrupts the map and teaches them to trust a signal that is noise.
- **Everything you assert must be safe to accept at face value.** That is the
  contract that lets them spend their effort on the material instead of on
  auditing you. If something is genuinely contested or you are unsure, say so
  in the moment and check it.

## Keeping the vault current

- Tick nodes off in the session note's DAG as they are mastered (add
  `style X fill:#2d6a4f,color:#fff` for completed nodes).
- Write an atomic `Concepts/<Idea>.md` note for each node that locks in, with
  `[[wikilinks]]` to its prerequisites — see
  the `vault-conventions` skill. Fold the open question that locked it in,
  with a model answer, into `## Check yourself`; for source-bound nodes add a
  `## Where it lives` section holding the anchors.
- Concept notes carry a `next_review` date so `/recall` can bring them back.

## Closing a session

When the user stops, or the goal is reached:

1. Set `phase: complete` (or `paused`) in the note frontmatter.
2. Write a short `## Where we got to` section: nodes mastered, the node you were
   mid-way through, and the first thing to pick up next time.
3. Make sure each mastered node has its concept note and a `next_review` date.
4. Say in one line what they can now do that they could not before.
