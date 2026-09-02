"""Shared, deterministic LevNytt production renderer.

The renderer owns the public document shell, metadata normalization and link
policy. Editorial markup remains page-specific and is preserved verbatim apart
from unsafe event handlers, inline presentation and obsolete shared shells.
"""
from __future__ import annotations

import html as html_lib
import base64
import hashlib
import json
import re
import struct
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

SITE = "https://levnytt.se"
SITE_HOSTS = {"levnytt.se", "www.levnytt.se"}
SPONSOR_ID = "41-830928"
OG_IMAGE = f"{SITE}/assets/brand/og-brand.png"
GOOGLE_VERIFY = "kAcoLDFGCpGh42gIFRgPeWlC253vTP3OLBs6wI8KDQ0"
PINTEREST_VERIFY = "6a9e88f7014abe0735767f464c08f337"


def asset_url(root: Path, href: str) -> str:
    """Return a content-versioned URL for a repository-owned static asset."""
    if not href.startswith("/") or "?" in href:
        return href
    path = root / href.lstrip("/")
    if not path.is_file():
        return href
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    return f"{href}?v={digest}"


FAMILY_LABELS = {
    "sv": {
        "home-editorial-hub": "Redaktionell kunskapsplattform",
        "library-category-index": "Kunskapsbibliotek",
        "utility-legal": "Information",
        "authority-editorial-trust": "Om LevNytt",
        "product-category": "Produkter och konsumentkunskap",
        "informational-article": "Konsumentguide",
    },
    "no": {
        "home-editorial-hub": "Kunnskapsplattform",
        "library-category-index": "Artikkelbibliotek",
        "utility-legal": "Informasjon",
        "authority-editorial-trust": "Om LevNytt",
        "product-category": "Produkter og forbrukerkunnskap",
        "informational-article": "Forbrukerguide",
    },
}


def family_for(public_path: str) -> str:
    name = Path(public_path.rstrip("/") or "index").name
    if public_path in {"/", "/no/", "/no"}:
        return "home-editorial-hub"
    if name == "artiklar":
        return "library-category-index"
    if name in {"integritetspolicy", "404"}:
        return "utility-legal"
    if name in {"om-oss", "den-fundersamma-mannen", "var-metod", "levnytt-principer"}:
        return "authority-editorial-trust"
    if name.startswith("neolife-") or name in {"golden-home-care", "personlig-vard", "super-10"}:
        return "product-category"
    return "informational-article"


def canonical_href(href: str) -> str:
    fragment_aliases = {
        "vem-behöver-kosttillskott": "vem-behover-verkligen-kosttillskott",
        "vitamin-d-undantaget": "vitamin-d-undantaget-varfor-galler-andra-regler",
        "kostnader-onödig-användning": "risker-med-onodig-kosttillskottsanvandning",
        "risker-överdosering": "risker-med-onodig-kosttillskottsanvandning",
    }
    if href.strip().startswith("#"):
        fragment = href.strip()[1:]
        return "#" + fragment_aliases.get(fragment, fragment)
    split = urlsplit(href.strip())
    if split.scheme in {"mailto", "tel"}:
        return href
    if split.netloc and (split.hostname or "").lower() not in SITE_HOSTS:
        return href
    if split.scheme and split.scheme not in {"http", "https"}:
        return href
    if split.path == "/" and split.fragment and not split.query:
        return "#" + fragment_aliases.get(split.fragment, split.fragment)
    path = re.sub(r"/{2,}", "/", split.path or "/")
    if path.endswith(".html"):
        path = path[:-5] or "/"
    if not path.startswith("/"):
        path = "/" + path
    stale_routes = {
        "/pro-vitality": "/neolife-pro-vitality",
        "/content/articles/neolife-vetenskap": "/neolife-vetenskap",
        "/produkter/neolife-vitamin-d": "/neolife-vitamin-d",
        "/content/articles/varfor-tar-d-vitamin-slut-pa-ditt-magnesium": "/varfor-tar-d-vitamin-slut-pa-ditt-magnesium",
        "/omega-3-salmon-oil-plus": "/neolife-omega-3-plus",
    }
    path = stale_routes.get(path.rstrip("/"), path)
    return urlunsplit(("", "", path, split.query, split.fragment))


