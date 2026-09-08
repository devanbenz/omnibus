#!/usr/bin/env python3
"""Create a learning-session note and bind it to the running session.

    python3 scripts/newsession.py "differential forms"

Bootstraps the vault folders on first run, seeds the user-owned learning
philosophy from the plugin template, then prints the note path. Everything the
session says from here on is mirrored into that note by mdlog.py.
"""
import datetime as dt
import os
import re
import sys
from pathlib import Path


def slug(text):
    text = re.sub(r"[^\w\s-]", "", text).strip()
    text = re.sub(r"[\s_]+", " ", text)
    return text[:60] or "session"


def bootstrap(root):
    """Create the vault layout, and seed the philosophy file if absent."""
    for folder in ("Sessions", "Concepts", "Attachments", "Reviews"):
        (root / folder).mkdir(parents=True, exist_ok=True)

    learning = root / ".learning" / "state"
    learning.mkdir(parents=True, exist_ok=True)

    philosophy = root / ".learning" / "philosophy.md"
    if not philosophy.exists():
        template = Path(__file__).resolve().parent.parent / "templates" / "philosophy.md"
        try:
            philosophy.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
        except OSError:
            pass


def main():
    if len(sys.argv) < 2:
        print("usage: newsession.py <topic>", file=sys.stderr)
        return 1

    topic = " ".join(sys.argv[1:]).strip()
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    today = dt.date.today().isoformat()

    bootstrap(root)
    sessions = root / "Sessions"

    base = f"{today} {slug(topic)}"
    note = sessions / f"{base}.md"
    n = 2
    while note.exists():
        note = sessions / f"{base} ({n}).md"
        n += 1

    note.write_text(
        "---\n"
        f'topic: "{topic}"\n'
        f"date: {today}\n"
        "type: learning-session\n"
        "phase: probe\n"
        "tags: [learning/session]\n"
        "---\n\n"
        f"# {topic}\n\n"
        f"> [!abstract] Goal\n> {topic}\n\n"
        "## Probe\n",
        encoding="utf-8",
    )

    state = root / ".learning" / "state"
    state.mkdir(parents=True, exist_ok=True)
    (state / "pending-link").write_text(
        str(note.relative_to(root)), encoding="utf-8"
    )

    print(note.relative_to(root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
