"""Tests for screen.py, the presence-only publish screen.

Every credential-shaped string in this file is synthetic: it matches a
pattern structurally (prefix, length, alphabet) but was generated for these
tests and is not a credential. The screen itself never prints values, so the
tests also assert that synthetic fixtures do not leak into the report.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import screen


# Synthetic fixtures: structurally valid, not credentials. The "0" payload
# appears nowhere in real tokens and makes the fake obvious on inspection.
SYNTHETIC_HITS = [
    ("github-token", "ghp_" + "0" * 36),
    ("gitlab-token", "glpat-" + "0" * 20),
    ("aws-access-key", "AKIA" + "0" * 16),
    ("google-api-key", "AIza" + "0" * 35),
    ("slack-token", "xoxb-" + "0" * 24),
    ("anthropic-key", "sk-ant-" + "0" * 24),
    ("private-key-block", "-----BEGIN OPENSSH PRIVATE KEY-----"),
    ("jwt", "eyJ" + "0" * 8 + "." + "0" * 8 + "." + "0" * 5),
    ("bearer-value", "Authorization: Bearer " + "a" * 24),
    # Line-anchored, as copied .env/terminal lines are.
    ("credential-assignment", "api_key: " + "b" * 16),
]

# Mid-line mentions stay unflagged: assignments are only screened at the
# start of a line, where copied .env or terminal output puts them.
MIDLINE_ASSIGNMENT = f"the config uses api_key: {'b' * 16} inline"

CLEAN_TEXT = """\
Working notes on tokens. The pipeline burns tokens; the screen run had a
trap battery. `api_key = $FROM_ENV` and `token: REDACTED` and
`password = <your-password-here>` are placeholders, not values.
No terminal transcript here carries a secret.
"""


class PatternTests(unittest.TestCase):
    def test_synthetic_values_are_detected(self):
        for expected_name, value in SYNTHETIC_HITS:
            with self.subTest(pattern=expected_name):
                findings = screen.screen_text(f"prefix\n{value}\nsuffix")
                self.assertIn(expected_name, [name for _, name in findings])

    def test_midline_assignment_not_flagged(self):
        self.assertEqual(screen.screen_text(MIDLINE_ASSIGNMENT), [])

    def test_clean_prose_passes(self):
        self.assertEqual(screen.screen_text(CLEAN_TEXT), [])

    def test_empty_text_passes(self):
        self.assertEqual(screen.screen_text(""), [])


class ArtifactSelectionTests(unittest.TestCase):
    def test_text_artifacts_included_code_and_fixtures_excluded(self):
        artifacts = {p.name for p in screen.find_artifacts(ROOT)}
        self.assertIn("index.html", artifacts)
        self.assertIn("feed.xml", artifacts)
        self.assertNotIn("build.py", artifacts)
        self.assertNotIn("test_screen_publish.py", artifacts)

    def test_single_file_root(self):
        target = ROOT / "index.html"
        self.assertEqual(screen.find_artifacts(target), [target])


class CliTests(unittest.TestCase):
    def _run(self, *argv):
        import contextlib
        import io
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = screen.main(list(argv))
        return code, out.getvalue()

    def test_dirty_temp_dir_exits_one_and_never_shows_value(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            dirty = Path(tmp) / "article.html"
            secret = "ghp_" + "0" * 36
            dirty.write_text(f"<p>see {secret}</p>\n", encoding="utf-8")
            (Path(tmp) / "clean.md").write_text("plain\n", encoding="utf-8")
            code, report = self._run("--paths", dirty.parent)
        self.assertEqual(code, 1)
        self.assertIn("github-token", report)
        self.assertIn("article.html:1", report)
        self.assertNotIn(secret, report)          # presence-only, no value

    def test_clean_temp_dir_exits_zero(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "note.md").write_text("no secrets here\n",
                                               encoding="utf-8")
            code, report = self._run("--paths", tmp)
        self.assertEqual(code, 0)
        self.assertIn("0 findings", report)

    def test_missing_path_exits_two(self):
        code, _ = self._run("--paths", "no/such/path")
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