def sponsored_shop_href(href: str) -> str:
    split = urlsplit(href)
    if (split.hostname or "").lower() not in {"se.neolifeshop.com", "www.neolifeshop.com"}:
        return href
    query = dict(parse_qsl(split.query, keep_blank_values=True))
    if not query.get("sponsor") and not query.get("sponsorId"):
        query["sponsor"] = SPONSOR_ID
    return urlunsplit((split.scheme or "https", split.netloc, split.path, urlencode(query), split.fragment))


def serialise_attrs(attrs: list[tuple[str, str | None]]) -> str:
    return "".join(
        f" {name}" if value is None else f' {name}="{html_lib.escape(value, quote=True)}"'
        for name, value in attrs
    )


def image_dimensions_bytes(data: bytes) -> tuple[int, int] | None:
    try:
        if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
            return struct.unpack(">II", data[16:24])
        if data.startswith(b"\xff\xd8"):
            offset = 2
            while offset + 9 < len(data):
                if data[offset] != 0xFF:
                    offset += 1
                    continue
                marker = data[offset + 1]
                if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                    height, width = struct.unpack(">HH", data[offset + 5:offset + 9])
                    return width, height
                if offset + 4 > len(data): break
                offset += 2 + struct.unpack(">H", data[offset + 2:offset + 4])[0]
        if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
            kind = data[12:16]
            if kind == b"VP8X" and len(data) >= 30:
                return 1 + int.from_bytes(data[24:27], "little"), 1 + int.from_bytes(data[27:30], "little")
            if kind == b"VP8 " and len(data) >= 30:
                return int.from_bytes(data[26:28], "little") & 0x3FFF, int.from_bytes(data[28:30], "little") & 0x3FFF
            if kind == b"VP8L" and len(data) >= 25 and data[20] == 0x2F:
                bits = int.from_bytes(data[21:25], "little")
                return 1 + (bits & 0x3FFF), 1 + ((bits >> 14) & 0x3FFF)
    except (IndexError, struct.error):
        return None
    return None


def image_dimensions(path: Path) -> tuple[int, int] | None:
    """Read common raster dimensions without adding an image dependency."""
    try:
        return image_dimensions_bytes(path.read_bytes())
    except (OSError, struct.error):
        return None
    return None


def materialise_data_image(root: Path, source: str) -> tuple[str, tuple[int, int] | None] | None:
    match = re.fullmatch(r"data:image/(png|jpeg|webp);base64,([A-Za-z0-9+/=\s]+)", source, re.I)
    if not match:
        return None
    try:
        data = base64.b64decode(match.group(2), validate=False)
    except (ValueError, base64.binascii.Error):
        return None
    if not data or len(data) > 5_000_000:
        return None
    extension = {"jpeg": "jpg", "png": "png", "webp": "webp"}[match.group(1).lower()]
    relative = Path("images/generated") / f"{hashlib.sha256(data).hexdigest()[:20]}.{extension}"
    destination = root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.is_file():
        destination.write_bytes(data)
    return "/" + relative.as_posix(), image_dimensions_bytes(data)


