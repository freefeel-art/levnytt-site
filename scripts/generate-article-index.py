#!/usr/bin/env python3
"""
Article Index Generator — LevNytt

Scans published root HTML files and regenerates the article cards,
stats, and schema in artiklar.html so every published article is
automatically listed on the index, search, and category pages.

Usage:
    python scripts/generate-article-index.py
"""

import json
import os
import re
import sys
from datetime import datetime
from html.parser import HTMLParser

ROOT_DIR = "."
INDEX_FILE = "artiklar.html"
SITE_DOMAIN = "https://levnytt.se"

EXCLUDED_FILES = {
    "index.html", "artiklar.html", "404.html", "integritetspolicy.html",
    "om-oss.html", "pillar.css",
}

CATEGORY_MAP = [
    ("vitaminer", "Vitaminer & mineraler", "VITAMINER & MINERALER",
     "Evidensbaserade guider om vitaminer, mineraler, kosttillskott och cellulär nutrition.",
     []),  # catch-all — everything else falls here

    ("fettsyror", "Fettsyror & antioxidanter", "FETTSYROR & ANTIOXIDANTER",
     "Omega-3, fettsyror och antioxidanter — forskning om EPA, DHA och ALA.",
     ["omega-3", "omega.3", "fiskolja", "algolja", "krillolja", "epa", "dha",
      "ala-vs-epa", "triglycerid", "etylester", "hjärthälsa", "ledvärk",
      "fettsyra", "neolife-omega", "nar.och.hur.ska.man.ta.omega",
      "varfor-fiskolja"]),

    ("tarmhalsa", "Tarmhälsa & kostfiber", "TARMHÄLSA & KOSTFIBER",
     "Guider om tarmhälsa, kostfiber, probiotika och prebiotika.",
     ["kostfiber", "tarmhäl", "tarmhalsa", "probiotika", "prebiotika",
      "ibs", "förstoppning", "tarmflora", "fiber", "acidophilus",
      "vad.ar.kostfiber", "vad.ar.probiotika"]),

    ("halsa", "Hälsa & livsstil", "HÄLSA & LIVSSTIL",
     "Hälsa, nutrition och evidensbaserade livsstilsråd.",
     ["kollagen", "kreatin", "melatonin", "sömn", "klimakterium",
      "viktuppgång", "viktkontroll", "trött", "hälsa", "livsstil",
      "retinol", "hudvård", "hudtecken", "niacinamid", "näringsbrist",
      "naringsbrist", "c-vitamin.serum", "ar.jag.trott"]),

    ("goldenhomecare", "Golden Home Care", "GOLDEN HOME CARE",
     "Hållbara rengöringsprodukter från NeoLife Golden Home Care.",
     ["golden.home.care", "golden-home-care", "rengör", "städ", "diskmedel",
      "miljövänlig rengör", "greenwashing", "ldc", "super.10", "koncentrat",
      "kemikalie"]),

    ("direktforsaljning", "Direktförsäljning", "DIREKTFÖRSÄLJNING",
     "Fakta och analys om direktförsäljning, MLM och nätverksmarknadsföring.",
     ["direktförsäljning", "direktforsaljning", "mlm", "pyramidspel",
      "nätverksmarknadsföring", "inkomstredovisning", "konsumenträtt",
      "återförsäljare", "mlm-rekrytering", "mlm-produkter", "mlm-företag",
      "mlm-konsumentratt", "social.press", "natverksmarknadsforing"]),
]

SWEDISH_MONTHS = {
    1: "januari", 2: "februari", 3: "mars", 4: "april",
    5: "maj", 6: "juni", 7: "juli", 8: "augusti",
    9: "september", 10: "oktober", 11: "november", 12: "december",
}


def format_swedish_date(dt: datetime) -> str:
    return f"{dt.day} {SWEDISH_MONTHS[dt.month]} {dt.year}"


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


def extract_json_ld_blocks(html: str):
    pattern = re.compile(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
        re.DOTALL | re.IGNORECASE,
    )
    for match in pattern.finditer(html):
        yield match.group(1).strip()


def lenient_json_loads(raw: str):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    cleaned = re.sub(r'<[^>]+>', '', raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


def extract_ld_field(raw_ld: str, field: str) -> str | None:
    m = re.search(r'"' + field + r'":\s*"((?:[^"\\]|\\.)*)"', raw_ld)
    if m:
        return m.group(1).replace('\\"', '"').replace('\\\\', '\\')
    return None


def extract_title(html: str) -> str | None:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else None


def extract_meta_description(html: str) -> str | None:
    m = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']\s*/?>',
        html, re.IGNORECASE,
    )
    if m:
        return m.group(1)
    m = re.search(
        r'<meta\s+content=["\'](.*?)["\']\s+name=["\']description["\']\s*/?>',
        html, re.IGNORECASE,
    )
    return m.group(1) if m else None


