#!/usr/bin/env python3
"""
Homepage Generator — LevNytt

Reads all articles from content/articles/, extracts metadata,
and rewrites the hardcoded article sections of index.html.

Usage:
    python scripts/generate-homepage.py

The script looks for the following markers in index.html and replaces them:
    <!-- HP:LATEST-BANNER -->   → latest article banner
    <!-- HP:LATEST-LIST -->     → latest articles grid section
"""

import json
import os
import re
import sys
import importlib.util
import subprocess
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

ARTICLES_DIR = "content/articles"
INDEX_FILE = "index.html"
MAX_LATEST_ARTICLES = 6

SITE_DOMAIN = "https://levnytt.se"
ROOT = Path(__file__).resolve().parents[1]

SWEDISH_MONTHS = {
    1: "januari", 2: "februari", 3: "mars", 4: "april",
    5: "maj", 6: "juni", 7: "juli", 8: "augusti",
    9: "september", 10: "oktober", 11: "november", 12: "december",
}


def format_swedish_date(dt: datetime) -> str:
    return f"{dt.day} {SWEDISH_MONTHS[dt.month]} {dt.year}"


# ── Simple HTML → text extractor for word count ────────────────────

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            self.text.append(data)

    def get_text(self):
        return " ".join(self.text)


def strip_html(html: str) -> str:
    parser = TextExtractor()
    parser.feed(html)
    return parser.get_text()


def word_count(html: str) -> int:
    text = strip_html(html)
    return len(text.split())


def reading_time_minutes(word_count_val: int) -> int:
    return max(1, round(word_count_val / 200))


# ── JSON-LD extraction ────────────────────────────────────────────

def extract_json_ld_blocks(html: str):
    """Yield raw JSON-LD text blocks (pre-HTML-stripping)."""
    pattern = re.compile(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
        re.DOTALL | re.IGNORECASE,
    )
    for match in pattern.finditer(html):
        yield match.group(1).strip()


def lenient_json_loads(raw: str):
    """Try json.loads; on failure strip HTML tags from string values and retry."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    # Strip HTML tags from inside string values
    cleaned = re.sub(r'<[^>]+>', '', raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


def extract_ld_field(raw_ld: str, field: str) -> str | None:
    """Extract a single field from raw JSON-LD text using regex (robust to HTML in values)."""
    m = re.search(r'"' + field + r'":\s*"((?:[^"\\]|\\.)*)"', raw_ld)
    if m:
        # Unescape JSON escapes
        val = m.group(1).replace('\\"', '"').replace('\\\\', '\\')
        return val
    return None


def extract_article_data(filepath: str) -> dict | None:
    """Extract metadata from an article HTML file."""
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    # Try full JSON parse first; fall back to regex field extraction
    ld = None
    raw_lds = list(extract_json_ld_blocks(html))
    for raw in raw_lds:
        ld = lenient_json_loads(raw)
        if ld:
            break

    # Preferred: datePublished from JSON-LD (regex fallback)
    date_str = None

    if ld:
        # Navigate @graph structure
        article_obj = None
        if "@graph" in ld:
            for item in ld["@graph"]:
                if item.get("@type") in ("Article", "WebPage"):
                    article_obj = item
                    break
        elif ld.get("@type") in ("Article", "WebPage"):
            article_obj = ld

        if article_obj:
            date_str = article_obj.get("datePublished")

    if not date_str:
        # Fall back to regex on raw JSON-LD
        for raw in raw_lds:
            date_str = extract_ld_field(raw, "datePublished")
            if date_str:
                break

    if not date_str:
        result = subprocess.run(["git", "log", "--follow", "--diff-filter=A", "-1", "--format=%aI", "--", filepath], capture_output=True, text=True)
        date_str = result.stdout.strip() or datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()

    try:
        pub_date = datetime.fromisoformat(date_str)
    except (ValueError, TypeError):
        return None
    if pub_date.tzinfo is not None:
        pub_date = pub_date.replace(tzinfo=None)

    # headline/title
    headline = None
    if ld and article_obj:
        headline = article_obj.get("headline")
    if not headline:
        for raw in raw_lds:
            headline = extract_ld_field(raw, "headline")
            if headline:
                break
    if not headline:
        headline = extract_title(html)
    if not headline:
        return None

    # description
    description = None
    if ld and article_obj:
        description = article_obj.get("description")
    if not description:
        description = extract_meta_description(html) or ""

    # canonical URL
    url = extract_canonical_url(html, article_obj if (ld and article_obj) else {}, filepath)

    # word count & reading time
    wc = word_count(html)
    rt = reading_time_minutes(wc)

    return {
        "title": headline.strip(),
        "description": description.strip(),
        "url": url,
        "path": url.replace(SITE_DOMAIN, "").rstrip("/") or "/",
        "date": pub_date,
        "date_str": format_swedish_date(pub_date),
        "reading_time": rt,
        "word_count": wc,
    }


def extract_title(html: str) -> str | None:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else None


def extract_meta_description(html: str) -> str | None:
    m = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']\s*/?>',
        html,
        re.IGNORECASE,
    )
    if m:
        return m.group(1)
    m = re.search(
        r'<meta\s+content=["\'](.*?)["\']\s+name=["\']description["\']\s*/?>',
        html,
        re.IGNORECASE,
    )
    return m.group(1) if m else None


def extract_canonical_url(html: str, article_obj: dict, filepath: str) -> str:
    # 1. <link rel="canonical">
    m = re.search(
        r'<link\s+rel=["\']canonical["\']\s+href=["\'](.*?)["\']\s*/?>',
        html,
        re.IGNORECASE,
    )
    if m:
        return m.group(1).rstrip("/")

    # 2. mainEntityOfPage @id
    meop = article_obj.get("mainEntityOfPage", {})
    if isinstance(meop, dict):
        eid = meop.get("@id")
        if eid:
            return eid.rstrip("/")

    # 3. og:url
    m = re.search(
        r'<meta\s+property=["\']og:url["\']\s+content=["\'](.*?)["\']\s*/?>',
        html,
        re.IGNORECASE,
    )
    if m:
        return m.group(1).rstrip("/")

    # 4. Fallback: filename
    basename = os.path.splitext(os.path.basename(filepath))[0]
    return f"{SITE_DOMAIN}/{basename}"


# ── HTML generation ────────────────────────────────────────────────

def render_latest_banner(article: dict) -> str:
    title_escaped = article["title"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    return f"""<div class="latest-post" role="note" aria-label="Senaste artikeln">
  <div class="latest-post-inner">
    <span class="latest-post-label">Senaste artikeln</span>
    <span class="latest-post-title">{title_escaped}</span>
    <a href="{article['path']}" class="latest-post-link">Läs artikeln →</a>
  </div>
