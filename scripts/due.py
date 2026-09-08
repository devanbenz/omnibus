#!/usr/bin/env python3
"""Spaced-repetition scheduler over Concepts/*.md frontmatter.

    due.py                                  list notes due today or earlier
    due.py "linear algebra"                 filter by topic/tag/title substring
    due.py --all                            list every concept note with its date
    due.py --grade <note> <again|hard|good|easy>

Frontmatter fields used: next_review (YYYY-MM-DD), interval (days), ease.
Uses an SM-2 style schedule. No dependencies beyond the standard library.
"""
import datetime as dt
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
CONCEPTS = ROOT / "Concepts"
REVIEWS = ROOT / "Reviews"

MIN_EASE = 1.3
GRADES = ("again", "hard", "good", "easy")


def split_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw = text[3:end]
    body = text[end + 4:].lstrip("\n")
    meta = {}
    for line in raw.split("\n"):
        if ":" not in line or line.strip().startswith("#"):
            continue
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body


def write_frontmatter(path, meta, body, order):
    keys = [k for k in order if k in meta] + [k for k in meta if k not in order]
    lines = ["---"]
    for k in keys:
        v = meta[k]
        lines.append(f"{k}: {v}")
    lines += ["---", "", body.rstrip(), ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_date(value):
    try:
        return dt.date.fromisoformat(str(value).strip())
    except (ValueError, AttributeError):
        return None


def notes():
    if not CONCEPTS.is_dir():
        return
    for p in sorted(CONCEPTS.rglob("*.md")):
        meta, body = split_frontmatter(p.read_text(encoding="utf-8"))
        yield p, meta, body


def matches(p, meta, needle):
    if not needle:
        return True
    hay = " ".join([p.stem, meta.get("topic", ""), meta.get("tags", "")]).lower()
    return needle.lower() in hay


def cmd_list(needle, show_all):
    today = dt.date.today()
    rows = []
    for p, meta, _ in notes():
        if not matches(p, meta, needle):
            continue
        due = parse_date(meta.get("next_review"))
        if due is None:
            rows.append((today, p, "unscheduled"))
        elif show_all or due <= today:
            overdue = (today - due).days
            when = "today" if overdue == 0 else (
                f"{overdue}d overdue" if overdue > 0 else f"in {-overdue}d")
            rows.append((due, p, when))
    if not rows:
        upcoming = sorted(
            (d for _, m, _ in notes()
             if (d := parse_date(m.get("next_review"))) and d > today)
        )
        if upcoming:
            print(f"nothing due. next: {upcoming[0].isoformat()} "
                  f"({(upcoming[0] - today).days}d)")
        else:
            print("nothing due (no scheduled concept notes yet)")
        return 0
    rows.sort(key=lambda r: r[0])
    print(f"{len(rows)} due:")
    for due, p, when in rows:
        print(f"  {p.relative_to(ROOT)}  [{when}]")
    return 0


def cmd_grade(target, grade):
    if grade not in GRADES:
        print(f"grade must be one of {', '.join(GRADES)}", file=sys.stderr)
        return 1

    path = Path(target)
    if not path.is_absolute():
        path = ROOT / target
    if not path.exists():
        matches_ = [p for p, _, _ in notes() if target.lower() in p.stem.lower()]
        if len(matches_) != 1:
            print(f"no unique concept note for {target!r}", file=sys.stderr)
            return 1
        path = matches_[0]

    meta, body = split_frontmatter(path.read_text(encoding="utf-8"))

    try:
        ease = float(meta.get("ease", 2.5))
    except ValueError:
        ease = 2.5
    try:
        interval = float(meta.get("interval", 1))
    except ValueError:
        interval = 1.0

    if grade == "again":
        ease, interval = max(MIN_EASE, ease - 0.20), 1
    elif grade == "hard":
        ease, interval = max(MIN_EASE, ease - 0.15), max(1, interval * 1.2)
    elif grade == "good":
        interval = max(1, interval * ease) if interval > 1 else 3
    else:  # easy
        ease, interval = ease + 0.15, max(1, interval * ease * 1.3) if interval > 1 else 5

    interval = min(round(interval), 365)
    today = dt.date.today()
    nxt = today + dt.timedelta(days=interval)

    meta["next_review"] = nxt.isoformat()
    meta["interval"] = str(interval)
    meta["ease"] = f"{ease:.2f}"
    meta.setdefault("type", "concept")
    meta.setdefault("learned", today.isoformat())

    write_frontmatter(
        path, meta, body,
        ["type", "topic", "learned", "next_review", "interval", "ease", "tags"],
    )

    REVIEWS.mkdir(parents=True, exist_ok=True)
    log = REVIEWS / f"{today.isoformat()[:7]}.md"
    if not log.exists():
        log.write_text(
            f"---\ntype: review-log\nmonth: {today.isoformat()[:7]}\n---\n\n"
            f"# Reviews {today.isoformat()[:7]}\n\n",
            encoding="utf-8",
        )
    with open(log, "a", encoding="utf-8") as fh:
        fh.write(f"- {today.isoformat()} `{grade}` [[{path.stem}]] "
                 f"→ {nxt.isoformat()} ({interval}d, ease {ease:.2f})\n")

    print(f"{path.relative_to(ROOT)}: {grade} → next {nxt.isoformat()} ({interval}d)")
    return 0


def main(argv):
    if "--grade" in argv:
        i = argv.index("--grade")
        rest = argv[i + 1:]
        if len(rest) < 2:
            print("usage: due.py --grade <note> <again|hard|good|easy>", file=sys.stderr)
            return 1
        return cmd_grade(rest[0], rest[1].lower())
    show_all = "--all" in argv
    needle = next((a for a in argv if not a.startswith("--")), "")
    return cmd_list(needle, show_all)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
