#!/usr/bin/env python3
"""Render the index and the RSS feed from one list of entries.

Both outputs come from `ENTRIES`, so a new piece is added in one place and the
page and the feed cannot drift apart.

    python3 build.py
"""

from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = "https://evoclock.github.io/fieldnotes/"
TITLE = "fieldnotes"
TAGLINE = ("Writing and evidence: agent systems, models, evaluation and "
           "computational biology.")

# theme keys, ISO date, meta line, title, blurb, path, thumbnail, alt text.
# An entry may carry several themes; it then appears under each of them.
ENTRIES = [
 (["agent-systems"], "2026-07-30", "Multi-model systems · 30 July 2026",
  "Why I Started Building a Local Multi-Model Workforce, and Why the Industry May Be Heading There Too",
  "How a self-directed effort grew into a supervised multi-model architecture, a set of working products, and an emerging professional direction.",
  "articles/local-multi-model-workforce.html", "diagrams/00_workforce_overview.png",
  "Local model workforce roles, services and control boundaries"),
 (["models"], "2026-07-29", "LLM fine-tuning · 29 July 2026",
  "Building a 4B Local Implementer",
  "The task-bound Implementer, its behavioural adaptation, repeated coding evaluation, evidence flywheel and next steps.",
  "publications/project-brief.html", "publications/assets/task-type-effects-and-examples.svg",
  "Task-type effects and representative coding examples"),
 (["models", "evaluation"], "2026-07-27", "Technical report · 27 July 2026",
  "Building a 4B Local Implementer: technical report",
  "Training regime, paired evaluation across fifteen HumanEval+ runs, and what the numbers do and do not support.",
  "publications/technical-report.html", "publications/assets/humaneval-repeated-effects.svg",
  "Repeated HumanEval+ effects across paired runs"),

 (["comp-bio", "evaluation"], "2026-08-09", "Reproducibility audit · 9 August 2026",
  "Circadian ChIP-seq reproducibility audit",
  "A method reconstruction, sensitivity analysis and local ENCODE-equivalent comparison for public mouse liver circadian factor ChIP-seq. No tested condition reproduced both the deposited peak counts and the peak sets.",
  "compbio/circadian-chipseq-audit.html", "compbio/figures/peak_comparison.png",
  "Peak counts and overlap across eleven analysis conditions"),
 (["evaluation"], "2026-08-09", "Note · evaluation methodology · 9 August 2026",
  "Which model holds the seat, and what to do when it does not",
  "A leaderboard averages over the wrong axis. What matters is which model wins which seat, on what evidence, and which rung of the intervention ladder a failure points at.",
  "notes/seat-benchmarking.html", "notes/seat-benchmarking.svg",
  "Per-model failure modes, per-seat benchmarking, intervention levels"),
 (["agent-systems"], "2026-08-09", "Note · agent systems · 9 August 2026",
  "Memory management for LLM-on-corpus",
  "Parametric state, chain-of-thought, flat RAG and graph-RAG are four answers to the same question, and the partitioning algorithm separates the principled tools from the rest.",
  "notes/memory-management.html", "notes/memory-management.svg",
  "Four approaches to memory for models over a corpus"),
 (["evaluation"], "2026-08-09", "Note · running the hardware · 9 August 2026",
  "6.6W versus 35W, and a desk-scale PUE argument",
  "Sustained eval workloads are watts-bound on a desk-scale box, and the fan moving air through a hot chassis is a bigger share of that than it looks.",
  "notes/watts-per-token.html", "notes/watts-per-token.svg",
  "Desk fan at 35W against an NF-A14 industrialPPC at 6.6W"),

 (["evaluation"], "2026-07-10", "Operating manual · run 5 · 10 July 2026",
  "A reasoning manual helped a small model catch the trap",
  "On granite-4.0-h-small-FP8 the manual raised the catch rate from 8/24 to 16/24, while a same-length placebo did nothing. Small n, stated plainly.",
  "evals/fable-run5-granite.html", "evals/fable-run5-granite.svg",
  "Control 8 of 24, sham 7 of 24, manual 16 of 24"),
 (["evaluation", "models"], "2026-07-10", "CRUXEval-O · A/B · 10 July 2026",
  "The prompt is not the model",
  "Seven models over 184 output-prediction problems. The headline change is meaningless on its own, the effect is bimodal, and the real signal is the floor.",
  "evals/cruxeval-o-ab-184.html", "evals/cruxeval-o-ab-184.svg",
  "CRUXEval-O A/B across 184 problems"),
 (["evaluation"], "2026-07-08", "Capability screen · run 4 · 8 July 2026",
  "The gate opened, and the manual still moved nothing",
  "A weaker base model and a harder trap gave the manual room to show a capability effect. It did not.",
  "evals/screen_eval_run4.html", "evals/screen_eval_run4.svg",
  "Capability screen run 4 on Qwen3.6-35B"),
 (["evaluation", "models"], "2026-07-08", "CRUXEval-O · reviewer seat · 8 July 2026",
  "Seven local models on output prediction",
  "100 Python problems, graded strictly at Pass@1 and reported together with its prompt, infrastructure and harness failures.",
  "evals/cruxeval-o-results.html", "evals/cruxeval-o-results.svg",
  "CRUXEval-O results across seven local models"),
 (["evaluation"], "2026-07-07", "Capability screen · run 3 · 7 July 2026",
  "The manual moved only the labels",
  "Three arms, three tiers and twenty-seven agents, with a sham arm so a real capability effect would have had room to appear.",
  "evals/screen_eval.html", "evals/screen_eval.svg", "Capability screen run 3 on Sonnet 5"),
 (["evaluation"], "2026-07-07", "Trap battery · A/B · 7 July 2026",
  "It changed how the work was shown, not what was caught",
  "Nine traps, model held constant, one arm reading the operating manual and one not.",
  "evals/trap_eval.html", "evals/trap_eval.svg", "Trap battery A/B on Sonnet 5"),
]

