"""Public-page regressions; no dependency on the private editorial review folder."""
import html
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build
from evals import thumbnails

# Original URLs and dates, with the owner-approved titles.
REVISIONS = [
    ('notes/seat-benchmarking.html', 'Which local model is right for the job?', '2026-08-09'),
    ('notes/memory-management.html', 'Where should an agent keep its memory?', '2026-08-09'),
    ('notes/watts-per-token.html', 'Is cooling part of the inference budget?', '2026-08-09'),
    ('articles/local-multi-model-workforce.html', 'Why I started building a local model workforce', '2026-07-30'),
    ('publications/project-brief.html', 'Teaching a 4B model how I work', '2026-07-29'),
    ('publications/technical-report.html', 'Teaching a 4B model how I work: the technical report', '2026-07-27'),
    ('evals/fable-run5-granite.html', 'Can a reasoning manual give your small models a capability uplift?', '2026-07-10'),
    ('evals/cruxeval-o-ab-184.html', 'A better prompt is not a better model', '2026-07-10'),
    ('evals/screen_eval_run4.html', 'Does the reasoning manual help Qwen catch mistakes?', '2026-07-08'),
    ('evals/cruxeval-o-results.html', 'Can local models work out what Python code returns?', '2026-07-08'),
    ('evals/screen_eval.html', "Does a reasoning manual improve how Anthropic's Sonnet tackles error detection?", '2026-07-07'),
    ('evals/trap_eval.html', 'The reasoning manual changed the explanation, not the outcome', '2026-07-07'),
]


