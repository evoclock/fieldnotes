#!/usr/bin/env python3
"""Emit the "Writing and evidence" section for the profile README.

The profile and the site index are rendered from the same `ENTRIES` list in
`build.py`, so a piece added there appears in both and the two cannot drift.

    python3 profile-section.py > /tmp/section.md
"""

from __future__ import annotations

from build import ENTRIES, SITE, THEMES

# One alloy per theme, matching the marks in the profile repository. Evaluation
# has no mark of its own: it runs through everything else rather than sitting
# beside it.
MARKS = {
    "agent-systems": ("Shibuichi", "Shibuichi-origami-removebg-preview.png"),
    "models": ("Sentoku", "Sentoku-origami-removebg-preview.png"),
    "comp-bio": ("Yamagane", "Yamagane-origami-removebg-preview.png"),
}


def entry(e) -> str:
    _, _, meta, title, blurb, href, _, _ = e
    return f"- **[{title}]({SITE}{href})**  \n  <sub>{meta}</sub>  \n  {blurb}"


def main() -> None:
    out = [
        "## Technical reports, experiments, evals and thoughts",
        "",
        '<p align="center">',
        f'  <a href="{SITE}">',
        '    <img src="assets/Sentoku-origami-removebg-preview.png"'
        ' alt="fieldnotes" width="150">',
        "  </a>",
        "</p>",
        "",
        f'<p align="center"><strong><a href="{SITE}">fieldnotes</a></strong><br>',
        "<sub>Agent systems, models, evaluation and computational biology.<br>",
        f'Everything below is published at <a href="{SITE}">'
        "evoclock.github.io/fieldnotes</a>, and new pieces appear in the ",
        f'<a href="{SITE}feed.xml">RSS feed</a>.</sub></p>',
        "",
    ]

    for key, name, blurb in THEMES:
        items = sorted([e for e in ENTRIES if key in e[0]], key=lambda x: x[1], reverse=True)
        mark = MARKS.get(key)
        heading = name
        if not items:
            out += [
                "<details>",
                f"<summary><strong>{heading}</strong> &mdash; nothing published yet</summary>",
                "", blurb, "", "_Write-ups for this theme are in progress._", "",
                "</details>", "",
            ]
            continue
        out += [
            "<details open>",
            f"<summary><strong>{heading}</strong> ({len(items)})</summary>",
            "", blurb, "",
        ]
        if mark:
            out += [
                f'<img src="assets/{mark[1]}" alt="" width="58" align="right">',
                "",
            ]
        out += ["\n\n".join(entry(e) for e in items), "", "</details>", ""]

    print("\n".join(out))


if __name__ == "__main__":
    main()
