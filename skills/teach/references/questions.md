# Questions

Two instruments. Use both, and choose deliberately.

| | Closed (`AskUserQuestion`) | Open (prose, then stop) |
|---|---|---|
| What it measures | *Which* model they are running | *Whether they can produce* the idea |
| Cost to the user | Seconds | Minutes |
| Best for | Bisecting a strand fast; recognising a misconception | Confirming an edge; locking a node in; anything about code or a text |
| Failure mode | Recognition passes for understanding | Slow if used for every step |

Closed questions find the edge. Open questions prove it. A probe that is all
closed questions overestimates the user, because recognising the right option
is much easier than generating it. A teach phase that is all closed questions
never makes them *produce* anything — and producing is where the encoding
happens. Aim for roughly one open question per node taught and one or two per
strand probed, at the edge.

The exercise types below are adapted from Dr Cat Hicks's
[learning-opportunities](https://github.com/DrCatHicks/learning-opportunities)
skill (CC-BY-4.0), which grounds them in the learning-science literature on
generation, pre-testing and retrieval practice.

## The open-question protocol

An open question is a message that ends with a question and **nothing after
it**. This is the single rule that matters. Everything after the question
leaks information, and information leaked is effort the user did not spend.

Write it as a callout so it renders distinctly in the note:

```markdown
> [!question] Your turn
> The request has just passed `authenticate()` in `api/middleware.py:41`.
> Trace what happens to it next, step by step, up to the point a response
> is written. Name the functions in order.
>
> *(Best guess is fine — a wrong prediction is more useful to me than a skip.)*
```

Then **end the message.** Do not add:

- example answers, or the shape an answer should take beyond what the task
  itself needs
- hints disguised as encouragement ("think about what the cache does...")
- a second question
- any teaching

Allowed after the question: one content-free line of reassurance, and an
explicit escape hatch ("or say *skip*"). Nothing else.

**When the answer comes back:**

1. Say plainly whether it is right, partly right, or wrong. Do not soften
   wrongness into "interesting" or "close". Dynamic testing only works with
   clear feedback.
2. Credit exactly what they showed. If they described *what* happens but not
   *why*, say the what was correct and that the why is still open. Never
   attribute an insight they did not express.
3. For a wrong answer, name the misconception that produces that specific
   answer, then attack it — a different concrete case, a lower sub-step —
   and re-ask in a new form. Do not advance.
4. For a right answer, one line of feedback, then move. No recap.

## Exercise types

Each is a shape for an open question. Pick by what you need to measure.

**Predict → observe → reflect.** Set up a concrete scenario. Ask what happens.
Then show what actually happens (run it, trace it, quote the text). Ask what
surprised them. *Use for:* behaviour of code, consequence of a theorem's
hypothesis, what an author will argue next.

**Generate → compare.** Before showing how something is done, ask them to
sketch how they would do it. Then show the real thing and ask what differs and
why the author or codebase went that way. *Use for:* design decisions,
definitions that could have been made another way, proof strategies.

**Trace the path.** A concrete input, and a chain of decision points. Ask at
each one: "it is here now — what happens next?" Reveal one step at a time.
*Use for:* control flow, data flow, multi-step derivations.

**Debug this.** Present a plausible bug, edge case or broken hypothesis. Ask
what goes wrong and why. Then ask how they would fix it. *Use for:* checking
whether they hold the *reason* a constraint exists.

**Teach it back.** "Explain [X] to a new engineer joining tomorrow" or "to a
student who has the prerequisites but not this." Give targeted feedback: what
they nailed, what to refine. *Use for:* locking in a node; the strongest single
check that an idea is held rather than recognised.

**Locate → explain.** Point them at a place instead of quoting it: "Open
`file`, find the function that does X. Before I say anything — what does the
line after the early return do?" Locating builds a stronger trace than
reading. *Use for:* codebases and texts. See `sources.md` for how to point.

**Retrieval check-in.** At the start of a session that continues earlier
work: "What do you remember about how [previous node] handles [case]?" Fill
gaps, then proceed. *Use for:* every resumed session.

Weave in the elaborative questions whenever a node is locked: *why this way
rather than the alternative? how would it differ if [condition] changed? where
else would this apply?* Transfer is what makes a node worth the time.

## Scaffolding

Adjust the *setup* of a question to their demonstrated familiarity, never the
*answer*:

- Early: "Open `x.py`, go to around line 120, find `reconcile()`. What does it
  do with `pending`?"
- Later: "Find where pending items are reconciled."
- Eventually: "Where would you look to change how reconciliation works?"

If they are stuck, move **up** the ladder (a more specific question), not
toward a hint at the answer.

## Rendering in the vault

The Stop hook mirrors your `> [!question] Your turn` callout, then the user's
reply as a `> [!tldr] You` callout, then your feedback. Nothing extra is
needed for the note to read as a Q&A. If an exchange locks a node in, fold the
question and a model answer into the concept note's `## Check yourself`
section, so `/recall` can reuse it.

## Choosing, in one line each

- Bisecting a strand you have not located yet → closed.
- Confirming the edge you think you found → open, short (predict or locate).
- After teaching a node → open, application-shaped (predict, debug, or trace).
- After a cluster of nodes → teach it back.
- Anything where the answer is "which line / which passage" → locate → explain.
- The user is visibly tired → closed, then stop.
