#!/usr/bin/env python3
"""
md-to-article.py — LevNytt Publication Source V2 → PAS V1.0 HTML

Usage:
    python3 scripts/md-to-article.py <slug>

Reads:  content/articles/<slug>/<slug>.md
Writes: content/articles/<slug>/<slug>.html

Exit codes:
    0 — success
    1 — missing argument, file not found, or validation error
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
BASE_URL = "https://levnytt.se"
GOOGLE_VERIFY = "kAcoLDFGCpGh42gIFRgPeWlC253vTP3OLBs6wI8KDQ0"
PINTEREST_VERIFY = "6a9e88f7014abe0735767f464c08f337"
OG_IMAGE = f"{BASE_URL}/assets/brand/og-brand.png"
OG_IMAGE_ALT = "LevNytt — En oberoende NeoLife-distributör"

LEGAL_DISCLOSURE = (
    "LevNytt.se är en oberoende NeoLife-distributörswebbplats (Sponsor-ID: 41-830928). "
    "Innehållet är avsett för utbildningssyfte och har inte utvärderats av Livsmedelsverket. "
    "Produkterna är inte avsedda att diagnostisera, behandla, bota eller förebygga några sjukdomar. "
    "NeoLife® är ett registrerat varumärke tillhörande NeoLife International."
)

SWEDISH_MONTHS = {
    1: "januari", 2: "februari", 3: "mars", 4: "april",
    5: "maj", 6: "juni", 7: "juli", 8: "augusti",
    9: "september", 10: "oktober", 11: "november", 12: "december",
}

REQUIRED_FIELDS = [
    "title", "description", "slug", "category", "eyebrow",
    "author", "updated", "reading_time",
    "punchline", "takeaways", "method_note",
    "tierbox", "cta", "disclosure", "faq",
]

# PAS V1.0 Section 7 — exact inline CSS, verbatim from live articles
IA_CSS = """.ia-wrap{max-width:760px;margin:0 auto;padding:0 20px;font-family:Inter,system-ui,sans-serif;color:#1a1a1a;line-height:1.65}
.ia-wrap h1{font-family:"Playfair Display",Georgia,serif;font-size:2.1em;line-height:1.2;color:#1B4332;margin:0.6em 0 0.4em}
.ia-wrap h2{font-family:"Playfair Display",Georgia,serif;font-size:1.5em;color:#1B4332;margin:1.6em 0 0.6em}
.ia-wrap h3{font-size:1.15em;color:#1B4332;margin:1.2em 0 0.5em}
.ia-punchline{font-size:1.3em;font-weight:600;border-left:4px solid #C9A84C;padding:18px 22px;background:#F9F6EF;margin:24px 0;border-radius:0 6px 6px 0;color:#1B4332}
.ia-takeaways{background:#1B4332;color:#F9F6EF;border-radius:10px;padding:22px 26px;margin:26px 0}
.ia-wrap .ia-takeaways h3{margin:0 0 14px;color:#C9A84C;font-size:1.05em;letter-spacing:0.04em;text-transform:uppercase;font-weight:700}
.ia-takeaways ul{margin:0;padding-left:20px;color:#F9F6EF}
.ia-takeaways li{margin:9px 0;line-height:1.55;color:#F9F6EF}
.ia-takeaways a{color:#ffd47a;text-decoration-color:#ffd47a}
.ia-evidence-label{display:inline-block;font-size:0.72em;font-weight:700;letter-spacing:0.06em;padding:2px 7px;border-radius:3px;vertical-align:middle;margin-left:6px}
.ia-ev-t1{background:#1a3a2a;color:#4ade80}
.ia-ev-t2{background:#1a2e3a;color:#60a5fa}
.ia-ev-t3{background:#2e2a1a;color:#fbbf24}
.ia-ev-t4{background:#2a1a1a;color:#f87171}
.ia-stat-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:26px 0}
.ia-stat-card{background:#F9F6EF;border:1px solid #e3dcc9;border-radius:8px;padding:16px 18px}
.ia-stat-card .num{font-family:"Playfair Display",Georgia,serif;font-size:1.7em;font-weight:700;color:#1B4332;display:block}
.ia-stat-card .lbl{font-size:0.85em;color:#444}
.ia-stat-card .src{font-size:0.75em;color:#888;display:block;margin-top:4px}
.ia-method-table{width:100%;border-collapse:collapse;margin:24px 0;font-size:0.92em}
.ia-method-table th,.ia-method-table td{border:1px solid #e3dcc9;padding:10px 12px;text-align:left;vertical-align:top}
.ia-method-table th{background:#1B4332;color:#F9F6EF}
.ia-method-table tr:nth-child(even){background:#F9F6EF}
.ia-callout{background:#F9F6EF;border:1px solid #e3dcc9;border-radius:8px;padding:16px 20px;margin:22px 0}
.ia-callout h4{margin:0 0 8px;color:#1B4332;font-size:1em}
.ia-faq details{border-bottom:1px solid #e3dcc9;padding:14px 0}
.ia-faq summary{font-weight:600;cursor:pointer;color:#1B4332}
.ia-faq p{margin:10px 0 0}
.ia-tierbox{display:flex;gap:12px;flex-wrap:wrap;margin:30px 0}
.ia-tier{flex:1 1 150px;background:#1B4332;color:#F9F6EF;border-radius:8px;padding:14px 16px;text-decoration:none;font-size:0.9em}
.ia-tier b{color:#C9A84C;display:block;font-size:0.8em;letter-spacing:0.05em;margin-bottom:4px}
.ia-author-box{display:flex;gap:16px;align-items:flex-start;background:#F9F6EF;border-radius:10px;padding:20px;margin:34px 0}
.ia-author-avatar{width:48px;height:48px;border-radius:50%;background:#1B4332;color:#C9A84C;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0}
.ia-cta{background:#1B4332;color:#F9F6EF;border-radius:10px;padding:24px 26px;margin:30px 0;text-align:center}
.ia-wrap .ia-cta h3{color:#C9A84C;margin-top:0}
.ia-cta a{color:#F9F6EF;background:#C9A84C;padding:10px 20px;border-radius:6px;text-decoration:none;display:inline-block;margin-top:10px;font-weight:600}
.ia-cta-secondary{margin-top:14px;font-size:0.9em}
.ia-cta-secondary a{color:#ffd47a;background:none;padding:0;border-radius:0;display:inline;margin-top:0;font-weight:400;text-decoration:underline}
.ia-disclosure{font-size:0.82em;color:#666;border-top:1px solid #e3dcc9;padding-top:16px;margin-top:30px}
@media(max-width:900px){}@media(max-width:768px){}@media(max-width:600px){}"""


# ─── YAML Frontmatter Parser ────────────────────────────────────────────────

def _unquote(s):
    """Strip surrounding YAML quotes from a scalar value."""
    s = s.strip()
    if len(s) >= 2:
        if s[0] == '"' and s[-1] == '"':
            return s[1:-1].replace('\\"', '"').replace('\\n', '\n')
        if s[0] == "'" and s[-1] == "'":
            return s[1:-1].replace("''", "'")
    if re.match(r'^\d+$', s):
        return int(s)
    return s


def parse_frontmatter(text):
    """
    Parse V2 publication source YAML frontmatter using stdlib only.
    Handles: quoted strings, integers, folded block scalars (>),
    nested objects (2 levels), lists of strings, lists of objects.
    """
    lines = text.split('\n')
    n = len(lines)
    result = {}

    def indent_of(line):
        return len(line) - len(line.lstrip(' '))

    def collect_block_scalar(start):
        """Collect a folded (>) block scalar. Return (text, next_i)."""
        parts = []
        j = start
        while j < n:
            ln = lines[j]
            if ln and not ln[0].isspace():
                break
            parts.append(ln.strip())
            j += 1
        segments, cur = [], []
        for p in parts:
            if p:
                cur.append(p)
            elif cur:
                segments.append(' '.join(cur))
                cur = []
        if cur:
            segments.append(' '.join(cur))
        return '\n'.join(segments), j

    def collect_object(start, base_ind):
        """Collect an indented mapping. Return (dict, next_i)."""
        obj = {}
        j = start
        while j < n:
            ln = lines[j]
            if not ln.strip():
                j += 1
                continue
            if indent_of(ln) <= base_ind:
                break
            stripped = ln.strip()
            if ':' in stripped:
                k, _, v = stripped.partition(':')
                obj[k.strip()] = _unquote(v.strip()) if v.strip() else ''
            j += 1
        return obj, j

    def collect_list(start, base_ind):
        """Collect an indented sequence. Return (list, next_i)."""
        items = []
        j = start
        while j < n:
            ln = lines[j]
            if not ln.strip():
                j += 1
                continue
            if indent_of(ln) <= base_ind:
                break
            stripped = ln.strip()
            if not stripped.startswith('- '):
                j += 1
                continue
            item_text = stripped[2:]
            # Object item: `key: value` not starting with a quote
            is_obj = (
                ':' in item_text
                and not item_text.startswith('"')
                and not item_text.startswith("'")
            )
            if is_obj:
                obj = {}
                k, _, v = item_text.partition(':')
                obj[k.strip()] = _unquote(v.strip())
                j += 1
                item_ind = indent_of(ln) + 2
                while j < n:
                    inner = lines[j]
                    if not inner.strip():
                        j += 1
                        break
                    if indent_of(inner) < item_ind:
                        break
                    inner_s = inner.strip()
                    if inner_s.startswith('- '):
                        break
                    if ':' in inner_s:
                        k2, _, v2 = inner_s.partition(':')
                        obj[k2.strip()] = _unquote(v2.strip())
                    j += 1
                items.append(obj)
            else:
                items.append(_unquote(item_text))
                j += 1
        return items, j

    i = 0
    while i < n:
        ln = lines[i]
        if not ln.strip() or indent_of(ln) != 0:
            i += 1
            continue
        if ':' not in ln:
            i += 1
            continue
        key, _, rest = ln.strip().partition(':')
        key = key.strip()
        rest = rest.strip()

        if rest == '>':
            val, i = collect_block_scalar(i + 1)
            result[key] = val
        elif rest == '':
            j = i + 1
            while j < n and not lines[j].strip():
                j += 1
            if j < n and indent_of(lines[j]) > 0:
                if lines[j].strip().startswith('- '):
                    result[key], i = collect_list(i + 1, 0)
                else:
                    result[key], i = collect_object(i + 1, 0)
            else:
                result[key] = None
                i += 1
        else:
            result[key] = _unquote(rest)
            i += 1

    return result


def split_source(text):
    """Split a V2 .md file into (frontmatter_text, body_text)."""
    if not text.startswith('---'):
        raise ValueError("File does not begin with YAML frontmatter delimiter '---'")
    second = text.index('---', 3)
    fm = text[3:second].strip()
    body = text[second + 3:].strip()
    return fm, body


# ─── Markdown Body → HTML ───────────────────────────────────────────────────

def md_inline(text):
    """Apply inline Markdown: bold, links. HTML pass-through unchanged."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text


def md_body_to_html(body):
    """Convert Markdown article body to HTML string."""
    lines = body.split('\n')

    # Group lines into blocks separated by blank lines
    blocks, current = [], []
    for line in lines:
        if line.strip() == '':
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(line)
    if current:
        blocks.append(current)

    parts = []
    for block in blocks:
        first = block[0].strip()

        if first.startswith('## '):
            parts.append(f'<h2>{md_inline(first[3:].strip())}</h2>')

        elif first.startswith('### '):
            parts.append(f'<h3>{md_inline(first[4:].strip())}</h3>')

        elif first.startswith('| '):
            # Table: skip separator rows (only dashes/pipes/spaces)
            data_rows = [
                ln.strip() for ln in block
                if ln.strip() and not re.match(r'^\|[\s\-|]+\|$', ln.strip())
            ]
            if data_rows:
                html_rows = []
                for ri, row in enumerate(data_rows):
                    cells = [c.strip() for c in row.strip('|').split('|')]
                    if ri == 0:
                        html_rows.append(
                            '<tr>' + ''.join(f'<th>{md_inline(c)}</th>' for c in cells) + '</tr>'
                        )
                    else:
                        html_rows.append(
                            '<tr>' + ''.join(f'<td>{md_inline(c)}</td>' for c in cells) + '</tr>'
                        )
                parts.append(f'<table class="ia-method-table">{"".join(html_rows)}</table>')

        elif first.startswith('- '):
            items = []
            for ln in block:
                s = ln.strip()
                if s.startswith('- '):
                    items.append(md_inline(s[2:]))
                elif items:
                    items[-1] += ' ' + md_inline(s)
            li_html = ''.join(f'<li>{item}</li>' for item in items)
            parts.append(f'<ul>{li_html}</ul>')

        elif re.match(r'^<(div|table|aside|section|figure|blockquote|details|ul|ol)', first):
            parts.append('\n'.join(block))

        else:
            text = ' '.join(ln.strip() for ln in block)
            parts.append(f'<p>{md_inline(text)}</p>')

    return '\n\n'.join(parts)


# ─── Helpers ────────────────────────────────────────────────────────────────

def format_updated(date_str):
    """Format YYYY-MM-DD as 'månad år' in Swedish."""
    d = datetime.strptime(date_str, '%Y-%m-%d')
    return f"{SWEDISH_MONTHS[d.month]} {d.year}"


def page_title(title):
    """Build <title> content, truncating the title part if total exceeds 60 chars."""
    suffix = " | LevNytt"
    if len(title) + len(suffix) <= 60:
        return f"{title}{suffix}"
    max_t = 60 - len(suffix) - 1  # 1 char for ellipsis
    return f"{title[:max_t].rstrip()}…{suffix}"


def attr(s):
    """Escape a string for use in an HTML attribute value."""
    return s.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')


def build_json_ld(data, canonical_url):
    """Build the JSON-LD @graph (Article + FAQPage)."""
    graph = [
        {
            "@type": "Article",
            "headline": data['title'],
            "datePublished": data['updated'],
            "dateModified": data['updated'],
            "author": {
                "@type": "Person",
                "name": data['author']['name'],
                "url": data['author']['url'],
            },
            "publisher": {
                "@type": "Organization",
                "name": "LevNytt",
            },
        },
        {
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": item['q'],
                    "acceptedAnswer": {"@type": "Answer", "text": item['a']},
                }
                for item in data['faq']
            ],
        },
    ]
    return json.dumps(
        {"@context": "https://schema.org", "@graph": graph},
        ensure_ascii=False, indent=2
    )


# ─── HTML Assembly ──────────────────────────────────────────────────────────

def build_html(data, body_html):
    """Assemble a full PAS V1.0 HTML document from parsed frontmatter + body."""
    slug = data['slug']
    title = data['title']
    description = data['description']
    canonical_url = f"{BASE_URL}/{slug}"
    ptitle = page_title(title)
    updated_sv = format_updated(data['updated'])
    reading_time = data['reading_time']
    author = data['author']
    cta = data['cta']
    cta_sec = data.get('cta_secondary')
    topic = title.split(' — ')[0].split(' - ')[0].lower()

    # Tierbox HTML
    tier_items = []
    for t in data['tierbox']:
        tier_items.append(
            f'<a class="ia-tier" target="_blank" rel="noopener noreferrer"'
            f' href="{attr(t["url"])}"><b>{attr(t["label"])}</b>{attr(t["title"])}</a>'
        )
    tierbox_html = '\n'.join(tier_items)

    # Takeaways HTML (items may contain raw HTML, so pass through)
    takeaways_html = '\n'.join(f'<li>{item}</li>' for item in data['takeaways'])

    # FAQ HTML
    faq_items = []
    for item in data['faq']:
        faq_items.append(
            f'<details><summary>{attr(item["q"])}</summary>\n'
            f'<p>{attr(item["a"])}</p>\n'
            f'</details>'
        )
    faq_html = '\n\n'.join(faq_items)

    # CTA secondary
    cta_secondary_html = ''
    if cta_sec:
        cta_secondary_html = (
            f'\n<p class="ia-cta-secondary">'
            f'<a style="color:#F9F6EF;text-decoration:underline"'
            f' target="_blank" rel="noopener noreferrer"'
            f' href="{attr(cta_sec["url"])}">{attr(cta_sec["text"])}</a>'
            f'</p>'
        )

    json_ld = build_json_ld(data, canonical_url)

    return f"""<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{attr(ptitle)}</title>
<meta name="description" content="{attr(description)}">
<meta name="robots" content="index, follow, max-snippet:-1, max-video-preview:-1, max-image-preview:large">
<link rel="canonical" href="{canonical_url}">
<meta property="og:type" content="article">
<meta property="og:title" content="{attr(title)}">
<meta property="og:description" content="{attr(description)}">
<meta property="og:url" content="{canonical_url}">
<meta property="og:site_name" content="LevNytt">
<meta property="og:locale" content="sv_SE">
<meta property="og:image" content="{OG_IMAGE}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{attr(OG_IMAGE_ALT)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{attr(title)}">
<meta name="twitter:description" content="{attr(description)}">
<meta name="google-site-verification" content="{GOOGLE_VERIFY}">
<meta name="p:domain_verify" content="{PINTEREST_VERIFY}"/>
<script type="application/ld+json">
{json_ld}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/pillar.css">
<style>
{IA_CSS}
</style>
</head>
<body>
<div id="site-nav"></div>
<script src="/nav.js" defer></script>

<div class="ia-wrap">
<article>

<p style="font-size:0.85em;color:#888;text-transform:uppercase;letter-spacing:0.05em">{attr(data["category"])}</p>

<div class="ia-eyebrow">{attr(data["eyebrow"])}</div>
<h1>{attr(title)}</h1>

<p>Av <a target="_blank" rel="noopener noreferrer" href="{attr(author["url"])}">{attr(author["name"])}</a> · Senast uppdaterad: {updated_sv} · {reading_time} min läsning</p>

<p class="ia-punchline">{data["punchline"]}</p>

<div class="ia-takeaways">
<h3>Key Takeaways</h3>
<ul>
{takeaways_html}
</ul>
</div>

{body_html}

<div class="ia-tierbox">
{tierbox_html}
</div>


<div class="ia-method-note">
<strong>Metod:</strong> {attr(data["method_note"])}
</div>

<div class="ia-cta">
<h3>{attr(cta["headline"])}</h3>
<p>{attr(cta["body"])}</p>
<a target="_blank" rel="noopener noreferrer" href="{attr(cta["url"])}">{attr(cta["link_text"])}</a>{cta_secondary_html}
</div>

<div class="ia-faq">
<h2>Vanliga frågor om {attr(topic)}</h2>

{faq_html}
</div>

<p class="ia-disclosure">{data["disclosure"]}</p>

<div class="ia-author-box">
<div class="ia-author-avatar">{attr(author["initials"])}</div>
<div>
<strong>{attr(author["name"])}</strong><br>
{attr(author["bio"])} <a href="{attr(author["url"])}">Läs mer →</a>
</div>
</div>

<p class="ia-disclosure">{LEGAL_DISCLOSURE}</p>

</article>
</div>
<script src="/footer.js" defer></script>
<script src="/components.js" defer></script>
</body>
</html>"""


# ─── Validation ─────────────────────────────────────────────────────────────

def validate(data):
    """Return a list of error strings. Empty list = valid."""
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in data or data[field] is None:
            errors.append(f"Missing required field: '{field}'")

    if errors:
        return errors  # stop early — later checks assume fields exist

    if len(data['description']) > 155:
        errors.append(
            f"description too long: {len(data['description'])} chars (max 155)"
        )

    if len(page_title(data['title'])) > 60:
        errors.append(
            f"<title> too long after suffix: {len(page_title(data['title']))} chars (max 60)"
        )

    if not isinstance(data['tierbox'], list) or len(data['tierbox']) != 4:
        errors.append(
            f"tierbox must have exactly 4 items (found {len(data['tierbox']) if isinstance(data['tierbox'], list) else 'non-list'})"
        )

    if not isinstance(data['faq'], list) or not (6 <= len(data['faq']) <= 10):
        n = len(data['faq']) if isinstance(data['faq'], list) else 'non-list'
        errors.append(f"faq must have 6–10 items (found {n})")

    cta = data.get('cta', {})
    if isinstance(cta, dict):
        for sub in ('headline', 'body', 'url', 'link_text'):
            if sub not in cta:
                errors.append(f"cta.{sub} is required")

    author = data.get('author', {})
    if not isinstance(author, dict):
        errors.append("author must be a mapping")
    else:
        for sub in ('name', 'url', 'initials', 'bio'):
            if sub not in author:
                errors.append(f"author.{sub} is required")
        if 'initials' in author:
            if not re.match(r'^[A-Z]{2}$', str(author['initials'])):
                errors.append(f"author.initials must be exactly 2 uppercase letters (got '{author['initials']}')")

    return errors


# ─── Entry point ────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/md-to-article.py <slug>", file=sys.stderr)
        sys.exit(1)

    slug = sys.argv[1].strip('/')
    src_path = REPO_ROOT / 'content' / 'articles' / slug / f'{slug}.md'

    if not src_path.exists():
        print(f"ERROR: Source file not found: {src_path.relative_to(REPO_ROOT)}", file=sys.stderr)
        sys.exit(1)

    raw = src_path.read_text(encoding='utf-8')

    try:
        fm_text, body_text = split_source(raw)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    data = parse_frontmatter(fm_text)

    errors = validate(data)
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    # Verify slug consistency
    if data.get('slug') != slug:
        print(
            f"ERROR: frontmatter slug '{data.get('slug')}' does not match directory slug '{slug}'",
            file=sys.stderr,
        )
        sys.exit(1)

    body_html = md_body_to_html(body_text)
    html = build_html(data, body_html)

    out_path = REPO_ROOT / 'content' / 'articles' / slug / f'{slug}.html'
    out_path.write_text(html, encoding='utf-8')

    print(f"OK: {out_path.relative_to(REPO_ROOT)}")


if __name__ == '__main__':
    main()
