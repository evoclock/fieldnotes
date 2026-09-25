<p align="center">
  <img src="assets/logo.png" alt="Origami hummingbird in sentoku" width="140">
</p>

# fieldnotes

Writing and evidence: agent systems, models, evaluation and computational
biology.

Published at <https://evoclock.github.io/fieldnotes/>.

## Layout

| Path | What |
|---|---|
| `index.html` | the index, grouped by theme with a latest-first view |
| `articles/` | long-form pieces |
| `publications/` | project briefs, technical reports and slides |
| `evals/` | evaluation write-ups, and the script that renders their thumbnails |
| `diagrams/` | figures, with the sources that generate them |
| `assets/` | the marks, in three copper alloys: sentoku, shibuichi and yamagane |

Thumbnails and diagrams are generated rather than drawn by hand. Regenerate
them with:

```bash
python3 evals/thumbnails.py
python3 diagrams/00_workforce_overview.py
```

## Screening before publishing

`screen.py` is a publication-time gate over the outputs this site publishes:
articles, notes and eval pages, the generated `index.html` and `feed.xml`,
and the text-carrying figures. Run it before a push:

```bash
python3 screen.py
```

It is **presence-only**. A finding names the file, the line and the pattern
(`github-token`, `aws-access-key`, `private-key-block`, `credential-assignment`
and other high-signal shapes); it never prints, keeps or transmits the
matched value, reads no credential store or environment, and contacts no
service. The patterns are structural — prefix, length, alphabet — and not
derived from any real credential. A non-zero exit means: stop, open the file
yourself, and redact at the source (the terminal capture, the transcript, the
screenshot) rather than in the artifact.

Scope limits, stated plainly:

- **Screenshots and other binaries** (the PNGs under `articles/source_assets/`)
  are outside value screening: matching what pixels spell needs OCR, which is
  a different and heavier tool. Cover them at capture time — a clean prompt,
`history -c`, no exported secrets in the shell — and review them by eye.
- **Source code is not scanned.** Publishing artifacts are; `tests/` is
  excluded because its fixtures carry synthetic pattern-shaped fakes by
design.
- The screen catches *shapes*, not intent. It can miss a value whose format
  nobody has a pattern for, and it is not a substitute for not putting the
  secret on screen in the first place.

### Credential stores, present and future

The screen deliberately has **no credential-store integration**, and this
repository invents no provider support. Notes for the platforms this work may
reach:

- **Linux headless stores** (`pass`, `secret-tool`/libsecret, `keyctl`): a
  publication screen that loaded entries to compare against would itself be a
  leak channel. Presence-only pattern matching stays on the artifact side and
  needs no store access; keep it that way.
- **CI secret-provider adapters** (OIDC vault injections, masked-variable
  systems): masks are scoped to logs, not to files a job writes. If this repo
gains CI, `python3 screen.py` belongs in the pipeline *after* artifacts are
rendered and *before* they are published, with no secrets mounted at all.
- **Windows Credential Manager / DPAPI**: DPAPI-encrypted blobs are
  per-user/per-machine; a cross-platform screen cannot and should not touch
  them. Values only ever reach an artifact by being typed, pasted or captured
  — which is exactly the point the patterns watch.
- **A shared credential-store library policy** would be the right home for
  pattern definitions if more repositories adopt this gate: one reviewed list,
  presence-only semantics, and an absolute rule that the library never reads,
  returns or sends values — only names and positions.