def extract_canonical_url(html: str, article_obj: dict, filepath: str) -> str:
    m = re.search(
        r'<link\s+rel=["\']canonical["\']\s+href=["\'](.*?)["\']\s*/?>',
        html, re.IGNORECASE,
    )
    if m:
        return m.group(1).rstrip("/")
    meop = article_obj.get("mainEntityOfPage", {})
    if isinstance(meop, dict):
        eid = meop.get("@id")
        if eid:
            return eid.rstrip("/")
    if isinstance(meop, str):
        return meop.rstrip("/")
    m = re.search(
        r'<meta\s+property=["\']og:url["\']\s+content=["\'](.*?)["\']\s*/?>',
        html, re.IGNORECASE,
    )
    if m:
        return m.group(1).rstrip("/")
    basename = os.path.splitext(os.path.basename(filepath))[0]
    return f"{SITE_DOMAIN}/{basename}"


def extract_article_data(filepath: str) -> dict | None:
    """Extract metadata from an article HTML file."""
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    ld = None
    raw_lds = list(extract_json_ld_blocks(html))
    for raw in raw_lds:
        ld = lenient_json_loads(raw)
        if ld:
            break

    date_str = None
    article_obj = None

    if ld:
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
        for raw in raw_lds:
            date_str = extract_ld_field(raw, "datePublished")
            if date_str:
                break

    if not date_str:
        # Fallback: look for article:published_time meta tag
        m_date = re.search(
            r'<meta\s+property=["\']article:published_time["\']\s+content=["\'](.*?)["\']',
            html, re.IGNORECASE,
        )
        if m_date:
            date_str = m_date.group(1)

    if not date_str:
        # Fallback: og:article:published_time
        m_date = re.search(
            r'<meta\s+property=["\']og:article:published_time["\']\s+content=["\'](.*?)["\']',
            html, re.IGNORECASE,
        )
        if m_date:
            date_str = m_date.group(1)

    if not date_str:
        # Only use fallback if no JSON-LD exists at all, or if the LD was Article/WebPage
        if ld and article_obj is None and ld.get("@type") not in (None, "Article", "WebPage"):
            return None
        if raw_lds and not date_str:
            has_article_ld = False
            for raw in raw_lds:
                if '"@type":"Article"' in raw or '"@type":"WebPage"' in raw:
                    has_article_ld = True
                    break
            if not has_article_ld:
                # If JSON-LD exists but isn't Article/WebPage type, skip
                return None
        # Fallback: file modification time
        mtime = os.path.getmtime(filepath)
        date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

    try:
        pub_date = datetime.fromisoformat(date_str)
        # Strip timezone info for consistent comparison
        if pub_date.tzinfo is not None:
            pub_date = pub_date.replace(tzinfo=None)
    except (ValueError, TypeError):
        return None

    headline = None
    if article_obj:
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

    description = None
    if article_obj:
        description = article_obj.get("description")
    if not description:
        description = extract_meta_description(html) or ""

    url = extract_canonical_url(html, article_obj if article_obj else {}, filepath)

    return {
        "title": headline.strip(),
        "description": description.strip(),
        "url": url,
        "path": url.replace(SITE_DOMAIN, "").rstrip("/") or "/",
        "date": pub_date,
        "date_str": format_swedish_date(pub_date),
        "date_month": pub_date.month,
        "date_year": pub_date.year,
    }


def normalise(s: str) -> str:
    return (s.lower()
            .replace("å", "a").replace("ä", "a").replace("ö", "o")
            .replace("é", "e").replace("-", ".").replace(" ", "."))


def classify_category(title: str, description: str, slug: str) -> str:
    """Classify an article into a category based on keywords."""
    text = normalise(f"{slug} {title} {description}")

    for cat_id, _, _, _, keywords in CATEGORY_MAP:
        for kw in keywords:
            if kw.lower() in text:
                return cat_id

    return "vitaminer"


def is_portalguide(title: str) -> bool:
    return "komplett guide" in title.lower() or "komplett" in title.lower() and "guide" in title.lower()


def get_article_type(title: str) -> str:
    return "Portalguide" if is_portalguide(title) else "Artikel"


def get_slug_from_filepath(filepath: str, is_subdir: bool = False) -> str:
    """Extract the URL slug from a file path."""
    if is_subdir:
        return os.path.basename(os.path.dirname(filepath))
    return os.path.splitext(os.path.basename(filepath))[0]


