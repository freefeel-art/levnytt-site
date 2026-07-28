import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("ui_audit", ROOT / "scripts" / "audit-production-ui.py")
audit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(audit)


class ProductionUiAuditTests(unittest.TestCase):
    def test_known_template_set_is_explicit(self):
        self.assertIn("rebuild-informational-article", audit.KNOWN_TEMPLATES)
        self.assertIn("rebuild-authority-editorial-trust", audit.KNOWN_TEMPLATES)

    def test_card_registry_classifies_shared_card(self):
        self.assertIn("article-card", audit.load_cards(ROOT))

    def test_production_inventory_has_no_contract_failures(self):
        report = audit.audit(ROOT)
        self.assertEqual([], report["failures"])
        self.assertEqual([], report["shared_style_literal_color_violations"])
        self.assertTrue(all(page["h1_count"] == 1 for page in report["pages"]))
        self.assertTrue(all(not page["missing_local_images"] for page in report["pages"]))


if __name__ == "__main__":
    unittest.main()
