#!/usr/bin/env python3
"""
gsc-fetch.py — Google Search Console Search Analytics fetcher (OAuth 2.0)

Fetches query-level search performance data from GSC API and writes
JSON reports to research/gsc/.

Authentication flow:
    1. Place an OAuth 2.0 Desktop Client credentials JSON at
       secrets/credentials.json (from Google Cloud Console)
    2. First run opens a browser for Google login
    3. Token is saved to secrets/token.json — subsequent runs use it

    The Google account must have access to the GSC property.
    No service account or GCP IAM changes needed.

Usage:
    python3 scripts/gsc-fetch.py [--site SITE_URL] [--days N] [--slug SLUG] [--dry-run]
"""

import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SECRETS_DIR = REPO_ROOT / "secrets"
CREDENTIALS_PATH = SECRETS_DIR / "credentials.json"
TOKEN_PATH = SECRETS_DIR / "token.json"
OUTPUT_DIR = REPO_ROOT / "research" / "gsc"
DEFAULT_SITE = "https://levnytt.se"
DEFAULT_DAYS = 90
ROW_LIMIT = 1000

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


def _get_credentials():
    """Load/create OAuth 2.0 credentials. Opens browser on first run."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("ERROR: Required packages not installed.", file=sys.stderr)
        print("  Run: pip install google-api-python-client google-auth-oauthlib google-auth-httplib2", file=sys.stderr)
        sys.exit(1)

    # Check for existing token
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    # Refresh or re-authenticate
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _save_token(creds)
        return creds

    # First run — browser OAuth flow
    if not CREDENTIALS_PATH.exists():
        print(f"ERROR: OAuth client secrets not found at {CREDENTIALS_PATH}", file=sys.stderr)
        print("  1. Go to https://console.cloud.google.com/apis/credentials", file=sys.stderr)
        print('  2. Create an OAuth 2.0 Client ID (type: "Desktop application")', file=sys.stderr)
        print("  3. Download the JSON", file=sys.stderr)
        print(f"  4. Save it to {CREDENTIALS_PATH}", file=sys.stderr)
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
    creds = flow.run_local_server(port=0)
    _save_token(creds)
    return creds


def _save_token(creds):
    """Persist OAuth token to secrets/token.json."""
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_PATH, "w") as f:
        f.write(creds.to_json())


def _load_credentials_file():
    """Check that credentials.json is valid JSON — for --dry-run."""
    if not CREDENTIALS_PATH.exists():
        return None
    with open(CREDENTIALS_PATH) as f:
        return json.load(f)


def fetch_search_analytics(service, site_url, start_date, end_date, row_limit=ROW_LIMIT):
    request = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["query"],
        "rowLimit": row_limit,
        "startRow": 0,
    }
    rows = []
    while True:
        response = service.searchanalytics().query(
            siteUrl=site_url, body=request
        ).execute()
        batch = response.get("rows", [])
        rows.extend(batch)
        if len(batch) < row_limit:
            break
        request["startRow"] += row_limit
    return rows


def format_report(rows, site_url, start_date, end_date):
    total_clicks = sum(r.get("clicks", 0) for r in rows)
    total_impressions = sum(r.get("impressions", 0) for r in rows)
    avg_position = (
        sum(r.get("position", 0) * r.get("impressions", 1) for r in rows) / max(total_impressions, 1)
        if rows else 0
    )
    queries = []
    for r in rows:
        queries.append({
            "query": " ".join(r.get("keys", [""])),
            "clicks": r.get("clicks", 0),
            "impressions": r.get("impressions", 0),
            "ctr": round(r.get("ctr", 0) * 100, 2),
            "position": round(r.get("position", 0), 1),
        })
    queries.sort(key=lambda q: q["clicks"], reverse=True)
    return {
        "module": "gsc",
        "fetched_at": datetime.now().isoformat(),
        "site": site_url,
        "date_range": {"start": start_date, "end": end_date, "days": (datetime.fromisoformat(end_date) - datetime.fromisoformat(start_date)).days},
        "summary": {
            "total_queries": len(queries),
            "total_clicks": total_clicks,
            "total_impressions": total_impressions,
            "avg_ctr": round((total_clicks / max(total_impressions, 1)) * 100, 2),
            "avg_position": round(avg_position, 1),
        },
        "top_queries": queries[:50],
        "all_queries": queries,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fetch Google Search Console analytics (OAuth 2.0)")
    parser.add_argument("--site", default=DEFAULT_SITE, help=f"GSC property URL (default: {DEFAULT_SITE})")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help=f"Days of data to fetch (default: {DEFAULT_DAYS})")
    parser.add_argument("--slug", default=None, help="Topic slug — filters by query containing slug")
    parser.add_argument("--output", default=None, help="Override output path")
    parser.add_argument("--dry-run", action="store_true", help="Validate credentials only, don't fetch")
    args = parser.parse_args()

    if args.dry_run:
        creds_data = _load_credentials_file()
        if creds_data is None:
            print(f"Credentials not found at {CREDENTIALS_PATH}")
            print("  Create an OAuth 2.0 Desktop Client and download the JSON.")
            return
        client_type = creds_data.get("installed", {}).get("client_id", "unknown")[:20]
        print(f"OK: OAuth client secrets found (client_id: {client_type}...)")
        if TOKEN_PATH.exists():
            print(f"   Token exists at {TOKEN_PATH} — ready to fetch.")
        else:
            print(f"   No token yet — browser will open on first real run.")
        return

    # Full OAuth flow (may open browser)
    creds = _get_credentials()

    try:
        from googleapiclient.discovery import build
        service = build("searchconsole", "v1", credentials=creds)
    except ImportError:
        print("ERROR: google-api-python-client not installed.", file=sys.stderr)
        print("  Run: pip install google-api-python-client google-auth-oauthlib google-auth-httplib2", file=sys.stderr)
        sys.exit(1)

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")

    print(f"Fetching GSC data for {args.site}")
    print(f"  Range: {start_date} → {end_date} ({args.days} days)")

    rows = fetch_search_analytics(service, args.site, start_date, end_date)
    report = format_report(rows, args.site, start_date, end_date)

    if args.slug:
        slug_lower = args.slug.lower().replace("-", " ")
        report["all_queries"] = [
            q for q in report["all_queries"]
            if slug_lower in q["query"].lower()
        ]
        report["top_queries"] = report["all_queries"][:50]
        report["summary"]["total_queries"] = len(report["all_queries"])
        report["summary"]["total_clicks"] = sum(q["clicks"] for q in report["all_queries"])
        report["summary"]["total_impressions"] = sum(q["impressions"] for q in report["all_queries"])
        output_name = args.slug
    else:
        output_name = "sitewide"

    output_path = args.output or str(OUTPUT_DIR / f"{output_name}.json")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    s = report["summary"]
    print(f"\nDone. {s['total_queries']} queries | {s['total_clicks']} clicks | {s['total_impressions']} impressions | avg pos {s['avg_position']:.1f}")
    print(f"  → {output_path}")


if __name__ == "__main__":
    main()
