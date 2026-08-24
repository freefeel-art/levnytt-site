import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_bootstrap_and_build_all_sitemap_routes(tmp_path):
    data = tmp_path / "production-pages.json"
    output = tmp_path / "output"
    subprocess.run([sys.executable, "scripts/rebuild-production.py", "--root", str(ROOT), "--bootstrap", "--data", str(data)], check=True)
    subprocess.run([sys.executable, "scripts/rebuild-production.py", "--root", str(ROOT), "--build", "--data", str(data), "--output-root", str(output)], check=True)
    pages = json.loads(data.read_text(encoding="utf-8"))["pages"]
    assert len(pages) >= 100
    assert all((output / ("index.html" if p["path"] == "/" else p["path"].strip("/") + ".html")).is_file() for p in {p["path"]: p for p in pages}.values())


def test_generated_page_has_canonical_shell_and_link_policy(tmp_path):
    data = tmp_path / "production-pages.json"
    output = tmp_path / "output"
    subprocess.run([sys.executable, "scripts/rebuild-production.py", "--root", str(ROOT), "--bootstrap", "--data", str(data)], check=True)
    subprocess.run([sys.executable, "scripts/rebuild-production.py", "--root", str(ROOT), "--build", "--data", str(data), "--output-root", str(output)], check=True)
    html = (output / "levnytt-principer.html").read_text(encoding="utf-8")
    assert 'class="ln-site-header"' in html and 'class="ln-site-footer"' in html
    assert '<a href="/artiklar">Artiklar</a>' in html
    assert 'href="https://se.neolifeshop.com/i/shop.html?sponsor=41-830928" target="_blank"' in html
    shop_tag = re.search(r'<a class="ln-nav-commercial"[^>]+>', html).group(0)
    assert {"nofollow", "noopener", "noreferrer", "sponsored"}.issubset(set(re.search(r'rel="([^"]+)"', shop_tag).group(1).split()))
    assert "style=" not in html
    assert html.count("<h1") == 1


def test_rebuild_resolves_cloudflare_rewrites_and_includes_error_page(tmp_path):
    data = tmp_path / "production-pages.json"
    subprocess.run([sys.executable, "scripts/rebuild-production.py", "--root", str(ROOT), "--bootstrap", "--data", str(data)], check=True)
    pages = {page["path"]: page for page in json.loads(data.read_text(encoding="utf-8"))["pages"]}
    assert pages["/kosttillskott-aldre-65"]["source_file"] == "content/articles/kosttillskott-aldre-65.html"
    assert pages["/404"]["source_file"] == "404.html"
