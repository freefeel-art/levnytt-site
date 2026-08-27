"""LevNytt domain adapters and executors for the shared Commander loop.

Supplies only domain adapters/executors/evidence helpers. It does NOT encode
LevNytt's leadership decisions: the Commander decision comes from
``app.commander.decision.decide`` (the real LLM Commander), which loads the
authoritative ``docs/commander/SOUL.md``, the LevNytt objectives, and the
facts-only evidence. This file's ``execute`` maps the Commander's selected
capability to one bounded, NeoLife-scoped domain action.

LevNytt is the NeoLife project. No OLSP or Cashbackkollen objective,
attribution, runtime state, or business logic is used here.

Production chain implemented here (each step is a bounded domain action):
    measurement -> intelligence -> content-gap -> production (full page)
    -> acceptance gate -> staging -> deployment -> live verification
    -> truthful commitment resolution.
"""

from __future__ import annotations

import ast
import hashlib
import html as html_lib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Stockholm")
SITE = "https://levnytt.se"
GSC_PROPERTY = "sc-domain:levnytt.se"
SPONSOR_ID = "41-830928"
SHOP_URL = f"https://se.neolifeshop.com/i/shop.html?sponsor={SPONSOR_ID}"
REGISTRATION_URL = f"https://se.neolifeshop.com/i/registration.html?type=reseller&sponsor={SPONSOR_ID}"
D1_DATABASE = "levnytt-cta-events"
CTA_LATEST_FILENAME = "cta-events-latest.json"
CTA_ATTEMPT_FILENAME = "cta-events-last-attempt.json"
PENDING_DEPLOYMENT_FILENAME = "pending-deployment-verification.json"
USER_AGENT = "Mozilla/5.0 (compatible; LevNyttHermes/1.0; +https://levnytt.se)"
HERMES_REPO = Path("/home/yampa/projects/active/hermes")
HERMES_PYTHON = HERMES_REPO / ".venv" / "bin" / "python"

AUTHOR = {
    "name": "Jarmo Halonen",
    "url": "https://levnytt.se/den-fundersamma-mannen",
    "initials": "JH",
    "bio": "Oberoende NeoLife-distributör (Sponsor-ID 41-830928) och grundare av LevNytt.",
}

# ── research-evidence source hierarchy ────────────────────────────
# Public authorities (Swedish/EU) and authoritative reference sources. The
# skincare/hair and home-care product lines resolve to different authorities
# than the supplement lines: NHS/Mayo/MedlinePlus/AAD for skin and hair,
# the US EPA (and existing konsumentverket.se) for cleaning-product safety.
AUTHORITY_DOMAINS = (
    "livsmedelsverket.se", "efsa.europa.eu", "efsa.onlinelibrary.wiley.com",
    "who.int", "fda.gov", "konsumentverket.se", "1177.se",
    "folkhalsomyndigheten.se", "europa.eu", "ec.europa.eu",
    "nhs.uk", "mayoclinic.org", "medlineplus.gov", "aad.org",
    "health.harvard.edu", "dermnetnz.org", "epa.gov",
)
# Peer-reviewed / primary science and reference sources.
SCIENCE_DOMAINS = (
    "pubmed.ncbi.nlm.nih.gov", "pmc.ncbi.nlm.nih.gov", "ncbi.nlm.nih.gov",
    "nih.gov", "ods.od.nih.gov", "link.springer.com", "cambridge.org",
    "academic.oup.com", "sciencedirect.com", "mdpi.com", "nature.com",
    "nejm.org", "thelancet.com", "doi.org", "jamanetwork.com",
    "nutrition.org", "faseb.org", "frontiersin.org",
)
# First-party NeoLife + LevNytt material (never treated as independent science).
NEOLIFE_DOMAINS = ("neolifeshop.com", "neolife.com", "levnytt.se")

_SE_SERP_LOCATION = 2752  # Sweden
_US_SERP_LOCATION = 2840  # United States

# ── Community Intelligence: read-only discovery ─────────────────────
# Fixed, small, human-reviewed query set for community_intelligence. Kept
# deliberately bounded (not auto-expanded from arbitrary keyword candidates)
# so a single capability run has a known, small cost and a known, reviewable
# scope.
#
# Topic/category-map correction: the prior "rebalanced" 10-query set (4
# MLM/NeoLife-generic + 6 supplement-topic, after Stage 4.5 added
# probiotika/omega-3/antioxidanter/multivitamin) was itself still
# supplement-heavy -- every added query was a supplement topic, so it never
# represented LevNytt's other real, distinct content categories. Rebuilt
# from real evidence, not assumption:
#
#   - content/products/categories.json (LevNytt's real product taxonomy)
#     names five real categories: supplements/Kosttillskott,
#     weight_management/Viktkontroll, home_care/"Golden Rengöring",
#     personal_care/"Hår & Kroppsvård", skin_care/Hudvård (+ accessories,
#     not a discussion topic).
#   - config/content-inventory.json (139 real published content slugs)
#     confirms the real, UNEQUAL distribution across those categories:
#     supplements/nutrition dominate (~90+ real articles), business/MLM
#     transparency content is substantial (~12 real articles), while
#     personal_care+skin_care (~5), weight_management (~3), and home_care
#     (~3) are each real but thin.
#   - runtime/intelligence/gsc-latest.json (196 real GSC queries) confirms
#     the same skew in actual search demand, and additionally shows ZERO
#     current query demand for Rengöring or Personlig vård specifically,
#     and only two low-volume Viktkontroll queries (both about
#     klimakteriet/menopause weight gain). Demand signals alone would keep
#     reinforcing the supplement skew forever, so the three thin
#     categories below are seeded from real page titles/H1s in the content
#     inventory (verified via the live built pages), not from demand.
#
# Allocation is a deliberate floor-plus-weighted rule, not equal weighting
# and not proportional-to-content-share weighting (per-category source is
# recorded in the tuple below): supplements keep the largest single share
# (6 of 16) but far below their ~65% real content share, so one category
# cannot consume the discovery budget merely because it has the most
# searchable terms; MLM/business keeps 4 (above its ~9% content share,
# reflecting LevNytt's own editorial differentiation as transparency
# content); every thin-but-real category gets a guaranteed floor of 2 real,
# content-derived queries so none is reduced to zero or tokenized as a
# single bare category-name query. Total stays small and reviewable (16
# queries, up from the prior 10) -- still fixed and human-reviewed, not
# auto-generated at runtime from the full inventory.
_COMMUNITY_DISCOVERY_TOPIC_MAP: dict[str, tuple[tuple[str, str], ...]] = {
    "business_mlm": (
        ("neolife recension flashback", "content-inventory.json: neolife-historia, neolife-affarsmojlighet"),
        ("är neolife pyramidspel", "content-inventory.json: vad-ar-pyramidspel"),
        ("neolife kosttillskott forum", "content-inventory.json: mlm-produkter-kosttillskott-pris"),
        ("mlm sverige recension flashback", "content-inventory.json: hur-fungerar-natverksmarknadsforing-egentligen, mlm-foretag-skandaler-sverige-varlden"),
    ),
    "supplements_nutrition": (
        ("d-vitamin brist symptom forum", "categories.json supplements > targeted nutrient subcategory"),
        ("magnesium kosttillskott vilken forum", "categories.json supplements > mineral subcategory"),
        ("probiotika kosttillskott forum", "categories.json supplements > probiotic subcategory"),
        ("omega 3 kosttillskott vilken forum", "categories.json supplements > omega-3 subcategory"),
        ("antioxidanter kosttillskott forum", "categories.json supplements + gsc-latest.json: 'antioxidanter' 98 impressions"),
        ("multivitamin vilken bäst forum", "categories.json supplements > multivitamin subcategory"),
    ),
    "personal_care": (
        ("hudvård rekommendationer forum", "categories.json personal_care/skin_care: personlig-vard.html real page (Nutriance Organic hudvård)"),
        ("retinol hudvård forum", "content-inventory.json: retinol-pa-sommaren.html real article"),
    ),
    "weight_control": (
        ("viktuppgång klimakteriet forum", "categories.json weight_management: viktuppgang-klimakteriet.html + gsc-latest.json: 'viktuppgång klimakteriet' real query"),
        ("fibrer viktminskning forum", "content-inventory.json: fibrer-for-viktminskning.html real article"),
    ),
    "cleaning": (
        ("miljövänliga rengöringsmedel forum", "categories.json home_care/Golden Rengöring: ar-miljovanliga-rengoringsmedel-lika-effektiva.html real article"),
        ("ekologisk städning fungerar forum", "categories.json home_care/Golden Rengöring: ekologisk-stadning-greenwashing.html real article"),
    ),
}

_COMMUNITY_DISCOVERY_QUERIES: tuple[str, ...] = tuple(
    query for topic_queries in _COMMUNITY_DISCOVERY_TOPIC_MAP.values() for query, _source in topic_queries
)

# Public forums/platforms where Swedish product and MLM discussions occur.
# The Facebook Graph API does not support public group/page/post search for
# this app (confirmed via a live, read-only GET /pages/search call during
# this session: "requires the 'pages_read_engagement' permission or the
# 'Page Public Content Access' feature", neither of which this app has been
# granted). Discovery therefore runs through DataForSEO's organic SERP
# provider -- the same, already-credentialed, budget-guarded source used for
# content research elsewhere in this file -- and only keeps results whose
# domain is a known discussion venue.
_DISCUSSION_DOMAINS = {
    "facebook.com": "facebook",
    "m.facebook.com": "facebook",
    "flashback.org": "flashback_forum",
    "familjeliv.se": "familjeliv_forum",
    "reddit.com": "reddit",
    "flexans.se": "flexans_forum",
}

_QUESTION_MARKERS = ("?", "vet någon", "har någon", "vet ni", "hjälp", "undrar")


def _classify_discussion_platform(domain: str) -> str | None:
    domain = (domain or "").lower().lstrip("www.")
    for known, platform in _DISCUSSION_DOMAINS.items():
        if domain == known or domain.endswith("." + known):
            return platform
    return None


# Conservative, source-aware URL canonicalization for discovery dedup.
# Only Flashback's own real, documented URL variants are normalized -- a
# trailing page number (t<id>p<page>, e.g. .../t2406654p2 is page 2 of
# thread t2406654) or a single trailing letter (t<id>[a-z], e.g.
# t3431890n/t3431890s -- observed variants of the exact same thread,
# confirmed by identical titles in runtime/community/knowledge.json during
# the intelligence audit). Post-permalink URLs (/p<digits>, a different,
# unrelated numbering scheme with no reliable link back to a specific
# thread id) are deliberately left untouched -- merging those would risk
# conflating genuinely different threads, which this function must never do.
_FLASHBACK_THREAD_VARIANT = re.compile(r"^(/t\d+)(?:p\d+|[a-z])?$")


def _canonicalize_discussion_url(url: str) -> str:
    """Fold known same-thread URL variants (currently: Flashback thread
    pagination/anchor suffixes) into one canonical URL before dedup, so
    /t123456, /t123456p2, and /t123456s are recognized as the same
    discovery instead of three. Any URL this function doesn't specifically
    recognize is returned unchanged -- conservative by construction."""
    try:
        parts = urlsplit(url)
    except ValueError:
        return url
    domain = parts.netloc.lower().lstrip("www.")
    if domain != "flashback.org":
        return url
    match = _FLASHBACK_THREAD_VARIANT.match(parts.path)
    if not match:
        return url
    return urlunsplit((parts.scheme, parts.netloc, match.group(1), "", ""))


def _classify_discovery_item(item: dict[str, Any]) -> dict[str, Any]:
    """Attach a recommended_action label and reasoning to one discovered
    item. This is a reporting classification for a human/Owner decision --
    no code path in this repository consumes recommended_action to take any
    automated action. Third-party engagement is a separate, unbuilt
    capability."""
    url = str(item.get("url", ""))
    title = str(item.get("title", ""))
    snippet = str(item.get("snippet", ""))
    platform = item.get("platform", "")
    combined = f"{title} {snippet}".casefold()

    # A bare facebook.com hit with no path beyond a page/group slug is
    # almost always a page/group *listing*, not a specific discussion --
    # cannot responsibly recommend anything beyond noting it exists.
    path_depth = len([p for p in url.split("/")[3:] if p])
    if platform == "facebook" and path_depth <= 1:
        action, reason = "NO_ACTION", "Facebook result has no path beyond a page/group slug; not a specific discussion, just a listing."
    elif any(marker in combined for marker in _QUESTION_MARKERS):
        action, reason = "POSSIBLE_REPLY", "Title/snippet contains a direct question pattern on a topic LevNytt covers; flagged for Owner/human review, not automatic action."
    else:
        action, reason = "OBSERVE", "Discussion-shaped result on a relevant topic without a clear, specific question in the visible snippet."

    return {
        **item,
        "recommended_action": action,
        "reason": reason,
        "levnytt_relevant_content": True,  # every query is itself seeded from a LevNytt-covered topic
        "promotional_rules": "unknown_requires_manual_review",
        "provenance": {
            "method": "DataForSEO organic SERP (sv, Sweden location)",
            "classified_by": "community_intelligence heuristic v1: platform + question-marker match on title/snippet only, no page content fetched",
        },
    }


def _recover_historical_discovery_snippets(runtime: Path, production_root: Path) -> dict[str, int]:
    """Truthful, idempotent repair for discovery items persisted before the
    snippet field-name fix (code previously read item.get('description'),
    but DataForSEO's real field is 'snippet', so every historical item was
    saved with an empty snippet). Recovers the real snippet text from the raw
    normalized DataForSEO SERP artifacts that originally produced each item,
    matched by canonical URL -- the exact evidence that was actually
    observed, never invented. An item whose raw provider evidence can no
    longer be found (artifact rotated/deleted) is left untouched, snippet
    still empty, per instruction: do not fabricate history that isn't there.

    Re-classifies each recovered item with _classify_discovery_item so its
    recommended_action reflects the real title+snippet instead of the
    title-only classification computed at the time of the bug."""
    levnytt_community = _levnytt_community()
    store = levnytt_community.load_community_store(runtime)
    discovery = store.get("discovery", [])
    if not isinstance(discovery, list):
        return {"recovered": 0, "unrecoverable": 0, "unchanged": 0}

    url_to_snippet: dict[str, str] = {}
    serp_dir = production_root / "dataforseo-serp"
    for path in sorted(serp_dir.glob("*normalized.json")) if serp_dir.is_dir() else []:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        results = payload.get("organic_results") if isinstance(payload, dict) else None
        for result in results or []:
            if not isinstance(result, dict):
                continue
            url = _canonicalize_discussion_url(str(result.get("url", "")))
            snippet = str(result.get("snippet", "")).strip()
            if url and snippet and url not in url_to_snippet:
                url_to_snippet[url] = snippet

    recovered = unrecoverable = unchanged = 0
    for item in discovery:
        if not isinstance(item, dict):
            continue
        if str(item.get("snippet", "")).strip():
            unchanged += 1
            continue
        canonical_url = _canonicalize_discussion_url(str(item.get("url", "")))
        real_snippet = url_to_snippet.get(canonical_url)
        if not real_snippet:
            unrecoverable += 1
            continue
        item["snippet"] = real_snippet
        reclassified = _classify_discovery_item(item)
        item["recommended_action"] = reclassified["recommended_action"]
        item["reason"] = reclassified["reason"]
        item["provenance"] = reclassified["provenance"]
        item["snippet_recovered_at"] = datetime.now(timezone.utc).isoformat()
        item["snippet_recovery_note"] = (
            "Recovered from persisted raw DataForSEO SERP evidence after the "
            "snippet field-name bug fix; not fabricated."
        )
        recovered += 1

    if recovered:
        store["discovery"] = discovery
        levnytt_community.save_community_store(runtime, store)
    return {"recovered": recovered, "unrecoverable": unrecoverable, "unchanged": unchanged}


# Small Swedish→English topic dictionary for the general-science SERP layer.
_SE_EN_TERMS = {
    "antioxidanter": "antioxidants",
    "kosttillskott": "dietary supplements",
    "magnesium": "magnesium",
    "omega 3": "omega-3 fatty acids",
    "omega-3": "omega-3 fatty acids",
    "d vitamin": "vitamin d",
    "vitamin d": "vitamin d",
    "d-vitamin": "vitamin d",
    "probiotika": "probiotics",
    "multivitamin": "multivitamin",
    "kostfiber": "dietary fiber",
    "fibrer": "dietary fiber",
    "selen": "selenium",
    "zink": "zinc",
    "jarn": "iron",
    "kollagen": "collagen",
    "kreatin": "creatine",
    "melatonin": "melatonin",
    "protein": "protein",
    "karotenoider": "carotenoids",
    "betakarotenoider": "beta-carotene",
    "flavonoider": "flavonoids",
    "fytosteroler": "phytosterols",
    "direktforsaljning": "direct selling",
    "pyramidspel": "pyramid scheme",
    "neolife": "neolife",
    "vitamin b12": "vitamin b12",
    "c vitamin": "vitamin c",
    "vitamin c": "vitamin c",
    "vitamin e": "vitamin e",
    "adaptogen": "adaptogens",
    "adaptogener": "adaptogens",
    "cell membran": "cell membrane",
    "cellmembran": "cell membrane",
    # Personlig vård (skincare / hair) and Rengöring (home care) anchors: the
    # general-science SERP layer must query the English topic, otherwise a
    # Swedish e-commerce term is looked up on the US SERP and returns no
    # authoritative source (observed live: "hudvård" researched as "hudvård").
    "hudvård": "skin care",
    "hudvard": "skin care",
    "schampo": "shampoo",
    "håravfall": "hair loss",
    "haravfall": "hair loss",
    "torr hud": "dry skin",
    "miljövänlig rengöring": "eco-friendly cleaning products",
    "miljovanlig rengoring": "eco-friendly cleaning products",
    "diskmedel": "dish soap",
    "tvättmedel": "laundry detergent",
}

RESEARCH_CACHE_TTL_DAYS = 30

