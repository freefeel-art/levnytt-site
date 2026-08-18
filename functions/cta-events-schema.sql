-- Cloudflare D1 schema for approved LevNytt CTA event paths (NeoLife shop /
-- registration outbound clicks). No IP addresses, user agents, cookies,
-- referrers, or personal data are stored. Column names are generic and were
-- never OLSP-specific; only this file's top comment previously said
-- otherwise. OLSP is not part of the LevNytt project.
CREATE TABLE IF NOT EXISTS cta_click_events (
  event_id TEXT PRIMARY KEY,
  observed_at TEXT NOT NULL,
  page_path TEXT NOT NULL,
  cta_id TEXT NOT NULL,
  destination TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cta_click_events_path_time
ON cta_click_events (page_path, observed_at);
