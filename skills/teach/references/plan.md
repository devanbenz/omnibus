# Phase 2 — Plan

**Goal:** the shortest path from the measured edge to the goal, where every
step is reachable from the ones before it, and every fact on it is verified.

## 1. Verify the spine — in parallel, before you plan

Spawn `fact-checker` subagents (one per cluster of claims) on the factual spine
of the topic: the definitions, theorem statements, hypotheses, standard results
and numbers you are about to build on. Launch them in a single message so they
run concurrently, then plan while they work.

This is not ceremony. Trust is not built over time with an AI teacher — it is
engineered in, and it is what lets the user accept a step at face value instead
of hedging on every sentence. Do it even for topics you are confident about.

Fold the results in before presenting the plan. If a checker flags something,
fix the plan — never teach a step you know is shaky.

## 2. Reason the path out

Work backwards from the goal. For each node ask: *what must be understood
immediately before this, for this to be a single reasoning step?* Recurse until
you land on nodes the probe showed the user already holds. Those are the roots.

Then check the path forwards:

- **No node teaches something they already hold.** Cut it.
- **No edge requires a leap they cannot make.** Split it.
- **Every node is one idea.** If a node needs "and", it is two nodes.
- **Motivation comes before machinery.** The user should know why an object is
  worth defining before it is defined.

## 3. Draw the DAG

Write a mermaid graph into the session note under a `## Plan` heading, in a
fenced ```mermaid block. Obsidian renders it natively:

    graph TD
        A["Line integral as work"] --> B["Covectors: linear maps V to R"]
        B --> C["Covector fields = 1-forms"]
        C --> D["Wedge product: bilinear + antisymmetric"]
        D --> E["k-forms eat k-dimensional pieces"]
        E --> F["Exterior derivative d"]
        F --> G["Generalized Stokes"]

        style A fill:#2d6a4f,color:#fff
        style G fill:#b45309,color:#fff

Mark known roots in one colour and the goal in another. Keep node labels to a
short phrase. Avoid `$` inside mermaid labels — mermaid does not render LaTeX;
use plain unicode there. For source-bound topics a node may carry a short
location in plain text (`"Conflict truncation (log.py:96)"`); no `[[links]]`
inside mermaid.

While planning, decide per node how it will be checked — a closed quiz, an
open question, or a teach-it-back after a cluster (`questions.md`). Nodes
whose whole content is a *why* get an open question; nodes about a source
get a locate-and-explain.

**The graph is not decoration.** It exists for two reasons: it shows the user
the shape of what is coming, and — the real reason — it forces you to reason
the whole path out in advance instead of improvising one message at a time.
You may not begin teaching until the DAG exists.

## 4. Present it

Show the user the path in a few sentences: where you are starting (and why —
name the thing they already hold), the two or three landmarks along the way,
and where it ends. Invite correction of the *goal*, not the ordering — the
ordering is your job.

Set `phase: teach` in the note frontmatter.
