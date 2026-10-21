#!/usr/bin/env python3
"""Render dedicated index thumbnails from the current public entry metadata.

Reuses the SVG card renderer; never rewrites article figures or legacy assets.
No dependencies. Run from the repository root: python3 evals/thumbnails.py
"""
from __future__ import annotations

import html
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build import ENTRIES

W, H = 800, 450
COAL, PANEL, PAPER = '#171716', '#36322e', '#fff8e8'
MUTED, ORANGE, SAGE, TEAL = '#dfd6c7', '#ed7a3a', '#9bc9a9', '#2fb9b5'
FONT = "system-ui,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"


def esc(value: str) -> str:
    return html.escape(value, quote=False)


def wrap(content: str, width: int) -> list[str]:
    """Wrap whole words, without silently dropping any part of a title."""
    lines = []
    line = ''
    for word in content.split():
        candidate = f'{line} {word}'.strip()
        if len(candidate) > width and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def text(x, y, content, size, fill, weight=600, anchor='start', spacing=1.25, css_class=''):
    lines = content if isinstance(content, list) else [content]
    spans = ''.join(f'<tspan x="{x}" y="{y + i * size * spacing:.0f}">{esc(line)}</tspan>' for i, line in enumerate(lines))
    return f'<text class="{css_class}" text-anchor="{anchor}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}">{spans}</text>'


def bars(x, y, width, series, accent, unit=''):
    """Keep the published counts/ratings, with their units stated explicitly."""
    out = []
    for i, (label, value, maximum) in enumerate(series):
        top = y + i * 29
        colour = accent if i == len(series) - 1 else MUTED
        out.append(f'<rect x="{x}" y="{top}" width="{width}" height="14" rx="3" fill="{PANEL}"/>')
        out.append(f'<rect x="{x}" y="{top}" width="{width * value / maximum:.1f}" height="14" rx="3" fill="{colour}"/>')
        result = f'{value:g} {unit}' if unit else f'{value:g}/{maximum:g}'
        out.append(text(x + width + 18, top + 14, f'{label} {result}', 18, MUTED, 500))
    return ''.join(out)


def card(entry) -> str:
    themes, _, meta, title, blurb, source, _, _ = entry
    headline = wrap(title, 31)
    if len(headline) > 3:
        raise ValueError(f'Title needs a larger layout, not truncation: {title}')
    accent = TEAL if 'evaluation' in themes else ORANGE if 'agent-systems' in themes else SAGE
    category = ' / '.join(theme.replace('agent-systems', 'agent systems').upper() for theme in themes)
    body = text(56, 280, wrap(blurb, 56), 20, MUTED, 400)
    if source == 'evals/fable-run5-granite.html':
        body = bars(56, 278, 350, [('control', 8, 24), ('sham', 7, 24), ('manual', 16, 24)], SAGE)
    elif source == 'notes/watts-per-token.html':
        body = text(56, 270, 'Rated fan draw, not a matched-airflow test.', 18, MUTED, 400)
        body += bars(56, 294, 350, [('desk fan', 35, 35), ('NF-A14 iPPC', 6.6, 35)], ORANGE, 'W')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="title description">
<title id="title">{esc(title)}</title><desc id="description">{esc(blurb)}</desc>
<rect width="{W}" height="{H}" fill="#f7f0df"/>
<rect x="16" y="16" width="768" height="418" rx="20" fill="{COAL}"/>
<rect x="44" y="53" width="5" height="24" rx="2" fill="{accent}"/>
{text(62, 73, category, 18, accent, 700)}
{text(744, 73, 'FIELDNOTES', 18, MUTED, 600, anchor='end')}
{text(56, 132, headline, 40, PAPER, 700, spacing=1.12, css_class='headline')}
{body}
<path d="M56 376H744" stroke="{PANEL}"/>
{text(56, 407, meta, 18, MUTED, 400)}
</svg>
'''


def main() -> None:
    for entry in ENTRIES:
        if not entry[6].startswith('assets/thumbnails/'):
            continue
        target = ROOT / entry[6]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(card(entry), encoding='utf-8')
        print(f'  wrote {entry[6]}')


if __name__ == '__main__':
    main()
