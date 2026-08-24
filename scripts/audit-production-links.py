#!/usr/bin/env python3
"""Audit LevNytt's actual public routes and enforce the link policy."""
from __future__ import annotations

import argparse
import html as html_lib
import importlib.util
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
SITE_HOSTS = {"levnytt.se", "www.levnytt.se"}
ANCHOR_RE = re.compile(r"<a\b(?P<attrs>[^>]*)>", re.I | re.S)
ATTR_RE = re.compile(r"(?P<name>[\w:-]+)(?:\s*=\s*(?P<quote>[\"'])(?P<value>.*?)(?P=quote))?", re.S)
SAFE_REL = {"noopener", "noreferrer"}


def _rebuild_module(root: Path):
    spec = importlib.util.spec_from_file_location("levnytt_rebuild", root / "scripts" / "rebuild-production.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def redirects(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in (root / "_redirects").read_text(encoding="utf-8").splitlines():
        parts = raw.strip().split()
        if len(parts) >= 2 and not raw.lstrip().startswith("#"):
            result[parts[0].rstrip("/") or "/"] = parts[1]
    return result


def sitemap_pages(root: Path) -> list[tuple[str, Path]]:
    return _rebuild_module(root).sitemap_routes(root)


def read_attrs(raw: str) -> dict[str, str | None]:
    return {match.group("name").lower(): match.group("value") for match in ATTR_RE.finditer(raw)}


def classify(href: str) -> str:
    if not href.strip(): return "invalid"
    if href.startswith("#"): return "same-page-anchor"
    split = urlsplit(href)
    if split.scheme in {"mailto", "tel"}: return "protocol"
    if split.scheme and split.scheme not in {"http", "https"}: return "invalid"
    if split.netloc and (split.hostname or "").lower() not in SITE_HOSTS: return "external"
    return "internal"


def inverse_redirects(redirect_map: dict[str, str]) -> dict[str, str]:
    return {
        destination.rstrip("/") or "/": public
        for public, destination in redirect_map.items()
        if destination.startswith("/content/articles/")
    }


def canonical_internal(href: str, inverse: dict[str, str]) -> str:
    split = urlsplit(href)
    path = split.path or "/"
    path = inverse.get(path.rstrip("/") or "/", path)
    if path.endswith(".html"): path = path[:-5] or "/"
    path = re.sub(r"/{2,}", "/", path)
    if not path.startswith("/"): path = "/" + path
    return urlunsplit(("", "", path, split.query, split.fragment))


def local_exists(root: Path, redirect_map: dict[str, str], path: str) -> bool:
    clean = urlsplit(path).path.rstrip("/") or "/"
    if clean in redirect_map: return True
    if clean == "/": return (root / "index.html").is_file()
    relative = clean.lstrip("/")
    return any(candidate.is_file() for candidate in (root / relative, root / f"{relative}.html", root / relative / "index.html"))


def serialise(attrs: dict[str, str | None]) -> str:
    return "".join(f" {name}" if value is None else f' {name}="{html_lib.escape(value, quote=True)}"' for name, value in attrs.items())


def transform_tag(match: re.Match[str], root: Path, redirect_map: dict[str, str], inverse: dict[str, str], findings: list[dict], fix: bool) -> str:
    attrs = read_attrs(match.group("attrs")); href = html_lib.unescape(attrs.get("href") or ""); attrs["href"] = href; category = classify(href)
    target = (attrs.get("target") or "").lower(); rel = set((attrs.get("rel") or "").lower().split())
    record = {"href": href, "classification": category, "issues": []}; changed = False
    if category in {"internal", "same-page-anchor"}:
        if category == "internal":
            canonical = canonical_internal(href, inverse)
            if href != canonical:
                record["issues"].append("noncanonical_internal_url")
                if fix: attrs["href"] = canonical; changed = True
            if not local_exists(root, redirect_map, canonical): record["issues"].append("missing_local_target")
        if target == "_blank":
            record["issues"].append("internal_opens_new_tab")
            if fix: attrs.pop("target", None); changed = True
        cleaned_rel = rel - SAFE_REL
        if fix and cleaned_rel != rel:
            if cleaned_rel: attrs["rel"] = " ".join(sorted(cleaned_rel))
            else: attrs.pop("rel", None)
            changed = True
    elif category == "external":
        if target == "_blank" and not SAFE_REL.issubset(rel):
            record["issues"].append("unsafe_external_new_tab")
            if fix: attrs["rel"] = " ".join(sorted(rel | SAFE_REL)); changed = True
        if "neolifeshop.com" in (urlsplit(href).hostname or ""):
            sponsor = dict(re.findall(r"(?:^|[?&])(sponsor(?:Id)?)=([^&#]+)", href, re.I))
            if "41-830928" not in sponsor.values(): record["issues"].append("shop_sponsor_missing_or_wrong")
            if not {"nofollow", "sponsored"}.issubset(rel): record["issues"].append("shop_rel_missing")
    elif category == "invalid": record["issues"].append("invalid_href")
    if "localhost" in href.lower() or "127.0.0.1" in href: record["issues"].append("development_url")
    if record["issues"]: findings.append(record)
    return "<a" + serialise(attrs) + ">" if changed else match.group(0)


def audit_shared_component(source: str, component: str) -> dict:
    findings: list[dict] = []
    for match in ANCHOR_RE.finditer(source):
        attrs = read_attrs(match.group("attrs")); href = attrs.get("href") or ""; category = classify(href)
        if category in {"internal", "same-page-anchor"} and (attrs.get("target") or "").lower() == "_blank":
            findings.append({"href": href, "issue": "shared_internal_opens_new_tab"})
        if category == "external" and (attrs.get("target") or "").lower() == "_blank" and not SAFE_REL.issubset(set((attrs.get("rel") or "").split())):
            findings.append({"href": href, "issue": "shared_external_missing_safe_rel"})
    return {"component": component, "link_count": len(ANCHOR_RE.findall(source)), "issues": findings}


def run(root: Path, fix: bool) -> dict:
    redirect_map = redirects(root); inverse = inverse_redirects(redirect_map); totals: Counter[str] = Counter(); pages = []; exceptions = []
    for url, path in sitemap_pages(root):
        source = path.read_text(encoding="utf-8"); findings: list[dict] = []
        updated = ANCHOR_RE.sub(lambda match: transform_tag(match, root, redirect_map, inverse, findings, fix), source)
        ids = set(re.findall(r'\b(?:id|name)=["\']([^"\']+)', updated, re.I))
        for anchor in re.findall(r'<a\b[^>]*href=["\']#([^"\']+)', updated, re.I):
            decoded = html_lib.unescape(anchor)
            if decoded and decoded not in ids:
                findings.append({"href": f"#{decoded}", "classification": "same-page-anchor", "issues": ["missing_anchor_target"]})
        if fix and updated != source: path.write_text(updated, encoding="utf-8")
        for item in findings:
            totals.update(item["issues"])
            if any(issue in item["issues"] for issue in ("missing_local_target", "missing_anchor_target", "invalid_href", "development_url", "shop_sponsor_missing_or_wrong", "shop_rel_missing")):
                exceptions.append({"page": str(path.relative_to(root)), **item})
        pages.append({"url": url, "file": str(path.relative_to(root)), "findings": findings})
    components = []
    for path in sorted((root / "assets" / "fragments").glob("*.html")):
        components.append(audit_shared_component(path.read_text(encoding="utf-8"), str(path.relative_to(root))))
    return {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "scope": "all sitemap routes resolved through production rewrites", "fixed": fix, "production_page_count": len(pages), "issue_counts": dict(sorted(totals.items())), "unresolved_exceptions": exceptions, "pages": pages, "shared_components": components}


def write_reports(report: dict, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "link-audit.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# LevNytt Production Link Audit", "", f"Pages audited: **{report['production_page_count']}**", "", "## Findings", ""]
    lines += [f"- {key}: {value}" for key, value in report["issue_counts"].items()] or ["- No findings."]
    lines += ["", "## Unresolved exceptions", ""]
    lines += [f"- `{item['page']}` — `{item['href']}` — {', '.join(item['issues'])}" for item in report["unresolved_exceptions"]] or ["- None."]
    (output / "link-audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--root", type=Path, default=ROOT); parser.add_argument("--output", type=Path, default=ROOT / "docs/reports/link-audit"); parser.add_argument("--fix", action="store_true")
    args = parser.parse_args(); report = run(args.root, args.fix); write_reports(report, args.output)
    component_issues = sum(len(item["issues"]) for item in report["shared_components"])
    print(json.dumps({"pages": report["production_page_count"], "issues": report["issue_counts"], "exceptions": len(report["unresolved_exceptions"]), "shared_component_issues": component_issues}, ensure_ascii=False))
    return 1 if report["unresolved_exceptions"] or component_issues or report["issue_counts"].get("internal_opens_new_tab") else 0


if __name__ == "__main__": raise SystemExit(main())
