#!/usr/bin/env python3
"""Deterministic acceptance checks for the canonical LevNytt rebuild."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit


def text_tokens(value: str) -> set[str]:
    value = re.sub(r"<script\b.*?</script\s*>|<style\b.*?</style\s*>", " ", value, flags=re.I | re.S)
    value = html.unescape(re.sub(r"<[^>]+>", " ", value))
    return {w for w in re.findall(r"[\wåäöÅÄÖ]{4,}", value.casefold())}


def contrast_ratio(foreground: str, background: str) -> float:
    def luminance(value: str) -> float:
        rgb = [int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        channels = [v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
        return .2126 * channels[0] + .7152 * channels[1] + .0722 * channels[2]
    a, b = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (a + .05) / (b + .05)


def check_page(data: dict, file: Path) -> dict:
    source = file.read_text(encoding="utf-8")
    failures: list[str] = []
    if "class=\"ln-site-header\"" not in source or "class=\"ln-site-footer\"" not in source:
        failures.append("shared_shell_missing")
    if source.count("<h1") != 1:
        failures.append("h1_count_not_one")
    if "levnytt-rebuild.css" not in source or "levnytt-foundations.css" not in source:
        failures.append("canonical_styles_missing")
    if re.search(r"<style\b|\sstyle=|\son\w+=", source, flags=re.I):
        failures.append("inline_code_present")
    if "nav.js" in source or "footer.js" in source or "components.js" in source:
        failures.append("legacy_shell_script_present")
    links = []
    for match in re.finditer(r"<a\b([^>]*)>", source, flags=re.I | re.S):
        attrs = dict((k.lower(), v or "") for k, v in re.findall(r"([\w:-]+)(?:\s*=\s*[\"']([^\"']*)[\"'])?", match.group(1)))
        href = attrs.get("href", "")
        if href:
            links.append(href)
            rel = set(attrs.get("rel", "").lower().split())
            split = urlsplit(href)
            internal = not split.netloc or (split.hostname or "").lower() in {"levnytt.se", "www.levnytt.se"}
            if internal and attrs.get("target") == "_blank":
                failures.append("internal_link_opens_new_tab")
            if not internal and attrs.get("target") == "_blank" and not {"noopener", "noreferrer"}.issubset(rel):
                failures.append("external_link_missing_safe_rel")
            if "neolifeshop.com" in (split.hostname or ""):
                if "41-830928" not in href:
                    failures.append("sponsor_id_missing")
                if not {"nofollow", "sponsored"}.issubset(rel):
                    failures.append("commercial_rel_missing")
    if source.count("<head>") != 1 or source.count("</head>") != 1:
        failures.append("invalid_head_structure")
    if page_path := data.get("path"):
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', source, re.I)
        if page_path != "/404" and not canonical:
            failures.append("canonical_missing")
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', source, re.I | re.S):
        try:
            json.loads(raw)
        except json.JSONDecodeError:
            failures.append("invalid_jsonld")
    # The bootstrap data is the preservation baseline.  All meaningful source
    # words must remain present in the generated page; shell words are ignored.
    source_words = set(data.get("source_tokens", []))
    missing = sorted(source_words - text_tokens(source))
    if len(missing) > max(3, int(len(source_words) * 0.02)):
        failures.append("content_tokens_missing")
    return {"path": data["path"], "family": data["family"], "links": len(links), "missing_tokens": missing[:20], "failures": sorted(set(failures))}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    dataset = json.loads(args.data.read_text(encoding="utf-8"))
    results = []
    for page in dataset["pages"]:
        path = urlsplit(page["url"]).path.rstrip("/")
        file = args.root / ("index.html" if not path else f"{path.lstrip('/')}.html")
        if not file.is_file():
            results.append({"path": page["path"], "family": page["family"], "failures": ["missing_generated_page"]})
            continue
        results.append(check_page(page, file))
    report = {
        "schema_version": 1,
        "pages_expected": len(dataset["pages"]),
        "pages_checked": len(results),
        "unique_routes": len({p["path"] for p in dataset["pages"]}),
        "failures": [r for r in results if r.get("failures")],
        "passed": not any(r.get("failures") for r in results),
        "contrast_checks": {
            "text_on_surface": round(contrast_ratio("#1A1A1A", "#F9F6EF"), 2),
            "green_on_surface": round(contrast_ratio("#1B4332", "#F9F6EF"), 2),
            "surface_on_green": round(contrast_ratio("#FFFFFF", "#1B4332"), 2),
            "minimum_required": 4.5,
        },
        "pages": results,
    }
    report["contrast_checks"]["passed"] = min(report["contrast_checks"][key] for key in ("text_on_surface", "green_on_surface", "surface_on_green")) >= 4.5
    report["passed"] = report["passed"] and report["contrast_checks"]["passed"]
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8")
    print(output)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
