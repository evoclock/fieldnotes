#!/usr/bin/env python3
"""Render the public Local Model Workforce overview with fixed geometry."""

from __future__ import annotations

import html
import shutil
import subprocess
from pathlib import Path


W, H = 1800, 2240
BG, PANEL, NODE, CONTROL, WARM = "#18191a", "#242220", "#383431", "#4a4540", "#5c564f"
CREAM, TEAL, ORANGE, CORAL, COPPER = "#ead1b5", "#79c39e", "#e77843", "#ee9b69", "#b09080"
HERE = Path(__file__).resolve().parent


def text(x: int, y: int, lines: list[str], size: int = 25, weight: int = 600) -> str:
    step = int(size * 1.22)
    first = y - step * (len(lines) - 1) / 2
    spans = "".join(
        f'<tspan x="{x}" y="{first + i * step}">{html.escape(line)}</tspan>'
        for i, line in enumerate(lines)
    )
    return (
        f'<text text-anchor="middle" font-family="Arial,Helvetica,sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{CREAM}">{spans}</text>'
    )


def box(
    x: int,
    y: int,
    w: int,
    h: int,
    lines: list[str],
    stroke: str,
    *,
    fill: str = NODE,
    size: int = 22,
) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="15" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="4"/>'
        + text(x + w // 2, y + h // 2 + 6, lines, size)
    )


def panel(x: int, y: int, w: int, h: int, label: str, stroke: str = WARM) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" '
        f'fill="{PANEL}" stroke="{stroke}" stroke-width="4"/>'
        + text(x + w // 2, y + 34, [label], 27, 700)
    )


def marker(colour: str) -> str:
    name = colour[1:]
    return (
        f'<marker id="a{name}" viewBox="0 0 10 10" refX="8.5" refY="5" '
        f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{colour}"/></marker>'
    )


def edge(points: list[tuple[int, int]], colour: str, both: bool = False) -> str:
    route = " ".join(
        f'{"M" if i == 0 else "L"} {x} {y}' for i, (x, y) in enumerate(points)
    )
    start = f' marker-start="url(#a{colour[1:]})"' if both else ""
    return (
        f'<path d="{route}" fill="none" stroke="{colour}" stroke-width="4" '
        f'stroke-linejoin="round" stroke-linecap="round"{start} '
        f'marker-end="url(#a{colour[1:]})"/>'
    )


