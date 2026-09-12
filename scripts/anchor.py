#!/usr/bin/env python3
"""Pin a teaching point to an exact place in a source, in a form Obsidian renders.

    anchor.py code <path>[:<start>[-<end>]]          excerpt + git permalink
    anchor.py quote <Sources/Note.md> "<phrase>"     block link + quote callout
    anchor.py import <url | file.pdf | file.md> [--title "..."] [--kind article|paper|chapter|docs]

`code` prints a callout captioned with `path:start-end`, a permalink into the
hosting forge at the current commit when one can be derived, and the excerpt
itself in a fenced block. Paste it into the message - it lands in the note.

`quote` finds the paragraph of a Sources/ note that contains the phrase, gives
it a stable Obsidian block id (`^abc123`, written back into the note if it is
not already there), and prints a `[[Sources/Note#^abc123]]` link plus a quote
callout. Hovering the link in Obsidian previews exactly that paragraph.

`import` saves a text source into Sources/ so that `quote` has something to
anchor into. URLs are fetched and reduced to headings, paragraphs, lists and
code; PDFs go through pdftotext with one `## Page N` heading per page so
`[[Note#Page 7]]` works; markdown and plain text are copied.

Standard library only. pdftotext is optional and only needed for PDFs.
"""
import datetime as dt
import hashlib
import html
import os
import re
import subprocess
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
SOURCES = ROOT / "Sources"

LANG = {
    ".py": "python", ".js": "javascript", ".ts": "typescript", ".tsx": "tsx",
    ".jsx": "jsx", ".go": "go", ".rs": "rust", ".rb": "ruby", ".java": "java",
    ".kt": "kotlin", ".c": "c", ".h": "c", ".cpp": "cpp", ".hpp": "cpp",
    ".cs": "csharp", ".sh": "bash", ".zsh": "bash", ".sql": "sql",
    ".md": "markdown", ".json": "json", ".yaml": "yaml", ".yml": "yaml",
    ".toml": "toml", ".html": "html", ".css": "css", ".ex": "elixir",
    ".exs": "elixir", ".hs": "haskell", ".ml": "ocaml", ".scala": "scala",
    ".swift": "swift", ".lua": "lua", ".r": "r", ".R": "r", ".jl": "julia",
    ".tex": "latex", ".proto": "protobuf", ".tf": "hcl", ".zig": "zig",
}


# --------------------------------------------------------------------------
# shared helpers
# --------------------------------------------------------------------------

def die(msg, code=1):
    print(f"anchor: {msg}", file=sys.stderr)
    return code


def git(args, cwd):
    try:
        out = subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=10
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip()


def slug(text, limit=80):
    text = re.sub(r"[^\w\s-]", "", text).strip()
    text = re.sub(r"[\s_]+", " ", text)
    return text[:limit].strip() or "source"


def split_frontmatter(text):
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 3)
    if end == -1:
        return "", text
    return text[: end + 4], text[end + 4:]


def note_name(path):
    """Vault-relative name usable inside [[...]] (no extension)."""
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    try:
        rel = p.resolve().relative_to(ROOT.resolve())
    except ValueError:
        rel = Path(p.name)
    return str(rel.with_suffix("")).replace(os.sep, "/")


# --------------------------------------------------------------------------
# code
# --------------------------------------------------------------------------

REF = re.compile(r"^(?P<path>.+?)(?::(?P<start>\d+)(?:-(?P<end>\d+))?)?$")


def permalink(path):
    """Forge URL for this file at HEAD, or None if it cannot be derived."""
    top = git(["rev-parse", "--show-toplevel"], path.parent)
    if not top:
        return None, None
    sha = git(["rev-parse", "HEAD"], top)
    remote = git(["remote", "get-url", "origin"], top)
    if not sha or not remote:
        return None, None
    rel = path.resolve().relative_to(Path(top).resolve()).as_posix()

    m = re.match(r"^(?:git@|ssh://git@|https?://)([^/:]+)[/:](.+?)(?:\.git)?/?$", remote)
    if not m:
        return None, None
    host, repo = m.group(1), m.group(2)
    if "gitlab" in host:
        base = f"https://{host}/{repo}/-/blob/{sha}/{rel}"
    elif "bitbucket" in host:
        base = f"https://{host}/{repo}/src/{sha}/{rel}"
    else:  # github, codeberg, gitea, sourcehut-ish
        base = f"https://{host}/{repo}/blob/{sha}/{rel}"

    dirty = git(["status", "--porcelain", "--", rel], top)
    return base, (host, bool(dirty))