_DEFAULT_TIERBOX = [
    {"url": "/neolife-vetenskap", "label": "Vetenskap", "title": "Forskningen bakom produkterna"},
    {"url": "/neolife-historia", "label": "Historia", "title": "NeoLife sedan 1958"},
    {"url": "/direktforsaljning-fakta", "label": "Direktförsäljning", "title": "Fakta om modellen"},
    {"url": "/om-oss", "label": "Om LevNytt", "title": "Varför plattformen finns"},
]

_LEVNYTT_IDENTITY_CONTEXT = (
    "LevNytt (levnytt.se) is an independent Swedish NeoLife distributor consumer-education site. "
    "Write in Swedish (sv-SE). Editorial principles (binding): "
    "(1) Fakta före hype — facts and transparency, never marketing claims or income promises. "
    "(2) Värde före pris — value over price. "
    "(3) Evidence-first: distinguish independent scientific/authority sources from NeoLife first-party claims; never present NeoLife marketing as independent scientific validation. "
    "(4) No fabricated health claims, no guaranteed results, no urgency or scarcity, no income examples. "
    "(5) Reader-first explanation: help the reader understand before they decide; never hard-sell. "
    "(6) NeoLife is disclosed as the site's commercial interest (Sponsor-ID 41-830928); any CTA must be voluntary and proportionate. "
    "(7) Do not force NeoLife into unrelated sections."
)

_LEVNYTT_WRITING_INSTRUCTION_SOURCE = "docs/LEVNYTT-EDITORIAL-SYSTEM.md"


def _levnytt_editorial_context() -> str:
    """Load the project-owned writing rules used by autonomous Scribe.

    The global informational-article skill explicitly describes itself as
    operator assistance rather than a Commander production dependency.  The
    checked-in editorial system is therefore the durable instruction source.
    Missing instructions fail closed instead of borrowing another project's
    skill or silently falling back to generic copy.
    """
    source = Path(__file__).resolve().parents[1] / _LEVNYTT_WRITING_INSTRUCTION_SOURCE
    try:
        instructions = source.read_text(encoding="utf-8").strip()
    except OSError as error:
        raise RuntimeError(
            f"LevNytt writing instructions are unavailable at {_LEVNYTT_WRITING_INSTRUCTION_SOURCE}"
        ) from error
    if not instructions:
        raise RuntimeError(
            f"LevNytt writing instructions are empty at {_LEVNYTT_WRITING_INSTRUCTION_SOURCE}"
        )
    return f"{_LEVNYTT_IDENTITY_CONTEXT}\n\n{instructions}"


