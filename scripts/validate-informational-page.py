#!/usr/bin/env python3
"""Fail-fast structural guard for the LevNytt Informational Article v1 template."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ALLOWED_TEMPLATES = {"rebuild-informational-article"}
CTA_VALUES = {"none", "internal", "product-referral", "affiliate-referral", "existing-content-cta"}
LITERAL_BRAND_COLORS = ("#1B4332", "#E8C870", "#C9A84C", "#F9F6EF")


def meta(html: str, name: str) -> str | None:
    match = re.search(rf'<meta\s+name=["\']{re.escape(name)}["\']\s+content=["\']([^"\']+)["\']', html, re.I)
    return match.group(1) if match else None


def validate(path: Path) -> list[str]:
    html = path.read_text(encoding="utf-8")
    errors: list[str] = []
    template = meta(html, "levnytt-template")
    if template not in ALLOWED_TEMPLATES:
        errors.append("template must be rebuild-informational-article")
    for required in ('/assets/css/levnytt-foundations.css', '/assets/css/levnytt-components.css', '/assets/css/levnytt-rebuild.css', '/assets/css/informational-article.css', 'class="ln-site-header"', 'class="ln-site-footer"'):
        if required not in html:
            errors.append(f"missing shared shell requirement: {required}")
    for color in LITERAL_BRAND_COLORS:
        if color.lower() in html.lower():
            errors.append(f"unapproved literal brand color in template: {color}")
    if re.search(r"<style\b|\sstyle=|\son\w+=", html, re.I):
        errors.append("inline code is not allowed")
    cta = meta(html, "levnytt-cta")
    if cta not in CTA_VALUES:
        errors.append("CTA behavior is missing or unclassified")
    if cta in {"product-referral", "affiliate-referral"}:
        if not meta(html, "levnytt-disclosure"):
            errors.append("referral CTA requires disclosure metadata")
        if 'ia-disclosure' not in html:
            errors.append("referral CTA requires visible disclosure block")
    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: validate-informational-page.py <page.html> [...]")
        return 2
    failed = False
    for value in sys.argv[1:]:
        path = Path(value)
        if not path.is_file():
            print(f"FAIL {path}: file not found")
            failed = True
            continue
        errors = validate(path)
        if errors:
            print(f"FAIL {path}: " + "; ".join(errors))
            failed = True
        else:
            print(f"PASS {path}: informational-article-v1")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
