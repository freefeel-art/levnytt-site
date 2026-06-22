#!/usr/bin/env python3
"""
Genererar hero-bilder för tre artiklar via KIE.ai GPT Image 2.
Sparar PNG-originalen till images/originals/ för visuell verifiering,
konverterar sedan till WebP och bäddar in base64 i HTML.
"""
import json, urllib.request, urllib.error, base64, sys, pathlib, re, time, io, os

KIE_API_KEY = os.environ.get("KIE_API_KEY")
if not KIE_API_KEY:
    sys.exit("FEL: miljövariabeln KIE_API_KEY är inte satt. Kör t.ex.\n  export KIE_API_KEY='din-nya-nyckel'\nfore du startar scriptet.")
CREATE_URL   = "https://api.kie.ai/api/v1/jobs/createTask"
POLL_URL     = "https://api.kie.ai/api/v1/jobs/recordInfo"
ARTICLES_DIR = pathlib.Path(__file__).parent / "content" / "articles"
IMAGES_DIR   = pathlib.Path(__file__).parent / "images" / "originals"

ARTICLES = [
    {
        "slug": "retinol-pa-sommaren",
        "file": "retinol-pa-sommaren.html",
        "alt":  "Glasdroppflaska med hudvårdsserum på ett soligt fönsterbräde bredvid solskyddsmedel — sommarhudvård med retinol",
        "prompt": (
            "Editorial lifestyle photography, soft natural light. "
            "A glass skincare dropper bottle resting on a sunlit windowsill next to a small bottle of sunscreen, "
            "warm Scandinavian summer afternoon light, pale linen fabric in background, "
            "minimal and calm composition, no text, no people, no logos, "
            "muted forest-green and cream color palette"
        ),
    },
    {
        "slug": "vad-ar-niacinamid",
        "file": "vad-ar-niacinamid.html",
        "alt":  "Liten glasflaska med niacinamidserum med droppare på marmoryta bredvid vit handduk — minimalistisk hudvårdskomposition",
        "prompt": (
            "Editorial lifestyle photography, soft natural light. "
            "A small glass skincare serum bottle with dropper, pale cream-colored liquid visible inside, "
            "resting on a marble bathroom surface next to a folded white towel, "
            "calm minimal composition, no text, no people, no logos, "
            "muted forest-green and cream color palette, soft morning light"
        ),
    },
    {
        "slug": "ar-miljovanliga-rengoringsmedel-lika-effektiva",
        "file": "ar-miljovanliga-rengoringsmedel-lika-effektiva.html",
        "alt":  "Glassprayflaska med naturligt rengöringsmedel bredvid bomullstrasa och citroner på köksbänk — miljövänlig städning",
        "prompt": (
            "Editorial lifestyle photography, soft natural light. "
            "A glass spray bottle of natural cleaning solution next to a folded cotton cloth "
            "and a small bowl of lemon halves on a clean kitchen counter, "
            "Scandinavian minimal kitchen background, no text, no people, no logos, "
            "muted forest-green and cream color palette, bright natural daylight"
        ),
    },
]


def api_request(url, data=None):
    body = json.dumps(data).encode("utf-8") if data else None
    req  = urllib.request.Request(
        url, data=body,
        headers={
            "Authorization": f"Bearer {KIE_API_KEY}",
            "Content-Type":  "application/json",
        },
        method="POST" if body else "GET"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def poll(task_id, timeout=300):
    deadline = time.time() + timeout
    while time.time() < deadline:
        r     = api_request(f"{POLL_URL}?taskId={task_id}")
        state = r.get("data", {}).get("state", "")
        print(f"  [{task_id[:8]}] status: {state}", flush=True)
        if state == "success":
            result = json.loads(r["data"]["resultJson"])
            return result["resultUrls"][0]
        if state == "fail":
            raise RuntimeError(r["data"].get("failMsg", "task failed"))
        time.sleep(5)
    raise TimeoutError(f"task {task_id} not done within {timeout}s")


def generate_and_save_png(article):
    slug     = article["slug"]
    img_path = IMAGES_DIR / f"hero-{slug}.png"

    print(f"\n[{slug}] 1/3  Skapar uppgift…")
    r       = api_request(CREATE_URL, {
        "model": "gpt-image-2-text-to-image",
        "input": {
            "prompt":       article["prompt"],
            "aspect_ratio": "16:9",
            "resolution":   "2K",
        }
    })
    task_id = r["data"]["taskId"]
    print(f"[{slug}]      taskId: {task_id}")

    print(f"[{slug}] 2/3  Väntar på generering…")
    img_url  = poll(task_id)
    print(f"[{slug}]      URL: {img_url[:80]}…")

    print(f"[{slug}] 3/3  Laddar ner PNG…")
    req_dl = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"})
    with urllib.request.urlopen(req_dl, timeout=60) as resp:
        img_data = resp.read()
    img_path.write_bytes(img_data)
    print(f"[{slug}]      Sparad: {img_path}  ({len(img_data)//1024} KB)")
    return img_path


def convert_and_embed(article, png_path):
    slug      = article["slug"]
    html_path = ARTICLES_DIR / article["file"]

    img_data = png_path.read_bytes()
    mime     = "image/png"

    try:
        from PIL import Image
        webp_path = png_path.with_suffix(".webp")
        Image.open(io.BytesIO(img_data)).save(str(webp_path), "WEBP", quality=82, method=6)
        img_data = webp_path.read_bytes()
        mime     = "image/webp"
        print(f"[{slug}] WebP: {webp_path.name}  ({len(img_data)//1024} KB)")
    except ImportError:
        print(f"[{slug}] Pillow ej installerat — bäddar in PNG")

    b64     = base64.b64encode(img_data).decode()
    img_tag = (
        f'<img src="data:{mime};base64,{b64}" '
        f'alt="{article["alt"]}" '
        f'class="ia-hero-img" loading="lazy">'
    )

    placeholder = f"<!-- HERO_IMAGE_PLACEHOLDER: {slug} -->"
    html        = html_path.read_text(encoding="utf-8")
    if placeholder not in html:
        raise ValueError(f"Placeholder saknas i {article['file']}")

    html_path.write_text(html.replace(placeholder, img_tag), encoding="utf-8")
    print(f"[{slug}] ✓ Inbäddad  ({len(b64)//1024} KB base64)")


if __name__ == "__main__":
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"

    png_paths = {}
    if phase in ("generate", "all"):
        for article in ARTICLES:
            try:
                png_paths[article["slug"]] = generate_and_save_png(article)
            except Exception as e:
                print(f"FEL (generate) {article['slug']}: {e}")
                sys.exit(1)
        print("\nAlla PNG:er nedladdade. Kör visuell verifiering.")

    if phase in ("embed", "all"):
        for article in ARTICLES:
            slug     = article["slug"]
            png_path = png_paths.get(slug) or (IMAGES_DIR / f"hero-{slug}.png")
            if not png_path.exists():
                print(f"FEL: {png_path} saknas — kör generate-fasen först")
                sys.exit(1)
            try:
                convert_and_embed(article, png_path)
            except Exception as e:
                print(f"FEL (embed) {slug}: {e}")
                sys.exit(1)
        print("\nAlla tre artiklar inbäddade.")