def line_fragment(host, start, end):
    if start is None:
        return ""
    if "gitlab" in host:
        return f"#L{start}" if end == start else f"#L{start}-{end}"
    if "bitbucket" in host:
        return f"#lines-{start}" if end == start else f"#lines-{start}:{end}"
    return f"#L{start}" if end == start else f"#L{start}-L{end}"


def cmd_code(argv):
    if not argv:
        return die("usage: anchor.py code <path>[:<start>[-<end>]]")
    m = REF.match(argv[0])
    path = Path(m.group("path")).expanduser()
    if not path.exists():
        return die(f"no such file: {path}")
    start = int(m.group("start")) if m.group("start") else None
    end = int(m.group("end")) if m.group("end") else start

    lines = path.read_text(encoding="utf-8", errors="replace").split("\n")
    if start is not None:
        if start < 1 or end < start or start > len(lines):
            return die(f"bad range {start}-{end} for a {len(lines)}-line file")
        end = min(end, len(lines))
        excerpt = lines[start - 1:end]
    else:
        excerpt = lines[:min(len(lines), 60)]
        start, end = 1, len(excerpt)

    # de-indent so the excerpt reads cleanly out of context
    indents = [len(l) - len(l.lstrip()) for l in excerpt if l.strip()]
    cut = min(indents) if indents else 0
    excerpt = [l[cut:] if l.strip() else "" for l in excerpt]

    try:
        shown = path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        shown = str(path)
    caption = f"`{shown}:{start}`" if start == end else f"`{shown}:{start}-{end}`"

    url, info = permalink(path)
    if url:
        host, dirty = info
        caption += f" · [permalink]({url}{line_fragment(host, start, end)})"
        if dirty:
            print(f"anchor: {shown} has uncommitted changes - permalink shows HEAD, "
                  f"not the working tree", file=sys.stderr)

    lang = LANG.get(path.suffix, "")
    fence = "````" if any("```" in l for l in excerpt) else "```"
    out = [f"> [!example] {caption}", f"> {fence}{lang}"]
    out += ["> " + l if l else ">" for l in excerpt]
    out.append(f"> {fence}")
    print("\n".join(out))
    return 0


# --------------------------------------------------------------------------
# quote
# --------------------------------------------------------------------------

BLOCK_ID = re.compile(r"\s\^([A-Za-z0-9-]+)\s*$")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")


def paragraphs(body):
    """Yield (start_line, end_line, heading_context) for each non-empty block."""
    lines = body.split("\n")
    context, i, in_fence = [], 0, False
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        if lines[i].lstrip().startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].lstrip().startswith("```"):
                j += 1
            yield i, min(j, len(lines) - 1), list(context)
            i = j + 1
            continue
        h = HEADING.match(lines[i])
        if h:
            depth = len(h.group(1))
            context = [c for c in context if c[0] < depth] + [(depth, h.group(2).strip())]
            i += 1
            continue
        j = i
        while j + 1 < len(lines) and lines[j + 1].strip() and not HEADING.match(lines[j + 1]):
            j += 1
        yield i, j, list(context)
        i = j + 1


def squash(text):
    return re.sub(r"\s+", " ", text).strip().lower()


