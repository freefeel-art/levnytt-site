#!/usr/bin/env python3
"""Apply the shared LevNytt UI shell only to sitemap-listed production pages."""
from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLE_LINKS = ('<link rel="stylesheet" href="/assets/css/levnytt-foundations.css">', '<link rel="stylesheet" href="/assets/css/levnytt-components.css">')
NAV_BLOCK = '<div id="site-nav"></div>\n<script src="/nav.js" defer></script>'
NAV_BLOCK_RE = re.compile(r'\s*<div\s+id=["\']site-nav["\']\s*></div>\s*<script\s+src=["\']/nav\.js["\']\s+defer\s*></script>', re.I)
BODY_RE = re.compile(r'(<body\b[^>]*>)', re.I)


def pages(root: Path):
    for item in ET.parse(root / "sitemap.xml").getroot().iter():
        if not item.tag.endswith("loc") or not item.text:
            continue
        relative = item.text.removeprefix("https://levnytt.se/").rstrip("/")
        path = root / ("index.html" if not relative else f"{relative}.html")
        if path.exists():
            yield path


def migrate(html: str) -> str:
    for link in STYLE_LINKS:
        if link not in html:
            html = html.replace("</head>", link + "\n</head>", 1)
    # A legacy page can already load nav.js at the end of the document.  That
    # technically loads the component but places the header after the article.
    # Keep exactly one canonical mount point immediately inside <body>.
    html = NAV_BLOCK_RE.sub("", html)
    if "nav.js" not in html:
        html = BODY_RE.sub(r"\1\n" + NAV_BLOCK, html, count=1)
    else:
        html = BODY_RE.sub(r"\1\n" + NAV_BLOCK, html, count=1)
    if "footer.js" not in html:
        html = html.replace("</body>", '<script src="/footer.js" defer></script>\n<script src="/components.js" defer></script>\n</body>', 1)
    return html


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    changed = []
    for page in pages(args.root):
        before = page.read_text(encoding="utf-8")
        after = migrate(before)
        if before != after:
            changed.append(page.name)
            if args.apply:
                page.write_text(after, encoding="utf-8")
    print("changed=" + str(len(changed)))
    print("\n".join(changed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
