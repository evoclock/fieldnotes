import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import build


class QwenFieldnoteTests(unittest.TestCase):
    def test_canonical_entry_and_projections(self):
        title = "Wrangling Qwen's Long Thinking Runs"
        href = "articles/wrangling-qwens-long-thinking-runs.html"

        entries = [entry for entry in build.ENTRIES if entry[3] == title]
        self.assertEqual(len(entries), 1)

        themes, date, meta, _, blurb, entry_href, thumb, _ = entries[0]
        self.assertEqual(themes, ["models", "agent-systems"])
        self.assertEqual(date, "2026-08-26")
        self.assertEqual(entry_href, href)
        self.assertIn("manage Qwen", blurb)
        self.assertTrue((ROOT / entry_href).is_file())
        self.assertTrue((ROOT / thumb).is_file())

        for projection in ("index.html", "feed.xml"):
            self.assertIn(href, (ROOT / projection).read_text())


if __name__ == "__main__":
    unittest.main()
