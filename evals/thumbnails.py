#!/usr/bin/env python3
"""Render index thumbnails for the evaluation write-ups.

One SVG per write-up, sized for the card grid on the site index. Everything
shown here is taken from the page it links to: the figures are the published
result, not a summary invented for the picture.

No dependencies. The SVG is written directly, as in ``diagrams/``.

    python3 thumbnails.py
"""

from __future__ import annotations

import html
from pathlib import Path

W, H = 800, 450
COAL, PANEL, PAPER = "#151719", "#222629", "#f0f2f1"
MUTED, ORANGE, SAGE, TEAL = "#b8c0bd", "#e77843", "#79c39e", "#3fbec1"
FONT = "system-ui,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
HERE = Path(__file__).resolve().parent


def esc(value: str) -> str:
    return html.escape(value, quote=False)


def wrap(text: str, width: int) -> list[str]:
    """Greedy wrap on whole words."""
    lines: list[str] = []
    line = ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if len(candidate) > width and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def text(x, y, content, size, fill, weight=600, anchor="start", spacing=1.3):
    lines = content if isinstance(content, list) else [content]
    step = size * spacing
    spans = "".join(
        f'<tspan x="{x}" y="{y + i * step:.0f}">{esc(line)}</tspan>'
        for i, line in enumerate(lines)
    )
    return (
        f'<text text-anchor="{anchor}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}">{spans}</text>'
    )


def bars(x, y, width, series, accent):
    """A small comparison bar set. `series` is [(label, value, maximum), ...]."""
    out = []
    gap, bar_h = 34, 16
    longest = max(value / maximum for _, value, maximum in series) or 1
    for i, (label, value, maximum) in enumerate(series):
        top = y + i * gap
        frac = (value / maximum) / longest
        colour = accent if i == len(series) - 1 else PANEL
        out.append(f'<rect x="{x}" y="{top}" width="{width}" height="{bar_h}" rx="3" fill="{PANEL}"/>')
        out.append(
            f'<rect x="{x}" y="{top}" width="{width * frac:.0f}" height="{bar_h}" rx="3" fill="{colour}"/>'
        )
        out.append(text(x + width + 14, top + 13, f"{label} {value}/{maximum}", 15, MUTED, 500))
    return "".join(out)


def card(eyebrow: str, headline: str, footer: str, accent: str, body: str = "") -> str:
    head = wrap(headline, 30)[:3]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img">
<rect width="{W}" height="{H}" fill="{COAL}"/>
<rect x="0" y="0" width="{W}" height="6" fill="{accent}"/>
{text(56, 74, eyebrow.upper(), 16, accent, 700)}
{text(56, 138, head, 34, PAPER, 700, spacing=1.25)}
{body}
{text(56, H - 44, footer, 16, MUTED, 500)}
</svg>
"""


# Each entry mirrors the page it links to. Figures come from the published
# result; where a write-up reports no effect, the thumbnail says so rather than
# manufacturing a chart out of nothing.
THUMBNAILS = {
    "fable-run5-granite": card(
        "Operating manual · run 5",
        "A reasoning manual helped a small model catch the trap",
        "granite-4.0-h-small-FP8 · n=24 per arm · temperature 0.7",
        SAGE,
        bars(56, 210, 340, [("control", 8, 24), ("sham", 7, 24), ("manual", 16, 24)], SAGE),
    ),
    "cruxeval-o-ab-184": card(
        "CRUXEval-O · A/B",
        "The prompt is not the model",
        "7 models · 184 problems · one attempt each · temperature 0",
        TEAL,
        text(56, 250, ["The headline change is meaningless on its own.", "The effect is bimodal. The signal is the floor."], 19, MUTED, 500),
    ),
    "cruxeval-o-results": card(
        "CRUXEval-O · reviewer seat",
        "Seven local models on output prediction",
        "100 problems · Pass@1 · prompt, infra and harness failures excluded",
        TEAL,
        text(56, 250, ["A reviewer-seat battery across the local roster,", "graded strictly and reported with its failures."], 19, MUTED, 500),
    ),
    "screen_eval_run4": card(
        "Capability screen · run 4",
        "The gate opened, and the manual still moved nothing",
        "Qwen3.6-35B · local vLLM · thinking off · temperature 0.7",
        ORANGE,
        text(56, 250, ["A weaker base model and a harder trap gave the", "manual room to show an effect. It did not."], 19, MUTED, 500),
    ),
    "screen_eval": card(
        "Capability screen · run 3",
        "The manual moved only the labels",
        "Sonnet 5 · three arms · three tiers · 27 agents",
        ORANGE,
        text(56, 250, ["A sham arm and a difficulty ladder, so a real", "capability effect would have had room to appear."], 19, MUTED, 500),
    ),
    "trap_eval": card(
        "Trap battery · A/B",
        "It changed how the work was shown, not what was caught",
        "Sonnet 5 · nine traps · model held constant",
        ORANGE,
        text(56, 258, ["One arm reads the operating manual, one does not."], 19, MUTED, 500),
    ),
}


def main() -> None:
    for name, svg in THUMBNAILS.items():
        path = HERE / f"{name}.svg"
        path.write_text(svg, encoding="utf-8")
        print(f"  wrote {path.name}")


if __name__ == "__main__":
    main()
