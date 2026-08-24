#!/usr/bin/env python3
"""Build every public LevNytt route through the shared production renderer.

Cloudflare rewrites mean a public URL is not necessarily served by the
similarly named root HTML file. This module resolves those rewrites before it
extracts, renders or audits content so the build contract matches production.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from site_renderer import SITE, canonical_href, extract_document, family_for, render_page  # noqa: E402,F401

DATA_PATH = ROOT / "content" / "data" / "production-pages.json"


def rewrite_rules(root: Path) -> list[tuple[str, str]]:
    rules: list[tuple[str, str]] = []
    redirects = root / "_redirects"
    if not redirects.is_file():
        return rules
    for raw in redirects.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = re.split(r"\s+", line)
        if len(parts) >= 3 and parts[2] == "200" and not any(token in parts[0] for token in "*:?"):
            rules.append((parts[0].rstrip("/") or "/", parts[1]))
    return rules


def resolve_public_file(root: Path, public_path: str) -> Path:
    path = public_path.rstrip("/") or "/"
    for source, destination in rewrite_rules(root):
        if path == source:
            candidate = root / destination.lstrip("/")
            for resolved in (candidate, Path(str(candidate) + ".html"), candidate / "index.html"):
                if resolved.is_file():
                    return resolved
    if path == "/":
        return root / "index.html"
    direct = root / path.lstrip("/")
    if direct.is_dir() and (direct / "index.html").is_file():
        return direct / "index.html"
    return root / f"{path.lstrip('/')}.html"


def sitemap_routes(root: Path) -> list[tuple[str, Path]]:
    routes: list[tuple[str, Path]] = []
    seen: set[str] = set()
    for element in ET.parse(root / "sitemap.xml").getroot().iter():
        if not element.tag.endswith("loc") or not element.text:
            continue
        url = element.text.strip()
        public_path = urlsplit(url).path or "/"
        if public_path in seen:
            continue
        seen.add(public_path)
        routes.append((url, resolve_public_file(root, public_path)))
    return routes


# Backward-compatible name used by existing tests and tooling.
sitemap_pages = sitemap_routes


def bootstrap(root: Path, destination: Path) -> list[dict]:
    pages: list[dict] = []
    for url, source in sitemap_routes(root):
        if not source.is_file():
            raise FileNotFoundError(f"Sitemap route {url} has no source file: {source}")
        # Extraction always follows the file Cloudflare currently serves.
        # This prevents direct-page and rewrite-page data from drifting into
        # different generations of the template.
        page = extract_document(url, source.read_text(encoding="utf-8"), str(source.relative_to(root)), root)
        relative = str(source.relative_to(root))
        if not page.get("date_published"):
            created = subprocess.run(["git", "log", "--follow", "--diff-filter=A", "-1", "--format=%aI", "--", relative], cwd=root, capture_output=True, text=True).stdout.strip()
            page["date_published"] = created
        if not page.get("date_modified"):
            modified = subprocess.run(["git", "log", "-1", "--format=%aI", "--", relative], cwd=root, capture_output=True, text=True).stdout.strip()
            page["date_modified"] = modified or page.get("date_published", "")
        pages.append(page)

    not_found = root / "404.html"
    if not_found.is_file():
        pages.append(extract_document(f"{SITE}/404", not_found.read_text(encoding="utf-8"), "404.html", root))

    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pages": pages,
    }
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return pages


def public_output_path(output_root: Path, public_path: str) -> Path:
    path = public_path.rstrip("/")
    return output_root / ("index.html" if not path else f"{path.lstrip('/')}.html")


def build(root: Path, data_path: Path, output_root: Path, *, in_place: bool = False) -> list[Path]:
    data = json.loads(data_path.read_text(encoding="utf-8"))
    written: list[Path] = []
    canonical_copies: dict[str, list[Path]] = {}
    if in_place:
        for candidate in root.rglob("*.html"):
            relative = candidate.relative_to(root)
            if relative.parts and relative.parts[0] in {"docs", "assets", "node_modules"}:
                continue
            match = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)', candidate.read_text(encoding="utf-8", errors="replace"), re.I)
            if match:
                canonical_copies.setdefault(match.group(1).rstrip("/"), []).append(candidate)
    for page in data["pages"]:
        destination = root / page["source_file"] if in_place else public_output_path(output_root, page["path"])
        destination.parent.mkdir(parents=True, exist_ok=True)
        rendered = render_page(page, root)
        destination.write_text(rendered, encoding="utf-8")
        written.append(destination)

        # Keep historical root aliases coherent when a production rewrite
        # serves a content/articles source. They are not the public authority,
        # but stale copies are a recurring maintenance trap.
        if in_place and page["path"] not in {"/", "/404"}:
            alias = root / f"{page['path'].strip('/')}.html"
            if alias.is_file() and alias != destination:
                alias.write_text(rendered, encoding="utf-8")
                written.append(alias)
        if in_place:
            for copy in canonical_copies.get(page["url"].rstrip("/"), []):
                if copy != destination and copy not in written:
                    copy.write_text(rendered, encoding="utf-8")
                    written.append(copy)
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--bootstrap", action="store_true")
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--in-place", action="store_true")
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--output-root", type=Path)
    args = parser.parse_args()
    if args.bootstrap:
        pages = bootstrap(args.root, args.data)
        print(json.dumps({"mode": "bootstrap", "pages": len(pages), "data": str(args.data)}, ensure_ascii=False))
    if args.build:
        output = args.output_root or args.root
        paths = build(args.root, args.data, output, in_place=args.in_place)
        print(json.dumps({"mode": "build", "files": len(paths), "output": str(output), "in_place": args.in_place}, ensure_ascii=False))
    if not args.bootstrap and not args.build:
        parser.error("choose --bootstrap or --build")
    if args.in_place and not args.build:
        parser.error("--in-place requires --build")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