def cmd_quote(argv):
    if len(argv) < 2:
        return die('usage: anchor.py quote <Sources/Note.md> "<phrase>"')
    path = Path(argv[0])
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        cands = list(SOURCES.glob(f"*{argv[0]}*.md")) if SOURCES.is_dir() else []
        if len(cands) != 1:
            return die(f"no such note: {argv[0]}")
        path = cands[0]
    phrase = squash(" ".join(argv[1:]))
    if not phrase:
        return die("empty phrase")

    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    lines = body.split("\n")

    hits = [(s, e, ctx) for s, e, ctx in paragraphs(body)
            if phrase in squash(" ".join(lines[s:e + 1]))]
    if not hits:
        return die(f"phrase not found in {path.name}: {phrase[:60]!r}")
    if len(hits) > 1:
        print(f"anchor: phrase matches {len(hits)} blocks in {path.name}; using the first. "
              f"Quote a longer phrase to disambiguate.", file=sys.stderr)
    s, e, ctx = hits[0]

    block = lines[s:e + 1]
    m = BLOCK_ID.search(block[-1])
    if m:
        bid = m.group(1)
    else:
        bid = hashlib.sha1("\n".join(block).encode("utf-8")).hexdigest()[:6]
        block[-1] = block[-1].rstrip() + f" ^{bid}"
        lines[s:e + 1] = block
        path.write_text(fm + "\n".join(lines), encoding="utf-8")

    name = note_name(path)
    link = f"[[{name}#^{bid}]]"
    crumbs = " › ".join([Path(name).name] + [c[1] for c in ctx])
    quoted = [re.sub(r"\s\^[A-Za-z0-9-]+\s*$", "", l) for l in block]
    out = [link, f"> [!quote] {crumbs}"]
    out += ["> " + l if l else ">" for l in quoted]
    out.append(f"> — {link}")
    print("\n".join(out))
    return 0


# --------------------------------------------------------------------------
# import
# --------------------------------------------------------------------------

SKIP_TAGS = {"script", "style", "nav", "footer", "aside", "noscript",
             "svg", "form", "button", "iframe", "title"}
BLOCK_TAGS = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "pre", "blockquote",
              "div", "section", "article", "main", "tr", "dt", "dd", "figcaption"}


