# Source-anchored teaching

When the thing being learned *is* a specific artifact — a codebase, a paper,
a blog post, a book chapter, a spec — every claim you make about it should
point at the exact place it comes from, and every question you ask should be
answerable by going to a place and looking.

Two reasons. First, trust: a claim with a location can be checked in seconds;
a paraphrase cannot. Second, memory: the user who *found* the line remembers
it; the user who read your summary of it does not.

## Recognise the case

The topic is source-bound when the `/teach` or `/exercise` argument is, or
names:

- a path or repository (`src/`, `this repo`, `the auth module`)
- a URL, PDF, or file
- a specific text ("chapter 3 of Spivak", "the Raft paper", "this blog post")

Mixed cases are common — "how does this repo implement Raft" is both a
codebase and a paper. Anchor into both.

## Ingest before you probe

You cannot point at what you have not read. Before the probe:

**Code.** Read the parts of the codebase the goal depends on — entry points,
the module named, its callers and callees. Use `Grep`/`Glob`/`Read`; do not
ask the user to orient you. Note file paths and line numbers as you go; you
will need them for every question.

**Texts.** Import the source into the vault so it can be linked into:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/anchor.py" import "https://example.com/post" 
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/anchor.py" import paper.pdf --title "Ongaro & Ousterhout - Raft"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/anchor.py" import ch3.md --title "Spivak ch3" --kind chapter
```

It writes `Sources/<title>.md` with `type: source` frontmatter and prints the
path. URLs are reduced to headings and paragraphs; PDFs get one `## Page N`
heading per page; markdown is copied. If the import fails (no `pdftotext`, a
page that needs JavaScript), read the source with `WebFetch`/`Read` and write
the `Sources/` note yourself in the same shape — headings preserved, one
paragraph per block. Then read it properly.

Tell the user in one line that the source is in the vault. From here on it is
the reference of record: quote it, not your memory of it.

## Anchor forms

Use the script; do not hand-write these. It derives permalinks, de-indents,
and assigns stable block ids.

**Code** — a captioned excerpt with a permalink to the commit:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/anchor.py" code src/raft/log.py:88-104
```

```markdown
> [!example] `src/raft/log.py:88-104` · [permalink](https://github.com/o/r/blob/<sha>/src/raft/log.py#L88-L104)
> ```python
> def append_entries(self, prev_index, prev_term, entries):
>     ...
> ```
```

The caption is clickable in the Claude Code terminal; the permalink is
clickable in Obsidian and survives the file changing. If the file has
uncommitted changes the script says so on stderr — mention it if it matters.

**Text** — a block link and a quote callout:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/anchor.py" quote "Sources/Raft.md" "a leader never overwrites or deletes entries in its log"
```

```markdown
[[Sources/Raft#^4f2a1c]]
> [!quote] Raft › 5.3 Log replication
> ... the Log Matching Property ... a leader never overwrites or deletes
> entries in its log; it only appends new entries. ...
> — [[Sources/Raft#^4f2a1c]]
```

The script finds the paragraph containing the phrase, appends `^4f2a1c` to it
in the `Sources/` note if it is not already there, and prints the link.
Hovering `[[Sources/Raft#^4f2a1c]]` in Obsidian previews that exact
paragraph; clicking jumps to it. PDF pages are also addressable directly as
`[[Sources/Raft#Page 7]]`.

Quote a phrase long enough to be unique. If the script reports several
matches it used the first — give it more words.

## Asking questions that point

The question types in `questions.md` all work here; the change is that the
*setup* names a place and the *answer* is often a place.

- **Locate → explain.** "Open `src/raft/log.py` and find where entries with a
  conflicting term are handled. Before I say anything: what does it do to the
  entries *after* the conflict?" Then, once they answer, anchor the real lines
  with `anchor.py code` so the note holds the evidence.
- **Predict from the text.** Quote the setup paragraph of a proof or argument
  with `anchor.py quote`, then ask what the next step must be. Reveal by
  quoting the next paragraph.
- **Trace with locations.** "The request enters at `api/routes.py:31`. Which
  function does it reach next?" Every reveal is an anchored excerpt.
- **Debug at a location.** Anchor a real block. "If line 94's `>=` were `>`,
  what would break, and which test would catch it?"
- **Reconcile paper and code.** Anchor the paper's statement and the code's
  implementation side by side; ask where they differ and whether the
  difference is a bug, an optimisation, or a simplification.

Prefer sending them to a location over quoting it, when the file is not huge
and they have the tools open. Quote directly when the excerpt is a few lines,
the syntax is new to them, or they are stuck. Either way, the note ends up
holding the anchor — quote it after they have looked.

## In the vault

- Every anchored claim in a teaching message carries its anchor. A message
  that says "the leader appends and never overwrites" without a
  `[[Sources/...#^id]]` or a `path:line` caption is a paraphrase, not a
  teaching step.
- Concept notes for source-bound ideas get a `## Where it lives` section
  listing the anchors — the paper paragraphs and the code locations. Those
  links are what make the graph view connect concepts to sources.
- The probe table's *Edge* and *First gap* columns can name locations:
  `holds: log.py append path · gap: the conflict-truncation branch (log.py:96)`.
- DAG node labels may carry a short location in plain text
  (`"Conflict truncation (log.py:96)"`). No `[[links]]` inside mermaid — it
  does not render them.

## Scope discipline

Read what the goal depends on, not the whole artifact. A probe on "how does
this repo do auth" does not need the build system. A chapter is taught
section by section; import it whole but anchor only what the current node
uses. The user's effort goes into the material; yours goes into knowing
exactly where everything is so they never have to search.