def _levnytt_community():
    """Load the co-located LevNytt community domain-logic module. The procedure
    is itself loaded via importlib with a synthetic package name, so a relative
    ``from . import`` cannot resolve; load by explicit file path instead."""
    import importlib.util

    path = Path(__file__).resolve().parent / "community.py"
    spec = importlib.util.spec_from_file_location("levnytt_community", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LevNyttProcedure:
    project_id = "levnytt"
    procedure_contract = {
        "contract_id": "hermes-autonomous-procedure",
        "contract_version": "1.0",
        "project_id": "levnytt",
        "opportunity_selection": "EXACT_OPPORTUNITY_ID",
        "execution_receipt": "PRESERVE_AND_NORMALIZE",
        "recoverable_failures": [
            "RECOVERABLE_CAPABILITY_GAP",
            "RECOVERABLE_EXECUTOR_FAILURE",
            "RECOVERABLE_PUBLICATION_FAILURE",
            "RECOVERABLE_QA_REJECTION",
        ],
    }

    # ── execution ─────────────────────────────────────────────────
    def execute(self, ctx, action: dict[str, Any]) -> dict[str, Any]:
        capability = str(action.get("capability", "")).strip().casefold()
        if capability == "measurement":
            return self._execute_measurement(ctx, action)
        if capability == "seo_intelligence":
            return self._execute_seo_intelligence(ctx, action)
        if capability == "content_improvement":
            return self._execute_content_improvement(ctx, action)
        if capability == "content_production":
            return self._execute_content_production(ctx, action)
        if capability == "deployment":
            return self._execute_deployment(ctx, action)
        if capability == "technical_repair":
            return self._execute_technical_repair(ctx, action)
        if capability == "content_repair":
            return self._execute_content_repair(ctx, action)
        if capability == "legacy_audit":
            return self._execute_legacy_audit(ctx, action)
        if capability == "legacy_migration":
            return self._execute_legacy_migration(ctx, action)
        if capability == "community_acquisition":
            return self._execute_community_acquisition(ctx, action)
        if capability == "community_engagement":
            return self._execute_community_engagement(ctx, action)
        if capability == "community_intelligence":
            return self._execute_community_intelligence(ctx, action)
        if capability == "social_publishing":
            return self._execute_social_publishing(ctx, action)
        return {
            "status": "CAPABILITY_GAP",
            "failure_class": "RECOVERABLE_CAPABILITY_GAP",
            "detail": f"No bounded executor is wired for capability {capability!r}.",
            "evidence": {"capability": capability},
        }

    # ── measurement ───────────────────────────────────────────────
    def _execute_measurement(self, ctx, action: dict[str, Any]) -> dict[str, Any]:
        attempted_at = datetime.now(timezone.utc).isoformat()
        previous_gsc = _read_json(ctx.runtime_directory / "intelligence" / "gsc-latest.json")
        completed = subprocess.run(
            [str(HERMES_PYTHON), "-m", "scripts.collect_gsc",
             "--project", "levnytt", "--site", GSC_PROPERTY],
            cwd=str(HERMES_REPO),
            capture_output=True, text=True, check=False,
        )
        gsc: dict[str, Any] = {
            "source": GSC_PROPERTY,
            "attempted_at": attempted_at,
            "status": "available" if completed.returncode == 0 else "unavailable",
            "returncode": completed.returncode,
        }
        if completed.returncode != 0:
            gsc_diagnostic = _bounded_provider_diagnostic(completed.stderr, completed.stdout)
            if gsc_diagnostic:
                gsc["diagnostic"] = gsc_diagnostic
        if completed.returncode == 0:
            latest = _read_json(ctx.runtime_directory / "intelligence" / "gsc-latest.json")
            if (
                latest.get("site") == GSC_PROPERTY
                and latest.get("fetched_at")
                and latest.get("fetched_at") != previous_gsc.get("fetched_at")
            ):
                gsc["fetched_at"] = latest["fetched_at"]
            else:
                gsc["status"] = "unavailable"
                gsc["diagnostic"] = (
                    "GSC collector returned success without a newly fetched matching project artifact."
                )

        cta = _collect_cta_events(ctx)
        evidence = {"sources": {"gsc": gsc, "cta_d1": cta}}
        available = [name for name, source in evidence["sources"].items() if source.get("status") == "available"]
        failed = [name for name, source in evidence["sources"].items() if source.get("status") != "available"]
        if not failed:
            status = "SUCCEEDED"
            detail = (
                "Refreshed independent Search Console and NeoLife link-click evidence "
                f"({cta['total_events']} CTA events)."
            )
        elif available:
            status = "PARTIAL"
            detail = (
                f"Measurement is degraded: refreshed {', '.join(available)}, but "
                f"{', '.join(failed)} is unavailable. No zero-event inference was made."
            )
        else:
            status = "BLOCKED"
            detail = "Measurement failed: neither Search Console nor CTA/D1 evidence was refreshed."
        return {
            "status": status,
            "detail": detail,
            "evidence": evidence,
            "retry_eligible_this_run": not bool(available),
        }

    def _execute_seo_intelligence(self, ctx, action: dict[str, Any]) -> dict[str, Any]:
        _rebuild_content_inventory(ctx.working_repository)
        _seed_keyword_candidates(ctx)
        try:
            from app.commander.scout_executor import execute as scout_execute
            code, message = scout_execute(project=ctx.working_repository)
        except Exception as error:
            return {"status": "CAPABILITY_GAP", "failure_class": "RECOVERABLE_EXECUTOR_FAILURE", "detail": f"SEO Scout execution failed: {type(error).__name__}: {error}", "evidence": {}, "repair": {"repository_kind": "HERMES", "allowed_write_scope": ["app/commander/scout_executor.py"]}}
        if code != 0:
            return {"status": "BLOCKED", "detail": message, "evidence": {"scout_code": code}}
        gap_count = _coverage_gap_count(ctx)
        return {
            "status": "SUCCEEDED",
            "detail": message,
            "evidence": {"scout_code": 0, "artifact": "runtime/intelligence/keywords.json", "content_gap_count": gap_count},
        }

    # ── existing-page improvement (stage, never publish directly) ─
    def _execute_content_improvement(self, ctx, action: dict[str, Any]) -> dict[str, Any]:
        try:
            opportunity = _content_improvement_target(action)
        except Exception as error:
            return {
                "status": "CAPABILITY_GAP",
                "failure_class": "RECOVERABLE_EXECUTOR_FAILURE",
                "detail": f"LevNytt improvement evidence contract failed: {type(error).__name__}: {error}",
                "evidence": {"external_effect_attempted": False},
                "repair": {
                    "repository_kind": "HERMES",
                    "allowed_write_scope": [
                        "app/commander/evidence.py",
                        "app/commander/procedure_contract.py",
                    ],
                },
            }
        if opportunity is None:
            return {
                "status": "BLOCKED",
                "failure_class": "EVIDENCE_REQUIRED",
                "detail": (
                    "Content improvement requires one exact current "
                    "content-improvement:<slug> opportunity_id; no page was guessed or substituted."
                ),
                "evidence": {"external_effect_attempted": False},
                "retry_eligible_this_run": False,
            }

        repo = ctx.working_repository.resolve()
        slug = str(opportunity["slug"])
        keyword = str(opportunity.get("research_topic") or opportunity.get("title") or slug)
        source_rel = str(opportunity["source_file"])
        source = (repo / source_rel).resolve()
        try:
            source.relative_to(repo)
        except ValueError:
            return {
                "status": "BLOCKED",
                "failure_class": "EVIDENCE_REQUIRED",
                "detail": "Improvement source resolves outside the LevNytt repository.",
                "evidence": {"slug": slug, "external_effect_attempted": False},
                "retry_eligible_this_run": False,
            }
        if not source.is_file():
            return {
                "status": "BLOCKED",
                "failure_class": "EVIDENCE_REQUIRED",
                "detail": f"Current improvement source is missing: {source_rel}",
                "evidence": {"slug": slug, "external_effect_attempted": False},
                "retry_eligible_this_run": False,
            }

        evidence, research_packet = _topic_scribe_evidence(ctx, keyword, slug)
        sufficiency = research_packet.get("sufficiency", {})
        if not sufficiency.get("passed") or not evidence:
            notes = "; ".join(sufficiency.get("notes", [])) or "no authoritative source evidence"
            return {
                "status": "BLOCKED",
                "failure_class": "EVIDENCE_REQUIRED",
                "detail": (
                    f"Research sufficiency not met for existing page {slug!r}: {notes}. "
                    "Obtain evidence through the normal research capability before revising it."
                ),
                "evidence": {
                    "opportunity_id": opportunity["opportunity_id"],
                    "slug": slug,
                    "research_sufficiency": sufficiency,
                    "external_effect_attempted": False,
                },
                "retry_eligible_this_run": False,
            }

        try:
            from agents.scribe.run import run as scribe_run
        except Exception as error:
            return {
                "status": "CAPABILITY_GAP",
                "failure_class": "RECOVERABLE_EXECUTOR_FAILURE",
                "detail": f"Scribe import failed: {type(error).__name__}: {error}",
                "evidence": {"slug": slug, "external_effect_attempted": False},
                "repair": {
                    "repository_kind": "HERMES",
                    "allowed_write_scope": ["agents/scribe/run.py"],
                },
            }

        issues: list[str] = []
        for attempt in range(1, 4):
            brief = _scribe_brief(keyword, slug, evidence)
            brief.update({
                "assignment_id": f"levnytt-improve-{slug}",
                "brief_id": f"levnytt-improve-{slug}",
                "format": "evidence-bound replacement for one existing canonical page",
                "existing_page": _existing_page_context(source, opportunity),
                "improvement_evidence": opportunity.get("gsc", {}),
                "title_requirements": _title_requirements(keyword, issues),
            })
            try:
                scribe_result = scribe_run(brief, project_id="levnytt")
            except Exception as error:
                issues = [f"scribe_error:{type(error).__name__}"]
                continue
            if scribe_result.get("status") != "READY_FOR_HANDOFF":
                issues = list(scribe_result.get("failure_codes") or []) or ["scribe_blocked"]
                continue
            draft_ok, draft_issues = _content_gate(keyword, scribe_result)
            if not draft_ok:
                issues = list(draft_issues)
                continue
            try:
                rendered, production_data = _render_improved_production_page(
                    repo, opportunity, scribe_result, research_packet,
                )
            except (OSError, ValueError, json.JSONDecodeError) as error:
                return {
                    "status": "BLOCKED",
                    "failure_class": "RECOVERABLE_QA_REJECTION",
                    "detail": f"Canonical Phase 1 render failed: {type(error).__name__}: {error}",
                    "evidence": {"slug": slug, "external_effect_attempted": False},
                    "retry_eligible_this_run": False,
                }
            final_ok, final_issues = _final_publication_gate(rendered)
            if not final_ok:
                issues = list(final_issues)
                continue

            data_path = repo / "content" / "data" / "production-pages.json"
            _atomic_text_write(source, rendered)
            _atomic_text_write(data_path, production_data)
            return {
                "status": "SUCCEEDED",
                "detail": (
                    f"Staged evidence-backed improvement for {slug!r} through the current "
                    "Phase 1 renderer; normal deployment remains pending."
                ),
                "evidence": {
                    "opportunity_id": opportunity["opportunity_id"],
                    "slug": slug,
                    "keyword": keyword,
                    "gate_passed": True,
                    "final_gate_passed": True,
                    "attempt": attempt,
                    "source_file": source_rel,
                    "staged_path": str(source),
                    "production_data_path": str(data_path),
                    "staged_content_sha256": _file_sha256(source),
                    "production_data_sha256": _file_sha256(data_path),
                    "public_url_preserved": opportunity["canonical_url"],
                    "date_published_preserved": True,
                    "sponsor_id_preserved": SPONSOR_ID,
                    "renderer": "scripts/site_renderer.py",
                    "lifecycle": "STAGED",
                },
            }

        return {
            "status": "BLOCKED",
            "failure_class": "RECOVERABLE_QA_REJECTION",
            "detail": f"Content improvement exhausted after 3 gated attempts for {slug!r}: " + "; ".join(issues),
            "evidence": {
                "opportunity_id": opportunity["opportunity_id"],
                "slug": slug,
                "attempts": 3,
                "gate_issues": issues,
                "external_effect_attempted": False,
            },
        }

    # ── content production (stage a full production page) ─────────
    def _execute_content_production(self, ctx, action: dict[str, Any]) -> dict[str, Any]:
        keyword = _keyword_from_action(ctx, action)
        if not keyword:
            return {"status": "BLOCKED", "failure_class": "EVIDENCE_REQUIRED", "detail": "No SEO Scout keyword evidence is available to select a content target.", "evidence": {"external_effect_attempted": False}}
        slug = _slugify(keyword)
        off_strategy = _off_strategy(keyword)
        if off_strategy:
            return {"status": "SUCCEEDED", "detail": f"Keyword {keyword!r} is off-strategy ({off_strategy}); no article produced.", "evidence": {"slug": slug, "off_strategy": off_strategy, "skipped": True}}
        repo = ctx.working_repository

        lifecycle = _content_lifecycle(repo, slug)
        if lifecycle == "LIVE":
            return {"status": "SUCCEEDED", "detail": f"Article {slug!r} is already live at {SITE}/{slug}.", "evidence": {"slug": slug, "lifecycle": "LIVE", "already_live": True}}
        if lifecycle == "DEPLOYED":
            return {"status": "SUCCEEDED", "detail": f"Article {slug!r} is committed/deployed but not yet verified live.", "evidence": {"slug": slug, "lifecycle": "DEPLOYED", "already_deployed": True}}
        if lifecycle == "STAGED":
            return {"status": "SUCCEEDED", "detail": f"Article {slug!r} is already staged and awaiting deployment.", "evidence": {"slug": slug, "lifecycle": "STAGED", "already_staged": True}}

        evidence, research_packet = _topic_scribe_evidence(ctx, keyword, slug)
        if not research_packet.get("sufficiency", {}).get("passed"):
            notes = "; ".join(research_packet["sufficiency"].get("notes", []))
            return {
                "status": "BLOCKED",
                "detail": f"Research sufficiency not met for {keyword!r}: {notes}. Broaden/retry research rather than asking Scribe to fill gaps.",
                "evidence": {"keyword": keyword, "slug": slug, "research_sufficiency": research_packet["sufficiency"], "claim_count": len(research_packet.get("claims", []))},
            }
        if not evidence:
            return {"status": "BLOCKED", "failure_class": "EVIDENCE_REQUIRED", "detail": f"Insufficient project evidence to ground an article for {keyword!r}; Commander should first delegate research.", "evidence": {"keyword": keyword, "external_effect_attempted": False}}

        try:
            from agents.scribe.run import run as scribe_run
        except Exception as error:
            return {"status": "CAPABILITY_GAP", "failure_class": "RECOVERABLE_EXECUTOR_FAILURE", "detail": f"Scribe import failed: {type(error).__name__}: {error}", "evidence": {}, "repair": {"repository_kind": "HERMES", "allowed_write_scope": ["agents/scribe/run.py"]}}

        max_attempts = 3
        issues: list[str] = []
        for attempt in range(1, max_attempts + 1):
            brief = _scribe_brief(keyword, slug, evidence)
            brief["title_requirements"] = _title_requirements(keyword, issues)
            try:
                scribe_result = scribe_run(brief, project_id="levnytt")
            except Exception as error:
                issues = [f"scribe_error:{type(error).__name__}"]
                continue
            if scribe_result.get("status") != "READY_FOR_HANDOFF":
                issues = list(scribe_result.get("failure_codes") or []) or ["scribe_blocked"]
                continue
            ok, gate_issues = _content_gate(keyword, scribe_result)
            if ok:
                html = _assemble_page(slug, keyword, scribe_result, research_packet)
                final_ok, final_issues = _final_publication_gate(html)
                if final_ok:
                    destination = repo / "content" / "articles" / f"{slug}.html"
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_text(html, encoding="utf-8")
                    _rebuild_content_inventory(repo)
                    return {
                        "status": "SUCCEEDED",
                        "detail": f"Staged production page {slug!r} at content/articles/{slug}.html (awaiting deployment).",
                        "evidence": {"slug": slug, "keyword": keyword, "gate_passed": True, "final_gate_passed": True, "attempt": attempt, "staged_path": str(destination), "lifecycle": "STAGED"},
                    }
                issues = list(final_issues)
                continue
            issues = list(gate_issues)

        return {"status": "BLOCKED", "failure_class": "RECOVERABLE_QA_REJECTION", "detail": f"Content revision exhausted after {max_attempts} attempts for {keyword!r}: " + "; ".join(issues), "evidence": {"keyword": keyword, "slug": slug, "attempts": max_attempts, "gate_issues": issues}}

    # ── deployment ────────────────────────────────────────────────
    def _execute_deployment(self, ctx, action: dict[str, Any]) -> dict[str, Any]:
        repo = ctx.working_repository
        pending_path = ctx.runtime_directory / "commander" / PENDING_DEPLOYMENT_FILENAME
        pending = _read_json(pending_path)
        if pending:
            return _resume_pending_deployment(repo, pending_path, pending)

        work = _first_staged_work(repo)
        if work is None:
            return {"status": "SUCCEEDED", "detail": "No staged article is awaiting deployment.", "evidence": {"deployable": False}}
        slug = work["slug"]

        article = repo / work["source_file"]
        if not article.is_file():
            return {"status": "BLOCKED", "detail": f"Provenance-authorized staged source is missing: {article}", "evidence": {"slug": slug, "external_effect_attempted": False}}

        # 1. Repository/deployment safety checks.
        allowed_paths = set(work["files"])
        safety = _deployment_safety(repo, slug, allowed_paths)
        if not safety["ok"]:
            return {"status": "BLOCKED", "detail": "Deployment safety check failed: " + "; ".join(safety["reasons"]), "evidence": {**safety, "external_effect_attempted": False}}

        # 2. Register routing only for a newly produced page. An improvement
        # preserves its existing canonical route and must never manufacture a
        # stale /content/articles rewrite for a root-backed page.
        if work["capability_id"] == "content_improvement":
            if not _sitemap_has_slug(repo, slug):
                return {"status": "BLOCKED", "detail": "Existing canonical page is missing from the sitemap; refusing to invent a route during improvement deployment.", "evidence": {"slug": slug, "external_effect_attempted": False}}
        else:
            redirect_ok = _add_redirect(repo, slug)
            sitemap_ok = _add_sitemap_entry(repo, slug)
            if not (redirect_ok and sitemap_ok):
                return {"status": "BLOCKED", "detail": "Could not register the slug in routing/sitemap.", "evidence": {"redirect_ok": redirect_ok, "sitemap_ok": sitemap_ok, "external_effect_attempted": False}}

        # 3. Stage exactly the intended production files (never a broad add).
        files = list(work["files"])
        for candidate in ("_redirects", "sitemap.xml"):
            changed = subprocess.run(
                ["git", "-C", str(repo), "status", "--porcelain", "--", candidate],
                capture_output=True, text=True, check=False,
            ).stdout.strip()
            if changed and candidate not in files:
                files.append(candidate)
        add = subprocess.run(["git", "-C", str(repo), "add", "--", *files], capture_output=True, text=True, check=False)
        if add.returncode != 0:
            return {"status": "BLOCKED", "detail": f"git add failed: {(add.stderr or '')[-300:]}", "evidence": {"files": files, "external_effect_attempted": False}}

        staged = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"], capture_output=True, text=True, check=False)
        staged_paths = [line[3:].strip() for line in staged.stdout.splitlines() if line[:2] in {"A ", "M "}]
        unexpected = [p for p in staged_paths if p not in files and p != "config/content-inventory.json"]
        if unexpected:
            subprocess.run(["git", "-C", str(repo), "reset", "--", *files], capture_output=True, text=True, check=False)
            return {"status": "BLOCKED", "detail": f"Refusing to commit unexpected staged files: {unexpected}", "evidence": {"unexpected": unexpected, "external_effect_attempted": False}}

        verb = "Improve" if work["capability_id"] == "content_improvement" else "Publish"
        commit = subprocess.run(
            ["git", "-C", str(repo), "commit", "-m", f"{verb} NeoLife page: {slug}"],
            capture_output=True, text=True, check=False,
        )
        if commit.returncode != 0:
            subprocess.run(["git", "-C", str(repo), "reset", "--", *files], capture_output=True, text=True, check=False)
            return {"status": "BLOCKED", "detail": f"git commit failed: {(commit.stderr or commit.stdout or '')[-300:]}", "evidence": {"external_effect_attempted": False}}

        pending = {
            "slug": slug,
            "commit": _git_head(repo),
            "pushed": False,
            "files": files,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        _atomic_json_write(pending_path, pending)
        push_ok, push_detail = _push_main_with_rebase(repo)
        if not push_ok:
            return {"status": "BLOCKED", "detail": push_detail, "evidence": {"slug": slug, "commit_ok": True, "pending_recovery": True, "external_effect_attempted": True}}
        pending["pushed"] = True
        pending["commit"] = _git_head(repo)
        _atomic_json_write(pending_path, pending)

        # 4. Live verification (Cloudflare Pages auto-deploys on push).
        live = _verify_live(slug, wait_seconds=120)
        if not live:
            return {"status": "BLOCKED", "detail": f"Committed and pushed {slug!r}, but live verification failed (not yet 200).", "evidence": {"slug": slug, "deployed": True, "live_verified": False, "pending_recovery": True, "external_effect_attempted": True}}

        pending_path.unlink(missing_ok=True)
        return {
            "status": "SUCCEEDED",
            "detail": f"Deployed {slug!r} and verified live at {SITE}/{slug}.",
            "evidence": {"slug": slug, "live_url": f"{SITE}/{slug}", "live_verified": True, "deployed": True, "external_effect_attempted": True},
        }

    def _execute_technical_repair(self, ctx, action: dict[str, Any]) -> dict[str, Any]:
        if _https_serves_200():
            return {"status": "SUCCEEDED", "detail": "levnytt.se serves HTTPS 200.", "evidence": {"https_ok": True}}
        return {"status": "CAPABILITY_GAP", "failure_class": "RECOVERABLE_CAPABILITY_GAP", "detail": "The https/redirect repair executor is not wired; the deployment change is outside this domain executor.", "evidence": {"https_ok": False}}

    def _execute_content_repair(self, ctx, action: dict[str, Any]) -> dict[str, Any]:
        missing = _pages_missing_sponsor_disclosure(ctx.working_repository)
        if not missing:
            return {"status": "SUCCEEDED", "detail": "No root production page is missing the Sponsor-ID disclosure.", "evidence": {"missing_disclosure_count": 0}}
        return {"status": "BLOCKED", "detail": f"{len(missing)} pages are missing the Sponsor-ID disclosure.", "evidence": {"missing_disclosure_count": len(missing), "sample": missing[:10]}}

    # ── legacy content estate ──────────────────────────────────────
    def _execute_legacy_audit(self, ctx, action: dict[str, Any]) -> dict[str, Any]:
        """Discover + classify the legacy estate and persist the audit artifact.

        Read-only with respect to content: it never modifies a page. When the
        fresh classification is identical to the last persisted audit
        (audit["already_current"]), evidence["skipped"] is set so the shared
        no-new-work/supersession handling in autonomous.py recognizes a
        repeat audit as exactly that -- not a fresh production accomplishment
        to keep re-selecting."""
        audit = _build_legacy_audit(ctx)
        counts = audit.get("classification_counts", {})
        already_current = bool(audit.get("already_current"))
        evidence: dict[str, Any] = {
            "legacy_page_count": audit.get("legacy_page_count", 0),
            "classification_counts": counts,
            "audit_path": str(ctx.runtime_directory / "intelligence" / LEGACY_AUDIT_FILENAME),
        }
        if already_current:
            evidence["skipped"] = True
        return {
            "status": "SUCCEEDED",
            "detail": (
                f"Legacy audit unchanged since the last run: {audit.get('legacy_page_count', 0)} pages classified ({counts})."
                if already_current else
                f"Legacy audit complete: {audit.get('legacy_page_count', 0)} pages classified ({counts})."
            ),
            "evidence": evidence,
        }

    def _execute_legacy_migration(self, ctx, action: dict[str, Any]) -> dict[str, Any]:
        """Migrate ONE legacy page through the normal research → Scribe → gate →
        staging pipeline, preserving the page's slug and feeding its existing
        content as an additional (clearly separated) source."""
        repo = ctx.working_repository
        runtime = ctx.runtime_directory
        slug = _legacy_slug_from_action(ctx, action) or _legacy_migration_target(ctx)
        if not slug:
            return {"status": "SUCCEEDED", "detail": "No actionable legacy page is available to migrate.", "evidence": {"migratable": False}}

        legacy_path = repo / f"{slug}.html"
        if not legacy_path.is_file():
            return {"status": "BLOCKED", "detail": f"Legacy page {slug!r} not found at root.", "evidence": {"slug": slug}}

        keyword = _legacy_keyword_from_slug(slug)
        evidence, research_packet = _topic_scribe_evidence(ctx, keyword, slug)
        if not research_packet.get("sufficiency", {}).get("passed"):
            notes = "; ".join(research_packet["sufficiency"].get("notes", []))
            _record_legacy_outcome(runtime, slug, status="RESEARCH_INSUFFICIENT", note=notes)
            return {"status": "BLOCKED", "detail": f"Research sufficiency not met for legacy page {slug!r}: {notes}.", "evidence": {"slug": slug, "keyword": keyword, "research_sufficiency": research_packet["sufficiency"]}}

        legacy_title, legacy_body = _legacy_page_text(legacy_path)
        # Preserve the legacy page's own information as an explicit legacy source,
        # clearly separated from independent research evidence.
        evidence.append({
            "evidence_id": f"legacy-{slug}",
            "claim": legacy_body[:1200],
            "source_reference": f"{SITE}/{slug}",
            "source_type": "NEOLIFE_FIRST_PARTY",
        })

        try:
            from agents.scribe.run import run as scribe_run
        except Exception as error:
            return {"status": "CAPABILITY_GAP", "failure_class": "RECOVERABLE_EXECUTOR_FAILURE", "detail": f"Scribe import failed: {type(error).__name__}: {error}", "evidence": {}, "repair": {"repository_kind": "HERMES", "allowed_write_scope": ["agents/scribe/run.py"]}}

        max_attempts = 3
        issues: list[str] = []
        for attempt in range(1, max_attempts + 1):
            brief = _scribe_brief(keyword, slug, evidence)
            brief["title_requirements"] = _title_requirements(keyword, issues)
            try:
                scribe_result = scribe_run(brief, project_id="levnytt")
            except Exception as error:
                issues = [f"scribe_error:{type(error).__name__}"]
                continue
            if scribe_result.get("status") != "READY_FOR_HANDOFF":
                issues = list(scribe_result.get("failure_codes") or []) or ["scribe_blocked"]
                continue
            ok, gate_issues = _content_gate(keyword, scribe_result)
            if ok:
                html = _assemble_page(slug, keyword, scribe_result, research_packet)
                final_ok, final_issues = _final_publication_gate(html)
                if final_ok:
                    destination = repo / "content" / "articles" / f"{slug}.html"
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_text(html, encoding="utf-8")
                    _rebuild_content_inventory(repo)
                    _record_legacy_outcome(runtime, slug, status="STAGED", note="migrated, awaiting deployment")
                    return {
                        "status": "SUCCEEDED",
                        "detail": f"Staged migrated legacy page {slug!r} at content/articles/{slug}.html (awaiting deployment).",
                        "evidence": {"slug": slug, "keyword": keyword, "gate_passed": True, "final_gate_passed": True, "staged_path": str(destination), "lifecycle": "STAGED"},
                    }
                issues = list(final_issues)
                continue
            issues = list(gate_issues)

        _record_legacy_outcome(runtime, slug, status="GATE_FAILED", note="; ".join(issues))
        return {"status": "BLOCKED", "failure_class": "RECOVERABLE_QA_REJECTION", "detail": f"Legacy migration exhausted for {slug!r}: " + "; ".join(issues), "evidence": {"slug": slug, "gate_issues": issues}}

    # ── community (NeoLife, owned page only) ──────────────────────
    def _execute_community_acquisition(self, ctx, action: dict[str, Any]) -> dict[str, Any]:
        """Route one bounded, read-only community observation through the shared
        Community Manager, under LevNytt's own project context.

        This is project-level routing, not a second Community Manager
        implementation: the shared executor (agents/community_manager) performs
        discovery, evaluation, evidence grounding, and destination/attribution,
        all resolved from the active LevNytt project (commander/community.json
        and the levnytt_health_evidence provider). Never sends, posts, joins, or
        replies.

        A truthful no-opportunity observation is a success, not a failure.
        """
        from agents.community_manager.run import observation_assignment
        from agents.community_manager.run import run as run_community_manager

        assignment = observation_assignment(self.project_id)
        result = run_community_manager(assignment)

        status = str(result.get("status") or "FAILED").upper()
        signals = result.get("routed_signals") or []
        qualified = result.get("qualified_engagement_candidate") or {}
        evidence: dict[str, Any] = {
            "external_effect_attempted": False,
            "community_status": status,
            "signals_found": len(signals),
            "groups_assessed": len(result.get("group_assessments") or []),
            "qualified_engagement_candidate": qualified.get("status"),
            "project": result.get("project"),
            "language": assignment["response_policy"]["language"],
        }
        if result.get("failure_codes"):
            evidence["failure_codes"] = result["failure_codes"]

        if status in {"COMPLETE", "PARTIAL"}:
            return {
                "status": "SUCCEEDED",
                "detail": (
                    f"Community observation completed: {len(signals)} signal(s), "
                    f"{len(result.get('group_assessments') or [])} group(s) assessed; "
                    f"engagement candidate: {qualified.get('status')}."
                ),
                "evidence": evidence,
            }

        detail = "; ".join(result.get("limitations") or []) or status
        return {
            "status": "BLOCKED",
            "detail": detail,
            "evidence": evidence,
        }

    def _execute_community_intelligence(self, ctx, action: dict[str, Any]) -> dict[str, Any]:
        """Read-only discovery of relevant Swedish discussions across
        LevNytt's real category breadth (business/MLM/NeoLife,
        supplements/nutrition, personal_care, weight_control, cleaning --
        see _COMMUNITY_DISCOVERY_TOPIC_MAP), reported as structured
        evidence.

        Never posts, replies, joins a group, sends a friend/connection
        request, or messages anyone. Runs a fixed, small query set through
        the same DataForSEO organic-SERP provider already used for content
        research; keeps only results on known discussion-platform domains;
        attaches a recommended_action label (NO_ACTION / OBSERVE /
        POSSIBLE_REPLY) that is a reporting classification for a human/Owner
        decision -- nothing in this codebase consumes it to act
        automatically. Third-party engagement is a separate, unbuilt
        capability; this executor cannot reach it."""
        from app.providers.dataforseo import new_serp_budget, retrieve_organic_results

        levnytt_community = _levnytt_community()
        queries = _COMMUNITY_DISCOVERY_QUERIES
        budget = new_serp_budget(maximum_requests=len(queries))
        discovered: list[dict[str, Any]] = []
        errors: list[str] = []

        for query in queries:
            try:
                result = retrieve_organic_results(
                    query, location=_SE_SERP_LOCATION, language="sv",
                    root=Path("/home/yampa/projects/active/levnytt-site/runtime/production-data"),
                    budget=budget,
                )
            except Exception as exc:
                errors.append(f"{query}: {exc!r}")
                continue
            if result.get("execution_status") != "COMPLETED":
                errors.append(f"{query}: {result.get('execution_status', 'UNKNOWN')} ({result.get('task_status_message', '')})")
                continue
            for item in (result.get("organic_results") or []):
                if not isinstance(item, dict) or not item.get("url"):
                    continue
                platform = _classify_discussion_platform(str(item.get("domain", "")))
                if platform is None:
                    continue
                discovered.append({
                    "query": query,
                    "platform": platform,
                    "url": _canonicalize_discussion_url(str(item.get("url"))),
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "position": item.get("position"),
                    "observed_at": datetime.now(timezone.utc).isoformat(),
                })

        reports = [_classify_discovery_item(item) for item in discovered]
        new_item_count = levnytt_community.record_discovery(ctx.runtime_directory, reports)

        # Stage 2 (bounded third-party READ -> REASON -> DRAFT): reasons
        # about a small, delta-gated set of the persisted store's own
        # POSSIBLE_REPLY discoveries -- never just this cycle's fresh
        # results, so a NEW item from an earlier cycle that was never
        # reasoned about still gets picked up. Produces evidence only; never
        # constructs a community_engagement-shaped assignment or reaches the
        # Facebook interactor. See commander/community.py for the full
        # relevance/grounding/link-discipline logic.
        eligible = levnytt_community.community_reasoning_eligible_candidates(ctx.runtime_directory, limit=5)
        reasoning_results = [
            levnytt_community.reason_about_discovery_candidate(item, ctx.runtime_directory, ctx.working_repository)
            for item in eligible
        ]
        if reasoning_results:
            levnytt_community.record_community_reasoning(ctx.runtime_directory, reasoning_results)
            levnytt_community.record_reasoning_results(ctx.runtime_directory, reasoning_results)

        # Stage 3 (bounded full-thread fetching): adds only FULL THREAD
        # CONTEXT to a small, delta-gated set of Stage 2's own results --
        # never a write. Reuses the existing Firecrawl provider Scout
        # already uses (no second web-fetch stack). Fetchability was
        # verified for real during the Stage 3 audit: Flashback/Familjeliv
        # only -- Reddit's and Facebook's own robots.txt disallow/prohibit
        # automated collection, and both returned a real HTTP 403 via
        # Firecrawl; flexans.se does not resolve. See
        # commander/community.py's _FETCHABLE_PLATFORMS. A failed or
        # unsupported fetch is reported, never raised, so one bad thread can
        # never block this cycle. Community/forum posting rules are NOT
        # inferred here -- that remains a wholly separate, not-yet-built
        # boundary; promotional_rules stays "unknown" where not
        # independently known.
        from app.providers.firecrawl import scrape as firecrawl_scrape

        thread_eligible = levnytt_community.thread_fetch_eligible_candidates(ctx.runtime_directory)
        thread_traces: list[dict[str, Any]] = []
        fetched_urls: list[str] = []
        fetch_records: list[dict[str, Any]] = []
        updated_reasoning_records: list[dict[str, Any]] = []
        evaluated_candidates: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []
        for candidate in thread_eligible:
            url = str(candidate.get("source_url", ""))
            platform = str(candidate.get("source_platform", ""))
            fetch = levnytt_community.fetch_thread_context(url, platform, scrape=firecrawl_scrape)
            fetched_urls.append(url)
            fetch_records.append(fetch)
            context_text = levnytt_community.thread_context_text(fetch)
            discovery_item = levnytt_community.find_discovery_item(ctx.runtime_directory, url) or {
                "url": url, "title": candidate.get("question_context", ""), "snippet": "",
                "platform": platform, "query": candidate.get("source_query", ""),
                "observed_at": candidate.get("observed_at", ""),
                "community_demand_status": candidate.get("community_demand_status"),
            }
            updated = None
            if context_text:
                updated = levnytt_community.reason_about_discovery_candidate(
                    discovery_item, ctx.runtime_directory, ctx.working_repository, thread_context=context_text,
                )
                updated_reasoning_records.append(updated)
            thread_traces.append({
                "source_url": url,
                "fetch_status": fetch.get("fetch_status"),
                "before_outcome": candidate.get("outcome"),
                "after_outcome": updated.get("outcome") if updated else None,
                "outcome_changed": bool(updated and updated.get("outcome") != candidate.get("outcome")),
            })
            evaluated_candidates.append((discovery_item, fetch, updated or candidate))
        if fetched_urls:
            levnytt_community.record_thread_fetch(ctx.runtime_directory, fetched_urls)
        if fetch_records:
            levnytt_community.record_thread_evidence(ctx.runtime_directory, fetch_records)
        if updated_reasoning_records:
            levnytt_community.record_reasoning_results(ctx.runtime_directory, updated_reasoning_records)

        # Stage 4 (Community Rules + Engagement Policy): a separate
        # question from Stages 2-3 -- even if LevNytt can help, would
        # participation be appropriate and permitted? Combines platform
        # policy (a real, cached, first-party rules fetch -- never
        # re-fetched per discussion), social appropriateness, and
        # commercial disclosure into one recommendation, on top of the
        # existing Stage 2/3 outcome. None of these recommendations
        # authorizes execution; write_authorized is always False. See
        # commander/community.py::evaluate_engagement.
        engagement_evaluations = [
            levnytt_community.evaluate_engagement(item, fetch, reasoning, ctx.runtime_directory, scrape=firecrawl_scrape)
            for item, fetch, reasoning in evaluated_candidates
        ]
        if engagement_evaluations:
            levnytt_community.record_engagement_evaluations(ctx.runtime_directory, engagement_evaluations)

        possible_reply = [r for r in reports if r["recommended_action"] == "POSSIBLE_REPLY"]
        # Diminishing-returns detection, mirroring legacy_audit's
        # already_current/skipped pattern: DataForSEO's live SERP results
        # fluctuate run to run even for this fixed query list, so a nonzero
        # result_count alone doesn't mean anything genuinely new was found --
        # only new_item_count (post-dedup, against the persisted store) does.
        # A zero-new-item run is truthfully "no new work", which lets the
        # shared autonomous._is_no_new_work / _supersede_no_new_work_siblings
        # machinery classify it correctly instead of every repeat run looking
        # like fresh production activity forever.
        evidence: dict[str, Any] = {
            "query_count": len(queries),
            "result_count": len(reports),
            "new_item_count": new_item_count,
            "possible_reply_count": len(possible_reply),
            "errors": errors,
            "read_only": True,
            "results": reports,
            "reasoning_results": reasoning_results,
            "thread_fetch_traces": thread_traces,
            "engagement_evaluations": engagement_evaluations,
        }
        if new_item_count == 0 and not reasoning_results and not thread_traces:
            evidence["skipped"] = True
        outcome_counts: dict[str, int] = {}
        for r in reasoning_results:
            outcome_counts[r["outcome"]] = outcome_counts.get(r["outcome"], 0) + 1
        reasoning_summary = (
            f" Reasoned about {len(reasoning_results)} eligible candidate(s): "
            + ", ".join(f"{k}={v}" for k, v in sorted(outcome_counts.items())) + "."
            if reasoning_results else ""
        )
        changed = sum(1 for t in thread_traces if t["outcome_changed"])
        thread_summary = (
            f" Fetched full-thread context for {len(thread_traces)} eligible candidate(s); "
            f"{changed} outcome(s) changed after full context."
            if thread_traces else ""
        )
        recommendation_counts: dict[str, int] = {}
        for evaluation in engagement_evaluations:
            key = evaluation["engagement_recommendation"]
            recommendation_counts[key] = recommendation_counts.get(key, 0) + 1
        engagement_summary = (
            f" Engagement policy evaluated for {len(engagement_evaluations)} candidate(s): "
            + ", ".join(f"{k}={v}" for k, v in sorted(recommendation_counts.items())) + ". No write authorized."
            if engagement_evaluations else ""
        )
        return {
            "status": "SUCCEEDED",
            "detail": (
                f"Community Intelligence discovery: {len(queries)} queries, {len(reports)} "
                f"discussion-shaped result(s) seen, {new_item_count} genuinely new "
                f"(not already known), {len(possible_reply)} flagged POSSIBLE_REPLY for "
                "Owner/human review. Read-only: no post, reply, join, friend request, or "
                "message was made." + reasoning_summary + thread_summary + engagement_summary
            ) if reports else (
                f"Community Intelligence discovery: {len(queries)} queries, no "
                "discussion-shaped results found. Read-only: no post, reply, join, friend "
                "request, or message was made." + reasoning_summary + thread_summary
            ),
            "evidence": evidence,
        }

    def _execute_social_publishing(self, ctx, action: dict[str, Any]) -> dict[str, Any]:
        """Distribute the most recent, not-yet-distributed LevNytt article to
        the LevNytt Facebook Page through the shared, safety-gated Reach
        executor (kill switch, publication gate, duplicate ledger, and
        provider confirmation all apply, scoped to LevNytt's own runtime --
        never OLSP's or Cashbackkollen's identity, ledger, or gate
        reservations).

        Never invents a post: when the distribution evidence shows nothing
        genuinely new to distribute, this is a truthful no-op, not a defect.
        """
        from app.commander.evidence import _levnytt_distribution

        distribution = _levnytt_distribution(ctx.working_repository, ctx.runtime_directory)
        candidates = distribution.get("distribution_candidates") or []
        action_text = str(action.get("summary") or "")
        candidate = next(
            (
                item for item in candidates
                if isinstance(item, dict) and str(item.get("opportunity_id") or "") in action_text
            ),
            None,
        )
        if not candidate:
            if candidates:
                return {
                    "status": "BLOCKED",
                    "detail": "Social publishing requires one exact social-distribution:<slug> opportunity_id; no article was substituted.",
                    "evidence": {"external_effect_attempted": False},
                }
            return {
                "status": "SUCCEEDED",
                "detail": "No published LevNytt article is currently undistributed on Facebook; nothing to post.",
                "evidence": {"skipped": True, "reason": "nothing_new_to_distribute"},
            }

        slug = str(candidate["slug"])
        article_path = ctx.working_repository / "content" / "articles" / f"{slug}.html"
        try:
            article_html = article_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return {
                "status": "CAPABILITY_GAP",
                "failure_class": "RECOVERABLE_EXECUTOR_FAILURE",
                "detail": f"Candidate article {slug!r} disappeared from content/articles/ between evidence and execution.",
                "evidence": {},
            }
        h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", article_html, re.S)
        desc_match = re.search(r'<meta name="description" content="([^"]*)"', article_html)
        title = html_lib.unescape(re.sub(r"<[^>]+>", "", h1_match.group(1))).strip() if h1_match else slug.replace("-", " ")
        excerpt = html_lib.unescape(desc_match.group(1)).strip() if desc_match else ""
        message = _build_levnytt_facebook_message(title, excerpt)
        url = str(candidate["url"])

        assignment = {
            "assignment_id": f"levnytt-reach-{slug}",
            "project": "levnytt",
            "asset_id": f"levnytt-article-{slug}",
            "asset_type": "SOCIAL_POST",
            "channel": "facebook",
            "approved_content": message,
            "destination_url": url,
            "tracking_context": {
                "source": "facebook",
                "campaign": "levnytt_article_distribution",
                "slug": slug,
            },
            "approval_status": "APPROVED",
            "duplicate_ledger": "runtime/social/published.json",
            "verification_condition": "A public Facebook permalink is captured via the Graph API.",
            "retry_policy": {"max_attempts": 0, "rate_limit_action": "STOP", "transient_errors": []},
            "stop_condition": "Stop after one receipt is produced.",
            "handoff_consumers": ["commander"],
            "source_evidence": [f"content/articles/{slug}.html"],
        }

        from agents.reach.run import run as reach_run

        receipt = reach_run(assignment, project_id="levnytt")

        evidence: dict[str, Any] = {
            "opportunity_id": candidate["opportunity_id"],
            "slug": slug,
            "url": url,
            "reach_status": receipt.get("status"),
            "failure_codes": receipt.get("failure_codes"),
            "platform_id": receipt.get("platform_id"),
            "permalink": receipt.get("permalink"),
            "verification_status": receipt.get("verification_status"),
        }

        if receipt.get("status") == "PUBLISHED":
            return {
                "status": "SUCCEEDED",
                "detail": f"Published LevNytt article {slug!r} to Facebook: {receipt.get('permalink')}",
                "evidence": evidence,
            }
        if receipt.get("status") == "DUPLICATE":
            evidence["skipped"] = True
            return {
                "status": "SUCCEEDED",
                "detail": f"Article {slug!r} is already published to Facebook (duplicate-protected; no new post attempted).",
                "evidence": evidence,
            }
        return {
            "status": "BLOCKED",
            "detail": f"Facebook distribution blocked/unverified: {receipt.get('status')} {receipt.get('failure_codes')}",
            "evidence": evidence,
            # Forward Reach's own structural durability classification
            # unchanged (see agents/reach/run.py:_DURABLE_THIS_RUN_FAILURE_CODES)
            # rather than re-deriving it here: a publication window already
            # consumed, the daily cap reached, or the kill switch off cannot
            # change again within this run, so Commander should not spend
            # another decision re-selecting this action. Defaults to True
            # (retry-eligible) when Reach did not classify it, so an unknown
            # future failure mode is never silently treated as durable.
            "retry_eligible_this_run": receipt.get("retry_eligible_this_run", True),
        }

    def _execute_community_engagement(self, ctx, action: dict[str, Any]) -> dict[str, Any]:
        """Route one bounded reply through the shared Community Manager, using a
        qualified candidate from the durable Community Knowledge Store.

        This is project-level routing, not a second Community Manager
        implementation. The specific target is derived deterministically from the
        durable store (the same select_engagement_candidate the OLSP
        operating-loop planner uses), never named by the LLM decision. At most
        one reply; a reply occurs only when a genuinely qualified, current,
        on-subject candidate exists and all shared gates (evidence, safety,
        duplicate-prevention, policy) pass. No candidate is a truthful
        NO_ACTION, not a defect.
        """
        from agents.community_manager.engagement_targeting import select_engagement_candidate
        from agents.community_manager.knowledge import load_store
        from agents.community_manager.run import engagement_assignment
        from agents.community_manager.run import run as run_community_manager

        store = load_store(ctx.runtime_directory / "intelligence" / "community" / "knowledge.json")
        selection = select_engagement_candidate(store)

        if selection.get("status") != "QUALIFIED":
            return {
                "status": "SUCCEEDED",
                "detail": selection.get("reason", "No qualified community engagement opportunity."),
                "evidence": {
                    "external_effect_attempted": False,
                    "qualified": False,
                    "candidates_considered": len(selection.get("candidates_considered") or []),
                },
            }

        candidate = selection["selected_candidate"]
        target = {
            "platform": "facebook",
            "target_scope": "group",
            "group_reference": candidate.get("canonical_group_id") or candidate.get("group_reference"),
            "comment_reference": candidate.get("permalink"),
            "comment_text": candidate.get("candidate_text"),
            "group_rules_observed": True,
        }
        assignment = engagement_assignment(self.project_id, target)
        result = run_community_manager(assignment)

        status = str(result.get("status") or "FAILED").upper()
        receipts = result.get("interaction_receipts") or []
        receipt = receipts[0] if receipts else {}
        replied = receipt.get("action") == "REPLIED"
        evidence: dict[str, Any] = {
            "external_effect_attempted": replied,
            "qualified": True,
            "group_reference": target["group_reference"],
            "comment_reference": target["comment_reference"],
            "community_status": status,
            "replied": replied,
            "project": result.get("project"),
            "language": assignment["response_policy"]["language"],
        }
        if result.get("failure_codes"):
            evidence["failure_codes"] = result["failure_codes"]

        if status == "COMPLETE" and replied:
            return {
                "status": "SUCCEEDED",
                "detail": "Replied once to the qualified LevNytt community conversation.",
                "evidence": evidence,
            }
        return {
            "status": "BLOCKED",
            "detail": "; ".join(result.get("limitations") or []) or status,
            "evidence": evidence,
        }

    # ── verification ──────────────────────────────────────────────
    def verify(self, ctx, action: dict[str, Any], execution: dict[str, Any]) -> bool:
        capability = str(action.get("capability", "")).strip().casefold()
        evidence = execution.get("evidence") or {}
        if capability == "legacy_audit":
            # Verified when the audit genuinely persisted and its artifact's
            # classification_counts match what execution just reported --
            # not merely "the capability returned SUCCEEDED". Previously
            # missing entirely: with no branch here, verify() fell through
            # to `return False` unconditionally, so a legacy_audit
            # commitment could never resolve (see autonomous.py's
            # `elif execution.get("status") == "SUCCEEDED": pass` -- an
            # unverified SUCCEEDED execution leaves its commitment
            # permanently OPEN), which is what let one open commitment
            # consume an entire run's decision budget re-selecting the same
            # already-completed audit.
            audit_path = ctx.runtime_directory / "intelligence" / LEGACY_AUDIT_FILENAME
            if not audit_path.is_file():
                return False
            try:
                persisted = json.loads(audit_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return False
            return isinstance(persisted, dict) and persisted.get("classification_counts") == evidence.get("classification_counts")
        if capability == "legacy_migration":
            # Same missing-branch defect as legacy_audit, fixed the same way:
            # a real artifact check, not a bare True/False guess.
            if evidence.get("migratable") is False:
                return True  # no actionable legacy page -- a genuine, verifiable no-op
            slug = evidence.get("slug")
            if evidence.get("lifecycle") == "STAGED" and slug:
                return (ctx.working_repository / "content" / "articles" / f"{slug}.html").is_file()
            return False  # BLOCKED (research-insufficient / gate-failed) is correctly left unverified
        if capability == "measurement":
            sources = evidence.get("sources") if isinstance(evidence.get("sources"), dict) else {}
            gsc = sources.get("gsc") if isinstance(sources.get("gsc"), dict) else {}
            cta = sources.get("cta_d1") if isinstance(sources.get("cta_d1"), dict) else {}
            verified_sources = 0
            if gsc.get("status") == "available":
                latest = _read_json(ctx.runtime_directory / "intelligence" / "gsc-latest.json")
                if latest.get("site") != GSC_PROPERTY or latest.get("fetched_at") != gsc.get("fetched_at"):
                    return False
                verified_sources += 1
            if cta.get("status") == "available":
                latest = _read_json(ctx.runtime_directory / "intelligence" / CTA_LATEST_FILENAME)
                if latest.get("status") != "available" or latest.get("fetched_at") != cta.get("fetched_at"):
                    return False
                verified_sources += 1
            return verified_sources > 0
        if capability == "seo_intelligence":
            return (ctx.runtime_directory / "intelligence" / "keywords.json").is_file()
        if capability == "technical_repair":
            return _https_serves_200()
        if capability == "content_repair":
            return not _pages_missing_sponsor_disclosure(ctx.working_repository)
        if capability == "content_production":
            if evidence.get("already_live") or evidence.get("already_deployed") or evidence.get("already_staged") or evidence.get("skipped"):
                return True
            slug = evidence.get("slug")
            return bool(slug) and (ctx.working_repository / "content" / "articles" / f"{slug}.html").is_file()
        if capability == "content_improvement":
            source_file = str(evidence.get("source_file") or "")
            source = ctx.working_repository / source_file
            data_path = ctx.working_repository / "content" / "data" / "production-pages.json"
            if not source_file or not source.is_file() or not data_path.is_file():
                return False
            if _file_sha256(source) != evidence.get("staged_content_sha256"):
                return False
            if _file_sha256(data_path) != evidence.get("production_data_sha256"):
                return False
            html = source.read_text(encoding="utf-8", errors="ignore")
            final_ok, _issues = _final_publication_gate(html)
            return bool(
                evidence.get("gate_passed")
                and evidence.get("final_gate_passed")
                and final_ok
                and evidence.get("sponsor_id_preserved") == SPONSOR_ID
                and f'<link rel="canonical" href="{evidence.get("public_url_preserved")}"' in html
                and "levnytt-rebuild.js?v=" in html
            )
        if capability == "deployment":
            if evidence.get("deployable") is False:
                return True
            slug = evidence.get("slug")
            return bool(slug) and _verify_live(slug, wait_seconds=0)
        if capability == "community_acquisition":
            # Read-only observation through the shared Community Manager is
            # verified when its own status is a completed/partial observation;
            # a no-comment result is still a valid observation.
            return bool(evidence.get("community_status") in {"COMPLETE", "PARTIAL"})
        if capability == "community_engagement":
            if evidence.get("qualified") is False:
                return True
            return bool(evidence.get("replied"))
        if capability == "community_intelligence":
            # Read-only discovery is verified when the run completed and
            # produced no writes (errors alone don't fail it -- a query
            # returning zero discussion-shaped results, or a provider error
            # on one of several queries, is still a valid, honest pass).
            return execution.get("status") == "SUCCEEDED" and bool(evidence.get("read_only"))
        if capability == "social_publishing":
            if evidence.get("skipped"):
                return True
            return bool(evidence.get("permalink")) and evidence.get("reach_status") == "PUBLISHED"
        return False

    # ── measurement ───────────────────────────────────────────────
    def measure(self, ctx, action: dict[str, Any], execution: dict[str, Any]) -> dict[str, Any]:
        capability = str(action.get("capability", "")).strip().casefold()
        if capability in {"social_publishing", "community_acquisition", "community_engagement"}:
            next_check = (date.today() + timedelta(days=1)).isoformat()
        else:
            next_check = (date.today() + timedelta(days=7)).isoformat()
        return {
            "summary": f"{action.get('summary')} — {execution.get('status')}. {execution.get('detail')}",
            "data": {"capability": capability, "evidence": execution.get("evidence", {})},
            "next_check": next_check,
        }


def build_procedure():
    return LevNyttProcedure()


def _build_levnytt_facebook_message(title: str, excerpt: str) -> str:
    """Compose an informational Facebook post from the article's own already
    fact-gated H1/meta-description. No new health claim, savings figure, or
    income promise is invented here -- the article itself already passed
    _final_publication_gate before it could ship: a rendered disclosure
    marker, at least one independent (non-NeoLife) citation link, the
    financial/scam-promise marker check, and a sentence-scoped check for
    bare affirmative treatment/cure/prevention claims and sensational
    language (not a full semantic guarantee -- see that gate's own
    docstring for its known limitation on compound sentences). This only
    formats what the article already says, plus LevNytt's standing NeoLife
    disclosure -- Facebook distribution is itself a point of commercial
    context, so the same disclosure principle applied to every on-site page
    (Sponsor-ID 41-830928, "Oberoende distributör") applies here too, in the
    exact phrasing already established on /om-oss."""
    body = excerpt.strip()
    text = f"{title.strip()}\n\n{body}" if body else title.strip()
    if len(text) > 350:
        text = text[:347].rstrip() + "…"
    return f"{text}\n\nLäs mer på LevNytt 👉\n\nOberoende NeoLife-distributör · Sponsor-ID {SPONSOR_ID}"


# ── content lifecycle ─────────────────────────────────────────────
def _content_lifecycle(repo: Path, slug: str) -> str:
    """ABSENT -> STAGED -> DEPLOYED -> LIVE. A local untracked file is NOT live."""
    if _verify_live(slug, wait_seconds=0):
        return "LIVE"
    tracked = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "--error-unmatch",
         f"content/articles/{slug}.html", f"{slug}.html"],
        capture_output=True, text=True, check=False,
    )
    if tracked.returncode == 0:
        return "DEPLOYED"
    if (repo / "content" / "articles" / f"{slug}.html").is_file() or (repo / f"{slug}.html").is_file():
        return "STAGED"
    return "ABSENT"


def _verify_live(slug: str, wait_seconds: int = 0) -> bool:
    import time

    deadline = time.monotonic() + wait_seconds
    while True:
        try:
            request = urllib.request.Request(f"{SITE}/{slug}", method="GET", headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=15) as response:
                if response.status == 200:
                    return True
        except urllib.error.HTTPError:
            return False
        except Exception:
            pass
        if time.monotonic() >= deadline:
            return False
        time.sleep(5)


def _verify_live_ok(slug: str) -> bool:
    return _verify_live(slug, wait_seconds=0)


def _git_head(repo: Path) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else ""


def _push_main_with_rebase(repo: Path) -> tuple[bool, str]:
    push = subprocess.run(
        ["git", "-C", str(repo), "push", "origin", "main"],
        capture_output=True, text=True, check=False,
    )
    if push.returncode == 0:
        return True, ""
    subprocess.run(
        ["git", "-C", str(repo), "fetch", "origin"],
        capture_output=True, text=True, check=False,
    )
    rebase = subprocess.run(
        ["git", "-C", str(repo), "pull", "--rebase", "origin", "main"],
        capture_output=True, text=True, check=False,
    )
    if rebase.returncode != 0:
        subprocess.run(
            ["git", "-C", str(repo), "rebase", "--abort"],
            capture_output=True, text=True, check=False,
        )
        return False, f"Deployment rebase failed (recoverable): {(rebase.stderr or '')[-300:]}"
    push = subprocess.run(
        ["git", "-C", str(repo), "push", "origin", "main"],
        capture_output=True, text=True, check=False,
    )
    if push.returncode != 0:
        return False, f"git push failed after rebase (recoverable): {(push.stderr or '')[-300:]}"
    return True, ""


def _resume_pending_deployment(
    repo: Path,
    pending_path: Path,
    pending: dict[str, Any],
) -> dict[str, Any]:
    """Resume the existing commit/push/live-verification deployment lifecycle."""
    slug = str(pending.get("slug") or "").strip()
    commit = str(pending.get("commit") or "").strip()
    if not slug or not commit:
        return {
            "status": "BLOCKED",
            "detail": "Pending deployment continuation state is malformed.",
            "evidence": {"pending_recovery": True, "external_effect_attempted": False},
            "retry_eligible_this_run": False,
        }
    if not pending.get("pushed"):
        if _git_head(repo) != commit:
            return {
                "status": "BLOCKED",
                "detail": "Pending deployment commit is not repository HEAD; refusing to push unrelated commits.",
                "evidence": {"slug": slug, "pending_recovery": True, "external_effect_attempted": False},
                "retry_eligible_this_run": False,
            }
        push_ok, push_detail = _push_main_with_rebase(repo)
        if not push_ok:
            return {
                "status": "BLOCKED",
                "detail": push_detail,
                "evidence": {"slug": slug, "pending_recovery": True, "external_effect_attempted": True},
            }
        pending["pushed"] = True
        pending["commit"] = _git_head(repo)
        _atomic_json_write(pending_path, pending)
    if not _verify_live(slug, wait_seconds=120):
        return {
            "status": "BLOCKED",
            "detail": f"Deployment continuation still cannot verify {slug!r} live.",
            "evidence": {"slug": slug, "deployed": True, "live_verified": False, "pending_recovery": True, "external_effect_attempted": True},
        }
    pending_path.unlink(missing_ok=True)
    return {
        "status": "SUCCEEDED",
        "detail": f"Resumed deployment and verified {slug!r} live at {SITE}/{slug}.",
        "evidence": {
            "slug": slug,
            "live_url": f"{SITE}/{slug}",
            "live_verified": True,
            "deployed": True,
            "recovered_pending_deployment": True,
            "external_effect_attempted": True,
        },
    }


def _deployment_safety(
    repo: Path, slug: str, allowed_paths: set[str] | None = None,
) -> dict[str, Any]:
    """Permit only the exact provenance-bound files and routing metadata."""
    reasons: list[str] = []
    allowed = set(allowed_paths or ()) | {"_redirects", "sitemap.xml"}
    status = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=all"],
        capture_output=True, text=True, check=False,
    ).stdout
    for line in status.splitlines():
        code = line[:2]
        path = line[3:].strip()
        if not path:
            continue
        if code == "??" and path in allowed:
            continue
        if path in allowed:
            continue
        reasons.append(f"unexpected tracked change {code!r} {path}")
    if reasons:
        return {"ok": False, "reasons": reasons}
    return {"ok": True, "reasons": []}