def render() -> str:
    shapes = [
        box(540, 20, 720, 105, ["LOCAL MODEL WORKFORCE", "Roles, tools and control boundaries"], CORAL, fill=WARM, size=31),
        panel(250, 150, 1300, 250, "1 · USER, PLANNING AND FEATURE CONTEXT"),
        box(300, 230, 260, 115, ["USER", "Feature objective", "Human authority"], CORAL, fill=WARM),
        box(620, 200, 490, 175, ["PLANNER MODEL", "Feature-bound coordination", "Clarify · decompose · approve scope"], CREAM, size=24),
        box(1170, 205, 350, 165, ["PROJECT KNOWLEDGE", "GraphRAG KB · Nuthatch", "Questions · codebase · corpus", "Token-efficient MCP retrieval"], TEAL, size=22),
        panel(500, 455, 800, 185, "2 · ROUTING"),
        box(640, 510, 520, 115, ["ROUTER / ORCHESTRATOR · HILLSTAR", "Dispatch by task complexity"], ORANGE, fill=CONTROL, size=24),
        panel(110, 700, 1580, 510, "3 · SECURE EXECUTION RUNTIME · TESTUDO / FIRECRACKER", ORANGE),
        box(180, 780, 430, 140, ["LOCAL CAPABILITIES", "Scripts · skills · tool calls", "MCP servers · hooks"], ORANGE, fill=CONTROL, size=23),
        box(680, 775, 440, 150, ["REASONING IMPLEMENTER", "Harder specified work", "May query Knowledge Base"], CREAM, size=21),
        box(1190, 770, 430, 160, ["TASK-BOUND FINE-TUNED", "IMPLEMENTER", "No direct knowledge-base access"], CREAM, size=22),
        box(500, 1010, 800, 145, ["IMPLEMENTATION", "Bounded files · tools · tests", "Hooks enforce scope and authority"], ORANGE, fill=CONTROL),
        panel(220, 1250, 1360, 390, "4 · RUBRIC-FIRST FEATURE REVIEW"),
        box(550, 1310, 700, 150, ["PRIMARY INPUT", "DoD / rubric", "Feature-scoped code and context"], ORANGE, fill=CONTROL, size=23),
        box(275, 1510, 520, 85, ["LOCAL REVIEWER MODEL"], CREAM, size=23),
        box(1005, 1510, 520, 85, ["CLOUD REVIEWER / REVIEWER PANEL"], CREAM, size=22),
        box(630, 1680, 540, 105, ["GIT WORKTREE", "Accepted change and reviewer report"], ORANGE, fill=CONTROL, size=23),
        box(665, 1825, 470, 105, ["HUMAN REVIEW", "Approve · revise · reject"], CORAL, fill=WARM, size=24),
        panel(160, 1990, 1480, 205, "5 · HARNESS-NEUTRAL LEARNING LOOP"),
        box(240, 2055, 450, 110, ["HARNESS-NEUTRAL FLYWHEEL", "Capture · attribute · route", "Construct · admit"], TEAL, size=21),
        box(755, 2060, 390, 100, ["FINE-TUNING / LoRA", "Versioned training output"], COPPER, fill=CONTROL, size=21),
        box(1210, 2060, 385, 100, ["NEXT VERSIONED", "LOCAL MODELS"], CREAM, size=21),
    ]
    arrows = [
        edge([(560, 287), (620, 287)], CORAL, True),
        edge([(1110, 287), (1170, 287)], TEAL, True),
        edge([(760, 360), (760, 425), (620, 425), (620, 567), (660, 567)], ORANGE),
        edge([(900, 625), (900, 665), (500, 665), (500, 700)], ORANGE),
        edge([(395, 920), (395, 970), (700, 970), (700, 1010)], ORANGE),
        edge([(900, 925), (900, 1010)], CREAM),
        edge([(1405, 930), (1405, 970), (1100, 970), (1100, 1010)], CREAM),
        edge([(900, 1155), (900, 1220), (500, 1220), (500, 1385), (550, 1385)], ORANGE, True),
        edge([(750, 1460), (750, 1485), (535, 1485), (535, 1510)], CREAM),
        edge([(1050, 1460), (1050, 1485), (1265, 1485), (1265, 1510)], CREAM),
        edge([(535, 1595), (535, 1645), (825, 1645), (825, 1680)], ORANGE),
        edge([(1265, 1595), (1265, 1645), (975, 1645), (975, 1680)], ORANGE),
        edge([(900, 1785), (900, 1825)], ORANGE),
        edge([(900, 1930), (900, 1960), (465, 1960), (465, 2055)], TEAL),
        edge([(690, 2110), (755, 2110)], COPPER),
        edge([(1145, 2110), (1210, 2110)], CREAM),
        # Feature-scoped Nuthatch access stays in an outside corridor.
        edge([(1520, 287), (1720, 287), (1720, 1385), (1250, 1385)], TEAL),
    ]
    defs = "".join(marker(c) for c in (CREAM, TEAL, ORANGE, CORAL, COPPER))
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
            f'<rect width="{W}" height="{H}" fill="{BG}"/>',
            f"<defs>{defs}</defs>",
            *shapes,
            *arrows,
            "</svg>",
        ]
    )


def main() -> None:
    svg = HERE / "00_workforce_overview.svg"
    png = HERE / "00_workforce_overview.png"
    html_path = HERE / "00_workforce_overview.html"
    svg_markup = render()
    svg.write_text(svg_markup, encoding="utf-8")
    html_path.write_text(
        "\n".join(
            [
                "<!doctype html>",
                '<html lang="en">',
                "<head>",
                '<meta charset="utf-8">',
                '<meta name="viewport" content="width=device-width, initial-scale=1">',
                "<title>Local Model Workforce overview</title>",
                "<style>",
                f'html,body{{margin:0;background:{BG};min-height:100%;}}',
                "main{width:max-content;min-width:100%;padding:24px;box-sizing:border-box;}",
                f"svg{{display:block;width:{W}px;height:{H}px;margin:0 auto;}}",
                "</style>",
                "</head>",
                "<body><main>",
                svg_markup,
                "</main></body>",
                "</html>",
            ]
        ),
        encoding="utf-8",
    )
    converter = shutil.which("rsvg-convert")
    if converter is None:
        raise SystemExit("rsvg-convert is required to render the PNG")
    subprocess.run([converter, "-w", "2200", str(svg), "-o", str(png)], check=True)


if __name__ == "__main__":
    main()
