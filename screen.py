#!/usr/bin/env python3
"""Presence-only screen for credential values in publishable outputs.

Run before publishing:

    python3 screen.py

Scans the text artifacts this site publishes (articles, notes, eval pages,
the generated index and feed, diagrams and thumbnails that carry text) for
structurally credential-shaped values. Presence-only: a finding reports the
file, the line number and the pattern name. It never prints, keeps or sends
the matched value, and the tool never reads credential stores, environment
values or any live service. The patterns below are structural (prefix,
length, alphabet) and are not derived from any real credential.

Binary assets such as PNG screenshots cannot be screened this way; see the
"Screening before publishing" section of the README for how they are covered.

Exit status: 0 when clean, 1 when any finding is reported, 2 on usage error.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Text artifact extensions that get published as-is.
TEXT_SUFFIXES = {".html", ".md", ".xml", ".svg", ".xsl"}

# Synthetic-tolerant directories: test fixtures intentionally contain
# structurally valid fake values, and source code is not a publishable output.
SKIP_DIRS = {".git", "__pycache__", "tests"}

# High-signal structural patterns. Named, ordered, presence-only.
PATTERNS: list[tuple[str, re.Pattern]] = [
    ("github-token", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}")),
    ("gitlab-token", re.compile(r"glpat-[A-Za-z0-9_\-]{20,}")),
    ("aws-access-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("google-api-key", re.compile(r"AIza[0-9A-Za-z_\-]{35}")),
    ("slack-token", re.compile(r"xox[abposr]-[A-Za-z0-9\-]{10,}")),
    ("openai-key", re.compile(r"sk-(?:ant-)?proj-[A-Za-z0-9_\-]{20,}")),
    ("anthropic-key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("private-key-block", re.compile(
        r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY(?: BLOCK)?-----")),
    ("jwt", re.compile(
        r"\beyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{5,}")),
    ("bearer-value", re.compile(
        r"(?i)\bbearer\s+[A-Za-z0-9._~+/=\-]{20,}\b")),
    ("credential-assignment", re.compile(
        r"(?im)^\s*\*{0,2}(?:password|passwd|secret|token|api[_-]?key|"
        r"access[_-]?key|client[_-]?secret|private[_-]?token)\*{0,2}"
        r"\s*[:=]\s*[\"'`]?[A-Za-z0-9+/_\-]{12,}")),
]


def find_artifacts(root: Path) -> list[Path]:
    """Publishable text artifacts under root, excluding fixtures and code."""
    if root.is_file():
        return [root]
    out = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            out.append(path)
    return out


def screen_text(text: str) -> list[tuple[int, str]]:
    """Return (line_number, pattern_name) for each finding. No values."""
    findings = []
    lines = text.splitlines()
    joined = "\n".join(lines)
    for name, pattern in PATTERNS:
        for match in pattern.finditer(joined):
            line = joined.count("\n", 0, match.start()) + 1
            findings.append((line, name))
    return sorted(findings)


def shown(path: Path) -> str:
    """Repo-relative name when possible, absolute path otherwise."""
    try:
        return str(path.relative_to(HERE))
    except ValueError:
        return str(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--paths", nargs="*", type=Path, default=None,
        help="screen specific files or directories instead of the site")
    args = parser.parse_args([str(a) for a in argv] if argv is not None else None)

    roots = args.paths if args.paths else [HERE]
    artifacts = []
    for root in roots:
        resolved = root if root.is_absolute() else HERE / root
        if not resolved.exists():
            print(f"screen: no such path: {root}", file=sys.stderr)
            return 2
        artifacts.extend(find_artifacts(resolved))

    total = 0
    for path in artifacts:
        try:
            text = path.read_text(encoding="utf-8", errors="strict")
        except (UnicodeDecodeError, ValueError):
            print(f"  not text, skipped  {shown(path)}")
            continue
        for line, name in screen_text(text):
            print(f"  {shown(path)}:{line}  {name}")
            total += 1

    print(f"  screened {len(artifacts)} text artifacts, {total} findings")
    if total:
        print("  presence-only report: values are never shown; "
              "inspect the file and line yourself")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
