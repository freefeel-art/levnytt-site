import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_commander_markdown_article_inherits_shared_shell_and_policy():
    generator = load_script("md_to_article", "scripts/md-to-article.py")
    raw = (ROOT / "content/articles/kalcium-brist-symtom/kalcium-brist-symtom.md").read_text(encoding="utf-8")
    frontmatter, body = generator.split_source(raw)
    data = generator.parse_frontmatter(frontmatter)
    source = generator.build_html(data, generator.md_body_to_html(body))
    assert source.count('class="ln-site-header"') == 1
    assert source.count('class="ln-site-footer"') == 1
    assert source.count("<h1") == 1
    assert "Det viktigaste" in source and "Key Takeaways" not in source
    assert not re.search(r"<style\b|\sstyle=|\son\w+=", source, re.I)
    assert 'href="/den-fundersamma-mannen"' in source
    assert 'href="/den-fundersamma-mannen" target="_blank"' not in source
    for raw_schema in re.findall(r'<script type="application/ld\+json">(.*?)</script>', source, re.I | re.S):
        json.loads(raw_schema)


def test_commander_source_gate_accepts_phase1_heading_ids():
    procedure = load_script("levnytt_procedure_source_gate", "commander/procedure.py")
    rendered = (
        '<h2 id="kallor" class="article-heading"> Källor </h2><ul><li>'
        '<a href="https://www.livsmedelsverket.se/example">Myndighetskälla</a>'
        '</li></ul><h2 id="nasta">Nästa avsnitt</h2>'
    )

    assert procedure._has_rendered_sources(rendered) is True


def test_commander_source_gate_still_rejects_only_neolife_sources_with_heading_attributes():
    procedure = load_script("levnytt_procedure_source_gate_neolife", "commander/procedure.py")
    rendered = (
        '<h2 id="kallor">Källor</h2><ul><li>'
        '<a href="https://se.neolifeshop.com/i/shop.html?sponsor=41-830928">NeoLife</a>'
        '</li></ul>'
    )

    assert procedure._has_rendered_sources(rendered) is False


def test_shared_fragments_have_disclosure_and_accessible_menu_contract():
    header = (ROOT / "assets/fragments/header-sv.html").read_text(encoding="utf-8")
    footer = (ROOT / "assets/fragments/footer-sv.html").read_text(encoding="utf-8")
    assert 'aria-controls="ln-primary-nav"' in header
    assert 'aria-expanded="false"' in header
    assert "Sponsor-ID 41-830928" in header and "Sponsor-ID: 41-830928" in footer
    assert 'rel="nofollow sponsored noopener noreferrer"' in header
    assert '<a href="/artiklar">' in header and 'href="/artiklar" target="_blank"' not in header


def test_shared_assets_are_content_versioned_and_not_immutable():
    renderer = load_script("site_renderer_assets", "scripts/site_renderer.py")
    rendered_url = renderer.asset_url(ROOT, "/assets/js/levnytt-rebuild.js")
    assert re.fullmatch(r"/assets/js/levnytt-rebuild\.js\?v=[0-9a-f]{12}", rendered_url)
    headers = (ROOT / "_headers").read_text(encoding="utf-8")
    assert "immutable" not in headers
    assert "must-revalidate" in headers


def test_worker_geo_banner_uses_valid_body_insertion_without_inline_code():
    source = (ROOT / "_worker.js").read_text(encoding="utf-8")
    assert "html.replace(/<body([^>]*)>/i" in source
    assert "data-dismiss-geo" in source
    assert "onclick=" not in source and 'style="' not in source


def test_redirect_catch_all_is_last_and_all_canonical_pages_are_indexed():
    rules = [line.strip() for line in (ROOT / "_redirects").read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]
    assert rules[-1] == "/* /404.html 404"
    rebuild = load_script("rebuild_routes", "scripts/rebuild-production.py")
    sitemap_urls = {url.rstrip("/") for url, _ in rebuild.sitemap_routes(ROOT)}
    for path in ROOT.rglob("*.html"):
        if path.relative_to(ROOT).parts[0] in {"assets", "docs", "node_modules"}:
            continue
        source = path.read_text(encoding="utf-8")
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', source, re.I)
        if canonical:
            assert canonical.group(1).rstrip("/") in sitemap_urls
        assert not re.search(r"<style\b|\sstyle=|\son\w+=", source, re.I)


def test_article_index_discovers_every_swedish_content_route_once():
    generator = load_script("article_index_generator", "scripts/generate-article-index.py")
    articles = generator.discover_articles()
    assert len(articles) == 138
    assert len({article["path"] for article in articles}) == len(articles)
