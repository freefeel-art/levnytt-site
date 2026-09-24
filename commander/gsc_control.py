"""Production-shaped GSC snapshots and comparable, non-causal trend evidence."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


WINDOWS = (7, 14, 28, 30, 60)
MAX_FETCH_AGE = timedelta(hours=36)
MAX_DATA_LAG = timedelta(days=5)


def valid_snapshot(data: dict[str, Any]) -> bool:
    if data.get("site") != "sc-domain:levnytt.se":
        return False
    for dimension, key in (("query", "all_queries"), ("page", "all_pages")):
        part = data.get(dimension)
        if not isinstance(part, dict) or not isinstance(part.get(key), list):
            return False
        dates = part.get("date_range") or {}
        if not dates.get("start") or not dates.get("end"):
            return False
        if any(not isinstance(row, dict) or not {dimension, "impressions", "clicks", "ctr", "position"}.issubset(row)
               for row in part[key]):
            return False
    return bool(data.get("fetched_at"))


def fresh(data: dict[str, Any], now: datetime | None = None) -> bool:
    trends = data.get("trends")
    if (not valid_snapshot(data) or not isinstance(trends, dict) or
            set((trends.get("windows") or {})) != {"7", "14", "30"} or
            trends.get("end") != data["page"]["date_range"]["end"]):
        return False
    now = now or datetime.now(timezone.utc)
    try:
        fetched = datetime.fromisoformat(data["fetched_at"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(data["page"]["date_range"]["end"] + "T00:00:00+00:00")
        if fetched.tzinfo is None:
            return False
        return timedelta(0) <= now - fetched <= MAX_FETCH_AGE and now - end <= MAX_DATA_LAG
    except (ValueError, TypeError, KeyError):
        return False


def _metrics(rows: list[dict[str, Any]]) -> dict[str, float | int]:
    impressions = sum(int(row["impressions"]) for row in rows)
    clicks = sum(int(row["clicks"]) for row in rows)
    return {"impressions": impressions, "clicks": clicks,
            "ctr": round(100 * clicks / impressions, 2) if impressions else 0.0,
            "position": round(sum(float(r["position"]) * int(r["impressions"]) for r in rows) / impressions, 2)
            if impressions else 0.0}


def _difference(longer: dict[str, Any], shorter: dict[str, Any], dimension: str) -> dict[str, Any]:
    key = "all_queries" if dimension == "query" else "all_pages"
    short_rows = {r[dimension]: r for r in shorter[dimension][key]}
    previous = []
    for row in longer[dimension][key]:
        prior = short_rows.get(row[dimension], {})
        impressions = max(0, int(row["impressions"]) - int(prior.get("impressions", 0)))
        clicks = max(0, int(row["clicks"]) - int(prior.get("clicks", 0)))
        # GSC positions are impression-weighted averages. A difference of
        # averages is not a position; reconstruct the disjoint-period average.
        weighted = float(row["position"]) * int(row["impressions"]) - float(prior.get("position", 0)) * int(prior.get("impressions", 0))
        if impressions:
            previous.append({dimension: row[dimension], "impressions": impressions, "clicks": clicks,
                             "position": round(weighted / impressions, 2)})
    return {"rows": previous, "summary": _metrics(previous)}


def build_trends(snapshots: dict[int, dict[str, Any]]) -> dict[str, Any]:
    if set(snapshots) != set(WINDOWS) or any(not valid_snapshot(s) for s in snapshots.values()):
        raise ValueError("All five production-shaped GSC snapshots are required")
    ends = {s["page"]["date_range"]["end"] for s in snapshots.values()}
    if len(ends) != 1 or any(s["query"]["date_range"]["end"] not in ends for s in snapshots.values()):
        raise ValueError("GSC comparison windows must end on the same date")
    result: dict[str, Any] = {"end": ends.pop(), "windows": {}}
    for days, double in ((7, 14), (14, 28), (30, 60)):
        entry = {}
        for dimension, key in (("query", "all_queries"), ("page", "all_pages")):
            current_rows = snapshots[days][dimension][key]
            previous = _difference(snapshots[double], snapshots[days], dimension)
            current = _metrics(current_rows)
            previous_keys = {r[dimension] for r in previous["rows"]}
            entry[dimension] = {
                "current": {"rows": current_rows, "summary": current},
                "previous": previous,
                "newly_observed": [{"identity": r[dimension], "impressions": r["impressions"],
                                     "clicks": r["clicks"], "previous_presence": "not_reported"}
                                    for r in current_rows if r[dimension] not in previous_keys],
                "impressions_change": current["impressions"] - previous["summary"]["impressions"],
                "clicks_change": current["clicks"] - previous["summary"]["clicks"],
            }
        result["windows"][str(days)] = entry
    return result


def page_metrics(snapshot: dict[str, Any], slug: str) -> dict[str, Any] | None:
    for row in (snapshot.get("page") or {}).get("all_pages", []):
        if row.get("page", "").rstrip("/").endswith("/" + slug):
            return {key: row[key] for key in ("impressions", "clicks", "ctr", "position")}
    return None


def page_trend(trends: dict[str, Any], slug: str, days: int = 7) -> dict[str, Any] | None:
    entry = ((trends.get("windows") or {}).get(str(days)) or {}).get("page") or {}
    def row(period: str) -> dict[str, Any] | None:
        return next((r for r in (entry.get(period) or {}).get("rows", [])
                     if r.get("page", "").rstrip("/").endswith("/" + slug)), None)
    current, previous = row("current"), row("previous")
    if current is None:
        return None
    if previous is None:
        return {"current": current, "previous": None, "impressions_change": None,
                "clicks_change": None, "newly_observed": True}
    return {"current": current, "previous": previous,
            "impressions_change": int(current["impressions"]) - int(previous["impressions"]),
            "clicks_change": int(current["clicks"]) - int(previous["clicks"])}
