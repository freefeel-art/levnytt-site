"""LevNytt intervention ledger: local action, proven publication, later GSC observation.

GSC is observational. Direction is a before/after comparison, never a claim
that the intervention caused the movement.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import hashlib
from pathlib import Path
from typing import Any

from app.core.files import atomic_json_write, load_json_dict

from commander import gsc_control

CONTENT = {"content_improvement", "content_production", "product_page", "legacy_migration", "internal_linking"}


def _path(runtime: Path) -> Path:
    return runtime / "commander" / "interventions.json"


def _rows(runtime: Path) -> list[dict[str, Any]]:
    path = _path(runtime)
    if not path.is_file():
        return []
    rows = load_json_dict(path).get("interventions")
    return rows if isinstance(rows, list) else []


def _seven_day_page(gsc: dict[str, Any], slug: str) -> dict[str, Any] | None:
    window = ((gsc.get("trends") or {}).get("windows") or {}).get("7", {})
    rows = ((window.get("page") or {}).get("current") or {}).get("rows") or []
    for row in rows:
        if row.get("page", "").rstrip("/").endswith("/" + slug):
            return {k: row[k] for k in ("impressions", "clicks", "ctr", "position")}
    return None


def record_result(runtime: Path, decision: dict[str, Any], outcome: dict[str, Any],
                  verification: dict[str, Any], observation: dict[str, Any]) -> None:
    capability = decision.get("capability_id")
    receipt = outcome.get("evidence") or {}
    rows = _rows(runtime)
    if capability == "link_repair" and verification.get("verified") and outcome.get("status") == "SUCCEEDED":
        gsc = load_json_dict(runtime / "intelligence" / "gsc-latest.json")
        for source, content_hash in (receipt.get("changed_files") or {}).items():
            slug = Path(source).stem
            if not slug or not (runtime.parent / source).is_file():
                continue
            if any(r.get("capability_id") == capability and r.get("source_file") == source
                   and r.get("source_sha256") == content_hash for r in rows):
                continue
            rows.append({"intervention_id": f"link_repair:{slug}:{content_hash[:16]}",
                         "capability_id": capability, "opportunity_id": decision.get("defect_id"),
                         "slug": slug, "source_file": source, "source_sha256": content_hash,
                         "execution_evidence": {"changed_file": source, "sha256": content_hash,
                                                "defect_id": decision.get("defect_id")},
                         "stage": "EXECUTED", "stage_history": ["EXECUTED"],
                         "executed_at": datetime.now(timezone.utc).isoformat(),
                         "baseline": {"fetched_at": gsc.get("fetched_at"),
                                      "end": (gsc.get("page") or {}).get("date_range", {}).get("end"),
                                      "page_7d": _seven_day_page(gsc, slug),
                                      "page_30d": gsc_control.page_metrics(gsc, slug)}})
    elif capability in CONTENT and verification.get("verified") and outcome.get("status") == "SUCCEEDED":
        slug = receipt.get("slug")
        source = receipt.get("source_file") or (f"content/articles/{slug}.html" if slug else None)
        if not slug or not source or not receipt.get("gate_passed"):
            return  # no-op/existing page is not a new intervention
        source_path = runtime.parent / source
        if not source_path.is_file():
            return
        content_hash = receipt.get("staged_content_sha256") or hashlib.sha256(source_path.read_bytes()).hexdigest()
        if any(r.get("capability_id") == capability and r.get("slug") == slug
               and r.get("source_sha256") == content_hash for r in rows):
            return
        gsc = load_json_dict(runtime / "intelligence" / "gsc-latest.json")
        rows.append({"intervention_id": f"{capability}:{slug}:{content_hash[:16]}",
                     "capability_id": capability, "opportunity_id": decision.get("opportunity_id"),
                     "slug": slug, "source_file": source,
                     "source_sha256": content_hash,
                     "execution_evidence": receipt, "stage": "EXECUTED", "stage_history": ["EXECUTED"],
                     "executed_at": datetime.now(timezone.utc).isoformat(),
                     "baseline": {"fetched_at": gsc.get("fetched_at"),
                                  "end": (gsc.get("page") or {}).get("date_range", {}).get("end"),
                                  "page_7d": _seven_day_page(gsc, slug),
                                  "page_30d": gsc_control.page_metrics(gsc, slug)}})
    elif capability == "deployment" and verification.get("verified") and outcome.get("status") == "SUCCEEDED":
        # The deployment may commit multiple accepted pages. Verify each live
        # revision independently before advancing its intervention state.
        from commander.procedure import _verify_live_revision
        files = set(receipt.get("files") or []) | {receipt.get("source_file")}
        for row in rows:
            if row.get("stage") != "EXECUTED" or row.get("source_file") not in files:
                continue
            if not row.get("source_sha256") or not _verify_live_revision(row["slug"], row["source_sha256"]):
                continue
            row.update(stage="MEASUREMENT_PENDING", published_at=datetime.now(timezone.utc).isoformat(),
                       publication_status="PUBLISHED/DEPLOYED_VERIFIED",
                       publication_evidence={"commit": receipt.get("commit"),
                                             "live_revision_sha256": row["source_sha256"]})
            row["stage_history"].extend(["PUBLISHED/DEPLOYED_VERIFIED", "MEASUREMENT_PENDING"])
    else:
        return
    atomic_json_write(_path(runtime), {"interventions": rows})


def follow_up(runtime: Path, gsc_path: Path) -> None:
    gsc = load_json_dict(gsc_path)
    if not gsc_control.fresh(gsc):
        return
    rows = _rows(runtime)
    changed = False
    end = date.fromisoformat(gsc["trends"]["end"])
    for row in rows:
        stage = row.get("stage")
        if stage not in {"MEASUREMENT_PENDING", "MEASURED"} or not row.get("published_at"):
            continue
        published = datetime.fromisoformat(row["published_at"]).date()
        baseline = row.get("baseline") or {}
        if stage == "MEASURED":
            prior_followup = row.get("followup") or {}
            if not prior_followup.get("end") or end < date.fromisoformat(prior_followup["end"]) + timedelta(days=7):
                continue
            before = prior_followup.get("page_7d")
        else:
            if end < published + timedelta(days=14) or gsc.get("fetched_at") == baseline.get("fetched_at"):
                continue
            before = baseline.get("page_7d")
        if not (gsc.get("fetched_at") and gsc.get("fetched_at") != (row.get("followup") or {}).get("fetched_at")):
            continue
        after = _seven_day_page(gsc, row["slug"])
        if before is None and after is None:
            continue  # both windows omitted this page: no defensible movement
        if before is None:
            direction = "NEWLY_OBSERVED"
        elif after is None:
            direction = "NOT_REPORTED"
        else:
            impressions = int(after["impressions"]) - int(before["impressions"])
            direction = "INCREASED" if impressions > 0 else "DECLINED" if impressions < 0 else "UNCHANGED"
        impressions_change = int(after["impressions"]) - int(before["impressions"]) if before and after else None
        clicks_change = int(after["clicks"]) - int(before["clicks"]) if before and after else None
        if stage == "MEASURED":
            row.setdefault("followup_history", []).append({"direction": row.get("direction"),
                                                             **(row.get("followup") or {})})
        row.update(stage="MEASURED", direction=direction,
                   measured_at=datetime.now(timezone.utc).isoformat(),
                   followup={"fetched_at": gsc["fetched_at"], "end": gsc["trends"]["end"],
                             "page_7d": after, "impressions_change": impressions_change,
                             "clicks_change": clicks_change,
                             "ctr_change": round(float(after["ctr"]) - float(before["ctr"]), 2) if before and after else None,
                             "baseline_presence": "reported" if before else "not_reported",
                             "followup_presence": "reported" if after else "not_reported",
                             "interpretation": "observed before/after GSC movement; causality not established"})
        if stage != "MEASURED":
            row["stage_history"].append("MEASURED")
        changed = True
    if changed:
        atomic_json_write(_path(runtime), {"interventions": rows})


def measured_outcomes(runtime: Path) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in _rows(runtime):
        if row.get("slug"):
            latest[row["slug"]] = row
    return [{"slug": r.get("slug"), "opportunity_id": r.get("opportunity_id"),
             "direction": r.get("direction"), "followup": r.get("followup")}
            for r in latest.values() if r.get("stage") == "MEASURED"]
