#!/usr/bin/env python3
"""Bootstrap and build LevNytt production pages from one content dataset.

The bootstrap step extracts the currently published content once. Subsequent
builds read only ``content/data/production-pages.json`` and render every
sitemap page through the same shell and family templates.
"""
from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "content" / "data" / "production-pages.json"
CSS_HREFS = ("/assets/css/levnytt-foundations.css", "/assets/css/levnytt-rebuild.css")
SITE_HOST = "levnytt.se"


def sitemap_pages(root: Path) -> list[tuple[str, Path]]:
    result = []
    for element in ET.parse(root / "sitemap.xml").getroot().iter():
        if not element.tag.endswith("loc") or not element.text:
            continue
        url = element.text.strip()
        path = urlsplit(url).path.rstrip("/")
        file = root / ("index.html" if not path else f"{path.lstrip('/')}.html")
        if file.is_file():
            result.append((url, file))
    return result


def family_for(path: str) -> str:
    name = Path(path).stem
    if name == "index":
        return "home-editorial-hub"
    if name == "artiklar":
        return "library-category-index"
    if name in {"integritetspolicy", "404"}:
        return "utility-legal"
    if name in {"om-oss", "den-fundersamma-mannen", "var-metod", "forsknings-faq", "levnytt-principer"}:
        return "authority-editorial-trust"
    if name.startswith("neolife-") or name in {"golden-home-care", "personlig-vard", "super-10"}:
        return "product-category"
    return "informational-article"


def clean_metadata(head: str) -> str:
    head = re.sub(r"<style\b[^>]*>.*?</style\s*>", "", head, flags=re.I | re.S)
    head = re.sub(r"<link\b[^>]*rel=[\"']stylesheet[\"'][^>]*>", "", head, flags=re.I)
    head = re.sub(r"<script\b(?![^>]*application/ld\+json)[^>]*>.*?</script\s*>", "", head, flags=re.I | re.S)
    head = re.sub(r"<meta\s+name=[\"']levnytt-(?:template|cta|disclosure)[\"'][^>]*>\s*", "", head, flags=re.I)
    return head.strip()


def tag_attrs(attrs: list[tuple[str, str | None]]) -> dict[str, str | None]:
    return {name.lower(): value for name, value in attrs}


def canonical_href(href: str) -> str:
    split = urlsplit(href)
    if split.netloc and split.hostname and split.hostname.lower() == SITE_HOST:
        return urlunsplit(("", "", split.path or "/", split.query, split.fragment))
    if not split.scheme and not split.netloc and href:
        path = re.sub(r"/{2,}", "/", split.path or "/")
        if path.endswith(".html"):
            path = path[:-5] or "/"
        return urlunsplit(("", "", path if path.startswith("/") else "/" + path, split.query, split.fragment))
    return href


def serialise_attrs(attrs: list[tuple[str, str | None]]) -> str:
    return "".join(f' {name}' if value is None else f' {name}="{html_lib.escape(value, quote=True)}"' for name, value in attrs)


