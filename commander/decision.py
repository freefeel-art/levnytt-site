"""LevNytt-specific decision model for the dedicated Commander loop.

The audited LevNytt business objective is a NeoLife organic-acquisition asset
(Sponsor-ID 41-830928) whose operating hierarchy is:

    NeoLife revenue/conversions            (unmeasured — Owner boundary)
    -> NeoLife conversion opportunities     (D1 link-click beacon, pending)
    -> qualified organic traffic            (GSC, measured today)
    -> search/AI visibility
    -> content and authority production.

The real, executable priorities derived from that hierarchy — and from LevNytt's
own SOUL.md production discipline — are, in order:

    1. repair an internally actionable operational defect
    1a. attempt stale GSC refresh once; then consider independent work
    2. resume an open durable commitment (interrupted work)
    3. deploy staged content that is already accepted but not yet live
       (SOUL §5a: deploy before producing more)
    4. route an observed commercial journey when its exact product route is missing
    5. complete a dedicated product page for a current NeoLife product
    6. improve an existing page with demonstrated near-page-one / CTR demand
    7. produce content for a verified demand gap
    8. distribute already published work
    9. research classified search/community opportunities and site routes
    10. refresh non-GSC measurement and due broader discovery
    11. truthful deferral (no fabricated action)

This is LevNytt's own procedure. It is NOT Cashbackkollen's merchant/cashback
taxonomy and NOT OLSP's lead/signup/sale funnel: the classes above name LevNytt
content, indexation, monetization-integrity and organic-acquisition work only.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from commander import identity

# Autonomous self-repair is data-driven, not a fixed kind list. A registered
# defect carries its own repair capability (``capability_id``) and a bounded
# repair scope; the decision layer routes any such defect to repair without the
# defect kind having to be pre-enumerated here. Only project (LevNytt) scopes
# are auto-repaired; cross-project (HERMES / shared) scopes are never
# auto-repaired inside the LevNytt loop (fail closed).
_AUTONOMOUS_REPAIR_SCOPES = frozenset({"", "PROJECT"})

# Daily content budgets: scheduling cadence is NOT publication cadence. The
# Commander may run several bounded cycles per day, but content actions are
# capped per day so more cycles never become more publishing. Publication and
# optimization are budgeted separately; defect repair, deployment of
# already-accepted work, measurement, commitment resumption, and verification
# are never budgeted.
_PUBLICATION_CAPABILITIES = frozenset({"content_production", "social_publishing", "product_page"})
_OPTIMIZATION_CAPABILITIES = frozenset({"content_improvement", "internal_linking"})

DAILY_PUBLICATION_LIMIT = 1
DAILY_OPTIMIZATION_LIMIT = 3
DAILY_MEASUREMENT_LIMIT = 1

_BUDGET_KEYS = {
    "publication": "daily_publication_budget",
    "optimization": "daily_optimization_budget",
    "measurement": "daily_measurement_budget",
}


def _budget_category(capability: str) -> str | None:
    if capability in _PUBLICATION_CAPABILITIES:
        return "publication"
    if capability in _OPTIMIZATION_CAPABILITIES:
        return "optimization"
    if capability == "measurement":
        return "measurement"
    return None


def daily_budget(state: dict[str, Any], today: str, category: str) -> dict[str, Any]:
    key = _BUDGET_KEYS[category]
    limit = {
        "publication": DAILY_PUBLICATION_LIMIT,
        "optimization": DAILY_OPTIMIZATION_LIMIT,
        "measurement": DAILY_MEASUREMENT_LIMIT,
    }[category]
    budget = state.get(key)
    if not isinstance(budget, dict) or budget.get("date") != today:
        return {"date": today, "used": 0, "limit": limit}
    return budget


def budget_available(state: dict[str, Any], today: str, capability: str) -> bool:
    category = _budget_category(capability)
    if category is None:
        return True
    budget = daily_budget(state, today, category)
    return int(budget.get("used", 0)) < int(budget.get("limit", DAILY_PUBLICATION_LIMIT))


def record_budget_use(state: dict[str, Any], today: str, capability: str) -> None:
    category = _budget_category(capability)
    if category is None:
        return
    budget = daily_budget(state, today, category)
    budget["used"] = int(budget.get("used", 0)) + 1
    state[_BUDGET_KEYS[category]] = budget


def budgets_summary(state: dict[str, Any], today: str) -> dict[str, Any]:
    return {
        "publication": daily_budget(state, today, "publication"),
        "optimization": daily_budget(state, today, "optimization"),
        "measurement": daily_budget(state, today, "measurement"),
    }


def action_key(action: dict[str, Any]) -> str:
    """Stable identity of one bounded attempt, independent of its prose reason."""
    return ":".join(str(action.get(key) or "") for key in
                    ("kind", "capability_id", "commitment_id", "defect_id", "opportunity_id", "code"))


def _due(timestamp: Any, days: int = 7) -> bool:
    if not isinstance(timestamp, str):
        return True
    try:
        observed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return observed.tzinfo is None or datetime.now(timezone.utc) - observed > timedelta(days=days)
    except ValueError:
        return True


def commitment_executable(
    evidence: dict[str, Any],
    commitment: dict[str, Any],
    *,
    budget_check=None,
    attempted: set[str] | None = None,
) -> bool:
    """Return whether one OPEN commitment can execute in the current state."""
    if budget_check is None:
        budget_check = lambda _capability: True
    attempted = attempted or set()
    capability = str(commitment.get("capability_id") or "")
    candidate = {
        "kind": "resume_commitment",
        "commitment_id": commitment.get("commitment_id"),
        "capability_id": capability,
    }
    if capability in set(evidence.get("blocked_capabilities") or []):
        return False
    if action_key(candidate) in attempted:
        return False
    retry_after = (commitment.get("metadata") or {}).get("retry_after")
    try:
        if (retry_after is not None
                and capability not in set(evidence.get("cleared_capability_blockers") or [])
                and datetime.now(timezone.utc).timestamp() < float(retry_after)):
            return False
    except (TypeError, ValueError):
        pass
    if capability in set(evidence.get("cleared_capability_blockers") or []):
        return True
    recent = evidence.get("recent_decisions") or []
    original_id = str(candidate.get("commitment_id") or "").split(":", 2)[-1]
    if any((row.get("commitment_id") == candidate.get("commitment_id")
            or (row.get("capability_id") == capability and row.get("opportunity_id") == original_id))
           and row.get("execution", {}).get("status") not in {"SUCCEEDED", "PARTIAL", "PUBLISHED"}
           and not _due(row.get("selected_at"), days=1) for row in recent):
        return False
    freshness = evidence.get("measurement_freshness") or {}
    if freshness.get("gsc_fresh") is False and capability == "content_improvement":
        return False
    return capability != "measurement" or budget_check("measurement")
def decide(
    evidence: dict[str, Any],
    defects: list[dict[str, Any]],
    commitments: list[dict[str, Any]],
    *,
    budget_check=None,
    attempted: set[str] | None = None,
) -> dict[str, Any]:
    """Select the next independent justified action within an invocation.

    Priority is the LevNytt operating hierarchy plus self-repair and deployment
    discipline. A measured zero / no qualified work is a truthful deferral,
    never a fabricated action.

    ``budget_check(capability)`` gates NEW content/measurement actions against
    their daily budget. When a capability's budget is exhausted, that
    opportunity is skipped so the cycle defers rather than exceeding the bound.
    """
    if budget_check is None:
        budget_check = lambda capability: True
    attempted = attempted or set()
    recent = evidence.get("recent_decisions") or []
    blocked_capabilities = set(evidence.get("blocked_capabilities") or [])

    def available(action: dict[str, Any]) -> bool:
        if action.get("capability_id") in blocked_capabilities:
            return False
        if action_key(action) in attempted:
            return False
        capability = action.get("capability_id")
        if action.get("kind") == "resume_commitment":
            if capability in set(evidence.get("cleared_capability_blockers") or []):
                return True  # an independently rechecked blocker has cleared
            original_id = str(action.get("commitment_id") or "").split(":", 2)[-1]
            return not any((r.get("commitment_id") == action.get("commitment_id")
                            or (r.get("capability_id") == capability and r.get("opportunity_id") == original_id))
                           and r.get("execution", {}).get("status") not in {"SUCCEEDED", "PARTIAL", "PUBLISHED"}
                            and not _due(r.get("selected_at"), days=1) for r in recent)
        # Do not pay for repeated discovery or re-run a blocked commitment at
        # every cron tick. A new observation or the next day reopens the lane.
        if capability in {"seo_intelligence", "search_demand_scout", "community_intelligence", "product_discovery"}:
            return not any(r.get("capability_id") == capability
                           and r.get("opportunity_id") == action.get("opportunity_id")
                           and not _due(r.get("selected_at"), days=1) for r in recent)
        return True

    # 1. Repair an actionable internal defect first. Routing is data-driven:
    #    any defect registered with a bounded repair capability and a project
    #    (LevNytt) repair scope is actionable, not only a known defect kind.
    for defect in defects:
        capability = str(defect.get("capability_id") or "").strip()
        if not capability:
            continue
        repair = defect.get("repair") or {}
        scope = str(repair.get("repository_kind") or "").upper()
        if scope not in _AUTONOMOUS_REPAIR_SCOPES:
            continue
        candidate = {
            "kind": "repair_defect",
            "defect_id": defect.get("defect_id"),
            "defect_kind": defect.get("kind"),
            "capability_id": capability,
            "reason": defect.get("description", "actionable defect"),
        }
        if available(candidate):
            return candidate

    # Organic-demand decisions must never treat an old GSC window as today's
    # market. Deterministic defect repair above does not depend on GSC.
    freshness = evidence.get("measurement_freshness") or {}
    if freshness.get("gsc_fresh") is False:
        if budget_check("measurement"):
            candidate = {"kind": "opportunity", "capability_id": "measurement",
                         "opportunity_id": "measurement:gsc-refresh",
                         "reason": "Decision-relevant GSC evidence is stale; refresh before selecting GSC-dependent work."}
            if available(candidate):
                return candidate
    gsc_current = freshness.get("gsc_fresh") is not False

    # 2. Resume an open commitment (durable, interrupted work).
    for commitment in commitments:
        candidate = {
            "kind": "resume_commitment",
            "commitment_id": commitment.get("commitment_id"),
            "capability_id": commitment.get("capability_id"),
            "reason": f"resume open commitment: {str(commitment.get('action') or '')[:160]}",
        }
        if (available(candidate) and commitment_executable(
                evidence, commitment, budget_check=budget_check, attempted=attempted)):
            return candidate

    # 3. Deploy staged content that is already accepted but not yet live.
    staged = list(evidence.get("staged_awaiting_deployment") or [])
    pending = evidence.get("pending_deployment_verification")
    if staged or pending:
        candidate = {
            "kind": "opportunity",
            "capability_id": "deployment",
            "opportunity_id": f"deployment:{staged[0]}" if staged else "deployment:pending",
            "reason": (
                "Staged content is awaiting deployment; deploy it before "
                "producing more (SOUL §5a)."
            ),
        }
        if available(candidate):
            return candidate

    # Refresh the official NeoLife catalog before selecting from a potentially
    # stale local Product Entity catalog. This is bounded by the catalog TTL and
    # does not consume a content budget.
    if evidence.get("product_catalog_discovery_due"):
        candidate = {
            "kind": "opportunity",
            "capability_id": "product_discovery",
            "opportunity_id": "product-catalog:refresh",
            "reason": "Refresh the official NeoLife catalog and ingest missing Product Entities.",
        }
        if available(candidate):
            return candidate

    def routing_candidate(row: dict[str, Any]) -> dict[str, Any]:
        return {"kind": "opportunity", "capability_id": "internal_linking",
                "opportunity_id": row["opportunity_id"], "target": row,
                "provenance": row.get("evidence"),
                "reason": "Route an observed reader journey to a relevant existing NeoLife product page."}

    # A real recent shop/registration click on a qualifying page makes its
    # missing product route a stronger commercial opportunity than page count.
    if budget_check("internal_linking"):
        for row in evidence.get("internal_link_opportunities") or []:
            if row.get("evidence", {}).get("cta_click_observed"):
                candidate = routing_candidate(row)
                if available(candidate):
                    return candidate

    # 4. Produce a dedicated product page for a current NeoLife product lacking
    # one. The coverage invariant is CURRENT_NEOLIFE_PRODUCT ->
    # DEDICATED_PRODUCT_PAGE; search volume affects ordering only, never
    # eligibility.
    backlog = list(evidence.get("product_backlog") or [])
    for item in backlog if budget_check("product_page") else []:
        candidate = {
            "kind": "product_backlog",
            "capability_id": "product_page",
            "opportunity_id": f"product-page:{item.get('code')}",
            "code": item.get("code"),
            "product_name": item.get("product_name"),
            "slug": item.get("slug"),
            "reason": (
                f"Current NeoLife product {item.get('product_name')!r} "
                f"(Kod {item.get('code')}) lacks a dedicated product page "
                f"({item.get('coverage')})."
            ),
        }
        if available(candidate):
            return candidate

    # 5. Improve an existing page with demonstrated near-page-one / CTR demand.
    availability = evidence.get("runtime_capability_availability") or {}
    ci_entry = availability.get("content_improvement")
    if gsc_current and isinstance(ci_entry, dict) and ci_entry.get("executable_now") is True and budget_check("content_improvement"):
        opportunities = evidence.get("content_improvement_opportunities") or {}
        rows = opportunities.get("opportunities") or []
        measured = evidence.get("intervention_followups") or []
        declines = {r.get("slug") for r in measured if r.get("direction") == "DECLINED"}
        current_scout = evidence.get("search_demand_scout") or {}
        updates = {str(r.get("term") or "").casefold(): r for r in
                   (current_scout.get("actionable_opportunities") or []) if not _due(current_scout.get("checked_at"))
                   if r.get("classification") == "UPDATE"}
        from commander.gsc_control import page_trend
        trends = evidence.get("gsc_trends") or {}
        # Within the existing improvement priority, use newly tested pages
        # rather than the incidental order of an absolute 28d snapshot.
        ranked = sorted(rows, key=lambda r: (
            str(r.get("research_topic") or r.get("title") or "").casefold() in updates,
            r.get("slug") in declines,
            bool(((page_trend(trends, str(r.get("slug"))) or {}).get("impressions_change") or 0) > 0),
            not bool((page_trend(trends, str(r.get("slug"))) or {}).get("newly_observed")),
        ), reverse=True)
        for selected in ranked:
            opportunity_id = str(selected.get("opportunity_id"))
            trend = page_trend(trends, str(selected.get("slug")))
            candidate = {
            "kind": "opportunity",
            "capability_id": "content_improvement",
            "opportunity_id": opportunity_id,
            "target": selected.get("slug"),
            "provenance": (updates.get(str(selected.get("research_topic") or selected.get("title") or "").casefold())
                           or selected.get("gsc")),
            "reason": ("A later GSC observation shows declining exposure for this previously improved page; "
                       "re-evaluate its current opportunity." if selected.get("slug") in declines else
                       (f"An existing page has measured near-page-one position or a CTR gap; "
                        f"its {trend['current']['impressions']} impressions in 7d versus "
                        f"{trend['previous']['impressions']} in the preceding 7d inform this choice."
                        if trend and trend.get("previous") else
                        "An existing page has measured near-page-one position or a CTR gap; it is newly observed in the 7d GSC window (prior presence not reported)."
                        if trend else "An existing page has measured near-page-one position or a CTR gap; improve it rather than producing new content.")),
            }
            if available(candidate):
                return candidate

    # 6. Produce content for a verified demand gap.
    cp_entry = availability.get("content_production")
    if gsc_current and isinstance(cp_entry, dict) and cp_entry.get("executable_now") is True and budget_check("content_production"):
        seo_intel = evidence.get("seo_intelligence") or {}
        keywords = list(seo_intel.get("next_eligible_keywords") or [])
        for keyword in keywords:
            source = next((r for r in seo_intel.get("keywords") or []
                           if isinstance(r, dict) and str(r.get("keyword", "")).casefold() == str(keyword).casefold()), {})
            gsc_query = next((r for r in evidence.get("gsc_queries") or []
                              if isinstance(r, dict) and str(r.get("query", "")).casefold() == str(keyword).casefold()
                              and int(r.get("impressions") or 0) > 0), None)
            if not ((source.get("monthly_search_volume") or 0) > 0 or gsc_query or
                    (source.get("evidence_type") == "COMMUNITY_DEMAND" and source.get("source_url"))):
                continue
            candidate = {
            "kind": "opportunity",
            "capability_id": "content_production",
            "opportunity_id": f"content-gap:{keyword}" if keyword else None,
            "target": keyword,
            "provenance": {"scout": source, "gsc_query": gsc_query},
            "reason": (
                f"A verified demand gap exists (e.g. {keyword!r}); produce one "
                "evidence-backed article." if keyword else
                "A verified demand gap exists; produce one evidence-backed article."
            ),
            }
            if available(candidate):
                return candidate

    # 7. Distribute a newly published article (social).
    distribution = evidence.get("distribution") or {}
    eligibility = distribution.get("execution_eligibility") or {}
    if eligibility.get("executable_now") is True and budget_check("social_publishing"):
        candidates = distribution.get("distribution_candidates") or []
        for item in candidates[:8]:
            candidate = {
            "kind": "opportunity",
            "capability_id": "social_publishing",
            "opportunity_id": str(item.get("opportunity_id")),
            "reason": "A newly published article is not yet distributed to the LevNytt Facebook page.",
            }
            if available(candidate):
                return candidate

    # 8. Distribute a Pin to the LevNytt Pinterest channel (dedup-guarded).
    pin_opportunities = list(evidence.get("pinterest_opportunities") or [])
    for item in pin_opportunities if budget_check("pinterest") else []:
        candidate = {
            "kind": "opportunity",
            "capability_id": "pinterest",
            "opportunity_id": f"pinterest:{item.get('pin_class')}:{item.get('slug') or item.get('code')}",
            "reason": (
                f"Distribute a {item.get('pin_class')} Pin for "
                f"{item.get('product_name') or item.get('title')!r} to Pinterest."
            ),
        }
        if available(candidate):
            return candidate

    # Search Scout's classified, exact CREATE/UPDATE candidates become
    # actionable only through the existing research/improvement pipelines.
    scout = evidence.get("search_demand_scout") or {}
    seo_intel = evidence.get("seo_intelligence") or {}
    known_terms = {str(k.get("keyword", "")).casefold() for k in seo_intel.get("keywords") or [] if isinstance(k, dict)}
    known_terms.update(str(term).casefold() for term in evidence.get("known_keyword_terms") or [])
    for row in (scout.get("actionable_opportunities") or []) if not _due(scout.get("checked_at")) else []:
        if row.get("classification") == "CREATE" and row.get("term") and row["term"].casefold() not in known_terms:
            candidate = {"kind": "opportunity", "capability_id": "seo_intelligence",
                          "opportunity_id": f"scout:create:{row['term']}", "target": row["term"],
                          "provenance": row,
                         "reason": "Validate a newly discovered, uncovered search-demand opportunity."}
            if available(candidate):
                return candidate
    for row in evidence.get("community_demand_candidates") or []:
        term = row.get("keyword")
        if not term or str(term).casefold() in known_terms:
            continue
        candidate = {"kind": "opportunity", "capability_id": "seo_intelligence",
                     "opportunity_id": f"community:research:{term}", "target": term,
                     "provenance": row,
                     "reason": "Validate an evidenced real-user question against search demand and existing content."}
        if available(candidate):
            return candidate

    # First-party CTA counts are a proxy, never an invented conversion count.
    # A clicked page with an exact, missing route to an existing product page
    # is more commercially grounded than another generic article.
    for row in evidence.get("internal_link_opportunities") or []:
        candidate = routing_candidate(row)
        if budget_check("internal_linking") and available(candidate):
            return candidate

    # 9. Refresh non-decision-blocking measurement once production is exhausted.
    #    Stale GSC was already handled by the pre-decision freshness gate.
    freshness = evidence.get("measurement_freshness") or {}
    if gsc_current and not freshness.get("fresh"):
        if budget_check("measurement"):
            candidate = {
                "kind": "opportunity",
                "capability_id": "measurement",
                "opportunity_id": "measurement:cta-refresh",
                "reason": "Measurement evidence is stale; refresh GSC + NeoLife link-click evidence.",
            }
            if available(candidate):
                return candidate

    # 9. Collect missing search-demand evidence (Scout / DataForSEO) when the
    #    content pool is not yet exhausted but no eligible keyword is ready.
    pool = seo_intel.get("opportunity_pool") or {}
    if not pool.get("exhausted") and seo_intel:
        # A seed with no measured demand is a research target, never an excuse
        # to produce an article. Preserve its exact identity through Scout.
        for keyword in seo_intel.get("next_eligible_keywords") or []:
            source = next((r for r in seo_intel.get("keywords") or []
                           if isinstance(r, dict) and str(r.get("keyword", "")).casefold() == str(keyword).casefold()), {})
            observed = any(isinstance(r, dict) and str(r.get("query", "")).casefold() == str(keyword).casefold()
                           and int(r.get("impressions") or 0) > 0 for r in evidence.get("gsc_queries") or [])
            if (source.get("monthly_search_volume") or 0) > 0 or observed or (
                source.get("evidence_type") == "COMMUNITY_DEMAND" and source.get("source_url")
            ):
                continue
            candidate = {"kind": "opportunity", "capability_id": "seo_intelligence",
                         "opportunity_id": f"seo:validate:{keyword}", "target": keyword,
                         "provenance": source, "reason": "Validate an unmeasured topic before any content decision."}
            if available(candidate):
                return candidate
        candidate = {
            "kind": "opportunity",
            "capability_id": "seo_intelligence",
            "opportunity_id": "seo:unresearched-pool",
            "reason": "Search-demand pool is not exhausted; collect/refresh keyword evidence.",
        }
        if available(candidate):
            return candidate

    if gsc_current and scout and _due(scout.get("checked_at")) and not any(
        gsc_current and budget_check(c) and
        (evidence.get("runtime_capability_availability") or {}).get(c, {}).get("executable_now")
        for c in ("content_improvement", "content_production")
    ):
        candidate = {"kind": "opportunity", "capability_id": "search_demand_scout",
                     "opportunity_id": "discovery:search-demand",
                     "reason": "Broader external search demand and site gaps are due for discovery."}
        if available(candidate):
            return candidate

    community = (evidence.get("community") or {}).get("community_intelligence") or {}
    if community and _due(community.get("last_run_at")):
        candidate = {"kind": "opportunity", "capability_id": "community_intelligence",
                     "opportunity_id": "discovery:community",
                     "reason": "Refresh real-user questions across LevNytt product categories."}
        if available(candidate):
            return candidate

    # 9. Truthful deferral.
    return {
        "kind": "idle",
        "capability_id": None,
        "reason": "No further justified executable work in this invocation; remaining work awaits evidence, budget, or an external boundary.",
    }
