#!/usr/bin/env python3
"""
Genererar hero-bild för varfor-tar-d-vitamin-slut-pa-ditt-magnesium.html via KIE.ai GPT Image 2.
Byter ut HERO_IMAGE_PLACEHOLDER-blocket med en base64-inbäddad <img>-tagg.

Användning:
  python3 generate_hero.py [--dry-run]

API (docs.kie.ai):
  POST https://api.kie.ai/api/v1/jobs/createTask  → taskId
  GET  https://api.kie.ai/api/v1/jobs/recordInfo?taskId=... → state + resultJson
"""
import json, urllib.request, urllib.error, base64, sys, pathlib, re, time

KIE_API_KEY  = "b074c4f67699d7197affce9047d6b99f"
CREATE_URL   = "https://api.kie.ai/api/v1/jobs/createTask"
POLL_URL     = "https://api.kie.ai/api/v1/jobs/recordInfo"

TARGET_FILE  = pathlib.Path(__file__).parent / "varfor-tar-d-vitamin-slut-pa-ditt-magnesium.html"
OUTPUT_IMAGE = pathlib.Path(__file__).parent / "images" / "originals" / "hero-varfor-tar-d-vitamin.png"

HERO_PROMPT = (
    "Editorial wellness blog hero image. "
    "Sunlit arrangement of lush leafy greens — spinach, kale, Swiss chard, parsley — "
    "on a light natural stone or linen surface. "
    "Warm golden sunlight streaming across the scene from the side, "
    "soft highlights and gentle shadows, fresh dew drops on some leaves. "
    "Color palette: deep forest greens, warm golden light, soft cream. "
    "Mood: calm, natural, health-conscious, Scandinavian editorial. "
    "No text, no labels, no overlays. "
    "No product packaging, no supplement bottles, no pills. "
    "No people. "
    "Editorial photography style, shallow depth of field, professional wellness composition."
)


def api_request(url: str, data: dict | None = None) -> dict:
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


def poll(task_id: str, timeout: int = 300) -> str:
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = api_request(f"{POLL_URL}?taskId={task_id}")
        state = r.get("data", {}).get("state", "")
        print(f"  status: {state}", flush=True)
        if state == "success":
            result = json.loads(r["data"]["resultJson"])
            return result["resultUrls"][0]
        if state == "fail":
            raise RuntimeError(r["data"].get("failMsg", "task failed"))
        time.sleep(5)
    raise TimeoutError(f"task {task_id} not done within {timeout}s")


def embed_image(img_data: bytes, mime: str) -> None:
    b64     = base64.b64encode(img_data).decode()
    img_tag = (
        f'<img src="data:{mime};base64,{b64}" '
        f'alt="Lehtivihanneksia ja auringonvaloa — editoriell wellness-bild för D-vitamin och magnesium" '
        f'style="width:100%;border-radius:10px;display:block;margin:24px 0 32px" '
        f'width="1536" height="864">'
    )
    html = TARGET_FILE.read_text(encoding="utf-8")
    new_html = re.sub(
        r'<!-- HERO_IMAGE_PLACEHOLDER -->.*?-->',
        img_tag,
        html,
        flags=re.S
    )
    if new_html == html:
        print("VARNING: HERO_IMAGE_PLACEHOLDER hittades inte.")
        return
    TARGET_FILE.write_text(new_html, encoding="utf-8")
    print(f"✓ Inbäddad i {TARGET_FILE.name}  ({len(b64)//1024} KB base64)")


def run(dry_run: bool = False) -> None:
    print(f"Målfil: {TARGET_FILE}")
    if dry_run:
        print("[DRY RUN] avslutar.")
        return

    print("1/4  Skapar uppgift på KIE.ai…")
    r = api_request(CREATE_URL, {
        "model": "gpt-image-2-text-to-image",
        "input": {
            "prompt":       HERO_PROMPT,
            "aspect_ratio": "16:9",
            "resolution":   "2K",
        }
    })
    task_id = r["data"]["taskId"]
    print(f"     taskId: {task_id}")

    print("2/4  Väntar på bildgenerering (max 5 min)…")
    img_url = poll(task_id)
    print(f"     URL: {img_url[:80]}…")

    print("3/4  Laddar ner bilden…")
    with urllib.request.urlopen(img_url, timeout=60) as resp:
        img_data = resp.read()

    OUTPUT_IMAGE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_IMAGE.write_bytes(img_data)
    print(f"     Sparad: {OUTPUT_IMAGE}  ({len(img_data)//1024} KB)")

    mime = "image/png"
    try:
        from PIL import Image
        import io
        webp_path = OUTPUT_IMAGE.with_suffix(".webp")
        Image.open(io.BytesIO(img_data)).save(str(webp_path), "WEBP", quality=82, method=6)
        img_data  = webp_path.read_bytes()
        mime      = "image/webp"
        print(f"     → WebP: {webp_path.name}  ({len(img_data)//1024} KB)")
    except ImportError:
        print("     (Pillow ej installerat — bäddar in PNG)")

    print("4/4  Bäddar in base64 i HTML…")
    embed_image(img_data, mime)


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    try:
        run(dry_run)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()[:300]}")
        sys.exit(1)
    except Exception as e:
        print(f"Fel: {e}")
        sys.exit(1)
