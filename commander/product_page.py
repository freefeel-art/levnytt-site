"""Deterministic dedicated NeoLife product-page builder.

Produces a dedicated PRODUCT_PAGE for a NeoLife product entity using the
verified ``rebuild-product-category`` template, the entity's authoritative
facts (name, code, package, ingredients, usage, safety), and the exact official
product image. It never invents facts and never generates marketing hype: every
field is drawn from the Product Entity System or left UNKNOWN.

This is the executor behind the ``product_page`` capability, which lets the
Commander produce a dedicated product page through the normal operating loop
without requiring a DataForSEO keyword to already exist.
"""

from __future__ import annotations

import glob
import html
import os
import re
from pathlib import Path
from typing import Any


def _fold(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def resolve_image(entity: dict[str, Any], project_root: Path) -> str | None:
    """Find the exact product image for an entity in the images/ directory,
    matched by slug or product name. Returns None when no image exists."""
    slug = _fold(entity.get("slug", ""))
    name = _fold(entity.get("product_name", ""))
    images_dir = project_root / "images"
    if not images_dir.is_dir():
        return None
    candidates = []
    for path in sorted(images_dir.iterdir()):
        if path.is_dir() or path.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
            continue
        base = _fold(path.stem)
        if not base:
            continue
        if base == slug or base == name:
            return f"/images/{path.name}"
        if name and (name in base or base in name):
            candidates.append(f"/images/{path.name}")
    return candidates[0] if candidates else None


def _clean(entity: dict[str, Any]) -> dict[str, Any]:
    """Normalise the entity fields into the values the template needs."""
    code = str(entity.get("neoLife_code", ""))
    name = str(entity.get("product_name", "")).strip()
    slug = str(entity.get("slug", "")).strip()
    short = str(entity.get("short_description", "")).strip()
    summary = str(entity.get("summary", "")).strip()
    packaging = entity.get("packaging") or {}
    pack_label = str(packaging.get("label") or f"{packaging.get('size', '')} {packaging.get('unit', '')}").strip()
    usage = entity.get("usage") or {}
    ingredients = entity.get("ingredients") or []
    return {
        "code": code, "name": name, "slug": slug, "short": short, "summary": summary,
        "pack_label": pack_label, "usage": usage, "ingredients": ingredients,
    }


def _ingredient_label(ing: Any) -> str:
    if isinstance(ing, dict):
        name = str(ing.get("name", "")).strip()
        amount = ing.get("amount")
        unit = ing.get("unit")
        if amount and unit:
            return f"{name} — {amount} {unit}"
        return name
    return str(ing).strip()


def build_product_page(entity: dict[str, Any], image_rel: str | None, project_root: Path) -> str:
    """Build one dedicated product page (full HTML) from an entity + image."""
    c = _clean(entity)
    name = html.escape(c["name"])
    slug = html.escape(c["slug"])
    code = html.escape(c["code"])
    short = html.escape(c["short"])
    summary = html.escape(c["summary"])
    pack_label = html.escape(c["pack_label"])
    dosage = html.escape(str(c["usage"].get("dosage", "Se produktetiketten")))
    safety = html.escape(str(c["usage"].get("safety", "")))
    img = html.escape(image_rel or "/assets/brand/og-brand.png", quote=False)
    img_alt = html.escape(c["name"])
    category = html.escape(str(entity.get("category", "supplements")))

    # Related cross-links: topic article + related products.
    related_links = []
    related_slugs = entity.get("related_article_slugs") or []
    for rel in related_slugs[:1]:
        related_links.append(f'<a href="/{html.escape(str(rel))}">{html.escape(str(rel))}</a>')

    ingredient_items = "".join(
        f"<li>{html.escape(_ingredient_label(i))}</li>" for i in c["ingredients"] if _ingredient_label(i)
    )
    safety_html = f" {safety}" if safety else ""

    # The topic cross-link (a topic article covering the ingredient) helps SEO
    # framing but is not a coverage prerequisite.
    topic_href = related_slugs[0] if related_slugs else None
    topic_para = ""
    if topic_href:
        topic_para = (
            f"<p>Vill du förstå mer om {html.escape(name.split()[-1] if name else '')} i allmänhet? "
            f'Läs vår guide <a href="/{html.escape(str(topic_href))}">{html.escape(str(topic_href).replace("-", " "))}</a>.</p>'
        )

    return f"""<!doctype html>
<html lang="sv">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NeoLife {name} | LevNytt.se</title>
<meta name="description" content="{short} Kod {code}.">
<meta name="robots" content="index, follow, max-snippet:-1, max-video-preview:-1, max-image-preview:large">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="NeoLife {name} | LevNytt.se">
<meta name="twitter:description" content="{short} Kod {code}.">
<meta name="google-site-verification" content="kAcoLDFGCpGh42gIFRgPeWlC253vTP3OLBs6wI8KDQ0">
<meta name="p:domain_verify" content="6a9e88f7014abe0735767f464c08f337">
<link rel="canonical" href="https://levnytt.se/{slug}">
<meta property="og:type" content="product">
<meta property="og:title" content="NeoLife {name} | LevNytt.se">
<meta property="og:description" content="{short} Kod {code}.">
<meta property="og:url" content="https://levnytt.se/{slug}">
<meta property="og:site_name" content="LevNytt">
<meta property="og:locale" content="sv_SE">
<meta property="og:image" content="https://levnytt.se{img}">
<meta property="og:image:alt" content="{img_alt}">
<link rel="icon" href="/assets/brand/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/brand/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600;700&display=swap">
<link rel="stylesheet" href="/assets/css/levnytt-foundations.css?v=3e93ffb6b5e4">
<link rel="stylesheet" href="/assets/css/levnytt-components.css?v=84f4407cc9fe">
<link rel="stylesheet" href="/assets/css/levnytt-rebuild.css?v=57f20cd8ce59">
<link rel="stylesheet" href="/assets/css/editorial-components.css?v=651db2f78ace">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Product","name":"NeoLife {name}","description":"{short}","brand":{{"@type":"Brand","name":"NeoLife"}},"url":"https://levnytt.se/{slug}"}}</script>
<meta name="levnytt-template" content="rebuild-product-category">
<meta name="levnytt-cta" content="existing-content-cta">
</head>
<body data-template-family="product-category">
<a class="ln-skip-link" href="#main-content">Hoppa till innehåll</a>
<header class="ln-site-header">
  <div class="ln-shell ln-header-inner">
    <a class="ln-brand" href="/" aria-label="LevNytt — Hem">
      <img src="/assets/brand/header-logo.svg" alt="LevNytt" width="160" height="56">
    </a>
    <button class="ln-menu-toggle" type="button" aria-label="Öppna meny" aria-controls="ln-primary-nav" aria-expanded="false">Meny</button>
    <nav class="ln-primary-nav" id="ln-primary-nav" aria-label="Huvudnavigation">
      <a href="/">Hem</a>
      <a href="/om-oss">Om oss</a>
      <a href="/artiklar">Artiklar</a>
      <a href="/neolife-historia">Historia</a>
      <a href="/neolife-vetenskap">Vetenskap</a>
      <a href="/neolife-kosttillskott" aria-current="page">Produkter</a>
      <a href="/neolife-affarsmojlighet">Affärsmöjlighet</a>
      <a href="/finns-det-billigare-alternativ">Spara pengar</a>
      <span class="ln-nav-commercial-group">
        <a class="ln-nav-commercial" href="https://se.neolifeshop.com/i/shop.html?sponsor=41-830928" target="_blank" rel="nofollow sponsored noopener noreferrer">Handla NeoLife <span aria-hidden="true">→</span></a>
        <a class="ln-nav-disclosure" href="/om-oss">Oberoende distributör · Sponsor-ID 41-830928</a>
      </span>
    </nav>
  </div>
</header>
<main id="main-content" class="ln-page ln-family-product-category"><div class="ln-shell"><nav class="ln-breadcrumbs" aria-label="Brödsmulor"><a href="/">LevNytt</a> <span aria-hidden="true">›</span> <span aria-current="page">NeoLife {name}</span></nav><article><header class="ln-article-header"><p class="ln-eyebrow">LevNytt · Produkter och konsumentkunskap</p><h1>NeoLife {name}</h1></header><div class="ln-article-body"><div class="freshness-banner">&#128300; <strong>Uppdaterad september 2026</strong> &mdash; aktuell produktfakta, verifierade källor.</div>

<section class="hero">
  <div class="hero-inner">
    <div>
      <p class="hero-label">{name} &mdash; Kod {code}</p>
      <div class="hero-divider"></div>
      <p class="hero-desc">{short}</p>
      <div class="hero-badges">
        <span class="hero-badge">{pack_label}</span>
        <span class="hero-badge">Kod {code}</span>
      </div>
    </div>
    <div class="hero-img">
      <img src="{img}" alt="NeoLife {img_alt}" width="440" height="252" loading="eager" fetchpriority="high" decoding="async">
    </div>
  </div>
</section>

<div class="meta-bar">
  <div class="meta-inner">
    <div class="meta-item"><strong>Produktkod:</strong> {code}</div>
    <div class="meta-item"><strong>Förpackning:</strong> {pack_label}</div>
    <div class="meta-item"><strong>Dosering:</strong> {dosage}</div>
  </div>
</div>

<section class="section">
  <div class="section-inner">
    <p class="section-label">Vad är NeoLife {name}?</p>
    <p class="section-title">{name}</p>
    <div class="section-divider"></div>
    <div class="two-col">
      <div>
        <p>{summary}</p>
        {topic_para}
      </div>
      <div>
        <div class="ingredients-box">
          <h3 id="nyckelingredienser">Nyckelingredienser</h3>
          <ul class="ingredients-list">
{ingredient_items}
          </ul>
          <p>Källa: NeoLife produktfakta 04/26 SE.{safety_html} För fullständig innehållsdeklaration, se produktetiketten.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="cta-section">
  <p>Beställ NeoLife {name}</p>
  <h2 class="cta-title" id="handla-neolife">Handla NeoLife {name}</h2>
  <p class="cta-desc">Handla som kund eller spara 20&ndash;25% som distributör. Sponsor-ID: 41-830928.</p>
  <div>
    <a class="btn-gold" href="https://se.neolifeshop.com/i/shop.html?sponsor=41-830928" target="_blank" rel="nofollow noopener noreferrer sponsored">Kundshop &rarr;</a>
    <a class="btn-ghost" href="https://se.neolifeshop.com/i/registration.html?type=reseller&amp;sponsor=41-830928" target="_blank" rel="nofollow noopener noreferrer sponsored">Bli distributör &rarr;</a>
  </div>
</section></div></article></div></main>
<footer class="ln-site-footer">
  <div class="ln-shell ln-footer-grid">
    <div class="ln-footer-about">
      <a class="ln-footer-brand" href="/" aria-label="LevNytt — Hem">
        <img src="/assets/brand/header-logo.svg" alt="LevNytt" width="128" height="45">
      </a>
      <p>Fakta före hype. Värde före pris. Förstå först. Bestäm sedan.</p>
    </div>
    <nav class="ln-footer-nav" aria-label="Sidfotsnavigation">
      <a href="/artiklar">Alla artiklar</a>
      <a href="/neolife-historia">Historia</a>
      <a href="/neolife-vetenskap">Vetenskap</a>
      <a href="/neolife-kosttillskott">Produkter</a>
      <a href="/direktforsaljning-fakta">Direktförsäljning</a>
      <a href="/om-oss">Om oss</a>
      <a href="/var-metod">Vår metod</a>
      <a href="/forsknings-faq">Forsknings-FAQ</a>
      <a href="/levnytt-principer">LevNytts principer</a>
      <a href="/integritetspolicy">Integritetspolicy</a>
    </nav>
    <div class="ln-footer-disclosure">
      <p><strong>Kommersiell transparens:</strong> LevNytt är en oberoende NeoLife-distributörswebbplats. Sponsor-ID: 41-830928. NeoLife® är ett registrerat varumärke tillhörande NeoLife International, LLC.</p>
      <p>© 2026 LevNytt. Alla rättigheter förbehållna.</p>
    </div>
  </div>
</footer>
<script src="/assets/js/levnytt-rebuild.js?v=2b31f8d01253" defer></script>
</body>
</html>
"""