def _sitemap_has_slug(repo: Path, slug: str) -> bool:
    try:
        return f"{SITE}/{slug}" in (repo / "sitemap.xml").read_text(encoding="utf-8")
    except OSError:
        return False


def _add_redirect(repo: Path, slug: str) -> bool:
    redirects = repo / "_redirects"
    entry = f"/{slug} /content/articles/{slug} 200"
    try:
        text = redirects.read_text(encoding="utf-8")
    except OSError:
        return False
    if f"/{slug} " in text:
        return True
    lines = text.splitlines()
    catch_all = next((i for i, line in enumerate(lines) if line.strip().startswith("/* ")), len(lines))
    lines.insert(catch_all, entry)
    redirects.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def _add_sitemap_entry(repo: Path, slug: str) -> bool:
    sitemap = repo / "sitemap.xml"
    entry = f"  <url><loc>{SITE}/{slug}</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>"
    try:
        text = sitemap.read_text(encoding="utf-8")
    except OSError:
        return False
    if f"{SITE}/{slug}" in text:
        return True
    if "</urlset>" not in text:
        return False
    text = text.replace("</urlset>", entry + "\n</urlset>")
    sitemap.write_text(text, encoding="utf-8")
    return True


def _provenance_verified_slugs(repo: Path) -> set[str]:
    """Slugs with a CONFIRMED production/migration/improvement commitment.

    This is historical provenance only. Deployment eligibility is stricter:
    ``_first_staged_work`` additionally binds existing-page improvements to
    the exact source and production-data hashes in the confirmation receipt.

    A file existing under content/articles/*.html is not by itself proof
    Commander produced it for real -- a manual run of this pipeline (e.g. to
    test a gate fix against a genuine keyword) writes an identical-looking
    untracked HTML file with no ledger entry at all. Only a CONFIRMED
    commitment -- written solely after a real Commander decision actually
    executed and verified this exact slug -- proves it is legitimate staged
    production work rather than a manual/verification artifact. Deployment
    must never commit and push one of the latter."""
    path = repo / "runtime" / "commander" / "commitments.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    rows = data.get("commitments") if isinstance(data, dict) else None
    verified: set[str] = set()
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        if row.get("capability_id") not in (
            "content_production", "content_improvement", "legacy_migration",
        ):
            continue
        if row.get("status") != "CONFIRMED":
            continue
        reason = row.get("resolution_reason")
        if not isinstance(reason, str):
            continue
        try:
            parsed = ast.literal_eval(reason)
        except (ValueError, SyntaxError):
            continue
        if isinstance(parsed, dict) and parsed.get("gate_passed") and parsed.get("slug"):
            verified.add(str(parsed["slug"]))
    return verified