class FragmentCleaner(HTMLParser):
    """Remove legacy shells/inline CSS while preserving content markup."""

    SKIP_TAGS = {"footer", "nav", "script", "style"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.out: list[str] = []
        self.skip_depth = 0
        self.skip_tags: list[str] = []

    def _is_skip(self, tag: str, attrs: list[tuple[str, str | None]]) -> bool:
        values = tag_attrs(attrs)
        classes = set((values.get("class") or "").split())
        return tag in self.SKIP_TAGS or tag == "h1" or "breadcrumbs" in classes or values.get("id") in {"site-nav", "site-footer"}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if self.skip_depth:
            self.skip_depth += 1
            self.skip_tags.append(tag)
            return
        if self._is_skip(tag, attrs):
            self.skip_depth = 1
            self.skip_tags = [tag]
            return
        if tag in {"body", "main"}:
            return
        filtered = [(name, value) for name, value in attrs if name.lower() != "style"]
        values = tag_attrs(filtered)
        if tag == "a" and values.get("href"):
            filtered = [(name, value) for name, value in filtered if name.lower() not in {"target", "rel"}]
            filtered.append(("target", "_blank"))
            existing_rel = set((values.get("rel") or "").lower().split())
            existing_rel.update({"noopener", "noreferrer"})
            filtered.append(("rel", " ".join(sorted(existing_rel))))
            for index, (name, value) in enumerate(filtered):
                if name.lower() == "href":
                    filtered[index] = (name, canonical_href(value or ""))
                    break
        self.out.append("<" + tag + serialise_attrs(filtered) + ">")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if not self.skip_depth:
            self.out.append("<" + tag + serialise_attrs(attrs) + "/>")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self.skip_depth:
            self.skip_depth -= 1
            if self.skip_tags:
                self.skip_tags.pop()
            return
        if tag not in {"body", "main"}:
            self.out.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.out.append(data)

    def handle_entityref(self, name: str) -> None:
        if not self.skip_depth:
            self.out.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if not self.skip_depth:
            self.out.append(f"&#{name};")

    def handle_comment(self, data: str) -> None:
        if not self.skip_depth:
            self.out.append(f"<!--{data}-->")


def first_text(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html_lib.unescape(text)).strip()


def source_tokens(fragment: str) -> list[str]:
    fragment = re.sub(r"<(?:nav|footer|script|style)\b.*?</(?:nav|footer|script|style)\s*>", " ", fragment, flags=re.I | re.S)
    text = first_text(fragment).casefold()
    return sorted(set(re.findall(r"[\wåäöÅÄÖ]{4,}", text)))


def extract_page(url: str, path: Path) -> dict:
    source = path.read_text(encoding="utf-8")
    head = source.split("</head>", 1)[0].split("<head", 1)[-1]
    body_match = re.search(r"<body\b[^>]*>(?P<body>.*?)</body\s*>", source, flags=re.I | re.S)
    body = body_match.group("body") if body_match else ""
    title_match = re.search(r"<title\b[^>]*>(.*?)</title\s*>", head, flags=re.I | re.S)
    title = first_text(title_match.group(1)) if title_match else Path(path).stem.replace("-", " ").title()
    h1_match = re.search(r"<h1\b[^>]*>(.*?)</h1\s*>", body, flags=re.I | re.S)
    h1 = first_text(h1_match.group(1)) if h1_match else title.split(" | ", 1)[0]
    intro_match = re.search(r"<(?:p|div)\b[^>]*class=[\"'][^\"']*(?:hero-intro|ia-punchline)[^\"']*[\"'][^>]*>(.*?)</(?:p|div)>", body, flags=re.I | re.S)
    intro = first_text(intro_match.group(1)) if intro_match else ""
    cleaner = FragmentCleaner()
    cleaner.feed(body)
    cleaned = "".join(cleaner.out).strip()
    # Inline SVG presentation styles are converted to attributes so page CSS
    # remains centralized without changing the embedded illustration.
    cleaned = re.sub(r'\sstyle=["\']\s*stop-color\s*:\s*([^;"\']+)\s*["\']', r' stop-color="\1"', cleaned, flags=re.I)
    cleaned = re.sub(r'\sstyle=["\'][^"\']*["\']', "", cleaned, flags=re.I)
    return {
        "url": url,
        "path": urlsplit(url).path or "/",
        "family": family_for(path.name),
        "title": title,
        "h1": h1,
        "intro": intro,
        "head_html": clean_metadata(head),
        "body_html": cleaned,
        "source_tokens": source_tokens(body),
        "source_file": path.name,
    }


def bootstrap(root: Path, destination: Path) -> list[dict]:
    pages = [extract_page(url, path) for url, path in sitemap_pages(root)]
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps({"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(), "pages": pages}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return pages


def shared_header() -> str:
    links = [("/", "Hem"), ("/om-oss", "Om oss"), ("/artiklar", "Artiklar"), ("/neolife-historia", "Historia"), ("/neolife-vetenskap", "Vetenskap"), ("/neolife-kosttillskott", "Produkter"), ("/neolife-affarsmojlighet", "Affärsmöjlighet"), ("/finns-det-billigare-alternativ", "Spara Pengar?")]
    rendered = "\n".join(f'<a href="{href}" target="_blank" rel="noopener noreferrer">{label}</a>' for href, label in links)
    return f'''<header class="ln-site-header"><div class="ln-shell ln-header-inner"><a class="ln-brand" href="/" target="_blank" rel="noopener noreferrer" aria-label="LevNytt — Hem"><img src="/assets/brand/header-logo.svg" alt="LevNytt"></a><button class="ln-menu-toggle" type="button" aria-label="Meny" aria-expanded="false">Meny</button><nav class="ln-primary-nav" aria-label="Huvudnavigation">{rendered}<span class="ln-nav-commercial-group"><a class="ln-nav-commercial" href="https://se.neolifeshop.com/i/shop.html?sponsor=41-830928" target="_blank" rel="nofollow sponsored noopener noreferrer">Handla NeoLife →</a><a class="ln-nav-disclosure" href="/om-oss" target="_blank" rel="noopener noreferrer" style="font-size:11px;opacity:0.7;margin-left:6px;white-space:nowrap;">Oberoende distributör · Sponsor-ID 41-830928</a></span></nav></div></header>'''


def shared_footer() -> str:
    links = [("/neolife-historia", "Historia"), ("/neolife-vetenskap", "Vetenskap"), ("/direktforsaljning-fakta", "Direktförsäljning"), ("/neolife-kosttillskott", "Kosttillskott"), ("/om-oss", "Om oss"), ("/artiklar", "Alla artiklar"), ("/var-metod", "Vår metod"), ("/forsknings-faq", "Forsknings-FAQ"), ("/levnytt-principer", "LevNytt Principer"), ("/integritetspolicy", "Integritetspolicy")]
    rendered = "".join(f'<a href="{href}" target="_blank" rel="noopener noreferrer">{label}</a>' for href, label in links)
    return f'''<footer class="ln-site-footer"><div class="ln-shell"><a class="ln-footer-brand" href="/" target="_blank" rel="noopener noreferrer"><img src="/assets/brand/header-logo.svg" alt="LevNytt"></a><nav aria-label="Sidfot navigation">{rendered}</nav><p>© 2026 LevNytt. Alla rättigheter förbehållna.</p></div></footer>'''


def render_page(page: dict) -> str:
    family = page["family"]
    head = page["head_html"]
    head = re.sub(r"</head\s*>", "", head, flags=re.I).strip().lstrip("> ")
    styles = "\n".join(f'<link rel="stylesheet" href="{href}">' for href in CSS_HREFS)
    head += f'\n<meta name="levnytt-template" content="rebuild-{family}">\n<meta name="levnytt-cta" content="existing-content-cta">\n{styles}\n</head>'
    intro = f'<p class="ln-page-intro">{html_lib.escape(page["intro"])}</p>' if page["intro"] else ""
    crumbs = f'<p class="ln-breadcrumbs"><a href="/" target="_blank" rel="noopener noreferrer">LevNytt</a> <span aria-hidden="true">›</span> {html_lib.escape(page["h1"])}</p>'
    body_html = re.sub(r"[ \t]+(?=\n)", "", page["body_html"])
    return f'''<!doctype html><html lang="sv">{head}<body data-template-family="{family}">{shared_header()}<main class="ln-page ln-family-{family}"><div class="ln-shell">{crumbs}<article><header class="ln-article-header"><p class="ln-eyebrow">LevNytt · {family.replace('-', ' ')}</p><h1>{html_lib.escape(page["h1"])}</h1>{intro}</header><div class="ln-article-body">{body_html}</div></article></div></main>{shared_footer()}<script src="/assets/js/levnytt-rebuild.js" defer></script></body></html>'''


def build(root: Path, data_path: Path, output_root: Path) -> list[Path]:
    data = json.loads(data_path.read_text(encoding="utf-8"))
    written = []
    for page in data["pages"]:
        path = urlsplit(page["url"]).path.rstrip("/")
        destination = output_root / ("index.html" if not path else f"{path.lstrip('/')}.html")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(render_page(page), encoding="utf-8")
        written.append(destination)
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--bootstrap", action="store_true")
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--output-root", type=Path)
    args = parser.parse_args()
    if args.bootstrap:
        pages = bootstrap(args.root, args.data)
        print(json.dumps({"mode": "bootstrap", "pages": len(pages), "data": str(args.data)}, ensure_ascii=False))
    if args.build:
        output = args.output_root or args.root
        pages = build(args.root, args.data, output)
        print(json.dumps({"mode": "build", "pages": len(pages), "output": str(output)}, ensure_ascii=False))
    if not args.bootstrap and not args.build:
        parser.error("choose --bootstrap or --build")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