def normalise_attrs(tag: str, attrs: list[tuple[str, str | None]], root: Path | None = None, image_index: int = 0) -> list[tuple[str, str | None]]:
    values = {name.lower(): value for name, value in attrs}
    filtered = [(name, value) for name, value in attrs if name.lower() != "style" and not name.lower().startswith("on")]
    if tag == "img" and values.get("src") == "/images/author/den-fundersamma-mannen.jpg":
        filtered = [(name, "/images/jarmo-halonen.jpg" if name.lower() == "src" else value) for name, value in filtered]
        values["src"] = "/images/jarmo-halonen.jpg"
    if tag == "img":
        filtered = [(name, value) for name, value in filtered if name.lower() not in {"width", "height", "loading", "fetchpriority", "decoding"}]
        src = values.get("src") or ""
        materialised = materialise_data_image(root, src) if root and src.startswith("data:image/") else None
        if materialised:
            src, dimensions = materialised
            filtered = [(name, src if name.lower() == "src" else value) for name, value in filtered]
        else:
            dimensions = image_dimensions(root / src.lstrip("/")) if root and src.startswith("/") else None
        if dimensions:
            filtered.extend((("width", str(dimensions[0])), ("height", str(dimensions[1]))))
        if image_index == 0:
            filtered.extend((("loading", "eager"), ("fetchpriority", "high")))
        else:
            filtered.append(("loading", "lazy"))
        filtered.append(("decoding", "async"))
    if tag != "a" or not values.get("href"):
        return filtered

    href = values["href"] or ""
    split = urlsplit(href)
    external = bool(split.netloc and (split.hostname or "").lower() not in SITE_HOSTS)
    rel = set((values.get("rel") or "").lower().split())
    filtered = [(name, value) for name, value in filtered if name.lower() not in {"href", "target", "rel"}]
    if external:
        href = sponsored_shop_href(href)
        filtered.append(("href", href))
        filtered.append(("target", "_blank"))
        rel.update({"noopener", "noreferrer"})
        if "neolifeshop.com" in (split.hostname or "").lower():
            rel.update({"nofollow", "sponsored"})
        filtered.append(("rel", " ".join(sorted(rel))))
    else:
        filtered.append(("href", canonical_href(href)))
        rel.difference_update({"noopener", "noreferrer"})
        if rel:
            filtered.append(("rel", " ".join(sorted(rel))))
    return filtered


class FragmentCleaner(HTMLParser):
    """Remove legacy shells and inline presentation while retaining content."""

    def __init__(self, root: Path | None = None) -> None:
        super().__init__(convert_charrefs=False)
        self.out: list[str] = []
        self.skip_depth = 0
        self.root = root
        self.image_index = 0
        self.tag_stack: list[tuple[str, bool]] = []

    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    @staticmethod
    def _values(attrs: list[tuple[str, str | None]]) -> dict[str, str | None]:
        return {name.lower(): value for name, value in attrs}

    def _is_skip(self, tag: str, attrs: list[tuple[str, str | None]]) -> bool:
        values = self._values(attrs)
        classes = set((values.get("class") or "").split())
        if tag in {"script", "style", "footer"} or tag == "h1":
            return True
        if tag == "header" and "ln-site-header" in classes:
            return True
        if tag == "header" and "ln-article-header" in classes:
            return True
        if tag == "nav" and (values.get("id") in {"site-nav", "levnytt-nav", "ln-primary-nav"} or "ln-primary-nav" in classes):
            return True
        if tag == "header" and classes.intersection({"masthead", "site-header", "legacy-header"}):
            return True
        if values.get("id") == "site-nav" or "ln-skip-link" in classes or any("breadcrumb" in value for value in classes):
            return True
        return False

    @staticmethod
    def _is_transparent(tag: str, attrs: list[tuple[str, str | None]]) -> bool:
        classes = set((FragmentCleaner._values(attrs).get("class") or "").split())
        return tag in {"body", "main", "article"} or (tag == "div" and bool(classes.intersection({"ln-shell", "ln-article-body"})))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if self.skip_depth:
            if tag not in self.VOID_TAGS:
                self.skip_depth += 1
            return
        if self._is_skip(tag, attrs):
            if tag not in self.VOID_TAGS:
                self.skip_depth = 1
            return
        emitted = not self._is_transparent(tag, attrs)
        if tag not in self.VOID_TAGS:
            self.tag_stack.append((tag, emitted))
        if emitted:
            self.out.append("<" + tag + serialise_attrs(normalise_attrs(tag, attrs, self.root, self.image_index)) + ">")
        if tag == "img":
            self.image_index += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if not self.skip_depth:
            self.out.append("<" + tag + serialise_attrs(normalise_attrs(tag.lower(), attrs, self.root, self.image_index)) + "/>")
            if tag.lower() == "img":
                self.image_index += 1

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self.skip_depth:
            self.skip_depth -= 1
            return
        if self.tag_stack:
            opened, emitted = self.tag_stack.pop()
            if emitted:
                self.out.append(f"</{opened}>")

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


class HeadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.title = ""
        self._in_title = False
        self._in_jsonld = False
        self._json_parts: list[str] = []
        self.jsonld: list[str] = []
        self.meta: dict[tuple[str, str], str] = {}
        self.alternates: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name.lower(): value or "" for name, value in attrs}
        if tag.lower() == "title":
            self._in_title = True
        elif tag.lower() == "meta":
            for key in ("name", "property", "http-equiv"):
                if values.get(key) and "content" in values:
                    self.meta[(key, values[key].lower())] = values["content"]
                    break
        elif tag.lower() == "link" and "alternate" in values.get("rel", "").lower().split() and values.get("href"):
            self.alternates.append(values)
        elif tag.lower() == "script" and values.get("type", "").lower() == "application/ld+json":
            self._in_jsonld = True
            self._json_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False
        elif tag.lower() == "script" and self._in_jsonld:
            self.jsonld.append("".join(self._json_parts).strip())
            self._in_jsonld = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        elif self._in_jsonld:
            self._json_parts.append(data)


def first_text(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html_lib.unescape(text)).strip()


def heading_slug(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", ascii_value))


def add_heading_ids(fragment: str) -> str:
    used = set(re.findall(r'\bid=["\']([^"\']+)', fragment, re.I))
    def replace(match: re.Match[str]) -> str:
        tag, attributes, content = match.group(1), match.group(2), match.group(3)
        if re.search(r"\bid=[\"']", attributes, re.I):
            return match.group(0)
        base = heading_slug(first_text(content)) or "avsnitt"
        candidate = base; number = 2
        while candidate in used:
            candidate = f"{base}-{number}"; number += 1
        used.add(candidate)
        return f'<{tag}{attributes} id="{candidate}">{content}</{tag}>'
    return re.sub(r'<(h[23])\b([^>]*)>(.*?)</\1>', replace, fragment, flags=re.I | re.S)


def source_tokens(fragment: str) -> list[str]:
    """Return stable editorial tokens used by rebuild preservation tests."""
    text = first_text(re.sub(r"<(?:nav|footer|script|style)\b.*?</(?:nav|footer|script|style)\s*>", " ", fragment, flags=re.I | re.S))
    return sorted(set(re.findall(r"[\wåäöÅÄÖ]{4,}", text.casefold())))


def _head_fragment(source: str) -> str:
    match = re.search(r"<head\b[^>]*>(.*?)</head\s*>", source, re.I | re.S)
    if match:
        return match.group(1)
    before_body = re.split(r"<body\b", source, maxsplit=1, flags=re.I)[0]
    return re.sub(r"^.*?<html\b[^>]*>", "", before_body, count=1, flags=re.I | re.S)


def _body_fragment(source: str) -> str:
    match = re.search(r"<body\b[^>]*>(.*?)</body\s*>", source, re.I | re.S)
    return match.group(1) if match else source


def _extract_language(source: str, public_path: str) -> str:
    match = re.search(r"<html\b[^>]*\blang=[\"']([^\"']+)", source, re.I)
    value = (match.group(1) if match else ("no" if public_path.startswith("/no") else "sv")).lower()
    return "no" if value.startswith(("no", "nb", "nn")) else "sv"


def _normalise_schema(value, canonical: str, page_name: str = ""):
    if isinstance(value, list):
        return [_normalise_schema(item, canonical, page_name) for item in value]
    if not isinstance(value, dict):
        return value
    result = {key: _normalise_schema(item, canonical, page_name) for key, item in value.items()}
    schema_type = result.get("@type")
    if schema_type in {"Article", "WebPage", "CollectionPage", "Product", "WebSite"}:
        if schema_type != "WebSite" or canonical.rstrip("/") == SITE:
            if "url" in result:
                result["url"] = canonical
            if isinstance(result.get("@id"), str) and result["@id"].startswith(SITE):
                fragment = urlsplit(result["@id"]).fragment
                result["@id"] = canonical + (f"#{fragment}" if fragment else "")
            main = result.get("mainEntityOfPage")
            if isinstance(main, dict):
                main["@id"] = canonical
            elif isinstance(main, str):
                result["mainEntityOfPage"] = canonical
    if schema_type == "FAQPage" and isinstance(result.get("@id"), str):
        result["@id"] = canonical + "#faq"
    if schema_type == "BreadcrumbList":
        result["itemListElement"] = [
            {"@type": "ListItem", "position": 1, "name": "LevNytt", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": page_name, "item": canonical},
        ]
    if schema_type == "WebSite":
        result.pop("potentialAction", None)
    return result


def _visible_faq(body_html: str) -> list[dict]:
    pairs = re.findall(r"<details\b[^>]*>\s*<summary\b[^>]*>(.*?)</summary>\s*(.*?)</details>", body_html, re.I | re.S)
    questions = []
    for question, answer in pairs:
        q = first_text(question)
        a = first_text(answer)
        if q and a:
            questions.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}})
    return questions