THEMES = [
 ("agent-systems", "Agent systems",
  "Harnesses, gates, sandboxes, orchestration, and the products built on them."),
 ("models", "Models", "Adapting models to a job, and serving them on hardware I own."),
 ("evaluation", "Evaluation",
  "Designing a study, running it, and reporting what it did and did not show."),
 ("comp-bio", "Computational biology",
  "Circadian genomics, phenome classification, and disease modelling."),
]


def card(entry) -> str:
    _, date, meta, title, blurb, href, thumb, alt = entry
    return f"""<article class="card" data-date="{date}">
  <a class="art" href="{href}"><img src="{thumb}" alt="{html.escape(alt)}" loading="lazy"></a>
  <div class="card-body">
    <p class="meta">{meta}</p>
    <h2><a href="{href}">{html.escape(title)}</a></h2>
    <p>{html.escape(blurb)}</p>
    <p><a class="read" href="{href}">Read this piece &rarr;</a></p>
  </div>
</article>"""


def rfc822(iso: str) -> str:
    return datetime.strptime(iso, "%Y-%m-%d").replace(
        tzinfo=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")


def build_feed() -> str:
    items = []
    for e in sorted(ENTRIES, key=lambda x: x[1], reverse=True):
        themes, date, _, title, blurb, href, _, _ = e
        url = SITE + href
        cats = "".join(f"\n      <category>{t}</category>" for t in themes)
        items.append(f"""    <item>
      <title>{html.escape(title)}</title>
      <link>{url}</link>
      <guid isPermaLink="true">{url}</guid>
      <pubDate>{rfc822(date)}</pubDate>
      <description>{html.escape(blurb)}</description>{cats}
    </item>""")
    newest = max(e[1] for e in ENTRIES)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{TITLE}</title>
    <link>{SITE}</link>
    <description>{TAGLINE}</description>
    <language>en-GB</language>
    <lastBuildDate>{rfc822(newest)}</lastBuildDate>
    <atom:link href="{SITE}feed.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items)}
  </channel>
</rss>
"""


def build_index(style: str) -> str:
    sections = []
    for key, name, blurb in THEMES:
        items = sorted([e for e in ENTRIES if key in e[0]], key=lambda x: x[1], reverse=True)
        if not items:
            sections.append(f"""<details class="theme">
  <summary>{name}<span class="count">nothing published yet</span>
    <span class="blurb">{blurb}</span>
  </summary>
  <div class="grid"><p class="empty">Write-ups for this theme are in progress.</p></div>
</details>""")
            continue
        n = len(items)
        sections.append(f"""<details class="theme" open>
  <summary>{name}<span class="count">{n} {'piece' if n == 1 else 'pieces'}</span>
    <span class="blurb">{blurb}</span>
  </summary>
  <div class="grid">
{chr(10).join(card(e) for e in items)}
  </div>
</details>""")

    latest = "\n".join(card(e) for e in sorted(ENTRIES, key=lambda x: x[1], reverse=True))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{TAGLINE}">
<title>{TITLE} | Writing and evidence</title>
<link rel="alternate" type="application/rss+xml" title="{TITLE}" href="feed.xml">
{style}
</head>
<body>
<main>
  <header>
    <div class="brand">
      <img src="assets/logo.png" alt="Origami hummingbird in sentoku" width="92" height="92">
      <div>
        <p class="eyebrow">Agent systems &middot; models &middot; evaluation</p>
        <h1>{TITLE}</h1>
      </div>
    </div>
    <p class="intro">{TAGLINE} An entry can belong to more than one theme, so
    some appear twice.</p>
  </header>

  <div class="toolbar">
    <span>View</span>
    <button type="button" id="view-theme" aria-pressed="true">By theme</button>
    <button type="button" id="view-date" aria-pressed="false">Latest first</button>
  </div>

{chr(10).join(sections)}

  <section class="grid" id="latest" aria-label="All pieces, most recent first">
{latest}
  </section>

  <footer>
    <p>Built and maintained by
    <a href="https://github.com/evoclock">Julen Gamboa</a>.
    Source is in the <a href="https://github.com/evoclock/fieldnotes">public
    repository</a>. New pieces appear in the
    <a href="feed.xml">RSS feed</a>.</p>
  </footer>
</main>
<script>
(function () {{
  var byTheme = document.getElementById("view-theme");
  var byDate = document.getElementById("view-date");
  function show(dateFirst) {{
    document.body.classList.toggle("by-date", dateFirst);
    byTheme.setAttribute("aria-pressed", String(!dateFirst));
    byDate.setAttribute("aria-pressed", String(dateFirst));
    try {{ localStorage.setItem("fn-view", dateFirst ? "date" : "theme"); }} catch (e) {{}}
  }}
  byTheme.addEventListener("click", function () {{ show(false); }});
  byDate.addEventListener("click", function () {{ show(true); }});
  try {{ if (localStorage.getItem("fn-view") === "date") show(true); }} catch (e) {{}}
}})();
</script>
</body>
</html>
"""


def main() -> None:
    style = re.search(r"<style>.*?</style>", (HERE / "index.html").read_text(), re.S).group(0)
    (HERE / "index.html").write_text(build_index(style), encoding="utf-8")
    (HERE / "feed.xml").write_text(build_feed(), encoding="utf-8")
    print(f"  index.html  {len(ENTRIES)} entries")
    print(f"  feed.xml    {len(ENTRIES)} items")


if __name__ == "__main__":
    main()
