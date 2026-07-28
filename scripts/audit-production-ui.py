#!/usr/bin/env python3
"""Deterministic production-page inventory and UI contract audit."""
from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META_RE = re.compile(r'<meta\s+name=["\'](?P<name>[^"\']+)["\']\s+content=["\'](?P<value>[^"\']+)["\']', re.I)
CLASS_RE = re.compile(r'class=["\'](?P<value>[^"\']+)["\']', re.I)
BODY_RE = re.compile(r'<body\b[^>]*>', re.I)
H1_RE = re.compile(r'<h1\b', re.I)
IMAGE_RE = re.compile(r'<img\b[^>]*\bsrc=["\'](?P<src>[^"\']+)', re.I)
KNOWN_TEMPLATES = {"informational-article-v1", "authority-editorial-trust-v1"}
CANONICAL_COLOR_LITERALS = {"#1b4332", "#e8c870", "#c9a84c", "#f9f6ef", "#ddd8ce"}
SHARED_STYLE_FILES = ("assets/css/levnytt-components.css", "assets/css/authority-trust.css")


def production_pages(root: Path):
    for item in ET.parse(root / "sitemap.xml").getroot().iter():
        if item.tag.endswith("loc") and item.text:
            path = item.text.removeprefix("https://levnytt.se/").rstrip("/")
            file = root / ("index.html" if not path else f"{path}.html")
            if file.is_file():
                yield item.text, file


def inferred_family(file: Path, metadata: dict[str, str]) -> str:
    if metadata.get("levnytt-template") in KNOWN_TEMPLATES:
        return metadata["levnytt-template"]
    name = file.stem
    if name == "index": return "home-editorial-hub"
    if name == "artiklar": return "library-category-index"
    if name in {"integritetspolicy", "404"}: return "utility-legal"
    if name in {"om-oss", "den-fundersamma-mannen", "var-metod", "forsknings-faq", "levnytt-principer"}: return "authority-editorial-trust"
    if name.startswith("neolife-") or name in {"golden-home-care", "personlig-vard", "super-10"}: return "product-category"
    return "legacy-or-informational"


def load_cards(root: Path) -> set[str]:
    value = json.loads((root / "config" / "ui-card-classification.json").read_text(encoding="utf-8"))
    result = set(value.get("supporting_classes", []))
    for members in value.get("variants", {}).values():
        result.update(members)
    return result


def missing_local_images(root: Path, file: Path, html: str) -> list[str]:
    missing = []
    for match in IMAGE_RE.finditer(html):
        src = match.group("src")
        if not src or src.startswith(("http:", "https:", "data:")):
            continue
        candidate = root / src.lstrip("/") if src.startswith("/") else file.parent / src
        if not candidate.is_file():
            missing.append(src)
    return missing


def audit(root: Path) -> dict:
    allowed_cards = load_cards(root)
    records=[]; failures=[]; families=Counter()
    for url, file in production_pages(root):
        html=file.read_text(encoding="utf-8")
        metadata={m.group("name").lower():m.group("value") for m in META_RE.finditer(html)}
        family=inferred_family(file, metadata); families[family]+=1
        cards=sorted({c for m in CLASS_RE.finditer(html) for c in m.group("value").split() if "card" in c.lower() or "box" in c.lower()})
        unclassified=[c for c in cards if c not in allowed_cards]
        issues=[]
        for required in ("nav.js", "footer.js"):
            if required not in html: issues.append(f"missing_{required}")
        body = BODY_RE.search(html)
        nav_mount = html.find('<div id="site-nav"></div>')
        if not body or nav_mount < body.end() or html[body.end():nav_mount].strip():
            issues.append("missing_canonical_nav_mount")
        if len(H1_RE.findall(html)) != 1:
            issues.append("invalid_h1_count")
        missing_images = missing_local_images(root, file, html)
        if missing_images:
            issues.append("missing_local_image")
        if "logo-light.svg" in html: issues.append("deprecated_logo")
        if metadata.get("levnytt-template") and metadata["levnytt-template"] not in KNOWN_TEMPLATES: issues.append("unknown_template")
        if metadata.get("levnytt-template") == "informational-article-v1" and not metadata.get("levnytt-cta"): issues.append("missing_cta_classification")
        if metadata.get("levnytt-cta") in {"product-referral", "affiliate-referral"} and not metadata.get("levnytt-disclosure"): issues.append("missing_disclosure_metadata")
        if unclassified: issues.append("unclassified_card")
        if issues: failures.append({"file":file.name,"issues":issues,"unclassified_cards":unclassified,"missing_images":missing_images})
        records.append({"url":url,"file":file.name,"current_template_family":family,"target_template_family":family,"visual_consistency":"STANDARDIZED" if not issues else "MIGRATION_REQUIRED","navigation_footer_compliance":not any(i.startswith("missing_") for i in issues),"link_compliance":"see link-audit.json","card_compliance":not unclassified,"cta_classification":metadata.get("levnytt-cta","legacy-not-declared"),"disclosure_compliance":"required" if metadata.get("levnytt-cta") in {"product-referral","affiliate-referral"} else "not-required","migration_status":"MIGRATED" if metadata.get("levnytt-template") else "SHARED-SHELL-MIGRATED","h1_count":len(H1_RE.findall(html)),"missing_local_images":missing_images,"issues":issues})
    literal_violations = []
    for relative in SHARED_STYLE_FILES:
        text = (root / relative).read_text(encoding="utf-8").lower()
        if any(token in text for token in CANONICAL_COLOR_LITERALS):
            literal_violations.append(relative)
    return {"generated_at":datetime.now(timezone.utc).isoformat(timespec="seconds"),"production_page_count":len(records),"family_counts":dict(sorted(families.items())),"pages":records,"failures":failures,"shared_style_literal_color_violations":literal_violations}


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--root",type=Path,default=ROOT); parser.add_argument("--output",type=Path,default=ROOT/"docs"/"reports"/"production-ui-inventory.json")
    args=parser.parse_args(); report=audit(args.root); args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"pages":report["production_page_count"],"families":report["family_counts"],"failures":len(report["failures"]),"shared_style_literal_color_violations":len(report["shared_style_literal_color_violations"])},ensure_ascii=False))
    return 1 if report["failures"] or report["shared_style_literal_color_violations"] else 0


if __name__=="__main__":
    raise SystemExit(main())