def discover_articles():
    """Discover all published articles in root directory."""
    articles = []

    # Scan flat .html files in root
    for fname in os.listdir(ROOT_DIR):
        if not fname.endswith(".html"):
            continue
        if fname in EXCLUDED_FILES:
            continue

        fpath = os.path.join(ROOT_DIR, fname)
        if not os.path.isfile(fpath):
            continue

        data = extract_article_data(fpath)
        if data:
            data["slug"] = get_slug_from_filepath(fpath)
            data["filepath"] = fpath
            articles.append(data)
        else:
            print(f"  [skip] {fpath} — no valid article metadata", file=sys.stderr)

    # Scan subdirectory articles (root/subdir/index.html)
    for entry in os.listdir(ROOT_DIR):
        subdir = os.path.join(ROOT_DIR, entry)
        if not os.path.isdir(subdir):
            continue
        if entry.startswith("."):
            continue
        if entry in ("assets", "content", "docs", "scripts", "images", ".github", ".opencode"):
            continue

        index_path = os.path.join(subdir, "index.html")
        if not os.path.isfile(index_path):
            continue

        data = extract_article_data(index_path)
        if data:
            data["slug"] = entry
            data["filepath"] = index_path
            articles.append(data)
        else:
            print(f"  [skip] {index_path} — no valid article metadata", file=sys.stderr)

    return articles


def render_card_html(article: dict, cat: str) -> str:
    """Render a single article card HTML block."""
    title = article["title"]
    desc = article["description"]
    path = article["path"]
    date_str = article["date_str"]
    article_type = get_article_type(title)
    is_pg = is_portalguide(title)

    search_data = normalise(f"{title} {desc} {article['slug']}")

    title_escaped = (title.replace("&", "&amp;").replace("<", "&lt;")
                     .replace(">", "&gt;").replace('"', "&quot;"))
    desc_escaped = (desc.replace("&", "&amp;").replace("<", "&lt;")
                    .replace(">", "&gt;").replace('"', "&quot;"))

    badge = ""
    if is_pg:
        badge = '        <span class="idx-card-badge star">&#9733; Portalguide</span>\n'

    return (
        f'      <a href="{path}" class="idx-card" data-cat="{cat}" '
        f'data-search="{search_data}">\n'
        f'{badge}'
        f'        <span class="idx-card-title">{title_escaped}</span>\n'
        f'        <span class="idx-card-desc">{desc_escaped}</span>\n'
        f'        <div class="idx-card-meta">'
        f'<span>{date_str}</span>'
        f'<span class="idx-card-meta-sep">·</span>'
        f'<span>{article_type}</span></div>\n'
        f'        <span class="idx-card-arrow">→</span>\n'
        f'      </a>'
    )


def render_category_section(cat_id: str, cat_title: str, cat_intro: str, articles: list) -> str:
    """Render a full category section with its article cards."""
    if not articles:
        return ""

    cards_html = "\n".join(articles)

    return (
        f'  <section class="idx-cat" id="cat-{cat_id}" data-category="{cat_id}">\n'
        f'    <h2 class="idx-cat-h">{cat_title}</h2>\n'
        f'    <div class="idx-cat-grid">\n\n'
        f'{cards_html}\n\n'
        f'    </div>\n'
        f'  </section>'
    )