class EditorialRefreshTests(unittest.TestCase):
    def test_public_metadata_and_unchanged_feed_identity(self):
        items = {item.findtext('guid'): item for item in ET.parse(ROOT / 'feed.xml').findall('channel/item')}
        index = (ROOT / 'index.html').read_text()
        for path, title, date in REVISIONS:
            with self.subTest(page=path):
                entries = [e for e in build.ENTRIES if e[5] == path]
                self.assertEqual(len(entries), 1)
                self.assertEqual((entries[0][3], entries[0][1]), (title, date))
                page = (ROOT / path).read_text()
                self.assertEqual(html.unescape(re.search(r'<title>(.*?)</title>', page, re.S)[1]), title)
                self.assertIn(f'<link rel="canonical" href="{build.SITE}{path}">', page)
                self.assertIn(html.escape(title), index)
                item = items[build.SITE + path]
                self.assertEqual(item.findtext('title'), title)
                self.assertEqual(item.findtext('pubDate'), build.rfc822(date))
        self.assertEqual((ROOT / 'feed.xml').read_text(), build.build_feed())

    def test_reader_pages_have_no_review_framing_or_missing_assets(self):
        for path, _, _ in REVISIONS:
            with self.subTest(page=path):
                page = (ROOT / path).read_text()
                self.assertNotIn('noindex', page)
                self.assertNotIn('Editorial review copy', page)
                self.assertNotIn('review/voice-alignment', page)
                self.assertNotIn('class="generated"', page)
                self.assertIn('class="fieldnote-page"', page)
                self.assertIn('../assets/fieldnote.css', page)
                self.assertIn('../assets/tables.js', page)
                self.assertEqual(page.count('<h2>One-line takeaway</h2>'), 1)
                for value in re.findall(r'(?:href|src)=["\']([^"\']+)["\']', page):
                    link = urlsplit(html.unescape(value))
                    if link.path and not link.scheme and not link.netloc and not value.startswith('/'):
                        self.assertTrue((ROOT / path).parent.joinpath(unquote(link.path)).exists(), value)

    def test_circadian_fieldnote_and_diagrams_are_public_and_complete(self):
        path = 'articles/60-percent-of-the-time-it-works-every-time.html'
        page = (ROOT / path).read_text()
        feed = ET.parse(ROOT / 'feed.xml')
        self.assertEqual(sum(e[5] == path for e in build.ENTRIES), 1)
        self.assertIsNotNone(next((item for item in feed.findall('channel/item')
                                   if item.findtext('link') == build.SITE + path), None))
        self.assertIn(path, (ROOT / 'index.html').read_text())
        self.assertIn(f'<link rel="canonical" href="{build.SITE}{path}">', page)
        self.assertNotIn('noindex', page)
        self.assertNotIn('../.scratch/', page)
        self.assertEqual(page.count('class="pipeline-disclosure"'), 2)
        self.assertIn('When they are not, no amount of compute will solve that problem.',
                      ' '.join(page.split()))
        self.assertNotIn('Circadian-ChIP-seq-reproducibility-audit', page)
        for value in re.findall(r'(?:href|src)="([^"]+)"', page):
            link = urlsplit(html.unescape(value))
            if link.path and not link.scheme and not link.netloc and not value.startswith('/'):
                self.assertTrue((ROOT / path).parent.joinpath(unquote(link.path)).exists(), value)
        for name in ('encode-replicated', 'encode-unreplicated'):
            self.assertTrue((ROOT / f'articles/circadian-diagrams/{name}.bower.json').is_file())
            self.assertTrue((ROOT / f'articles/circadian-diagrams/exports/{name}.html').is_file())
            self.assertTrue((ROOT / f'articles/circadian-diagrams/exports/{name}.light.svg').is_file())

    def test_thumbnails_use_complete_current_metadata_and_reproduce_exactly(self):
        namespace = {'svg': 'http://www.w3.org/2000/svg'}
        for path, title, _ in REVISIONS:
            with self.subTest(page=path):
                entry = next(e for e in build.ENTRIES if e[5] == path)
                self.assertEqual(entry[6], f'assets/thumbnails/{Path(path).stem}.svg')
                source = (ROOT / entry[6]).read_text()
                svg = ET.fromstring(source)
                self.assertEqual(svg.findtext('svg:title', namespaces=namespace), title)
                self.assertEqual(svg.findtext('svg:desc', namespaces=namespace), entry[4])
                headline = svg.find('svg:text[@class="headline"]', namespace)
                self.assertEqual(' '.join(headline.itertext()), title)
                self.assertEqual(source, thumbnails.card(entry))

    def test_homepage_tagline_has_no_artificial_width_cap(self):
        page = (ROOT / 'index.html').read_text()
        for selector in ('header', r'\.intro'):
            rule = re.search(selector + r'\s*\{(.*?)\}', page, re.S)[1]
            self.assertIn('max-width: none;', rule)
            self.assertNotIn('white-space: nowrap', rule)

    def test_thumbnail_counts_and_power_ratings_stay_explicit(self):
        granite = (ROOT / 'assets/thumbnails/fable-run5-granite.svg').read_text()
        for label in ('control 8/24', 'sham 7/24', 'manual 16/24'):
            self.assertIn(label, granite)
        cooling = (ROOT / 'assets/thumbnails/watts-per-token.svg').read_text()
        self.assertIn('desk fan 35 W', cooling)
        self.assertIn('NF-A14 iPPC 6.6 W', cooling)
        self.assertIn('not a matched-airflow test', cooling)

    def test_cruxeval_scorecards_keep_the_original_values_attached_to_labels(self):
        page = (ROOT / 'evals/cruxeval-o-ab-184.html').read_text()
        expected = {
            'card-super-120b': ['174/184', '179/184', '+5', '7', '2', '3', '172'],
            'card-nemotron-30b': ['157/184', '158/184', '+1', '11', '10', '16', '147'],
            'card-gemma-4-26b': ['176/184', '161/184', '-15', '2', '17', '6', '159'],
            'card-ornith-fp8': ['168/184', '168/184', '0', '7', '7', '9', '161'],
            'card-holo-3.1-35b': ['88/184', '141/184', '+53', '54', '1', '42', '87'],
            'card-qwen3.6-35b': ['163/184', '149/184', '-14', '9', '23', '12', '140'],
            'card-granite-small': ['75/184', '120/184', '+45', '55', '10', '54', '65'],
        }
        heads = re.findall(r'<div class="card" id="([^"]+)"><div class="card-head scorecard-head">(.*?)</div><div class="card-body"', page, re.S)
        self.assertEqual({ident for ident, _ in heads}, set(expected))
        for ident, head in heads:
            with self.subTest(model=ident):
                self.assertEqual(re.findall(r'<dt>(.*?)</dt>', head), ['Baseline', 'Mitigated', 'Change', 'Fixed', 'Broken', 'Wrong under both', 'Both right'])
                values = [re.sub(r'\s+', '', re.sub(r'<[^>]*>', '', value)) for value in re.findall(r'<dd(?: class="[^"]+")?>(.*?)</dd>', head)]
                self.assertEqual(values, expected[ident])
                self.assertNotIn('card-idsub', head)
                self.assertIn(f'aria-controls="{ident}-problems"', head)
                self.assertIn('aria-expanded="false"', head)


if __name__ == '__main__':
    unittest.main()
