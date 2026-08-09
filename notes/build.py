#!/usr/bin/env python3
"""Render short notes as standalone pages, in the site palette.

A note is a piece with an argument but not much length. Rather than pad one
into an article, it gets its own page and is labelled as a note so nobody
arrives expecting more than is there.

No dependencies. Run from anywhere:

    python3 notes/build.py
"""

from __future__ import annotations

import html
from pathlib import Path

HERE = Path(__file__).resolve().parent

COAL, PANEL, PAPER = "#151719", "#222629", "#f0f2f1"
MUTED, ORANGE, SAGE, TEAL = "#b8c0bd", "#e77843", "#79c39e", "#3fbec1"

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{description}">
<title>{title}</title>
<style>
:root {{
  --coal: {coal};
  --panel: {panel};
  --paper: {paper};
  --muted: {muted};
  --orange: {orange};
  --sage: {sage};
  --teal: {teal};
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  min-height: 100vh;
  background:
    radial-gradient(circle at 15% 0%, rgba(63,190,193,.12), transparent 34rem),
    var(--coal);
  color: var(--muted);
  font: 18px/1.65 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
main {{
  width: min(720px, calc(100% - 2rem));
  margin: 0 auto;
  padding: 4rem 0 5rem;
}}
.eyebrow {{
  color: var(--sage);
  font-size: .78rem;
  font-weight: 800;
  letter-spacing: .11em;
  text-transform: uppercase;
}}
h1 {{
  margin: .4rem 0 .5rem;
  color: var(--paper);
  font-size: clamp(1.9rem, 4vw, 2.7rem);
  line-height: 1.12;
}}
.byline {{ color: var(--muted); font-size: .95rem; margin: 0 0 2.2rem; }}
h2 {{ color: var(--paper); font-size: 1.3rem; margin: 2.2rem 0 .6rem; }}
p {{ margin: 0 0 1.1rem; }}
ul {{ margin: 0 0 1.2rem; padding-left: 1.2rem; }}
li {{ margin: 0 0 .7rem; }}
strong {{ color: var(--paper); }}
a {{ color: var(--sage); }}
a:hover {{ color: var(--teal); }}
code {{
  padding: .1rem .35rem;
  border-radius: 4px;
  background: var(--panel);
  font-size: .92em;
}}
.back {{
  display: inline-block;
  margin-bottom: 2.5rem;
  color: var(--orange);
  font-weight: 800;
  text-decoration: none;
}}
footer {{
  margin-top: 3rem;
  padding-top: 1.2rem;
  border-top: 1px solid rgba(240,242,241,.14);
  font-size: .95rem;
}}
</style>
</head>
<body>
<main>
  <a class="back" href="../index.html">&larr; fieldnotes</a>
  <p class="eyebrow">Note &middot; {eyebrow}</p>
  <h1>{heading}</h1>
  <p class="byline">Julen Gamboa &middot; {date}</p>
{body}
  <footer>
    <p>A note rather than an article: an argument worth writing down, without
    the length to justify more.</p>
  </footer>
</main>
</body>
</html>
"""

NOTES = {
    "seat-benchmarking": dict(
        title="Which model holds the seat",
        heading="Which model holds the seat, and what to do when it does not",
        eyebrow="Evaluation methodology",
        date="9 August 2026",
        description="A leaderboard averages over the wrong axis. What I want to "
        "know is which model wins which seat, on what evidence, and which rung "
        "of the intervention ladder a failure points at.",
        body="""
  <p>A DGX Spark at home, more ideas than time, and one use case pulling harder
  than the others. The question I keep coming back to is not which model is
  generally smarter. It is which model holds the <em>seat</em> I need it to
  hold, and what I do when it does not.</p>

  <p>That decomposes into three things I want a battery to actually
  measure.</p>

  <ul>
    <li><strong>Per-model failure modes.</strong> What does this model get
    wrong, and under what conditions? Authority pressure, buried ledes,
    re-derivation, drift over a long context. The things a leaderboard score
    does not surface.</li>
    <li><strong>Per-seat benchmarking.</strong> Different roles in an agentic
    setup, planner, retriever, executor, critic, need different strengths. A
    general benchmark averages over the wrong axis. I want to know which model
    wins which seat, and on what evidence.</li>
    <li><strong>Intervention levels.</strong> When a model fails, the fix lives
    at one of several levels: fine-tuning, harness engineering, prompt and
    context distillation, or OPRO and promptbreeding-style search. Different
    failures want different fixes, and conflating them is the expensive
    mistake.</li>
  </ul>

  <h2>What I want from a benchmark</h2>

  <ul>
    <li>A pass or fail signal on the thing the model is actually being asked to
    do, not a composite score.</li>
    <li>A way to see which failure mode fired, not just that it failed.</li>
    <li>A methodology that points at which rung of the intervention ladder the
    result wants, based on what the eval surfaced rather than what was assumed
    going in.</li>
  </ul>
""",
    ),
    "memory-management": dict(
        title="Memory management for LLM-on-corpus",
        heading="Memory management for LLM-on-corpus",
        eyebrow="Agent systems",
        date="9 August 2026",
        description="Parametric state, chain-of-thought, flat RAG and graph-RAG "
        "are four different answers to the same question, and the partitioning "
        "algorithm is what separates the principled tools from the rest.",
        body="""
  <p>Not an exhaustive list, but these are the areas I have been experimenting
  on or validating against.</p>

  <ul>
    <li><strong>Parametric.</strong> Mamba, SSMs and Jamba hybrids
    (<a href="https://arxiv.org/abs/2312.00752">Gu and Dao, 2023</a>) compress
    context into a bounded recurrent state during inference. Deterministic for a
    given input, ephemeral across calls.</li>
    <li><strong>Chain-of-thought.</strong> The model's own scratchpad. It pays
    tokens for working memory on every call, which is poor return for the cost
    and the overhead.</li>
    <li><strong>External flat RAG.</strong> Vector similarity and BM25. Memory
    lives in an index, freshness wins, and recall is bounded by embedding
    quality.</li>
    <li><strong>Graph-RAG.</strong> The same external memory with structure:
    nodes, edges, communities. The partitioning algorithm is what separates the
    principled tools from the embedding-only ones. Microsoft's GraphRAG uses
    <a href="https://arxiv.org/abs/2404.16130">Leiden community detection</a>;
    <a href="https://github.com/evoclock/nuthatch">nuthatch</a> is the
    SBM-based entry in this space.</li>
  </ul>

  <p>Worth saying why frontier labs might not be in a hurry to solve this. The
  more rounds it takes to solve a problem, the more tokens get burned, and that
  is ultimately in their commercial interest.</p>
""",
    ),
    "watts-per-token": dict(
        title="Watts per token, at desk scale",
        heading="6.6W versus 35W, and a desk-scale PUE argument",
        eyebrow="Running the hardware",
        date="9 August 2026",
        description="Sustained eval workloads are watts-bound on a desk-scale "
        "box, and the fan you use to move air through a hot chassis is a bigger "
        "share of that than it looks.",
        body="""
  <p>Sustained eval workloads are watts-bound on a desk-scale box. Not
  thermally bound, though that comes into it, but bound by what the whole
  machine draws to keep producing tokens for hours.</p>

  <p>An external Noctua NF-A14 industrialPPC-3000 draws 6.6W to move air
  through a hot chassis. A desk fan pulls around 35W to move roughly the same
  air. That difference runs for the entire length of every eval, so it lands in
  watts per token rather than in a peak figure nobody measures.</p>

  <p>It saves on power and it prolongs the hardware, but the watts-per-token
  argument is the one that matters. It is the same reasoning behind power usage
  effectiveness in a datacenter, applied at the scale of one desk: the useful
  work is the tokens, and everything else spent keeping the box able to produce
  them is overhead worth measuring.</p>
""",
    ),
}


def main() -> None:
    for slug, note in NOTES.items():
        page = PAGE.format(
            coal=COAL, panel=PANEL, paper=PAPER, muted=MUTED,
            orange=ORANGE, sage=SAGE, teal=TEAL,
            title=html.escape(note["title"]),
            heading=html.escape(note["heading"]),
            eyebrow=html.escape(note["eyebrow"]),
            date=note["date"],
            description=html.escape(note["description"]),
            body=note["body"],
        )
        (HERE / f"{slug}.html").write_text(page, encoding="utf-8")
        print(f"  wrote {slug}.html")


if __name__ == "__main__":
    main()