class Extract(HTMLParser):
    """Reduce an HTML page to markdown-ish blocks. Crude on purpose: it only
    needs to be good enough for `quote` to find paragraphs in later."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks, self.buf, self.kind = [], [], "p"
        self.skip, self.title, self.in_title = 0, "", False
        self.pre = 0

    def flush(self):
        text = "".join(self.buf)
        self.buf = []
        if self.pre:
            text = text.strip("\n")
        else:
            text = re.sub(r"[ \t\r\f\v]+", " ", text).strip()
            text = re.sub(r"\s*\n\s*", " ", text)
        if not text:
            return
        k = self.kind
        if k in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.blocks.append("#" * int(k[1]) + " " + text)
        elif k == "li":
            self.blocks.append("- " + text)
        elif k == "pre":
            self.blocks.append("```\n" + text + "\n```")
        elif k == "blockquote":
            self.blocks.append("\n".join("> " + l for l in text.split("\n")))
        else:
            self.blocks.append(text)

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True
        if tag in SKIP_TAGS:
            self.skip += 1
            return
        if self.skip:
            return
        if tag in BLOCK_TAGS:
            self.flush()
            self.kind = tag if tag in ("h1", "h2", "h3", "h4", "h5", "h6",
                                       "li", "pre", "blockquote") else "p"
            if tag == "pre":
                self.pre += 1
        elif tag == "br":
            self.buf.append("\n")
        elif tag == "code" and not self.pre:
            self.buf.append("`")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag in SKIP_TAGS:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if tag in BLOCK_TAGS:
            self.flush()
            if tag == "pre":
                self.pre = max(0, self.pre - 1)
            self.kind = "p"
        elif tag == "code" and not self.pre:
            self.buf.append("`")

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif not self.skip:
            self.buf.append(data)


def fetch(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (omnibus anchor.py)"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
        ctype = resp.headers.get("Content-Type", "")
    if "pdf" in ctype or url.lower().endswith(".pdf"):
        return "pdf", raw
    charset = "utf-8"
    m = re.search(r"charset=([\w-]+)", ctype)
    if m:
        charset = m.group(1)
    return "html", raw.decode(charset, errors="replace")


def pdf_to_md(pdf_bytes_or_path):
    try:
        if isinstance(pdf_bytes_or_path, bytes):
            out = subprocess.run(["pdftotext", "-layout", "-", "-"],
                                 input=pdf_bytes_or_path, capture_output=True, timeout=120)
        else:
            out = subprocess.run(["pdftotext", "-layout", str(pdf_bytes_or_path), "-"],
                                 capture_output=True, timeout=120)
    except FileNotFoundError:
        return None
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    text = out.stdout.decode("utf-8", errors="replace")
    pages = [p for p in text.split("\f")]
    chunks = []
    for n, page in enumerate(pages, 1):
        page = page.strip("\n")
        if not page.strip():
            continue
        # collapse hard-wrapped lines into paragraphs; keep blank-line breaks
        paras = re.split(r"\n\s*\n", page)
        paras = [re.sub(r"\s*\n\s*", " ", p).strip() for p in paras]
        chunks.append(f"## Page {n}\n\n" + "\n\n".join(p for p in paras if p))
    return "\n\n".join(chunks)


def cmd_import(argv):
    if not argv:
        return die("usage: anchor.py import <url | file> [--title T] [--kind K]")
    title = kind = None
    rest = []
    i = 0
    while i < len(argv):
        if argv[i] == "--title" and i + 1 < len(argv):
            title, i = argv[i + 1], i + 2
        elif argv[i] == "--kind" and i + 1 < len(argv):
            kind, i = argv[i + 1], i + 2
        else:
            rest.append(argv[i])
            i += 1
    if not rest:
        return die("nothing to import")
    origin = rest[0]

    if re.match(r"^https?://", origin):
        try:
            fmt, payload = fetch(origin)
        except Exception as exc:  # noqa: BLE001 - report and stop
            return die(f"could not fetch {origin}: {exc}")
        if fmt == "pdf":
            body = pdf_to_md(payload)
            if body is None:
                return die("pdftotext is not installed; Read the PDF yourself and "
                           "write Sources/<title>.md by hand (see references/sources.md)")
            kind = kind or "paper"
        else:
            ex = Extract()
            ex.feed(payload)
            ex.flush()
            body = "\n\n".join(ex.blocks)
            title = title or html.unescape(ex.title).strip()
            kind = kind or "article"
    else:
        src = Path(origin).expanduser()
        if not src.exists():
            return die(f"no such file: {src}")
        if src.suffix.lower() == ".pdf":
            body = pdf_to_md(src)
            if body is None:
                return die("pdftotext is not installed; Read the PDF yourself and "
                           "write Sources/<title>.md by hand (see references/sources.md)")
            kind = kind or "paper"
        else:
            _, body = split_frontmatter(src.read_text(encoding="utf-8", errors="replace"))
            kind = kind or "chapter"
        title = title or src.stem.replace("-", " ").replace("_", " ")

    if not body or not body.strip():
        return die("nothing extractable at that origin - write the Sources/ note by hand")
    title = title or origin
    name = slug(title)

    SOURCES.mkdir(parents=True, exist_ok=True)
    note = SOURCES / f"{name}.md"
    if note.exists():
        print(f"anchor: {note.relative_to(ROOT)} already exists - leaving it", file=sys.stderr)
        print(note.relative_to(ROOT))
        return 0

    safe_title = title.replace('"', "'")
    note.write_text(
        "---\n"
        "type: source\n"
        f'title: "{safe_title}"\n'
        f"kind: {kind}\n"
        f'origin: "{origin}"\n'
        f"imported: {dt.date.today().isoformat()}\n"
        "tags: [source]\n"
        "---\n\n"
        f"# {title}\n\n"
        f"> [!info] Source\n> {origin}\n\n"
        + body.rstrip() + "\n",
        encoding="utf-8",
    )
    print(note.relative_to(ROOT))
    return 0


# --------------------------------------------------------------------------

def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd == "code":
        return cmd_code(rest)
    if cmd == "quote":
        return cmd_quote(rest)
    if cmd == "import":
        return cmd_import(rest)
    return die(f"unknown command {cmd!r}; try --help")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