def _confirmed_staged_work(repo: Path) -> list[dict[str, Any]]:
    ledger = _read_json(repo / "runtime" / "commander" / "commitments.json")
    rows = ledger.get("commitments") if isinstance(ledger.get("commitments"), list) else []
    records: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict) or row.get("status") != "CONFIRMED":
            continue
        capability = str(row.get("capability_id") or "")
        if capability not in {"content_production", "content_improvement", "legacy_migration"}:
            continue
        reason = row.get("resolution_reason")
        if not isinstance(reason, str):
            continue
        try:
            parsed = ast.literal_eval(reason)
        except (ValueError, SyntaxError):
            continue
        if not isinstance(parsed, dict) or not parsed.get("gate_passed") or not parsed.get("slug"):
            continue
        slug = str(parsed["slug"])
        source_file = str(parsed.get("source_file") or f"content/articles/{slug}.html")
        record = {
            "capability_id": capability,
            "slug": slug,
            "source_file": source_file,
            "files": [source_file],
        }
        if capability == "content_improvement":
            content_hash = str(parsed.get("staged_content_sha256") or "")
            data_hash = str(parsed.get("production_data_sha256") or "")
            if not content_hash or not data_hash:
                continue
            record.update({
                "staged_content_sha256": content_hash,
                "production_data_sha256": data_hash,
                "files": [source_file, "content/data/production-pages.json"],
            })
        records.append(record)
    return records


def _git_status_paths(repo: Path) -> dict[str, str]:
    completed = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=all"],
        capture_output=True, text=True, check=False,
    )
    if completed.returncode != 0:
        return {}
    return {
        line[3:].strip(): line[:2]
        for line in completed.stdout.splitlines()
        if len(line) > 3 and line[3:].strip()
    }


def _first_staged_work(repo: Path) -> dict[str, Any] | None:
    status = _git_status_paths(repo)
    eligible: list[dict[str, Any]] = []
    for record in _confirmed_staged_work(repo):
        source = repo / record["source_file"]
        if not source.is_file() or record["source_file"] not in status:
            continue
        if record["capability_id"] == "content_improvement":
            data = repo / "content" / "data" / "production-pages.json"
            if "content/data/production-pages.json" not in status:
                continue
            if _file_sha256(source) != record["staged_content_sha256"]:
                continue
            if _file_sha256(data) != record["production_data_sha256"]:
                continue
        elif status[record["source_file"]] != "??":
            continue
        eligible.append(record)
    return sorted(eligible, key=lambda item: item["slug"])[0] if eligible else None


def _first_staged_slug(repo: Path) -> str | None:
    work = _first_staged_work(repo)
    return str(work["slug"]) if work else None


def _staged_article_path(repo: Path, slug: str) -> Path | None:
    work = _first_staged_work(repo)
    if work is None or work["slug"] != slug:
        return None
    return repo / work["source_file"]


def _slug_from_action(ctx, action: dict[str, Any]) -> str | None:
    keyword = _keyword_from_action(ctx, action)
    return _slugify(keyword) if keyword else None


# ── content inventory / coverage ──────────────────────────────────
def _rebuild_content_inventory(repo: Path) -> Path:
    paths: set[str] = set()
    for p in repo.glob("*.html"):
        if p.name == "404.html":
            continue
        paths.add(str(p.relative_to(repo)))
    for p in repo.glob("content/**/*.html"):
        paths.add(str(p.relative_to(repo)))
    for p in repo.glob("*/index.html"):
        if p.parts[0] == "no":
            continue
        paths.add(str(p.relative_to(repo)))
    inventory = {"version": 1, "content_paths": sorted(paths)}
    dest = repo / "config" / "content-inventory.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return dest


def _coverage_gap_count(ctx) -> int:
    coverage = _read_json(ctx.runtime_directory / "intelligence" / "content-coverage.json")
    records = coverage.get("coverage") if isinstance(coverage.get("coverage"), list) else []
    return sum(1 for r in records if isinstance(r, dict) and r.get("coverage") == "NONE")


def _content_improvement_target(action: dict[str, Any]) -> dict[str, Any] | None:
    """Resolve exactly one current opportunity through the Hermes contract."""
    from app.commander.evidence import build_factual_evidence
    from app.commander.procedure_contract import select_exact_opportunity

    snapshot = build_factual_evidence(project_id="levnytt")
    levnytt = (snapshot.get("sources") or {}).get("levnytt") or {}
    bundle = levnytt.get("content_improvement_opportunities") or {}
    candidates = bundle.get("opportunities") if isinstance(bundle, dict) else []
    selected = select_exact_opportunity(action, candidates or [])
    if selected is None:
        return None
    required = {
        "opportunity_id", "slug", "canonical_url", "public_path", "source_file",
    }
    if not required.issubset(selected) or any(not str(selected[key]).strip() for key in required):
        raise ValueError("Selected content-improvement opportunity lacks canonical identity fields")
    return selected


def _load_site_renderer():
    path = Path(__file__).resolve().parents[1] / "scripts" / "site_renderer.py"
    spec = importlib.util.spec_from_file_location("levnytt_content_improvement_renderer", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _existing_page_context(source: Path, opportunity: dict[str, Any]) -> dict[str, Any]:
    """Bound the existing page context supplied to Scribe."""
    current = source.read_text(encoding="utf-8", errors="replace")
    visible = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", current, flags=re.I | re.S)
    visible = html_lib.unescape(re.sub(r"<[^>]+>", " ", visible))
    visible = re.sub(r"\s+", " ", visible).strip()
    return {
        "canonical_url": opportunity["canonical_url"],
        "source_file": opportunity["source_file"],
        "current_title": opportunity.get("title"),
        "current_content_excerpt": visible[:6000],
        "instruction": (
            "Revise this exact existing page using the supplied research. Preserve its "
            "canonical identity and do not invent claims or create a different article."
        ),
    }


def _render_improved_production_page(
    repo: Path,
    opportunity: dict[str, Any],
    scribe_result: dict[str, Any],
    research_packet: dict[str, Any],
) -> tuple[str, str]:
    """Render one replacement with the canonical Phase 1 renderer and data."""
    data_path = repo / "content" / "data" / "production-pages.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    pages = data.get("pages")
    if not isinstance(pages, list):
        raise ValueError("production-pages.json has no pages list")
    index = next(
        (
            index for index, page in enumerate(pages)
            if isinstance(page, dict) and page.get("path") == opportunity["public_path"]
        ),
        None,
    )
    if index is None:
        raise ValueError(f"Canonical production page is missing for {opportunity['public_path']}")
    previous = pages[index]
    if previous.get("source_file") != opportunity["source_file"]:
        raise ValueError("Current production source no longer matches the selected opportunity")
    if previous.get("url") != opportunity["canonical_url"]:
        raise ValueError("Current canonical URL no longer matches the selected opportunity")

    draft = _assemble_page(
        str(opportunity["slug"]),
        str(opportunity.get("research_topic") or opportunity.get("title") or opportunity["slug"]),
        scribe_result,
        research_packet,
    )
    renderer = _load_site_renderer()
    updated = renderer.extract_document(
        previous["url"], draft, previous["source_file"], repo,
    )
    for key in ("url", "path", "family", "language", "source_file", "date_published"):
        updated[key] = previous.get(key, updated.get(key))
    updated["date_modified"] = date.today().isoformat()
    pages[index] = updated
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    rendered = renderer.render_page(updated, repo)
    return rendered, json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def _atomic_text_write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False,
    ) as handle:
        handle.write(value)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ── page assembly (reuses the canonical LevNytt article template) ─
