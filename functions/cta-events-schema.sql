-- Cloudflare D1 schema for the approved LevNytt → OLSP CTA event path.
-- No IP addresses, user agents, cookies, referrers, or personal data are stored.
CREATE TABLE IF NOT EXISTS cta_click_events (
  event_id TEXT PRIMARY KEY,
  observed_at TEXT NOT NULL,
  page_path TEXT NOT NULL,
  cta_id TEXT NOT NULL,
  destination TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cta_click_events_path_time
ON cta_click_events (page_path, observed_at);
