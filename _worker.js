// Cloudflare Pages Advanced Mode worker — language helper and first-party CTA event receiver.
// CTA events are deliberately limited to configured, non-personal event fields.

const NEO_LIFE_HOSTS = Object.freeze(["se.neolifeshop.com", "www.neolifeshop.com"]);
const SPONSOR_ID = "41-830928";

// Allowlist for any approved non-NeoLife CTA event path. Empty: OLSP is not
// part of the LevNytt project (config/conversion-attribution.json), and the
// one outbound OLSP link this validated (/direktforsaljning-fakta) has been
// removed from the page. Kept as a generic mechanism for future use.
const CTA_PATHS = Object.freeze({});

function eventResponse(status, detail = "") {
  return new Response(detail, {
    status,
    headers: {
      "Cache-Control": "no-store",
      "Content-Type": "text/plain; charset=utf-8",
    },
  });
}

// Validate a NeoLife outbound destination and return the canonical destination
// string, or null when it is not a Sponsor-ID 41-830928 link to the Swedish
// NeoLife shop / registration. Privacy-first: only the validated destination
// and page path are ever stored.
function classifyNeoLifeDestination(ctaId, destination) {
  if (typeof destination !== "string" || destination.length > 500) return null;
  let url;
  try {
    url = new URL(destination);
  } catch {
    return null;
  }
  if (!NEO_LIFE_HOSTS.includes(url.hostname)) return null;
  const sponsor = url.searchParams.get("sponsor") || url.searchParams.get("sponsorId");
  if (sponsor !== SPONSOR_ID) return null;
  if (ctaId === "levnytt-neolife-shop") {
    return url.pathname.includes("shop") && !url.pathname.includes("registration") ? destination : null;
  }
  if (ctaId === "levnytt-neolife-registration") {
    return url.pathname.includes("registration") ? destination : null;
  }
  return null;
}

function validPagePath(value) {
  return typeof value === "string" && value.length > 0 && value.length <= 300 && value.startsWith("/");
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

  let ctaId = "";
  let pagePath = "";
  let destination = "";

  if (payload.cta_id === "levnytt-neolife-shop" || payload.cta_id === "levnytt-neolife-registration") {
    destination = classifyNeoLifeDestination(payload.cta_id, payload.destination);
    if (!destination) return eventResponse(400, "Unrecognized CTA event path");
    if (!validPagePath(payload.page_path)) return eventResponse(400, "Invalid page path");
    ctaId = payload.cta_id;
    pagePath = payload.page_path;
  } else {
    const expected = CTA_PATHS[payload.cta_id];
    if (!expected || payload.page_path !== expected.page_path || payload.destination !== expected.destination) {
      return eventResponse(400, "Unrecognized CTA event path");
    }
    ctaId = payload.cta_id;
    pagePath = expected.page_path;
    destination = expected.destination;
  }

  await env.CTA_EVENTS_DB.prepare(
    "INSERT INTO cta_click_events (event_id, observed_at, page_path, cta_id, destination) VALUES (?, ?, ?, ?, ?)"
  ).bind(
    crypto.randomUUID(),
    new Date().toISOString(),
    pagePath,
    ctaId,
    destination
  ).run();
  return new Response(null, { status: 204, headers: { "Cache-Control": "no-store" } });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Canonicalize www.levnytt.se -> levnytt.se (previously served both as
    // identical, non-redirected duplicate hosts). _worker.js Advanced Mode
    // bypasses _redirects, so this has to be handled here to actually take
    // effect.
    if (url.hostname === "www.levnytt.se") {
      url.hostname = "levnytt.se";
      return Response.redirect(url.toString(), 301);
    }

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