def _fallback_schema(page: dict, body_html: str) -> dict:
    canonical = page["url"]
    family = page["family"]
    kind = "Article" if family == "informational-article" else "WebPage"
    primary = {
        "@type": kind,
        "headline" if kind == "Article" else "name": page["h1"],
        "description": page["description"],
        "url": canonical,
        "inLanguage": page["language"],
        "publisher": {"@type": "Organization", "name": "LevNytt", "url": SITE},
    }
    if kind == "Article":
        primary["mainEntityOfPage"] = {"@type": "WebPage", "@id": canonical}
        if page.get("date_published"):
            primary["datePublished"] = page["date_published"]
        if page.get("date_modified"):
            primary["dateModified"] = page["date_modified"]
        if page.get("author"):
            primary["author"] = {"@type": "Person", "name": page["author"]}
    graph = [primary]
    faq = _visible_faq(body_html)
    if faq:
        graph.append({"@type": "FAQPage", "mainEntity": faq})
    return {"@context": "https://schema.org", "@graph": graph}


def render_head(page: dict, body_html: str, root: Path) -> str:
    parser = HeadParser()
    parser.feed(page["head_html"])
    meta = parser.meta
    title = parser.title.strip() or page["title"] or page["h1"]
    description = meta.get(("name", "description"), "").strip() or page["description"] or page["h1"]
    canonical = page["url"]
    language = page["language"]
    locale = "no_NO" if language == "no" else "sv_SE"
    robots = meta.get(("name", "robots"), "index, follow, max-snippet:-1, max-image-preview:large")
    if page["path"] == "/404":
        robots = "noindex, follow"

    og_image = meta.get(("property", "og:image"), OG_IMAGE)
    if og_image.startswith(SITE + "/") and not (root / urlsplit(og_image).path.lstrip("/")).is_file():
        og_image = OG_IMAGE

    name_meta = {
        "description": description,
        "robots": robots,
        "twitter:card": meta.get(("name", "twitter:card"), "summary_large_image"),
        "twitter:title": meta.get(("name", "twitter:title"), title),
        "twitter:description": meta.get(("name", "twitter:description"), description),
        "google-site-verification": meta.get(("name", "google-site-verification"), GOOGLE_VERIFY),
        "p:domain_verify": meta.get(("name", "p:domain_verify"), PINTEREST_VERIFY),
    }
    property_meta = {
        "og:type": meta.get(("property", "og:type"), "article" if page["family"] == "informational-article" else "website"),
        "og:title": meta.get(("property", "og:title"), title),
        "og:description": meta.get(("property", "og:description"), description),
        "og:url": canonical,
        "og:site_name": "LevNytt",
        "og:locale": locale,
        "og:image": og_image,
        "og:image:width": meta.get(("property", "og:image:width"), "1200"),
        "og:image:height": meta.get(("property", "og:image:height"), "630"),
        "og:image:alt": meta.get(("property", "og:image:alt"), "LevNytt"),
    }

    schemas = []
    for raw in parser.jsonld:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            cleaned = re.sub(r"<[^>]+>", "", raw)
            cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)
            try:
                parsed = json.loads(cleaned)
            except json.JSONDecodeError:
                continue
        schemas.append(_normalise_schema(parsed, canonical, page["h1"]))
    if not schemas:
        schemas = [_fallback_schema({**page, "description": description}, body_html)]

    style_hrefs = [
        "/assets/css/levnytt-foundations.css",
        "/assets/css/levnytt-components.css",
        "/assets/css/levnytt-rebuild.css",
        "/assets/css/editorial-components.css",
    ]
    if page["family"] == "informational-article":
        style_hrefs.append("/assets/css/informational-article.css")
    if page["family"] == "authority-editorial-trust":
        style_hrefs.append("/assets/css/authority-trust.css")
    if page["family"] == "home-editorial-hub":
        style_hrefs.append("/assets/css/home.css")
    if page["family"] == "library-category-index":
        style_hrefs.append("/assets/css/article-index.css")
    if page["path"] == "/finns-det-billigare-alternativ":
        style_hrefs.append("/assets/css/savings-calculator.css")

    lines = [
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f"<title>{html_lib.escape(title)}</title>",
    ]
    lines += [f'<meta name="{html_lib.escape(key)}" content="{html_lib.escape(value, quote=True)}">' for key, value in name_meta.items() if value]
    if page["path"] != "/404":
        lines.append(f'<link rel="canonical" href="{html_lib.escape(canonical, quote=True)}">')
    lines += [f'<meta property="{html_lib.escape(key)}" content="{html_lib.escape(value, quote=True)}">' for key, value in property_meta.items() if value]
    for alternate in parser.alternates:
        if alternate.get("hreflang") and alternate.get("href"):
            lines.append(f'<link rel="alternate" hreflang="{html_lib.escape(alternate["hreflang"], quote=True)}" href="{html_lib.escape(alternate["href"], quote=True)}">')
    lines += [
        '<link rel="icon" href="/assets/brand/favicon.svg" type="image/svg+xml">',
        '<link rel="apple-touch-icon" href="/assets/brand/apple-touch-icon.png">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600;700&display=swap">',
    ]
    lines += [f'<link rel="stylesheet" href="{asset_url(root, href)}">' for href in style_hrefs]
    for schema in schemas:
        lines.append('<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False, separators=(",", ":")) + "</script>")
    lines += [
        f'<meta name="levnytt-template" content="rebuild-{page["family"]}">',
        '<meta name="levnytt-cta" content="existing-content-cta">',
    ]
    return "\n".join(lines)


def _fragment(root: Path, name: str, language: str) -> str:
    return (root / "assets" / "fragments" / f"{name}-{language}.html").read_text(encoding="utf-8").strip()


def _mark_active(header: str, current_path: str) -> str:
    def replace(match: re.Match[str]) -> str:
        tag = match.group(0)
        href_match = re.search(r'href="([^"]+)"', tag)
        if not href_match:
            return tag
        href = urlsplit(href_match.group(1)).path.rstrip("/") or "/"
        current = current_path.rstrip("/") or "/"
        active = current == href
        if href == "/neolife-kosttillskott" and current.startswith("/neolife-") and current not in {"/neolife-historia", "/neolife-vetenskap", "/neolife-affarsmojlighet"}:
            active = True
        return tag[:-1] + ' aria-current="page">' if active and "aria-current" not in tag else tag
    return re.sub(r"<a\b[^>]*>", replace, header, flags=re.I)


def render_page(page: dict, root: Path) -> str:
    cleaner = FragmentCleaner(root)
    cleaner.feed(page["body_html"])
    body_html = re.sub(r"[ \t]+(?=\n)", "", "".join(cleaner.out))
    body_html = body_html.replace(">Key Takeaways<", ">Det viktigaste<")
    body_html = re.sub(
        r'<p\b[^>]*class=["\'][^"\']*ia-disclosure[^"\']*["\'][^>]*>\s*Denna artikel handlar om.*?</p>',
        "",
        body_html,
        flags=re.I | re.S,
    )
    body_html = add_heading_ids(body_html)
    language = page["language"]
    label = FAMILY_LABELS[language][page["family"]]
    header = _mark_active(_fragment(root, "header", language), page["path"])
    footer = _fragment(root, "footer", language)
    if page["path"] in {"/", "/no", "/no/"}:
        breadcrumbs = ""
    else:
        home_href = "/no/" if language == "no" else "/"
        home_label = "LevNytt Norge" if language == "no" else "LevNytt"
        breadcrumb_label = "Brødsmuler" if language == "no" else "Brödsmulor"
        breadcrumbs = (
            f'<nav class="ln-breadcrumbs" aria-label="{breadcrumb_label}">'
            f'<a href="{home_href}">{home_label}</a> <span aria-hidden="true">›</span> '
            f'<span aria-current="page">{html_lib.escape(page["h1"])}</span></nav>'
        )
    scripts = [f'<script src="{asset_url(root, "/assets/js/levnytt-rebuild.js")}" defer></script>']
    if page["family"] == "library-category-index":
        scripts.append(f'<script src="{asset_url(root, "/assets/js/article-index.js")}" defer></script>')
    if page["path"] == "/finns-det-billigare-alternativ":
        scripts.append(f'<script src="{asset_url(root, "/assets/js/savings-calculator.js")}" defer></script>')
    head = render_head(page, body_html, root)
    skip_label = "Hopp til innhold" if language == "no" else "Hoppa till innehåll"
    return (
        '<!doctype html>\n'
        f'<html lang="{language}">\n<head>\n{head}\n</head>\n'
        f'<body data-template-family="{page["family"]}">\n'
        f'<a class="ln-skip-link" href="#main-content">{skip_label}</a>\n{header}\n'
        f'<main id="main-content" class="ln-page ln-family-{page["family"]}"><div class="ln-shell">{breadcrumbs}'
        f'<article><header class="ln-article-header"><p class="ln-eyebrow">LevNytt · {html_lib.escape(label)}</p>'
        f'<h1>{html_lib.escape(page["h1"])}</h1></header><div class="ln-article-body">{body_html}</div></article>'
        f'</div></main>\n{footer}\n' + "\n".join(scripts) + "\n</body>\n</html>\n"
    )


def extract_document(url: str, source: str, source_name: str, root: Path) -> dict:
    public_path = urlsplit(url).path or "/"
    head_html = _head_fragment(source)
    body = _body_fragment(source)
    head_parser = HeadParser()
    head_parser.feed(head_html)
    title = head_parser.title.strip() or Path(source_name).stem.replace("-", " ").title()
    h1_match = re.search(r"<h1\b[^>]*>(.*?)</h1\s*>", body, re.I | re.S)
    h1 = first_text(h1_match.group(1)) if h1_match else title.split(" | ", 1)[0]
    cleaner = FragmentCleaner(root)
    cleaner.feed(body)
    cleaned = "".join(cleaner.out).strip()
    cleaned = re.sub(r'\sstyle=["\']\s*stop-color\s*:\s*([^;"\']+)\s*["\']', r' stop-color="\1"', cleaned, flags=re.I)
    cleaned = re.sub(r'\sstyle=["\'][^"\']*["\']', "", cleaned, flags=re.I)
    cleaned = re.sub(r"[ \t]+(?=\n)", "", cleaned)
    description = head_parser.meta.get(("name", "description"), "")
    dates = re.findall(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})"', head_html)
    modified = re.findall(r'"dateModified"\s*:\s*"(\d{4}-\d{2}-\d{2})"', head_html)
    author = "Jarmo Halonen" if "Jarmo Halonen" in source else ""
    return {
        "url": SITE + (public_path if public_path != "/" else ""),
        "path": public_path,
        "family": family_for(public_path),
        "language": _extract_language(source, public_path),
        "title": title,
        "h1": h1,
        "description": description,
        "head_html": head_html,
        "body_html": cleaned,
        "source_tokens": source_tokens(
            re.sub(
                r'<p\b[^>]*class=["\'][^"\']*ia-disclosure[^"\']*["\'][^>]*>\s*Denna artikel handlar om.*?</p>',
                "",
                cleaned.replace(">Key Takeaways<", ">Det viktigaste<"),
                flags=re.I | re.S,
            )
        ),
        "source_file": source_name,
        "date_published": dates[0] if dates else "",
        "date_modified": modified[0] if modified else "",
        "author": author,
    }


def canonicalize_html(source: str, url: str, source_name: str, root: Path) -> str:
    return render_page(extract_document(url, source, source_name, root), root)
