import json
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
    assert all((output / ("index.html" if p["path"] == "/" else p["path"].lstrip("/") + ".html")).is_file() for p in {p["path"]: p for p in pages}.values())


def test_generated_page_has_canonical_shell_and_link_policy(tmp_path):
    data = tmp_path / "production-pages.json"
    output = tmp_path / "output"
    subprocess.run([sys.executable, "scripts/rebuild-production.py", "--root", str(ROOT), "--bootstrap", "--data", str(data)], check=True)
    subprocess.run([sys.executable, "scripts/rebuild-production.py", "--root", str(ROOT), "--build", "--data", str(data), "--output-root", str(output)], check=True)
    html = (output / "levnytt-principer.html").read_text(encoding="utf-8")
    assert 'class="ln-site-header"' in html and 'class="ln-site-footer"' in html
    assert 'target="_blank"' in html
    assert 'rel="noopener noreferrer"' in html
    assert "style=" not in html
    assert html.count("<h1") == 1
