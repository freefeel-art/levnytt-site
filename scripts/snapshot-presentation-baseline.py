#!/usr/bin/env python3
"""Snapshot and compare LevNytt's non-visual production contract.

The redesign may change markup and styles, but not published text, SEO metadata,
routes, structured data, link destinations, disclosures, or tracking behavior.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def digest(value: str | bytes) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def normalise_text(value: str) -> str:
    return " ".join(value.split())


class ContractParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.main_depth: int | None = None
        self.footer_depth: int | None = None
        self.main_text: list[str] = []
        self.footer_text: list[str] = []
        self.hrefs: list[str] = []
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        self.depth += 1
        if tag == "main" and self.main_depth is None:
            self.main_depth = self.depth
        if tag == "footer" and self.footer_depth is None:
            self.footer_depth = self.depth
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"] or "")
        if tag == "script" and values.get("src"):
            self.scripts.append(values["src"] or "")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"] or "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "main" and self.main_depth == self.depth:
            self.main_depth = None
        if tag == "footer" and self.footer_depth == self.depth:
            self.footer_depth = None
        self.depth -= 1

    def handle_data(self, data: str) -> None:
        if self.main_depth is not None:
            self.main_text.append(data)
        if self.footer_depth is not None:
            self.footer_text.append(data)


def load_rebuild(root: Path):
    path = root / "scripts" / "rebuild-production.py"
    spec = importlib.util.spec_from_file_location("levnytt_contract_rebuild", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def meta_value(source: str, key: str) -> str:
    patterns = (
        rf'<meta\s+name=["\']{re.escape(key)}["\']\s+content=["\']([^"\']*)',
        rf'<meta\s+content=["\']([^"\']*)["\']\s+name=["\']{re.escape(key)}["\']',
    )
    for pattern in patterns:
        match = re.search(pattern, source, re.I)
        if match:
            return match.group(1)
    return ""


def element_text(source: str, tag: str) -> str:
    match = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}\s*>", source, re.I | re.S)
    return normalise_text(re.sub(r"<[^>]+>", " ", match.group(1))) if match else ""


def canonical(source: str) -> str:
    match = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)', source, re.I)
    return match.group(1) if match else ""


def schema(source: str) -> list[object]:
    values = []
    for raw in re.findall(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script\s*>', source, re.I | re.S):
        values.append(json.loads(raw))
    return values


def function_source(source: str, name: str) -> str:
    start = source.find(f"function {name}(")
    if start < 0:
        return ""
    brace = source.find("{", start)
    depth = 0
    for index in range(brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    return ""


def snapshot(root: Path) -> dict:
    rebuild = load_rebuild(root)
    routes = list(rebuild.sitemap_routes(root))
    not_found = root / "404.html"
    if not_found.is_file():
        routes.append(("https://levnytt.se/404", not_found))

    pages = {}
    for url, path in routes:
        source = path.read_text(encoding="utf-8")
        parser = ContractParser()
        parser.feed(source)
        hrefs = Counter(parser.hrefs)
        affiliate = Counter(href for href in parser.hrefs if "neolifeshop.com" in href)
        pages[url] = {
            "source_file": str(path.relative_to(root)),
            "title": element_text(source, "title"),
            "description": meta_value(source, "description"),
            "canonical": canonical(source),
            "schema": schema(source),
            "main_text_sha256": digest(normalise_text(" ".join(parser.main_text))),
            "main_text_length": len(normalise_text(" ".join(parser.main_text))),
            "footer_text_sha256": digest(normalise_text(" ".join(parser.footer_text))),
            "hrefs": dict(sorted(hrefs.items())),
            "affiliate_hrefs": dict(sorted(affiliate.items())),
            # Asset version hashes are expected to change when presentation
            # code changes; script identity and protected tracking functions
            # are verified separately.
            "script_srcs": [urlsplit(value).path if value.startswith("/") else value for value in parser.scripts],
        }

    runtime_js = (root / "assets/js/levnytt-rebuild.js").read_text(encoding="utf-8")
    protected_files = ["sitemap.xml", "_redirects", "robots.txt", "_worker.js"]
    return {
        "schema_version": 1,
        "routes": [url for url, _ in routes],
        "pages": pages,
        "tracking": {
            name: digest(function_source(runtime_js, name))
            for name in ("ensureSponsorAttribution", "trackNeoLifeClicks")
        },
        "protected_file_sha256": {
            name: digest((root / name).read_bytes()) for name in protected_files
        },
    }


def differences(before: object, after: object, path: str = "") -> list[str]:
    if type(before) is not type(after):
        return [f"{path}: type changed"]
    if isinstance(before, dict):
        result = []
        for key in sorted(set(before) | set(after)):
            child = f"{path}.{key}" if path else str(key)
            if key not in before:
                result.append(f"{child}: added")
            elif key not in after:
                result.append(f"{child}: removed")
            else:
                result.extend(differences(before[key], after[key], child))
        return result
    if isinstance(before, list):
        if before == after:
            return []
        return [f"{path}: list changed"]
    return [] if before == after else [f"{path}: value changed"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--compare", type=Path)
    args = parser.parse_args()
    current = snapshot(args.root)
    if args.output:
        args.output.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.compare:
        expected = json.loads(args.compare.read_text(encoding="utf-8"))
        diff = differences(expected, current)
        print(json.dumps({"passed": not diff, "differences": diff}, ensure_ascii=False, indent=2))
        return 1 if diff else 0
    print(json.dumps({"routes": len(current["routes"]), "pages": len(current["pages"]), "output": str(args.output) if args.output else None}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
