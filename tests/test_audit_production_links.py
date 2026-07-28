import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("link_audit", ROOT / "scripts" / "audit-production-links.py")
audit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(audit)


class LinkAuditTests(unittest.TestCase):
    def test_shared_component_requires_new_tab_and_safe_rel(self):
        source = '<a href="/inside" target="_blank" rel="noopener noreferrer">Inside</a><a href="https://example.test" target="_blank" rel="noopener noreferrer">External</a>'
        result = audit.audit_shared_component(source, "fixture")
        self.assertEqual(2, result["link_count"])
        self.assertEqual([], result["issues"])

    def test_shared_component_rejects_missing_policy(self):
        result = audit.audit_shared_component('<a href="/inside">Inside</a>', "fixture")
        self.assertEqual({"shared_navigation_link_missing_new_tab", "shared_navigation_link_missing_safe_rel"}, {item["issue"] for item in result["issues"]})

    def test_real_shared_components_follow_policy(self):
        report = audit.run(ROOT, fix=False)
        self.assertEqual([], [item for component in report["shared_components"] for item in component["issues"]])

    def test_internal_absolute_link_is_same_tab_and_root_relative(self):
        findings = []
        match = audit.ANCHOR_RE.search('<a href="https://levnytt.se/guide" target="_blank" rel="noopener noreferrer">')
        result = audit.transform_tag(match, Path("."), {"/guide": "/guide.html"}, {}, findings, True)
        self.assertIn('href="/guide"', result)
        self.assertNotIn('target=', result)
        self.assertIn("internal_new_tab", findings[0]["issues"])

    def test_external_new_tab_preserves_sponsored_and_adds_safe_tokens(self):
        findings = []
        match = audit.ANCHOR_RE.search('<a href="https://example.org" target="_blank" rel="sponsored">')
        result = audit.transform_tag(match, Path("."), {}, {}, findings, True)
        self.assertIn('rel="noopener noreferrer sponsored"', result)

    def test_unknown_local_target_is_not_rewritten_to_a_guess(self):
        findings = []
        match = audit.ANCHOR_RE.search('<a href="/missing">')
        result = audit.transform_tag(match, Path("."), {}, {}, findings, True)
        self.assertIn('href="/missing"', result)
        self.assertIn("missing_local_target", findings[0]["issues"])


if __name__ == "__main__":
    unittest.main()
