#!/usr/bin/env python3
"""Deterministic UI, metadata and asset audit of actual public files."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
META_RE = re.compile(r'<meta\s+(?:name|property)=["\'](?P<name>[^"\']+)["\']\s+content=["\'](?P<value>[^"\']*)["\']', re.I)
CLASS_RE = re.compile(r'class=["\'](?P<value>[^"\']+)["\']', re.I)
H1_RE = re.compile(r'<h1\b', re.I)
IMAGE_RE = re.compile(r'<img\b[^>]*\bsrc=["\'](?P<src>[^"\']+)', re.I)
JSONLD_RE = re.compile(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script\s*>', re.I | re.S)
KNOWN_TEMPLATES = {"rebuild-home-editorial-hub", "rebuild-library-category-index", "rebuild-utility-legal", "rebuild-authority-editorial-trust", "rebuild-product-category", "rebuild-informational-article"}
CANONICAL_COLOR_LITERALS = {"#1b4332", "#e8c870", "#c9a84c", "#f9f6ef", "#ddd8ce"}
SHARED_STYLE_FILES = ("assets/css/levnytt-components.css", "assets/css/authority-trust.css")


def _rebuild(root: Path):
    spec = importlib.util.spec_from_file_location("levnytt_rebuild_ui", root / "scripts/rebuild-production.py")
    module = importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(module); return module


def production_pages(root: Path):
    yield from _rebuild(root).sitemap_routes(root)
    if (root / "404.html").is_file(): yield "https://levnytt.se/404", root / "404.html"


def inferred_family(file: Path, metadata: dict[str, str]) -> str:
    value = metadata.get("levnytt-template", "")
    return value.removeprefix("rebuild-") if value in KNOWN_TEMPLATES else "unknown"


def load_cards(root: Path) -> set[str]:
    value = json.loads((root / "config/ui-card-classification.json").read_text(encoding="utf-8")); result = set(value.get("supporting_classes", []))
    for members in value.get("variants", {}).values(): result.update(members)
    return result


def missing_local_images(root: Path, file: Path, source: str) -> list[str]:
    missing = []
    for match in IMAGE_RE.finditer(source):
        src = match.group("src")
        if src.startswith(("http:", "https:", "data:")): continue
        candidate = root / src.lstrip("/") if src.startswith("/") else file.parent / src
        if not candidate.is_file(): missing.append(src)
    return sorted(set(missing))


def jsonld_errors(source: str) -> list[str]:
    errors = []
    for index, raw in enumerate(JSONLD_RE.findall(source), 1):
        try: json.loads(raw)
        except json.JSONDecodeError as error: errors.append(f"schema_{index}:{error.msg}")
    if not JSONLD_RE.search(source): errors.append("missing_jsonld")
    return errors


def audit(root: Path) -> dict:
    allowed_cards = load_cards(root); records = []; failures = []; families: Counter[str] = Counter(); titles: Counter[str] = Counter(); canonicals: Counter[str] = Counter()
    for url, file in production_pages(root):
        source = file.read_text(encoding="utf-8"); metadata = {m.group("name").lower(): m.group("value") for m in META_RE.finditer(source)}; family = inferred_family(file, metadata); families[family] += 1
        title_match = re.search(r"<title>(.*?)</title>", source, re.I | re.S); title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip() if title_match else ""; titles[title] += 1
        canonical_match = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)', source, re.I); canonical = canonical_match.group(1) if canonical_match else ""
        if canonical: canonicals[canonical] += 1
        cards = sorted({item for match in CLASS_RE.finditer(source) for item in match.group("value").split() if "card" in item.lower() or "box" in item.lower()}); unclassified = [item for item in cards if item not in allowed_cards]
        issues = []
        if 'class="ln-site-header"' not in source: issues.append("missing_canonical_header")
        if 'class="ln-site-footer"' not in source: issues.append("missing_canonical_footer")
        if source.count("<head>") != 1 or source.count("</head>") != 1: issues.append("invalid_head_structure")
        if "levnytt-foundations.css" not in source or "levnytt-components.css" not in source or "levnytt-rebuild.css" not in source: issues.append("missing_canonical_styles")
        if re.search(r"<style\b|\sstyle=|\son\w+=", source, re.I): issues.append("inline_code_present")
        if len(H1_RE.findall(source)) != 1: issues.append("invalid_h1_count")
        if not title: issues.append("missing_title")
        if not metadata.get("description"): issues.append("missing_description")
        if url.endswith("/404"):
            if metadata.get("robots", "").lower().startswith("noindex") is False: issues.append("404_not_noindex")
        else:
            expected = url.rstrip("/") if url != "https://levnytt.se/" else "https://levnytt.se"
            if canonical.rstrip("/") != expected: issues.append("canonical_mismatch")
        if not all(metadata.get(key) for key in ("og:title", "og:description", "og:image", "twitter:card")): issues.append("social_metadata_incomplete")
        schema_errors = jsonld_errors(source)
        if schema_errors: issues.append("invalid_structured_data")
        missing_images = missing_local_images(root, file, source)
        if missing_images: issues.append("missing_local_image")
        if "logo-light.svg" in source: issues.append("deprecated_logo")
        if metadata.get("levnytt-template") not in KNOWN_TEMPLATES: issues.append("unknown_template")
        # Unknown historical editorial components remain legitimate, but any
        # new shared card must be classified. Ignore classes already scoped to
        # a page family (ia/idx), which are intentionally editorial-specific.
        unclassified = [item for item in unclassified if not item.startswith(("ia-", "idx-"))]
        if unclassified: issues.append("unclassified_card")
        if issues: failures.append({"file": str(file.relative_to(root)), "url": url, "issues": issues, "unclassified_cards": unclassified, "missing_images": missing_images, "schema_errors": schema_errors})
        records.append({"url": url, "file": str(file.relative_to(root)), "current_template_family": family, "h1_count": len(H1_RE.findall(source)), "missing_local_images": missing_images, "issues": issues})

    duplicates = {"titles": sorted(value for value, count in titles.items() if value and count > 1), "canonicals": sorted(value for value, count in canonicals.items() if count > 1)}
    if duplicates["titles"] or duplicates["canonicals"]: failures.append({"file": "site-wide", "issues": ["duplicate_metadata"], **duplicates})
    literal_violations = []
    for relative in SHARED_STYLE_FILES:
        text = (root / relative).read_text(encoding="utf-8").lower()
        if any(token in text for token in CANONICAL_COLOR_LITERALS): literal_violations.append(relative)
    return {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "production_page_count": len(records), "family_counts": dict(sorted(families.items())), "duplicates": duplicates, "pages": records, "failures": failures, "shared_style_literal_color_violations": literal_violations}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--root", type=Path, default=ROOT); parser.add_argument("--output", type=Path, default=ROOT / "docs/reports/production-ui-inventory.json")
    args = parser.parse_args(); report = audit(args.root); args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"pages": report["production_page_count"], "families": report["family_counts"], "failures": len(report["failures"]), "shared_style_literal_color_violations": len(report["shared_style_literal_color_violations"])}, ensure_ascii=False))
    return 1 if report["failures"] or report["shared_style_literal_color_violations"] else 0


if __name__ == "__main__": raise SystemExit(main())
