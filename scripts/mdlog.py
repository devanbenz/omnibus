#!/usr/bin/env python3
"""Stop hook: mirror the live session into a linked Obsidian note.

This is the Claude Code equivalent of the `md-log` extension in the source
system. Obsidian becomes the UI: LaTeX renders, mermaid renders, SVGs embed,
and every learning session leaves a persistent artifact behind.

Binding a note to a session:
  A skill writes the note path into  .learning/state/pending-link
  The next Stop hook claims it, binds it to this session_id, and back-fills
  the conversation so far. From then on each turn is appended incrementally.

State lives in  .learning/state/<session_id>.json  as {"note", "cursor"}.
"""
import json
import os
import re
import sys
import time
from pathlib import Path

PENDING_MAX_AGE = 900  # a pending-link older than 15 min is stale


def vault_root(payload):
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or ".")


# --------------------------------------------------------------------------
# transcript reading
# --------------------------------------------------------------------------

def read_transcript(path):
    entries = []
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except OSError:
        return []
    return entries


def is_human_turn(o):
    """A prompt the human actually typed - not a tool_result carrier."""
    if o.get("type") != "user" or o.get("isSidechain"):
        return False
    if (o.get("origin") or {}).get("kind") != "human":
        return False
    content = (o.get("message") or {}).get("content")
    if isinstance(content, str):
        return bool(content.strip())
    if isinstance(content, list):
        return any(b.get("type") == "text" and b.get("text", "").strip() for b in content)
    return False


def human_text(o):
    content = (o.get("message") or {}).get("content")
    if isinstance(content, str):
        return content.strip()
    return "\n\n".join(
        b.get("text", "").strip()
        for b in content
        if b.get("type") == "text" and b.get("text", "").strip()
    )


def blocks_of(o):
    content = (o.get("message") or {}).get("content")
    return content if isinstance(content, list) else []


# --------------------------------------------------------------------------
# LaTeX normalisation - Obsidian speaks $ and $$, not \( and \[
# --------------------------------------------------------------------------

FENCE = re.compile(r"^(\s*)(```|~~~)")


def normalise_latex(text):
    out, in_fence, fence_tok = [], False, None
    for line in text.split("\n"):
        m = FENCE.match(line)
        if m:
            tok = m.group(2)
            if not in_fence:
                in_fence, fence_tok = True, tok
            elif tok == fence_tok:
                in_fence, fence_tok = False, None
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        line = line.replace(r"\[", "$$").replace(r"\]", "$$")
        line = line.replace(r"\(", "$").replace(r"\)", "$")
        out.append(line)
    return "\n".join(out)


# --------------------------------------------------------------------------
# quiz rendering - AskUserQuestion is this system's quiz tool
# --------------------------------------------------------------------------

def render_quiz(tool_input, answers):
    """Render an AskUserQuestion call as a readable, reviewable quiz block."""
    lines = []
    for q in tool_input.get("questions", []):
        prompt = (q.get("question") or "").strip()
        chosen = answers.get(prompt, "")
        lines.append("> [!question] Quiz")
        for pl in normalise_latex(prompt).split("\n"):
            lines.append("> " + pl)
        lines.append(">")
        for opt in q.get("options", []):
            label = (opt.get("label") or "").strip()
            mark = "x" if chosen and label and label in chosen else " "
            lines.append(f"> - [{mark}] {normalise_latex(label)}")
        if chosen:
            lines.append(">")
            lines.append(f"> **Answered:** {normalise_latex(chosen)}")
        lines.append("")
    return "\n".join(lines)


def collect_answers(entries):
    """Map tool_use_id -> {question: chosen answer} from AskUserQuestion results."""
    by_id = {}
    for o in entries:
        if o.get("type") != "user":
            continue
        for b in blocks_of(o):
            if b.get("type") != "tool_result":
                continue
            tid = b.get("tool_use_id")
            content = b.get("content")
            if isinstance(content, list):
                content = " ".join(
                    c.get("text", "") for c in content if isinstance(c, dict)
                )
            if not isinstance(content, str):
                continue
            picked = {}
            try:
                data = json.loads(content)
                for item in data if isinstance(data, list) else [data]:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            if isinstance(v, str):
                                picked[k] = v
            except (json.JSONDecodeError, TypeError):
                for m in re.finditer(r'"([^"]+)"\s*:\s*"([^"]*)"', content):
                    picked[m.group(1)] = m.group(2)
            if picked:
                by_id[tid] = picked
    return by_id


# --------------------------------------------------------------------------
# rendering a slice of the conversation
# --------------------------------------------------------------------------

def render(entries, start_index, answers):
    chunks = []
    for o in entries[start_index:]:
        if o.get("isSidechain"):
            continue  # subagent chatter stays out of the note

        if is_human_turn(o):
            body = normalise_latex(human_text(o))
            if body.startswith("<") or body.startswith("[Request interrupted"):
                continue
            quoted = "\n".join("> " + l for l in body.split("\n"))
            chunks.append(f"> [!tldr] You\n{quoted}\n")
            continue

        if o.get("type") != "assistant":
            continue

        for b in blocks_of(o):
            kind = b.get("type")
            if kind == "text":
                txt = b.get("text", "").strip()
                if txt:
                    chunks.append(normalise_latex(txt) + "\n")
            elif kind == "tool_use" and b.get("name") == "AskUserQuestion":
                chunks.append(
                    render_quiz(b.get("input") or {}, answers.get(b.get("id"), {}))
                )
    return "\n".join(chunks)


# --------------------------------------------------------------------------

def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    root = vault_root(payload)
    session_id = payload.get("session_id") or "unknown"
    transcript = payload.get("transcript_path")
    state_dir = root / ".learning" / "state"
    state_file = state_dir / f"{session_id}.json"
    pending = state_dir / "pending-link"

    state = None
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            state = None

    # Claim a pending link written by the /teach skill this session.
    if state is None and pending.exists():
        try:
            age = time.time() - pending.stat().st_mtime
            note = pending.read_text(encoding="utf-8").strip()
            if note and age < PENDING_MAX_AGE:
                state = {"note": note, "cursor": 0}
                pending.unlink()
        except OSError:
            pass

    if state is None:
        return 0  # session isn't bound to a note - nothing to mirror

    if not transcript or not os.path.exists(transcript):
        return 0

    entries = read_transcript(transcript)
    cursor = int(state.get("cursor") or 0)
    if cursor >= len(entries):
        return 0

    body = render(entries, cursor, collect_answers(entries))

    note_path = root / state["note"]
    if body.strip():
        try:
            note_path.parent.mkdir(parents=True, exist_ok=True)
            with open(note_path, "a", encoding="utf-8") as fh:
                fh.write("\n" + body.rstrip() + "\n")
        except OSError as exc:
            print(f"mdlog: could not write {note_path}: {exc}", file=sys.stderr)
            return 0

    state["cursor"] = len(entries)
    try:
        state_dir.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