def _load_md_to_article():
    path = Path(__file__).resolve().parents[1] / "scripts" / "md-to-article.py"
    spec = importlib.util.spec_from_file_location("md_to_article", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _assemble_page(slug: str, keyword: str, scribe_result: dict[str, Any], research_packet: dict[str, Any] | None = None) -> str:
    module = _load_md_to_article()
    title = str(scribe_result.get("title_or_subject") or "").strip()
    sections = scribe_result.get("sections_or_messages") or []
    bodies = [str(s.get("body", "")).strip() for s in sections if isinstance(s, dict) and str(s.get("body", "")).strip()]
    first_body = bodies[0] if bodies else title
    description = first_body[:155]
    takeaways = bodies[:3]
    faq = _build_faq(sections, keyword)
    data = {
        "title": title,
        "description": description,
        "slug": slug,
        "category": "Kosttillskott & hälsa",
        "eyebrow": "LevNytt · Konsumentguide",
        "author": dict(AUTHOR),
        "updated": date.today().isoformat(),
        "reading_time": max(3, sum(len(b) for b in bodies) // 900),
        "punchline": first_body,
        "takeaways": takeaways,
        "method_note": (
            "Fakta baseras på tillgängligt källmaterial och evidens; LevNytt gör inga "
            "hälso- eller inkomstlöften. Informationen är avsedd för utbildningssyfte."
        ),
        "tierbox": _DEFAULT_TIERBOX,
        "cta": {
            "headline": "Handla NeoLife till konsumentpris",
            "body": "LevNytt är en oberoende NeoLife-distributörswebbplats (Sponsor-ID 41-830928). Besök den officiella shopen om du vill veta mer om produkterna.",
            "url": SHOP_URL,
            "link_text": "Till NeoLife-shopen →",
        },
        "disclosure": (
            f"Denna artikel handlar om \"{keyword}\". LevNytt fokuserar på konsumentutbildning "
            "och gör inga ogrundade hälsopåståenden eller inkomstlöften."
        ),
        "faq": faq,
    }
    body_html = _body_html(sections)
    if research_packet:
        sources_html = _sources_html(research_packet)
        if sources_html:
            body_html = body_html + "\n" + sources_html
    return module.build_html(data, body_html)


def _sources_html(packet: dict[str, Any]) -> str:
    """Build a Källorna section that separates independent science/authority
    sources from NeoLife first-party sources, so NeoLife marketing is never
    presented as independent scientific validation."""
    claims = packet.get("claims", []) if isinstance(packet, dict) else []
    science: list[dict[str, Any]] = []
    neo: list[dict[str, Any]] = []
    seen: set[str] = set()
    for c in claims:
        url = str(c.get("source_url", "")).strip()
        if not url or url in seen:
            continue
        if c.get("source_type") in {"AUTHORITY", "GENERAL_SCIENCE"}:
            science.append(c)
        elif c.get("source_type") == "NEOLIFE_FIRST_PARTY" and url != "https://levnytt.se/om-oss":
            neo.append(c)
        seen.add(url)
    parts: list[str] = []
    if science:
        parts.append("<h2>Källor</h2>")
        parts.append("<p><strong>Oberoende vetenskapliga och myndighetskällor:</strong></p><ul>")
        for c in science[:6]:
            label = c.get("source_title") or c.get("source_reference") or c["source_url"]
            parts.append(f'<li><a target="_blank" rel="noopener noreferrer" href="{_escape_html(c["source_url"])}">{_escape_html(label)}</a></li>')
        parts.append("</ul>")
    if neo:
        if not science:
            parts.append("<h2>Källor</h2>")
        parts.append("<p><strong>NeoLife (förstahandsinformation):</strong></p><ul>")
        for c in neo[:3]:
            label = c.get("source_title") or c.get("source_reference") or c["source_url"]
            parts.append(f'<li><a target="_blank" rel="noopener noreferrer" href="{_escape_html(c["source_url"])}">{_escape_html(label)}</a></li>')
        parts.append("</ul>")
    return "\n".join(parts)


def _body_html(sections: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for unit in sections:
        if not isinstance(unit, dict):
            continue
        heading = str(unit.get("heading_or_subject") or "").strip()
        body = str(unit.get("body") or "").strip()
        if heading:
            parts.append(f"<h2>{_escape_html(heading)}</h2>")
        if body:
            for paragraph in body.split("\n\n"):
                paragraph = paragraph.strip()
                if paragraph:
                    parts.append(f"<p>{_escape_html(paragraph)}</p>")
    return "\n".join(parts)


def _build_faq(sections: list[dict[str, Any]], keyword: str) -> list[dict[str, str]]:
    faq: list[dict[str, str]] = []
    for unit in sections:
        if not isinstance(unit, dict):
            continue
        heading = str(unit.get("heading_or_subject") or "").strip()
        body = str(unit.get("body") or "").strip()
        if heading and body and not heading.endswith("?"):
            faq.append({"q": _question_form(heading), "a": body[:300]})
        if len(faq) >= 6:
            break
    if len(faq) < 3:
        generic = [
            {"q": "Är informationen på LevNytt oberoende?",
             "a": "LevNytt är en oberoende NeoLife-distributörswebbplats. Vi skiljer tydligt mellan oberoende forskning och NeoLifes egna produktpåståenden."},
            {"q": "Hur väljer jag ett kosttillskott?",
             "a": "Fokusera på evidens, kvalitet och tydlig information om vad produkten faktiskt innehåller — inte på marknadsföringslöften."},
        ]
        for g in generic:
            if len(faq) < 3:
                faq.append(g)
    return faq[:8]


def _question_form(heading: str) -> str:
    heading = heading.rstrip(":.!?")
    if heading.lower().startswith(("vad är", "hur", "varför", "när", "vilka", "vilken", "är")):
        return heading + "?"
    return f"{heading} — vad innebär det?"


# ── scribe brief / gate / title requirements ──────────────────────
def _scribe_brief(keyword: str, slug: str, evidence: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "assignment_id": f"levnytt-scribe-{slug}",
        "project": "levnytt",
        "brief_id": f"levnytt-{slug}",
        "audience": "Svenska konsumenter som vill förstå kosttillskott, hälsa och direktförsäljning innan de bestämmer sig",
        "user_problem": keyword,
        "content_type": "ARTICLE",
        "format": "production-ready evidence-bound draft",
        "source_evidence": evidence,
        "knowledge_gaps": [],
        "project_context": _levnytt_editorial_context(),
        # Claude Code has no production authentication on this host. LevNytt
        # selects the already-configured shared OpenAI provider explicitly;
        # OLSP's default Claude + olsp-article contract remains unchanged.
        "writer_provider": "openai",
        "writing_instruction_source": _LEVNYTT_WRITING_INSTRUCTION_SOURCE,
        "link_requirements": {
            "cta": "presenterar fakta om NeoLife och kosttillskott utan hype, inkomstlöften eller påhittade siffror; länkar vidare till NeoLife shop med Sponsor-ID 41-830928 endast som ett frivilligt nästa steg"
        },
        "language": "Swedish",
        "handoff_consumer": "editorial_builder",
        "stop_condition": "Return one bounded content result and stop.",
    }


# Shared with the final publication gate below -- one authoritative
# definition, never duplicated. These are the specific financial/scam
# phrasing patterns the editorial constitution's "no income examples, no
# guaranteed results" rule has always meant in practice.
_UNSUBSTANTIATED_PROMISE_MARKERS = ("garanterad vinst", "säkert att", "gratis pengar", "riskfritt", "tjäna 50")


def _content_gate(keyword: str, scribe_result: dict[str, Any]) -> tuple[bool, list[str]]:
    """Draft-level editorial-quality gate: runs on Scribe's raw output,
    before assembly. Catches defects that are only visible in the draft
    (title shape, section count, near-duplicate/filler prose, length) and
    are meaningfully retry-able by asking Scribe again. Does NOT verify what
    actually ships -- see _final_publication_gate for the artifact-level
    gate that runs after _assemble_page."""
    issues: list[str] = []
    title = str(scribe_result.get("title_or_subject") or "").strip()
    if not title:
        issues.append("missing_title")
    elif len(title) > 60:
        issues.append(f"title_too_long({len(title)})")
    sections = scribe_result.get("sections_or_messages")
    if not isinstance(sections, list) or len(sections) < 2:
        issues.append("too_few_sections")
    claims = scribe_result.get("claims")
    if not isinstance(claims, list) or not claims:
        issues.append("no_grounded_claims")
    if _normalize(keyword) and _normalize(keyword) not in _normalize(title):
        issues.append("keyword_absent_from_title")
    body = _body_html(sections).casefold()
    for marker in _UNSUBSTANTIATED_PROMISE_MARKERS:
        if marker in body:
            issues.append(f"unsubstantiated_promise({marker})")
            break
    # Editorial quality (deterministic): near-duplicate paragraphs, generic
    # filler, and substantive length are rejected — these catch the "thin
    # repeated filler" failure mode rather than passing it as content.
    paragraphs = [p for p in re.split(r"</p>\s*<p>|<p>|</p>", body) if len(p.strip()) > 20]
    normalized_paragraphs = [_normalize(p) for p in paragraphs]
    if len(normalized_paragraphs) != len(set(normalized_paragraphs)):
        issues.append("repeated_paragraphs")
    filler = "på levnytt.se publicerar vi evidensbaserade"
    if body.strip().startswith(filler) or filler in body[:400]:
        issues.append("generic_filler_intro")
    words = len(body.split())
    if words < 180:
        issues.append(f"insufficient_body_length({words})")
    return (not issues), issues


_SOURCES_SECTION_PATTERN = re.compile(
    r"<h2\b[^>]*>\s*Källor\s*</h2>(.*?)(?=<h2\b|\Z)",
    re.I | re.S,
)


def _has_rendered_sources(html: str) -> bool:
    """True only when the page's Källor section exists AND contains at
    least one real citation link to a domain outside LevNytt/NeoLife's own
    (levnytt.se, neolifeshop.com, neolife.com) -- i.e. genuine independent
    provenance, not merely the heading, and not merely a self-referential or
    NeoLife-marketing link standing in for evidence. This is the exact
    property _sources_html is supposed to guarantee; this function verifies
    it survived into the artifact that will actually ship, rather than
    trusting that the pre-assembly research packet had it."""
    match = _SOURCES_SECTION_PATTERN.search(html)
    if not match:
        return False
    for url in re.findall(r'href="(https?://[^"]+)"', match.group(1)):
        domain = urlsplit(url).netloc.casefold()
        if not any(domain == d or domain.endswith("." + d) for d in NEOLIFE_DOMAINS):
            return True
    return False


# Prohibited when used as a bare, unhedged, unattributed affirmative claim.
# These are exactly the finite present-tense forms the editorial rules
# (originally documented only in the neolife-product-pillar Claude Code
# skill, now enforced here) single out: "bidrar till"/"stödjer" are fine,
# "behandlar"/"botar"/"förebygger" stated as plain fact are not.
_PROHIBITED_HEALTH_VERBS = ("behandlar", "botar", "förebygger", "förhindrar", "kurerar")
_SENSATIONAL_MARKERS = ("mirakel", "revolutionerande", "hemlighet", "genombrott", "bevisat att")
# A bare negation word anywhere in the same sentence as a prohibited verb or
# sensational marker means the sentence is negating the claim rather than
# asserting it -- e.g. "Det finns inget vetenskapligt stöd för att X
# förebygger Y" must pass despite containing "förebygger". Word-boundary
# matched (\b) so "inte" never matches inside an unrelated word like
# "vinter"; deliberately NOT a fixed multi-word phrase like "inget stöd
# för", which breaks the moment a real sentence inserts another word (e.g.
# "vetenskapligt") between "inget" and "stöd för".
_HEALTH_CLAIM_NEGATION_PATTERN = re.compile(r"\b(inte|inget|ingen|inga|saknas)\b", re.I)
# Multi-word hedge phrases: lower collision risk as substrings since they're
# several words long, so no word-boundary regex needed.
_HEALTH_CLAIM_HEDGE_PHRASES = (
    "kan bidra till", "kan bidra", "tyder på att", "misstänks",
    "möjligen", "eventuellt", "i vissa fall", "påstås", "påstår",
)


def _strip_html_tags(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html)


def _split_sentences(plain_text: str) -> list[str]:
    text = re.sub(r"\s+", " ", plain_text).strip()
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def _health_claim_violations(html: str) -> list[str]:
    """Sentence-scoped, negation/hedge/quote-aware check for bare affirmative
    treatment/cure/prevention claims and sensational certainty language.

    Deliberately NOT a whole-document substring ban -- that would fail a
    sentence explaining research does NOT show something prevents a
    condition, purely for containing "förebygger". Scoping to the sentence
    and checking it for a negation/hedge marker (or a quotation, i.e.
    attributed discussion rather than a site claim) before flagging is the
    smallest mechanism that distinguishes a prohibited affirmative claim
    from an appropriately hedged one. It is not a full semantic checker: a
    compound sentence that hedges one clause while smuggling a bare claim
    into another joined by "och" can still slip through. Known, accepted
    limitation -- see the commissioning report for this gate."""
    plain = _strip_html_tags(html)
    violations: list[str] = []
    for sentence in _split_sentences(plain):
        lowered = sentence.casefold()
        if '"' in sentence or "”" in sentence or "»" in sentence:
            continue  # quoted/attributed, not a direct site claim
        if _HEALTH_CLAIM_NEGATION_PATTERN.search(sentence) or any(p in lowered for p in _HEALTH_CLAIM_HEDGE_PHRASES):
            continue
        for verb in _PROHIBITED_HEALTH_VERBS:
            if verb in lowered:
                violations.append(f"affirmative_health_claim({verb}): {sentence[:120]!r}")
        for marker in _SENSATIONAL_MARKERS:
            if marker in lowered:
                violations.append(f"sensational_language({marker}): {sentence[:120]!r}")
    return violations


def _final_publication_gate(html: str) -> tuple[bool, list[str]]:
    """The one authoritative gate over the artifact that will actually ship.

    Runs on the fully assembled HTML (after _assemble_page), never the
    pre-assembly draft, so it can catch defects that only exist once
    assembly has happened -- a missing disclosure marker, a Källor heading
    with no real citation inside it -- which _content_gate structurally
    cannot see. Both content_production and legacy_migration call this
    immediately before writing the article to disk; neither path may bypass
    it. Verifies: disclosure structure, rendered independent source
    presentation, the existing financial/scam-promise markers, and
    sentence-scoped health-claim/sensational-language safety."""
    issues: list[str] = []
    if not _has_applied_disclosure_marker(html):
        issues.append("missing_disclosure_marker")
    if not _has_rendered_sources(html):
        issues.append("missing_rendered_sources")
    body = html.casefold()
    for marker in _UNSUBSTANTIATED_PROMISE_MARKERS:
        if marker in body:
            issues.append(f"unsubstantiated_promise({marker})")
            break
    issues.extend(_health_claim_violations(html))
    return (not issues), issues


def _title_requirements(keyword: str, issues: list[str]) -> str:
    lines = ["The title must be 60 characters or fewer.", f'The title must contain the keyword "{keyword}".']
    if issues:
        lines.append("Rejection reasons to correct from the previous attempt: " + "; ".join(issues) + ".")
    return " ".join(lines)


# ── general helpers ───────────────────────────────────────────────
def _slugify(value: str) -> str:
    slug = value.casefold().strip().replace("å", "a").replace("ä", "a").replace("ö", "o")
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")[:80]


def _normalize(value: str) -> str:
    return "".join(ch for ch in value.casefold().replace("å", "a").replace("ä", "a").replace("ö", "o") if ch.isalnum())


def _escape_html(value: str) -> str:
    import html
    return html.escape(value, quote=False)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _bounded_provider_diagnostic(*parts: str | None) -> str:
    """Return a short provider diagnostic with common secret shapes redacted."""
    value = "\n".join(str(part or "") for part in parts).strip()
    value = re.sub(
        r"(?i)\b(authorization|api[_-]?key|token|password)\b\s*[:=]\s*\S+",
        r"\1=[REDACTED]",
        value,
    )
    return value[-500:]


def _atomic_json_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent, text=True,
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def _persist_cta_attempt(ctx, result: dict[str, Any]) -> None:
    _atomic_json_write(
        ctx.runtime_directory / "intelligence" / CTA_ATTEMPT_FILENAME,
        result,
    )


def _collect_cta_events(ctx) -> dict[str, Any]:
    attempted_at = datetime.now(timezone.utc).isoformat()
    result: dict[str, Any] = {
        "attempted_at": attempted_at,
        "source": f"Cloudflare D1 {D1_DATABASE}",
        "status": "unavailable",
        "provider": "wrangler",
    }
    node = shutil.which("node")
    npx = shutil.which("npx")
    result["runtime"] = {"node": node or "not-found", "npx": npx or "not-found"}
    if not node or not npx:
        result["diagnostic"] = "Supported Node/npm runtime was not found on the scheduled PATH."
        _persist_cta_attempt(ctx, result)
        return result

    version = subprocess.run(
        [node, "--version"], capture_output=True, text=True, check=False, timeout=10,
    )
    node_version = (version.stdout or version.stderr or "").strip()
    result["runtime"]["node_version"] = node_version
    match = re.match(r"v?(\d+)", node_version)
    if version.returncode != 0 or not match or int(match.group(1)) < 22:
        result["diagnostic"] = _bounded_provider_diagnostic(
            f"Wrangler requires Node 22 or newer; scheduled runtime reported {node_version or 'unknown'}."
        )
        _persist_cta_attempt(ctx, result)
        return result

    aggregate_sql = (
        "SELECT COUNT(*) AS total_events, "
        "COALESCE(SUM(CASE WHEN cta_id = 'levnytt-neolife-shop' THEN 1 ELSE 0 END), 0) AS shop_clicks, "
        "COALESCE(SUM(CASE WHEN cta_id = 'levnytt-neolife-registration' THEN 1 ELSE 0 END), 0) AS registration_clicks "
        "FROM cta_click_events"
    )
    recent_sql = (
        "SELECT cta_id, page_path, destination, observed_at FROM cta_click_events "
        "ORDER BY observed_at DESC LIMIT 10"
    )
    command_prefix = [npx, "--no-install", "wrangler", "d1", "execute", D1_DATABASE, "--remote", "--command"]
    try:
        completed = subprocess.run(
            [*command_prefix, aggregate_sql, "--json"],
            cwd=str(ctx.working_repository), capture_output=True, text=True, check=False, timeout=90,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        result["diagnostic"] = _bounded_provider_diagnostic(f"{type(exc).__name__}: {exc}")
        _persist_cta_attempt(ctx, result)
        return result
    if completed.returncode != 0:
        result["returncode"] = completed.returncode
        result["diagnostic"] = _bounded_provider_diagnostic(completed.stderr, completed.stdout)
        _persist_cta_attempt(ctx, result)
        return result
    try:
        raw = json.loads(completed.stdout or "[]")
    except json.JSONDecodeError as exc:
        result["diagnostic"] = _bounded_provider_diagnostic(f"Wrangler output parse failed: {exc}")
        _persist_cta_attempt(ctx, result)
        return result
    aggregate_rows = raw[0].get("results") if isinstance(raw, list) and raw and isinstance(raw[0], dict) else None
    if not isinstance(aggregate_rows, list) or len(aggregate_rows) != 1 or not isinstance(aggregate_rows[0], dict):
        result["diagnostic"] = "Wrangler returned no aggregate results row."
        _persist_cta_attempt(ctx, result)
        return result
    aggregate = aggregate_rows[0]
    try:
        counts = {
            "total_events": int(aggregate["total_events"]),
            "shop_clicks": int(aggregate["shop_clicks"]),
            "registration_clicks": int(aggregate["registration_clicks"]),
        }
    except (KeyError, TypeError, ValueError):
        result["diagnostic"] = "Wrangler returned malformed CTA aggregate counts."
        _persist_cta_attempt(ctx, result)
        return result

    recent_events: list[dict[str, Any]] = []
    recent_status = "available"
    try:
        recent = subprocess.run(
            [*command_prefix, recent_sql, "--json"],
            cwd=str(ctx.working_repository), capture_output=True, text=True, check=False, timeout=90,
        )
        recent_raw = json.loads(recent.stdout or "[]") if recent.returncode == 0 else []
        recent_rows = (
            recent_raw[0].get("results")
            if isinstance(recent_raw, list) and recent_raw and isinstance(recent_raw[0], dict)
            else None
        )
        if not isinstance(recent_rows, list):
            recent_status = "unavailable"
        else:
            recent_events = [
                {k: row.get(k) for k in ("cta_id", "page_path", "destination", "observed_at") if row.get(k) is not None}
                for row in recent_rows[:10]
                if isinstance(row, dict)
            ]
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        recent_status = "unavailable"
    result.update({
        "status": "available",
        "fetched_at": attempted_at,
        **counts,
        "recent_events": recent_events,
        "recent_events_status": recent_status,
    })
    _atomic_json_write(ctx.runtime_directory / "intelligence" / CTA_LATEST_FILENAME, result)
    _persist_cta_attempt(ctx, result)
    return result


def _find_research_packet(ctx, keyword: str) -> dict[str, Any] | None:
    """Locate the cached topic-research packet for a keyword, tolerant of
    spacing/diacritic differences between the keyword candidate and the topic
    that was actually researched (e.g. 'cellmembran' vs 'cell membran')."""
    intel = ctx.runtime_directory / "intelligence"
    direct = intel / f"research-{_slugify(keyword)}.json"
    if direct.is_file():
        try:
            data = json.loads(direct.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (OSError, json.JSONDecodeError):
            pass
    norm = _normalize(keyword)
    if norm:
        for path in intel.glob("research-*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(data, dict) and _normalize(str(data.get("topic", ""))) == norm:
                return data
    return None


def _research_insufficient_recent(ctx, keyword: str) -> bool:
    """True when a fresh (within TTL) research packet already found this topic
    research-insufficient. An insufficient result is itself a durable finding:
    it must not be re-selected until the research cache expires and the topic
    becomes eligible for a fresh attempt."""
    cached = _find_research_packet(ctx, keyword)
    if cached is None:
        return False
    sufficiency = cached.get("sufficiency")
    if not isinstance(sufficiency, dict) or sufficiency.get("passed") is not False:
        return False
    generated = str(cached.get("generated_at", "")).replace("Z", "+00:00")
    try:
        age = datetime.now(timezone.utc) - datetime.fromisoformat(generated)
    except ValueError:
        return True
    return age.days < RESEARCH_CACHE_TTL_DAYS


def _top_keyword(ctx) -> str | None:
    data = _read_json(ctx.runtime_directory / "intelligence" / "keywords.json")
    rows = data.get("keywords") if isinstance(data.get("keywords"), list) else []
    ranked = [r for r in rows if isinstance(r, dict) and str(r.get("keyword", "")).strip()]
    if not ranked:
        return None
    eligible = [r for r in ranked if not _research_insufficient_recent(ctx, str(r["keyword"]).strip())]
    if not eligible:
        return None
    eligible.sort(key=lambda r: (isinstance(r.get("priority_score"), (int, float)), r.get("priority_score") or 0, isinstance(r.get("monthly_search_volume"), (int, float)), r.get("monthly_search_volume") or 0), reverse=True)
    return str(eligible[0]["keyword"]).strip()


def _keyword_from_action(ctx, action: dict[str, Any]) -> str | None:
    action_text = str(action.get("summary") or action.get("action") or "").casefold()
    data = _read_json(ctx.runtime_directory / "intelligence" / "keywords.json")
    rows = data.get("keywords") if isinstance(data.get("keywords"), list) else []
    candidates = [r for r in rows if isinstance(r, dict) and str(r.get("keyword", "")).strip()]
    matches = [r for r in candidates if str(r["keyword"]).casefold() in action_text]
    if matches:
        matches.sort(key=lambda r: (-len(str(r["keyword"])), -(r.get("priority_score") or 0)))
        for match in matches:
            keyword = str(match["keyword"]).strip()
            if not _research_insufficient_recent(ctx, keyword):
                return keyword
    return _top_keyword(ctx)


OFF_STRATEGY_TERMS = ("casino", "betting", "spel", "lån", "loan", "kredit", "försäkring", "insurance", "crypto", "krypto", "aktier", "forex", "trading")


def _off_strategy(keyword: str) -> str | None:
    folded = keyword.casefold()
    for marker in OFF_STRATEGY_TERMS:
        if re.search(rf"\b{re.escape(marker)}\b", folded):
            return marker
    return None


def _en_keyword(keyword: str) -> str:
    """Best-effort Swedish→English topic translation for the general-science
    SERP layer. Falls back to the raw keyword when no mapping exists."""
    folded = keyword.casefold().strip()
    if folded in _SE_EN_TERMS:
        return _SE_EN_TERMS[folded]
    return " ".join(_SE_EN_TERMS.get(word, word) for word in folded.split())


def _source_type(domain: str) -> str | None:
    d = (domain or "").casefold().strip()
    if any(d == a or d.endswith("." + a) for a in AUTHORITY_DOMAINS):
        return "AUTHORITY"
    if any(d == s or d.endswith("." + s) for s in SCIENCE_DOMAINS):
        return "GENERAL_SCIENCE"
    if any(d == n or d.endswith("." + n) for n in NEOLIFE_DOMAINS):
        return "NEOLIFE_FIRST_PARTY"
    return None


def _serp_organic(keyword: str, location: int, language: str) -> list[dict[str, Any]]:
    try:
        from app.providers.dataforseo import retrieve_organic_results

        result = retrieve_organic_results(
            keyword, location=location, language=language,
            root=Path("/home/yampa/projects/active/levnytt-site/runtime/production-data"),
        )
    except Exception:
        return []
    if result.get("execution_status") != "COMPLETED":
        return []
    return [r for r in (result.get("organic_results") or []) if isinstance(r, dict) and r.get("url")]


_NOISE_PATTERNS = (
    r"^skip", r"expand all", r"table of contents", r"this fact sheet",
    r"for health professionals", r"share this", r"last updated", r"^print",
    r"^home", r"^news", r"^contact", r"^about", r"^privacy", r"cookie",
    r"ai generated", r"how useful is this", r"^review article",
    r"access to", r"sign in", r"log in", r"^download", r"^abstract",
    r"full text", r"official websites use \.gov", r"secure \.gov websites",
    r"share sensitive information", r"a lock \( lock", r"https? means you",
    r"before sharing sensitive", r"inclusion in an nlm database",
    r"does not imply endorsement", r"learn more: pmc", r"pmc disclaimer",
    r"pmc copyright", r"received 20", r"revised 20", r"accepted 20",
    r"collection date", r"© 20", r"this article is an open access",
    r"distributed under the terms", r"licensee", r"creative commons",
    r"^keywords", r"^citation", r"^references", r"^conflict of interest",
    r"^funding", r"^ethics approval", r"^data availability",
)


def _is_noise(sentence: str) -> bool:
    lowered = sentence.casefold()
    return any(re.search(pattern, lowered, re.IGNORECASE) for pattern in _NOISE_PATTERNS)


def _extract_sentences(markdown: str, limit: int) -> list[str]:
    """Deterministic verbatim sentence extraction — no LLM summarization."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", markdown or "")
    text = re.sub(r"#{1,6}\s*", "", text)
    text = re.sub(r"[*_]{1,3}", "", text)
    text = re.sub(r"\s+", " ", text)
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text)]
    out: list[str] = []
    for sentence in sentences:
        if not (50 <= len(sentence) <= 340):
            continue
        if _is_noise(sentence):
            continue
        out.append(sentence)
        if len(out) >= limit:
            break
    return out


_FETCH_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)


def _html_to_text(raw: str) -> str:
    """Strip script/style/tags and unescape entities into plain text."""
    text = re.sub(r"<(script|style|noscript)[^>]*>[\s\S]*?</\1>", " ", raw, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_lib.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _html_title(raw: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", raw, flags=re.IGNORECASE | re.DOTALL)
    return html_lib.unescape(match.group(1)).strip() if match else ""


def _fetch_source(url: str) -> tuple[str, str] | None:
    try:
        from app.providers.firecrawl import scrape

        data = scrape(url, formats=("markdown",), only_main_content=True)
        md = (data.get("markdown") or "").strip()
        title = (data.get("metadata") or {}).get("title") or ""
        if md:
            return md, title
    except Exception:
        pass
    # Fallback: direct bounded GET when the scraping provider is rate-limited
    # or out of credits. One URL, one read-only request, plain-text extraction
    # via the same deterministic sentence pipeline. The research-sufficiency
    # gate still applies verbatim source-type filtering afterwards.
    try:
        request = urllib.request.Request(url, headers={"User-Agent": _FETCH_USER_AGENT})
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read().decode("utf-8", errors="ignore")
        text = _html_to_text(raw)
        if not text:
            return None
        return text, _html_title(raw)
    except Exception:
        return None


def _detect_intent(ctx, keyword: str) -> str:
    data = _read_json(ctx.runtime_directory / "intelligence" / "search-intent.json")
    for item in data.get("intents", []) if isinstance(data.get("intents"), list) else []:
        if isinstance(item, dict) and _normalize(str(item.get("keyword", ""))) == _normalize(keyword):
            return str(item.get("detected_intent", "Unknown"))
    return "Unknown"


def _gsc_claim(ctx, keyword: str) -> dict[str, Any] | None:
    gsc = _read_json(ctx.runtime_directory / "intelligence" / "gsc-latest.json")
    query = gsc.get("query") if isinstance(gsc.get("query"), dict) else {}
    rows = query.get("all_queries", []) if isinstance(query.get("all_queries"), list) else []
    for row in rows:
        if isinstance(row, dict) and _normalize(str(row.get("query", ""))) == _normalize(keyword):
            return {
                "evidence_id": f"gsc-{_slugify(keyword)}",
                "claim": f"Google Search Console visar {row.get('impressions', 0)} visningar och genomsnittsposition {str(row.get('position', 0)).replace('.', ',')} för sökfrågan \"{keyword}\".",
                "source_type": "SEO",
                "source_title": "Google Search Console",
                "source_reference": "runtime/intelligence/gsc-latest.json",
                "source_url": "",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "confidence": "HIGH",
            }
    return None


# ── legacy content estate (audit + classification) ────────────────
# Legacy pages are the root .html files still served from the pre-rebuild
# pillar.css template generation. They are a normal evidence-driven production
# opportunity, not automatically bad: Commander classifies each page once,
# persists the audit, and only migrates a page when evidence justifies it.
LEGACY_STYLE_MARKER = "pillar.css"
LEGACY_AUDIT_FILENAME = "legacy-audit.json"
LEGACY_AUDIT_TTL_DAYS = 30
_LEGACY_NON_CONTENT_PAGES = frozenset({
    "404.html", "artiklar.html", "index.html", "integritetspolicy.html",
    "den-fundersamma-mannen.html",
})

# Numeric/unit and scientific-claim markers: a legacy page carrying these
# without a matching research packet is an EVIDENCE_RISK under the current
# evidence standard.
_LEGACY_EVIDENCE_MARKERS = re.compile(
    r"\b\d+(?:[.,]\d+)?\s*(?:mg|mcg|µg|ug|g|kg|IE|NE|%|procent)\b"
    r"|\b(studie|studier|studien|forskning|klinisk[a-z]*|dosering|rekommenderad[a-z]*|dagligt intag)\b",
    re.IGNORECASE,
)


def _legacy_keyword_from_slug(slug: str) -> str:
    """Derive a research keyword from a legacy page slug (first meaningful token)."""
    tokens = [t for t in re.split(r"[^a-z0-9]+", slug.casefold()) if t]
    if not tokens:
        return slug
    # Drop generic suffix tokens ("komplett", "guide", "symptom", "tillskott").
    meaningful = [t for t in tokens if t not in {"komplett", "guide", "vad", "ar", "for", "och", "i"}]
    if meaningful:
        return " ".join(meaningful[:2])
    return tokens[0]


def _discover_legacy_pages(repo: Path) -> list[Path]:
    """Root .html pages still using the legacy pillar.css template (excluding
    non-content infrastructure pages)."""
    pages: list[Path] = []
    for path in sorted(repo.glob("*.html")):
        if path.name in _LEGACY_NON_CONTENT_PAGES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if LEGACY_STYLE_MARKER in text:
            pages.append(path)
    return pages


def _legacy_page_text(path: Path) -> tuple[str, str]:
    """Return (title, plain-body) of a legacy page for deterministic inspection."""
    try:
        raw = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return "", ""
    title_match = re.search(r"<title>(.*?)</title>", raw, re.IGNORECASE | re.DOTALL)
    title = re.sub(r"<[^>]+>", " ", title_match.group(1)).strip() if title_match else path.stem
    body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.DOTALL | re.IGNORECASE)
    body = re.sub(r"<[^>]+>", " ", body)
    body = re.sub(r"\s+", " ", body).strip()
    return title, body


def _legacy_gsc_stats(runtime: Path, slug: str) -> dict[str, Any]:
    """Return GSC impressions/clicks/position for a legacy page, if present."""
    try:
        gsc = json.loads((runtime / "intelligence" / "gsc-latest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    page = gsc.get("page") if isinstance(gsc, dict) else {}
    rows = page.get("all_pages") if isinstance(page, dict) and isinstance(page.get("all_pages"), list) else []
    for row in rows:
        if not isinstance(row, dict):
            continue
        url = str(row.get("page", ""))
        if f"/{slug}" in url or f"/content/articles/{slug}" in url:
            return {
                "impressions": row.get("impressions", 0),
                "clicks": row.get("clicks", 0),
                "position": row.get("position"),
            }
    return {}


def _legacy_overlaps(repo: Path, slug: str, keyword: str) -> list[str]:
    """Other production pages whose slug/title shares the keyword's major term."""
    norm = _normalize(keyword)
    if not norm:
        return []
    overlaps: list[str] = []
    for path in sorted(repo.glob("*.html")):
        if path.stem == slug:
            continue
        if norm in _normalize(path.stem) or norm in _normalize(path.name):
            overlaps.append(path.stem)
    return overlaps[:5]


def _classify_legacy_page(repo: Path, runtime: Path, path: Path) -> dict[str, Any]:
    """Deterministically classify one legacy page. Classification priority:
    EVIDENCE_RISK > LEGACY_CONTENT_WEAK > SEO_OPPORTUNITY >
    CONSOLIDATION_CANDIDATE > LEGACY_STYLE_ONLY > CURRENT_OK."""
    slug = path.stem
    keyword = _legacy_keyword_from_slug(slug)
    title, body = _legacy_page_text(path)
    word_count = len(re.findall(r"\w+", body))
    has_evidence_claims = bool(_LEGACY_EVIDENCE_MARKERS.search(body))
    research_slug = _slugify(keyword)
    has_research_packet = (runtime / "intelligence" / f"research-{research_slug}.json").is_file()
    gsc = _legacy_gsc_stats(runtime, slug)
    overlaps = _legacy_overlaps(repo, slug, keyword)
    already_migrated = (repo / "content" / "articles" / f"{slug}.html").is_file()

    if already_migrated:
        classification = "CONSOLIDATION_CANDIDATE"
        reason = "a new-style article already exists at content/articles; the legacy root page is superseded"
    elif has_evidence_claims and not has_research_packet:
        classification = "EVIDENCE_RISK"
        reason = f"numeric/scientific/health claims present without a research packet for '{keyword}'"
    elif word_count < 250:
        classification = "LEGACY_CONTENT_WEAK"
        reason = f"thin content ({word_count} words)"
    elif gsc.get("impressions", 0) >= 10 and (int(gsc.get("clicks", 0)) < 1 or float(gsc.get("position") or 99) > 15):
        classification = "SEO_OPPORTUNITY"
        reason = f"{gsc.get('impressions')} impressions, {gsc.get('clicks')} clicks, position {gsc.get('position')}"
    elif overlaps:
        classification = "CONSOLIDATION_CANDIDATE"
        reason = f"overlaps existing pages: {overlaps}"
    elif has_research_packet:
        classification = "CURRENT_OK"
        reason = "sufficiently supported by an existing research packet"
    else:
        classification = "LEGACY_STYLE_ONLY"
        reason = "substantive content on the older template; migration optional"

    return {
        "slug": slug,
        "keyword": keyword,
        "title": title[:180],
        "classification": classification,
        "reason": reason,
        "word_count": word_count,
        "has_evidence_claims": has_evidence_claims,
        "has_research_packet": has_research_packet,
        "already_migrated": already_migrated,
        "gsc": gsc,
        "overlaps": overlaps,
    }


def _build_legacy_audit(ctx) -> dict[str, Any]:
    """Discover and classify the legacy estate; persist the audit artifact.

    Preserves the prior artifact's "outcomes" list (per-slug migration
    history written by _record_legacy_outcome) across rewrites -- a fresh
    audit used to silently replace the whole file, discarding every
    recently-processed-page suppression record _legacy_migration_target
    depends on to avoid reselecting the same page every run. Also carries
    forward "already_current" -- see the no-new-work note below.
    """
    repo = ctx.working_repository
    runtime = ctx.runtime_directory
    previous = _load_legacy_audit(runtime)
    previous_counts = previous.get("classification_counts") if isinstance(previous, dict) else None
    previous_pages = previous.get("pages") if isinstance(previous, dict) else None

    pages = _discover_legacy_pages(repo)
    results = [_classify_legacy_page(repo, runtime, path) for path in pages]
    counts: dict[str, int] = {}
    for r in results:
        counts[r["classification"]] = counts.get(r["classification"], 0) + 1
    audit = {
        "schema": "levnytt-legacy-audit-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "legacy_page_count": len(results),
        "classification_counts": counts,
        "pages": results,
        # True when this run reclassified the exact same estate the last
        # persisted audit already found -- i.e. genuinely no new work, not
        # merely "the audit ran again." _execute_legacy_audit surfaces this
        # as evidence["skipped"] so the shared no-new-work/supersession
        # machinery (autonomous.py's _is_no_new_work /
        # _supersede_no_new_work_siblings) recognizes a repeat audit for
        # what it is instead of treating every run as fresh production work.
        "already_current": bool(previous_counts is not None and previous_counts == counts and previous_pages == results),
    }
    if isinstance(previous.get("outcomes"), list):
        audit["outcomes"] = previous["outcomes"]
    path = runtime / "intelligence" / LEGACY_AUDIT_FILENAME
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except OSError:
        pass
    return audit


def _load_legacy_audit(runtime: Path) -> dict[str, Any]:
    try:
        data = json.loads((runtime / "intelligence" / LEGACY_AUDIT_FILENAME).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _actionable_legacy_classes() -> frozenset[str]:
    return frozenset({"EVIDENCE_RISK", "LEGACY_CONTENT_WEAK", "SEO_OPPORTUNITY"})


def _record_legacy_outcome(runtime: Path, slug: str, *, status: str, note: str) -> None:
    """Append one legacy action outcome to the audit (loop prevention).

    A page recorded as CURRENT_OK, RESEARCH_INSUFFICIENT, STAGED, or recently
    audited is suppressed from reselection within the TTL window, so Commander
    does not repeatedly select the same page."""
    path = runtime / "intelligence" / LEGACY_AUDIT_FILENAME
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    outcomes = data.get("outcomes") if isinstance(data, dict) and isinstance(data.get("outcomes"), list) else []
    outcomes = [o for o in outcomes if isinstance(o, dict) and o.get("slug") != slug]
    outcomes.append({"slug": slug, "status": status, "note": note, "at": datetime.now(timezone.utc).isoformat()})
    data["outcomes"] = outcomes
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except OSError:
        pass


def _legacy_migration_target(ctx) -> str | None:
    """Select the highest-value actionable legacy page for one migration."""
    repo = ctx.working_repository
    runtime = ctx.runtime_directory
    audit = _load_legacy_audit(runtime)
    outcomes = audit.get("outcomes") if isinstance(audit.get("outcomes"), list) else []
    recent = {o.get("slug") for o in outcomes if isinstance(o, dict) and o.get("slug")}
    pages = audit.get("pages") if isinstance(audit.get("pages"), list) else []
    actionable = [p for p in pages if isinstance(p, dict)
                  and p.get("classification") in _actionable_legacy_classes()
                  and p.get("slug") not in recent]
    # EVIDENCE_RISK first, then by GSC impressions (objective impact).
    order = {"EVIDENCE_RISK": 0, "LEGACY_CONTENT_WEAK": 1, "SEO_OPPORTUNITY": 2}
    actionable.sort(key=lambda p: (order.get(p.get("classification"), 9), -(p.get("gsc", {}).get("impressions", 0) or 0)))
    return actionable[0].get("slug") if actionable else None


def _legacy_slug_from_action(ctx, action: dict[str, Any]) -> str | None:
    """Resolve a legacy page slug from the action's evidence or its text."""
    evidence = action.get("evidence") if isinstance(action.get("evidence"), dict) else {}
    if evidence.get("slug"):
        return str(evidence["slug"]).strip()
    action_text = str(action.get("summary") or action.get("action") or "").casefold()
    for path in _discover_legacy_pages(ctx.working_repository):
        if path.stem.casefold() in action_text:
            return path.stem
    return None


def _research_sufficiency(claims: list[dict[str, Any]]) -> dict[str, Any]:
    sources = {c.get("source_url") for c in claims if c.get("source_url")}
    substantive = [c for c in claims if c.get("source_type") in {"AUTHORITY", "GENERAL_SCIENCE"}]
    substantive_sources = {c.get("source_url") for c in substantive if c.get("source_url")}
    notes: list[str] = []
    if len(substantive_sources) < 2:
        notes.append("fewer than 2 distinct authoritative (AUTHORITY/GENERAL_SCIENCE) sources")
    if len(substantive) < 4:
        notes.append("fewer than 4 substantive authoritative claims")
    if len(claims) < 4:
        notes.append("insufficient claim count")
    return {
        "passed": not notes,
        "source_count": len(sources),
        "claim_count": len(claims),
        "authoritative_claim_count": len(substantive),
        "authoritative_source_count": len(substantive_sources),
        "notes": notes,
    }


def _build_topic_research(ctx, keyword: str, slug: str) -> dict[str, Any]:
    """Topic-specific research: DataForSEO SERP (sv + en) → authoritative URL
    discovery → Firecrawl scrape → deterministic verbatim claim extraction →
    evidence packet. Never synthesizes facts; every claim carries provenance."""
    now = datetime.now(timezone.utc).isoformat()
    claims: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    en_query = _en_keyword(keyword)

    candidates: list[dict[str, Any]] = []
    for location, language in ((_SE_SERP_LOCATION, "sv"), (_US_SERP_LOCATION, "en")):
        query = keyword if location == _SE_SERP_LOCATION else en_query
        for item in _serp_organic(query, location, language):
            if item.get("url") not in {c["url"] for c in candidates}:
                candidates.append(item)

    def _rank(item: dict[str, Any]) -> tuple[int, int]:
        st = _source_type(item.get("domain", ""))
        order = {"AUTHORITY": 0, "GENERAL_SCIENCE": 1, "NEOLIFE_FIRST_PARTY": 2}.get(st, 3)
        return (order, int(item.get("position") or 99))

    candidates.sort(key=_rank)

    for item in candidates:
        url = item.get("url", "")
        domain = item.get("domain", "")
        source_type = _source_type(domain)
        if not source_type or url in seen_urls or "levnytt.se" in domain:
            continue
        if len({c["source_url"] for c in claims if c.get("source_url")}) >= 6:
            break
        fetched = _fetch_source(url)
        if not fetched:
            continue
        markdown, title = fetched
        sentences = _extract_sentences(markdown, 6)
        if not sentences:
            continue
        seen_urls.add(url)
        for sentence in sentences:
            claims.append({
                "evidence_id": f"{slug}-src{len(claims) + 1}",
                "claim": sentence,
                "source_type": source_type,
                "source_title": title or domain,
                "source_reference": domain,
                "source_url": url,
                "retrieved_at": now,
                "confidence": "HIGH" if source_type in {"AUTHORITY", "GENERAL_SCIENCE"} else "MEDIUM",
            })
        if len(claims) >= 20:
            break

    gsc_claim = _gsc_claim(ctx, keyword)
    if gsc_claim:
        claims.append(gsc_claim)

    claims.append({
        "evidence_id": f"{slug}-neolife",
        "claim": f"LevNytt är en oberoende NeoLife-distributörswebbplats med Sponsor-ID {SPONSOR_ID}; NeoLife är ett direktförsäljningsföretag grundat 1958.",
        "source_type": "NEOLIFE_FIRST_PARTY",
        "source_title": "LevNytt — om oss",
        "source_reference": "levnytt.se",
        "source_url": "https://levnytt.se/om-oss",
        "retrieved_at": now,
        "confidence": "HIGH",
    })

    return {
        "schema": "levnytt-topic-research-v1",
        "topic": keyword,
        "slug": slug,
        "search_intent": _detect_intent(ctx, keyword),
        "reader_question": keyword,
        "swedish_query": keyword,
        "english_query": en_query,
        "generated_at": now,
        "claims": claims,
        "knowledge_gaps": [],
        "contradictions": [],
        "sufficiency": _research_sufficiency(claims),
    }


def _topic_research(ctx, keyword: str, slug: str) -> dict[str, Any]:
    """Cache-aware topic research: reuse a fresh (≤30-day) packet, including an
    insufficient one (an insufficient result is itself a durable finding — it
    must not be re-researched every decision)."""
    cache_path = ctx.runtime_directory / "intelligence" / f"research-{slug}.json"
    if cache_path.is_file():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            generated = str(cached.get("generated_at", "")).replace("Z", "+00:00")
            age = datetime.now(timezone.utc) - datetime.fromisoformat(generated)
            if age.days < RESEARCH_CACHE_TTL_DAYS:
                return cached
        except (OSError, json.JSONDecodeError, ValueError):
            pass
    packet = _build_topic_research(ctx, keyword, slug)
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass
    return packet


def _topic_scribe_evidence(ctx, keyword: str, slug: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    packet = _topic_research(ctx, keyword, slug)
    evidence = [
        {
            "evidence_id": c["evidence_id"],
            "claim": c["claim"],
            "source_reference": c.get("source_url") or c.get("source_reference", ""),
            "source_type": c.get("source_type", ""),
        }
        for c in packet.get("claims", [])
    ]
    return evidence, packet


def _https_serves_200() -> bool:
    class _NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        request = urllib.request.Request(SITE, method="HEAD", headers={"User-Agent": USER_AGENT})
        response = opener.open(request, timeout=15)
        return response.status == 200
    except urllib.error.HTTPError as error:
        return error.code == 200
    except Exception:
        return False


_DISCLOSURE_CLASS_PATTERN = re.compile(r'class="[^"]*\b(?:ln-nav-disclosure|ia-disclosure)\b[^"]*"')


def _has_applied_disclosure_marker(text: str) -> bool:
    """True only when a disclosure marker class is actually applied to an
    element (a real class="..." attribute), never merely present anywhere in
    the file. A naive substring check on "ia-disclosure" was a false-positive
    risk: content/articles/*.html pages embed a shared <style> block defining
    ".ia-disclosure{...}" on every page regardless of whether any element in
    that specific page actually uses the class -- discovered on
    kosttillskott-aldre-65.html during commissioning, where the substring
    happened to be present (in CSS) alongside a genuinely correct, separately
    applied disclosure paragraph elsewhere in the same file. The two facts
    are unrelated; only the applied-class check proves the second one."""
    return bool(_DISCLOSURE_CLASS_PATTERN.search(text))


def _pages_missing_sponsor_disclosure(repo: Path) -> list[str]:
    """Pages with a NeoLife shop/registration link but no point-of-content
    disclosure marker actually applied. Presence of the Sponsor-ID string
    alone (e.g. buried in an author bio) is not sufficient -- it must appear
    via one of the two established disclosure mechanisms: the site-wide
    "ln-nav-disclosure" link next to the header's commercial CTA (rendered by
    every page through scripts/rebuild-production.py's shared_header(), or
    hand-applied to index.html/artiklar.html, which sit outside that
    pipeline), or an in-article "ia-disclosure" paragraph (the pattern used
    by both older root pages like direktforsaljning-fakta.html/om-oss.html
    and every content_production/legacy_migration article under
    content/articles/ -- e.g. kosttillskott-aldre-65.html).

    Covers both live production content paths: root-level *.html (the
    scripts/rebuild-production.py-owned estate) and content/articles/**/*.html
    at any depth (the content_production/legacy_migration-owned estate,
    including the rare nested per-locale layout -- e.g.
    content/articles/nattblindhet/nattblindhet.html -- which _redirects can
    still route live). The previous version of this check only scanned
    root-level files, so no article produced through content_production or
    legacy_migration was ever actually verified by this gate."""
    missing: list[str] = []
    candidates = sorted(repo.glob("*.html")) + sorted((repo / "content" / "articles").rglob("*.html"))
    for path in candidates:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "neolifeshop.com" not in text:
            continue
        if not _has_applied_disclosure_marker(text):
            missing.append(str(path.relative_to(repo)))
        if len(missing) >= 50:
            break
    return missing


def _seed_keyword_candidates(ctx) -> None:
    """Re-seed the SEO Scout candidates from three real evidence sources,
    each tagged with its own evidence_type so Commander/Scout can reason
    about GSC_DEMAND (first-party measured search impressions) separately
    from COMMUNITY_DEMAND (real discussion, never keyword-volume evidence --
    a forum question is never converted into fabricated search volume).

    Community-derived candidates are seeded FIRST and reserved dedicated
    slots, ahead of the GSC ranking fill: without this, a GSC result set
    with >=20 high-impression queries would silently crowd every community
    signal out of the bounded 20-slot list every single cycle, defeating the
    entire point of the Community Intelligence -> Scout join. Bounded to 20
    overall; off-strategy queries excluded throughout."""
    candidates_path = ctx.runtime_directory / "intelligence" / "keyword-candidates.json"
    levnytt_community = _levnytt_community()

    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()

    def _add(keyword: str, **fields: Any) -> None:
        # Universally enforced (not just at the community-derived call
        # sites): app.providers.dataforseo.normalize_keywords rejects the
        # ENTIRE keyword-volume batch if any single keyword exceeds its
        # limits (confirmed live -- a real Flashback thread title broke a
        # real Scout cycle this way), so one bad candidate from any future
        # source must never be able to poison every other candidate's lookup.
        keyword = levnytt_community.dataforseo_safe_keyword(keyword.strip())
        key = keyword.casefold()
        if not keyword or key in seen or _off_strategy(keyword):
            return
        seen.add(key)
        candidates.append({"keyword": keyword, **fields})

    # Real third-party forum discussions -- only sufficiently-supported
    # discoveries are promoted (see community.community_derived_candidates);
    # never every SERP result. This is the Community Intelligence -> Scout
    # join and the phase's central objective.
    community_candidates = levnytt_community.community_derived_candidates(ctx.runtime_directory, limit=5)
    for item in community_candidates:
        _add(
            item["keyword"],
            evidence_type=item["evidence_type"],
            community_demand_status=item["community_demand_status"],
            source_platform=item["source_platform"],
            source_url=item["source_url"],
            source_query=item["source_query"],
            retrieved_at=item["retrieved_at"],
            confidence=item["confidence"],
            question_context=item["question_context"],
        )
    if community_candidates:
        levnytt_community.record_scout_promotions(ctx.runtime_directory, community_candidates)

    # Category floor: the three NeoLife product lines each get Scout seeds,
    # reserved before the demand-driven GSC fill, so a supplement-heavy
    # GSC/forum result set cannot permanently starve Personlig vård and
    # Rengöring of search research and content. Each line seeds its full
    # anchor set, not only the broad category name: the broad name ("hudvård")
    # resolves to e-commerce SERPs with no authoritative source, while the
    # specific topics ("håravfall", "torr hud", "diskmedel", ...) resolve to
    # medical/authority sources the research-sufficiency gate can use. _add
    # deduplicates, so a line already represented by GSC/community is left
    # untouched.
    for anchor in (
        "kosttillskott",
        "hudvård", "schampo", "håravfall", "torr hud",
        "miljövänlig rengöring", "diskmedel", "tvättmedel",
    ):
        _add(anchor, evidence_type="GSC_DEMAND")

    # First-party measured GSC search-impression evidence fills the
    # remaining slots, ranked by impressions.
    gsc = _read_json(ctx.runtime_directory / "intelligence" / "gsc-latest.json")
    query = gsc.get("query") if isinstance(gsc.get("query"), dict) else {}
    rows = query.get("all_queries", []) if isinstance(query.get("all_queries"), list) else []
    ranked = sorted(
        [r for r in rows if isinstance(r, dict) and str(r.get("query", "")).strip() and not _off_strategy(str(r["query"]))],
        key=lambda r: -(int(r.get("impressions") or 0)),
    )
    remaining = max(0, 20 - len(candidates))
    for r in ranked[:remaining]:
        _add(str(r["query"]), evidence_type="GSC_DEMAND", impressions=r.get("impressions"))

    if not candidates:
        # The fallback covers LevNytt's full three product categories
        # (kosttillskott, personlig vård, rengöring) plus the direct-selling
        # model -- never supplements alone, so the Scout researches the whole
        # NeoLife business scope even before any community/forum evidence
        # exists.
        candidates = [
            {"keyword": k, "evidence_type": "GSC_DEMAND"}
            for k in (
                "kosttillskott", "multivitamin", "magnesium", "omega 3",
                "d vitamin", "probiotika", "kostfiber", "viktminskning",
                "hudvård", "schampo", "håravfall", "torr hud",
                "miljövänlig rengöring", "diskmedel", "tvättmedel",
                "neolife", "direktförsäljning", "pyramidspel",
            )
        ]
    candidates = candidates[:20]
    candidates_path.parent.mkdir(parents=True, exist_ok=True)
    candidates_path.write_text(json.dumps({"candidates": candidates}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