def main():
    print("=== LevNytt Article Index Generator ===")

    # 1. Scan root for articles
    print("Scanning published articles...")
    all_articles = discover_articles()

    if not all_articles:
        print("Error: No articles found", file=sys.stderr)
        sys.exit(1)

    # Remove duplicates by URL (in case an article exists both as flat file and subdir)
    seen_urls = set()
    unique_articles = []
    for a in all_articles:
        if a["url"] not in seen_urls:
            seen_urls.add(a["url"])
            unique_articles.append(a)
    all_articles = unique_articles

    print(f"  Found {len(all_articles)} published articles")

    # 2. Classify each article
    for a in all_articles:
        a["category"] = classify_category(a["title"], a["description"], a["slug"])

    # 3. Sort by date descending
    all_articles.sort(key=lambda a: a["date"], reverse=True)

    # 4. Group by category
    categorized = {}
    for cat_id, cat_label, cat_title, cat_intro, _ in CATEGORY_MAP:
        cat_articles = [a for a in all_articles if a["category"] == cat_id]
        cat_articles.sort(key=lambda a: a["date"], reverse=True)
        categorized[cat_id] = {
            "label": cat_label,
            "title": cat_title,
            "intro": cat_intro,
            "articles": cat_articles,
        }

    # 5. Calculate stats
    total_articles = len(all_articles)
    total_categories = sum(1 for c in categorized.values() if c["articles"])
    total_portalguides = sum(1 for a in all_articles if is_portalguide(a["title"]))

    print(f"  Categories: {total_categories}")
    print(f"  Portalguides: {total_portalguides}")

    # 6. Generate category sections HTML
    sections_html_parts = []
    for cat_id, _, cat_title, cat_intro, _ in CATEGORY_MAP:
        cat_data = categorized[cat_id]
        if not cat_data["articles"]:
            continue

        cards = []
        for a in cat_data["articles"]:
            cards.append(render_card_html(a, cat_id))

        sections_html_parts.append(
            render_category_section(cat_id, cat_title, cat_intro, cards)
        )

    sections_html = "\n\n".join(sections_html_parts)

    # 7. Read artiklar.html
    if not os.path.isfile(INDEX_FILE):
        print(f"Error: {INDEX_FILE} not found", file=sys.stderr)
        sys.exit(1)

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # 8. Replace markers

    # 8a. Replace article cards between markers
    cards_pattern = re.compile(
        r'<!--\s*IDX:ARTICLE-CARDS\s*-->(.*?)<!--\s*/IDX:ARTICLE-CARDS\s*-->',
        re.DOTALL,
    )
    if not cards_pattern.search(html):
        print("Error: Marker <!-- IDX:ARTICLE-CARDS --> not found in artiklar.html",
              file=sys.stderr)
        sys.exit(1)

    html = cards_pattern.sub(
        f"<!-- IDX:ARTICLE-CARDS -->\n{sections_html}\n<!-- /IDX:ARTICLE-CARDS -->",
        html,
    )

    # 8b. Replace article count
    count_pattern = re.compile(
        r'<!--\s*IDX:ARTICLE-COUNT\s*-->\d+<!--\s*/IDX:ARTICLE-COUNT\s*-->',
    )
    if count_pattern.search(html):
        html = count_pattern.sub(f"<!-- IDX:ARTICLE-COUNT -->{total_articles}<!-- /IDX:ARTICLE-COUNT -->", html)

    # 8c. Replace category count
    catcount_pattern = re.compile(
        r'<!--\s*IDX:CAT-COUNT\s*-->\d+<!--\s*/IDX:CAT-COUNT\s*-->',
    )
    if catcount_pattern.search(html):
        html = catcount_pattern.sub(f"<!-- IDX:CAT-COUNT -->{total_categories}<!-- /IDX:CAT-COUNT -->", html)

    # 8d. Replace portalguide count
    pgcount_pattern = re.compile(
        r'<!--\s*IDX:PORTAL-COUNT\s*-->\d+<!--\s*/IDX:PORTAL-COUNT\s*-->',
    )
    if pgcount_pattern.search(html):
        html = pgcount_pattern.sub(f"<!-- IDX:PORTAL-COUNT -->{total_portalguides}<!-- /IDX:PORTAL-COUNT -->", html)

    # 8e. Replace display count in controls
    display_count = f"{total_articles} artiklar"
    display_pattern = re.compile(
        r'<!--\s*IDX:DISPLAY-COUNT\s*-->.*?<!--\s*/IDX:DISPLAY-COUNT\s*-->',
    )
    if display_pattern.search(html):
        html = display_pattern.sub(
            f'<!-- IDX:DISPLAY-COUNT -->{display_count}<!-- /IDX:DISPLAY-COUNT -->',
            html,
        )

    # 8f. Replace meta description (update article count in SEO)
    meta_desc_pattern = re.compile(
        r'(<meta\s+name=["\']description["\']\s+content=["\'])([^"]*?)(["\'])',
    )
    def update_meta_desc(m):
        prefix = m.group(1)
        content = m.group(2)
        suffix = m.group(3)
        # Update the leading count in the description
        updated = re.sub(r'^\d+\s+artiklar', f'{total_articles} artiklar', content)
        return f'{prefix}{updated}{suffix}'
    html = meta_desc_pattern.sub(update_meta_desc, html)

    # 8g. Update og:description similarly
    ogdesc_pattern = re.compile(
        r'(<meta\s+property=["\']og:description["\']\s+content=["\'])([^"]*?)(["\'])',
    )
    def update_og_desc(m):
        prefix = m.group(1)
        content = m.group(2)
        suffix = m.group(3)
        updated = re.sub(r'^\d+\s+', f'{total_articles} ', content)
        return f'{prefix}{updated}{suffix}'
    html = ogdesc_pattern.sub(update_og_desc, html)

    # 8h. Update JSON-LD article count in description
    ld_desc_pattern = re.compile(
        r'(description["\:]\s*["\'])([^"]*?)(\d+)\s+artiklar',
    )
    def update_ld_desc(m):
        prefix = m.group(1)
        before = m.group(2)
        return f'{prefix}{before}{total_articles} artiklar'
    html = ld_desc_pattern.sub(update_ld_desc, html)

    # 9. Write
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nArticle index generated successfully.")
    print(f"  Total articles: {total_articles}")
    print(f"  Categories: {total_categories}")
    print(f"  Portalguides: {total_portalguides}")

    # Print per-category breakdown
    for cat_id, cat_label, _, _, _ in CATEGORY_MAP:
        cat_data = categorized[cat_id]
        if cat_data["articles"]:
            print(f"    {cat_label}: {len(cat_data['articles'])} articles")


if __name__ == "__main__":
    main()
