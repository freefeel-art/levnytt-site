// Cloudflare Pages Advanced Mode worker — language helper and first-party CTA event receiver.
// CTA events are deliberately limited to configured, non-personal event fields.

const CTA_PATHS = Object.freeze({
  "levnytt-direktforsaljning-olsp-primary": Object.freeze({
    page_path: "/direktforsaljning-fakta",
    destination: "https://olsp.profitandprivilege.com",
  }),
});

function eventResponse(status, detail = "") {
  return new Response(detail, {
    status,
    headers: {
      "Cache-Control": "no-store",
      "Content-Type": "text/plain; charset=utf-8",
    },
  });
}

async function recordCtaClick(request, env, url) {
  if (request.method !== "POST") return eventResponse(405, "Method not allowed");
  const origin = request.headers.get("Origin");
  if (origin && origin !== url.origin) return eventResponse(403, "Cross-origin event rejected");
  if (!env.CTA_EVENTS_DB || typeof env.CTA_EVENTS_DB.prepare !== "function") {
    return eventResponse(503, "CTA event storage is not configured");
  }

  let payload;
  try {
    payload = await request.json();
  } catch {
    return eventResponse(400, "Invalid event payload");
  }
  if (!payload || typeof payload !== "object") return eventResponse(400, "Invalid event payload");

  const expected = CTA_PATHS[payload.cta_id];
  if (!expected || payload.page_path !== expected.page_path || payload.destination !== expected.destination) {
    return eventResponse(400, "Unrecognized CTA event path");
  }

  await env.CTA_EVENTS_DB.prepare(
    "INSERT INTO cta_click_events (event_id, observed_at, page_path, cta_id, destination) VALUES (?, ?, ?, ?, ?)"
  ).bind(
    crypto.randomUUID(),
    new Date().toISOString(),
    expected.page_path,
    payload.cta_id,
    expected.destination
  ).run();
  return new Response(null, { status: 204, headers: { "Cache-Control": "no-store" } });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/events/cta-click") return recordCtaClick(request, env, url);
    const country = request.cf?.country;

    const response = await env.ASSETS.fetch(request);

    // Only modify HTML pages — skip assets, images, API calls.
    const contentType = response.headers.get("Content-Type") || "";
    if (!contentType.includes("text/html")) {
      return response;
    }

    // Determine if visitor should see language suggestion.
    const langSuggestion = country === "NO" && !url.pathname.startsWith("/no/") ? "no" : null;
    if (!langSuggestion) {
      return response;
    }

    const html = await response.text();
    const banner = `
<div style="background:#1B4332;color:#F9F6EF;padding:10px 20px;text-align:center;font-family:Inter,sans-serif;font-size:14px;z-index:9999;position:relative">
  🇳🇴 Hei! Vi har norsk innhold tilgjengelig.
  <a href="/no/" style="color:#E8C870;font-weight:600;margin-left:8px">Gå til norsk versjon →</a>
  <button onclick="this.parentElement.remove()" style="background:none;border:none;color:rgba(255,255,255,0.5);cursor:pointer;margin-left:12px;font-size:16px" title="Lukk">✕</button>
</div>`;

    return new Response(html.replace("<body", "<body" + banner), {
      status: response.status,
      headers: response.headers,
    });
  },
};
