import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "informational_page_validator", ROOT / "scripts" / "validate-informational-page.py"
)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validator)


class InformationalPageValidatorTests(unittest.TestCase):
    def write_page(self, extra: str = "") -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "page.html"
        path.write_text(
            """<!doctype html><html><head>
<meta name="levnytt-template" content="informational-article-v1">
<meta name="levnytt-cta" content="none">
<link rel="stylesheet" href="/assets/css/levnytt-foundations.css">
<link rel="stylesheet" href="/assets/css/informational-article.css">
</head><body><div id="site-nav"></div><script src="/nav.js"></script>
<article class="ia-wrap">Test</article><script src="/footer.js"></script>""" + extra + "</body></html>",
            encoding="utf-8",
        )
        return path

    def test_accepts_complete_informational_shell(self):
        self.assertEqual([], validator.validate(self.write_page()))

    def test_rejects_literal_brand_color(self):
        self.assertIn("unapproved literal brand color in template: #1B4332", validator.validate(self.write_page("#1B4332")))

    def test_requires_disclosure_for_referral_cta(self):
        path = self.write_page().read_text(encoding="utf-8").replace('content="none"', 'content="affiliate-referral"')
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "page.html"
            target.write_text(path, encoding="utf-8")
            self.assertIn("referral CTA requires disclosure metadata", validator.validate(target))


if __name__ == "__main__":
    unittest.main()
