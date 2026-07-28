#!/usr/bin/env python3
"""Audit and safely normalize links on LevNytt pages published in sitemap.xml.

The optional --fix mode changes only the attributes of individual anchor tags
whose classification is deterministic: internal links become canonical
root-relative same-tab links; external new-tab links gain noopener noreferrer.
Unknown local targets are reported, never rewritten to a guessed destination.
"""
from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
SITE_HOST = "levnytt.se"
ANCHOR_RE = re.compile(r"<a\b(?P<attrs>[^>]*)>", re.I)
ATTR_RE = re.compile(r"(?P<name>[\w:-]+)(?:\s*=\s*(?P<quote>[\"'])(?P<value>.*?)(?P=quote))?", re.S)
SAFE_REL = {"noopener", "noreferrer"}


def redirects(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    path = root / "_redirects"
    if not path.exists():
        return result
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split()
        if len(fields) >= 2:
            result[fields[0].rstrip("/") or "/"] = fields[1]
    return result


def sitemap_pages(root: Path) -> list[tuple[str, Path]]:
    values: list[tuple[str, Path]] = []
    tree = ET.parse(root / "sitemap.xml")
    for element in tree.getroot().iter():
        if not element.tag.endswith("loc") or not element.text:
            continue
        url = element.text.strip()
        split = urlsplit(url)
        path = split.path.rstrip("/")
        file = root / ("index.html" if not path else f"{path.lstrip('/')}.html")
        if file.is_file():
            values.append((url, file))
    return values


def read_attrs(raw: str) -> dict[str, str | None]:
    return {match.group("name").lower(): match.group("value") for match in ATTR_RE.finditer(raw)}


def local_exists(root: Path, redirect_map: dict[str, str], path: str) -> bool:
    clean = path.split("#", 1)[0].split("?", 1)[0].rstrip("/") or "/"
    if clean in redirect_map:
        return True
    if clean == "/":
        return (root / "index.html").is_file()
    relative = clean.lstrip("/")
    candidates = (root / relative, root / f"{relative}.html", root / relative / "index.html")
    return any(candidate.is_file() for candidate in candidates)


def inverse_redirects(redirect_map: dict[str, str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for public, destination in redirect_map.items():
        clean = destination.rstrip("/") or "/"
        if clean.startswith("/") and clean not in result:
            result[clean] = public
    return result


def classify(href: str) -> str:
    if not href.strip():
        return "invalid"
    if href.startswith("#"):
        return "same-page-anchor"
    split = urlsplit(href)
    if split.scheme in {"mailto", "tel"}:
        return "protocol"
    if split.scheme and split.scheme not in {"http", "https"}:
        return "invalid"
    if split.netloc and split.hostname and split.hostname.lower() != SITE_HOST:
        return "external"
    if split.netloc or href.startswith("/") or not split.scheme:
        return "internal"
    return "invalid"


def canonical_internal(href: str, inverse: dict[str, str]) -> str:
    split = urlsplit(href)
    path = split.path or "/"
    if path.startswith("/content/articles"):
        source = path.rstrip("/") or "/"
        path = inverse.get(source, path)
    if path.endswith(".html"):
        path = path[:-5] or "/"
    path = re.sub(r"/{2,}", "/", path)
    if not path.startswith("/"):
        path = "/" + path
    return urlunsplit(("", "", path, split.query, split.fragment))


def serialise(attrs: dict[str, str | None]) -> str:
    return "".join(f' {name}' if value is None else f' {name}="{value}"' for name, value in attrs.items())


def transform_tag(match: re.Match[str], root: Path, redirect_map: dict[str, str], inverse: dict[str, str], findings: list[dict], fix: bool) -> str:
    attrs = read_attrs(match.group("attrs"))
    href = attrs.get("href") or ""
    category = classify(href)
    record = {"href": href, "classification": category, "issues": []}
    target = (attrs.get("target") or "").lower()
    rel_tokens = set((attrs.get("rel") or "").lower().split())
    changed = False
    if category in {"internal", "same-page-anchor"}:
        if category == "internal":
            canonical = canonical_internal(href, inverse)
            if href != canonical:
                record["issues"].append("noncanonical_internal_url")
                if fix:
                    attrs["href"] = canonical
                    changed = True
            if not local_exists(root, redirect_map, canonical):
                record["issues"].append("missing_local_target")
        if target == "_blank":
            record["issues"].append("internal_new_tab")
            if fix:
                attrs.pop("target", None)
                attrs.pop("rel", None)
                changed = True
        elif rel_tokens & SAFE_REL:
            record["issues"].append("unnecessary_internal_rel")
            if fix:
                attrs.pop("rel", None)
                changed = True
    elif category == "external":
        if target == "_blank" and not SAFE_REL.issubset(rel_tokens):
            record["issues"].append("unsafe_external_new_tab")
            if fix:
                attrs["rel"] = " ".join(sorted(rel_tokens | SAFE_REL))
                changed = True
    else:
        record["issues"].append("invalid_href")
    if "localhost" in href.lower() or "127.0.0.1" in href:
        record["issues"].append("development_url")
    if record["issues"]:
        findings.append(record)
    return "<a" + serialise(attrs) + ">" if changed else match.group(0)


def run(root: Path, fix: bool) -> dict:
    redirect_map = redirects(root)
    inverse = inverse_redirects(redirect_map)
    totals: Counter[str] = Counter()
    pages: list[dict] = []
    exceptions: list[dict] = []
    for url, path in sitemap_pages(root):
        html = path.read_text(encoding="utf-8")
        findings: list[dict] = []
        updated = ANCHOR_RE.sub(lambda match: transform_tag(match, root, redirect_map, inverse, findings, fix), html)
        if fix and updated != html:
            path.write_text(updated, encoding="utf-8")
        for item in findings:
            totals.update(item["issues"])
            if "missing_local_target" in item["issues"] or "invalid_href" in item["issues"] or "development_url" in item["issues"]:
                exceptions.append({"page": path.name, **item})
        pages.append({"url": url, "file": path.name, "findings": findings})
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": "sitemap-listed production pages only",
        "fixed": fix,
        "production_page_count": len(pages),
        "issue_counts": dict(sorted(totals.items())),
        "unresolved_exceptions": exceptions,
        "pages": pages,
    }


def write_reports(report: dict, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "link-audit.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    counts = report["issue_counts"]
    lines = ["# LevNytt Production Link Audit", "", f"Pages audited: **{report['production_page_count']}**", "", "## Findings", ""]
    lines += [f"- {key}: {value}" for key, value in counts.items()] or ["- No findings."]
    lines += ["", "## Unresolved exceptions", ""]
    if report["unresolved_exceptions"]:
        for item in report["unresolved_exceptions"]:
            lines.append(f"- `{item['page']}` — `{item['href']}` — {', '.join(item['issues'])}")
    else:
        lines.append("- None.")
    (output / "link-audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=ROOT / "docs" / "reports" / "link-audit")
    parser.add_argument("--fix", action="store_true")
    args = parser.parse_args()
    report = run(args.root, args.fix)
    write_reports(report, args.output)
    print(json.dumps({"pages": report["production_page_count"], "issues": report["issue_counts"], "exceptions": len(report["unresolved_exceptions"])}, ensure_ascii=False))
    return 1 if report["unresolved_exceptions"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