</div>"""


def render_articles_section(articles: list) -> str:
    if not articles:
        return ""

    cards = []
    for a in articles:
        title_escaped = a["title"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        date_str = format_swedish_date(a["date"])
        rt = a["reading_time"]
        cards.append(f"""    <a href="{a['path']}" class="article-card">
      <span class="article-card-title">{title_escaped}</span>
      <span class="article-card-meta">
        <span>{date_str}</span>
        <span>{rt} min läsning</span>
      </span>
    </a>""")

    cards_html = "\n".join(cards)

    return f"""<section class="section section-alt" id="senaste-artiklar">
  <div class="container">
    <span class="section-label">Senaste publicerat</span>
    <h2 class="section-heading">Senaste artiklarna</h2>
    <p class="section-intro">De senaste konsumentguiderna och artiklarna från LevNytt.</p>
    <div class="articles-grid">
{cards_html}
    </div>
  </div>
</section>"""


# ── Main ───────────────────────────────────────────────────────────

def main():
    # 1. Scan articles
    articles = []
    if not os.path.isdir(ARTICLES_DIR):
        print(f"Error: {ARTICLES_DIR} not found", file=sys.stderr)
        sys.exit(1)

    spec = importlib.util.spec_from_file_location("levnytt_rebuild_home", ROOT / "scripts/rebuild-production.py")
    rebuild = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(rebuild)
    excluded = {"/", "/artiklar", "/om-oss", "/integritetspolicy", "/no/"}
    for url, path in rebuild.sitemap_routes(ROOT):
        if (url.replace(SITE_DOMAIN, "") or "/") in excluded:
            continue
        fpath = str(path)
        data = extract_article_data(fpath)
        if data:
            articles.append(data)
        else:
            print(f"Warning: Could not extract metadata from {fpath}", file=sys.stderr)

    if not articles:
        print("Error: No articles found", file=sys.stderr)
        sys.exit(1)

    # 2. Sort by date descending
    articles.sort(key=lambda a: a["date"], reverse=True)

    # 3. Read index.html
    if not os.path.isfile(INDEX_FILE):
        print(f"Error: {INDEX_FILE} not found", file=sys.stderr)
        sys.exit(1)

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # 4. Replace persistent marker blocks
    latest = articles[0]
    banner_html = render_latest_banner(latest)
    list_html = render_articles_section(articles[:MAX_LATEST_ARTICLES])

    # Replace banner block: <!-- HP:LATEST-BANNER --> ... <!-- /HP:LATEST-BANNER -->
    banner_pattern = re.compile(
        r'<!--\s*HP:LATEST-BANNER\s*-->(.*?)<!--\s*/HP:LATEST-BANNER\s*-->',
        re.DOTALL,
    )
    if not banner_pattern.search(html):
        print("Error: Marker <!-- HP:LATEST-BANNER --> not found in index.html", file=sys.stderr)
        sys.exit(1)

    list_pattern = re.compile(
        r'<!--\s*HP:LATEST-LIST\s*-->(.*?)<!--\s*/HP:LATEST-LIST\s*-->',
        re.DOTALL,
    )
    if not list_pattern.search(html):
        print("Error: Marker <!-- HP:LATEST-LIST --> not found in index.html", file=sys.stderr)
        sys.exit(1)

    html = banner_pattern.sub(
        f"<!-- HP:LATEST-BANNER -->\n{banner_html}\n<!-- /HP:LATEST-BANNER -->",
        html,
    )
    html = list_pattern.sub(
        f"<!-- HP:LATEST-LIST -->\n{list_html}\n<!-- /HP:LATEST-LIST -->",
        html,
    )

    # 5. Write
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Homepage generated successfully.")
    print(f"  Latest: {latest['title']} ({latest['date_str']})")
    print(f"  Articles listed: {min(len(articles), MAX_LATEST_ARTICLES)}")
    if len(articles) > MAX_LATEST_ARTICLES:
        print(f"  (sorted from {len(articles)} total articles)")


if __name__ == "__main__":
    main()
