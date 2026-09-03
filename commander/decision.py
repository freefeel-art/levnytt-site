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
    2. resume an open durable commitment (interrupted work)
    3. deploy staged content that is already accepted but not yet live
       (SOUL §5a: deploy before producing more)
    4. refresh stale measurement before acting on stale evidence
    5. improve an existing page with demonstrated near-page-one / CTR demand
    6. produce content for a verified demand gap
    7. distribute a newly published article (social)
    8. collect missing search-demand evidence (Scout / DataForSEO)
    9. truthful deferral (no fabricated action)

This is LevNytt's own procedure. It is NOT Cashbackkollen's merchant/cashback
taxonomy and NOT OLSP's lead/signup/sale funnel: the classes above name LevNytt
content, indexation, monetization-integrity and organic-acquisition work only.
"""

from __future__ import annotations

from typing import Any

from commander import identity

# Defect kinds that are internally actionable and the capability that repairs
# them. Only these participate in autonomous self-repair; anything else is an
# Owner boundary and is recorded but never silently "repaired".
_ACTIVE_DEFECT_CAPABILITY = {
    "broken_internal_link": "link_repair",
}

# Daily content budgets: scheduling cadence is NOT publication cadence. The
# Commander may run several bounded cycles per day, but content actions are
# capped per day so more cycles never become more publishing. Publication and
# optimization are budgeted separately; defect repair, deployment of
# already-accepted work, measurement, commitment resumption, and verification
# are never budgeted.
_PUBLICATION_CAPABILITIES = frozenset({"content_production", "social_publishing", "product_page"})
_OPTIMIZATION_CAPABILITIES = frozenset({"content_improvement"})

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


def decide(
    evidence: dict[str, Any],
    defects: list[dict[str, Any]],
    commitments: list[dict[str, Any]],
    *,
    budget_check=None,
) -> dict[str, Any]:
    """Select one action by business impact and evidence.

    Priority is the LevNytt operating hierarchy plus self-repair and deployment
    discipline. A measured zero / no qualified work is a truthful deferral,
    never a fabricated action.

    ``budget_check(capability)`` gates NEW content/measurement actions against
    their daily budget. When a capability's budget is exhausted, that
    opportunity is skipped so the cycle defers rather than exceeding the bound.
    """
    if budget_check is None:
        budget_check = lambda capability: True

    # 1. Repair an actionable internal defect first.
    for defect in defects:
        kind = str(defect.get("kind") or "")
        capability = _ACTIVE_DEFECT_CAPABILITY.get(kind)
        if capability:
            return {
                "kind": "repair_defect",
                "defect_id": defect.get("defect_id"),
                "defect_kind": kind,
                "capability_id": capability,
                "reason": defect.get("description", "actionable defect"),
            }

    # 2. Resume an open commitment (durable, interrupted work).
    for commitment in commitments:
        return {
            "kind": "resume_commitment",
            "commitment_id": commitment.get("commitment_id"),
            "capability_id": commitment.get("capability_id"),
            "reason": f"resume open commitment: {str(commitment.get('action') or '')[:160]}",
        }

    # 3. Deploy staged content that is already accepted but not yet live.
    staged = list(evidence.get("staged_awaiting_deployment") or [])
    pending = evidence.get("pending_deployment_verification")
    if staged or pending:
        return {
            "kind": "opportunity",
            "capability_id": "deployment",
            "opportunity_id": "deployment:staged",
            "reason": (
                "Staged content is awaiting deployment; deploy it before "
                "producing more (SOUL §5a)."
            ),
        }

    # 4. Produce a dedicated product page for a current NeoLife product lacking
    # one. The coverage invariant is CURRENT_NEOLIFE_PRODUCT ->
    # DEDICATED_PRODUCT_PAGE; search volume affects ordering only, never
    # eligibility.
    backlog = list(evidence.get("product_backlog") or [])
    if backlog and budget_check("product_page"):
        item = backlog[0]
        return {
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

    # 5. Refresh stale measurement before acting on stale evidence.
    freshness = evidence.get("measurement_freshness") or {}
    if not freshness.get("fresh"):
        if budget_check("measurement"):
            return {
                "kind": "opportunity",
                "capability_id": "measurement",
                "opportunity_id": None,
                "reason": "Measurement evidence is stale; refresh GSC + NeoLife link-click evidence.",
            }

    # 5. Improve an existing page with demonstrated near-page-one / CTR demand.
    availability = evidence.get("runtime_capability_availability") or {}
    ci_entry = availability.get("content_improvement")
    if isinstance(ci_entry, dict) and ci_entry.get("executable_now") is True and budget_check("content_improvement"):
        opportunities = evidence.get("content_improvement_opportunities") or {}
        rows = opportunities.get("opportunities") or []
        opportunity_id = str(rows[0].get("opportunity_id")) if rows else None
        return {
            "kind": "opportunity",
            "capability_id": "content_improvement",
            "opportunity_id": opportunity_id,
            "reason": (
                "An existing page has measured near-page-one position or a CTR "
                "gap; improve it rather than producing new content."
            ),
        }

    # 6. Produce content for a verified demand gap.
    cp_entry = availability.get("content_production")
    if isinstance(cp_entry, dict) and cp_entry.get("executable_now") is True and budget_check("content_production"):
        seo_intel = evidence.get("seo_intelligence") or {}
        keywords = list(seo_intel.get("next_eligible_keywords") or [])
        keyword = keywords[0] if keywords else None
        return {
            "kind": "opportunity",
            "capability_id": "content_production",
            "opportunity_id": None,
            "reason": (
                f"A verified demand gap exists (e.g. {keyword!r}); produce one "
                "evidence-backed article." if keyword else
                "A verified demand gap exists; produce one evidence-backed article."
            ),
        }

    # 7. Distribute a newly published article (social).
    distribution = evidence.get("distribution") or {}
    eligibility = distribution.get("execution_eligibility") or {}
    if eligibility.get("executable_now") is True and budget_check("social_publishing"):
        candidates = distribution.get("distribution_candidates") or []
        opportunity_id = str(candidates[0].get("opportunity_id")) if candidates else None
        return {
            "kind": "opportunity",
            "capability_id": "social_publishing",
            "opportunity_id": opportunity_id,
            "reason": "A newly published article is not yet distributed to the LevNytt Facebook page.",
        }

    # 8. Distribute a Pin to the LevNytt Pinterest channel (dedup-guarded).
    pin_opportunities = list(evidence.get("pinterest_opportunities") or [])
    if pin_opportunities and budget_check("pinterest"):
        item = pin_opportunities[0]
        return {
            "kind": "opportunity",
            "capability_id": "pinterest",
            "opportunity_id": f"pinterest:{item.get('pin_class')}:{item.get('slug') or item.get('code')}",
            "reason": (
                f"Distribute a {item.get('pin_class')} Pin for "
                f"{item.get('product_name') or item.get('title')!r} to Pinterest."
            ),
        }

    # 9. Collect missing search-demand evidence (Scout / DataForSEO) when the
    #    content pool is not yet exhausted but no eligible keyword is ready.
    seo_intel = evidence.get("seo_intelligence") or {}
    pool = seo_intel.get("opportunity_pool") or {}
    if not pool.get("exhausted"):
        return {
            "kind": "opportunity",
            "capability_id": "seo_intelligence",
            "opportunity_id": None,
            "reason": "Search-demand pool is not exhausted; collect/refresh keyword evidence.",
        }

    # 9. Truthful deferral.
    return {
        "kind": "idle",
        "capability_id": None,
        "reason": "no qualified evidence-backed work this cycle",
    }
