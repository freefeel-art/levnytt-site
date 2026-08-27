"""LevNytt (NeoLife) Community Manager domain logic.

Project-scoped, deterministic helpers for the LevNytt community_acquisition and
community_engagement capabilities. This module supplies ONLY the NeoLife
classification, evidence routing, and response-proposal logic. It never opens a
browser or performs a write: the shared Facebook observer/interactor transports
live in app/providers and are invoked from commander/procedure.py.

No OLSP or Cashbackkollen business context is used here.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── NeoLife-specific signal taxonomy ──────────────────────────────
# Distinct from OLSP's acquisition taxonomy (OBJECTION / BUYING_SIGNAL /
# PROBLEM_OR_FRUSTRATION / GOAL_OR_NEED / INTEREST_SIGNAL). LevNytt classifies
# consumer-facing questions, never affiliate/acquisition intent.
_PRODUCT_MARKERS = (
    "neolife", "carotenoid", "omega 3", "omega-3", "pro vitality", "pro-vitality",
    "tre en en", "formula iv", "elevate", "upbeet", "super 10", "golden home care",
    "produkt", "vilken produkt", "vad innehåller", "innehåll",
)
_SCIENCE_HEALTH_MARKERS = (
    "antioxidanter", "magnesium", "vitamin", "d vitamin", "d-vitamin", "probiotika",
    "kosttillskott", "kostfiber", "omega", "selen", "zink", "kollagen", "hälsa",
    "hjälper", "forskning", "evidens", "studier", "biverkning", "säker",
)
# Split by how unambiguous each term is on its own. STRONG terms name the
# business/distributor topic directly and are safe to trigger classification
# alone. WEAK terms are common, generic Swedish words that appear constantly
# in totally unrelated contexts (an account "registrera"-tion, a general
# "sälja"/"sell" mention, "inkomst"/income in any context, a bare "sponsor")
# -- one of these alone is not real evidence of a business/distributor
# discussion. Confirmed live: a real magnesium-supplement thread was
# misclassified as BUSINESS_DISTRIBUTOR purely because "registrera" appeared
# once, incidentally, with no other business-shaped language anywhere in the
# thread. Two or more independent weak markers together is treated as real
# corroborating evidence; one alone is not.
_BUSINESS_DISTRIBUTOR_STRONG_MARKERS = (
    "återförsäljare", "aterforsaljare", "distributör", "distributor",
    "affärsmöjlighet", "affarsmojlighet", "pyramidspel", "mlm",
)
_BUSINESS_DISTRIBUTOR_WEAK_MARKERS = (
    # "registrera sig" is deliberately not listed separately: it is a
    # substring superset of "registrera" and would otherwise silently count
    # as two independent markers for one single occurrence, defeating the
    # "two independent weak markers" corroboration requirement below.
    "tjäna pengar", "tjana pengar", "inkomst", "sponsor", "registrera", "sälja", "salja",
)
_CONSUMER_DECISION_MARKERS = (
    "värt", "vart", "billigare", "pris", "kostar", "vilket ska jag", "jämför",
    "jamfor", "köpa", "kopa", "rekommendera", "värt det", "vart det",
)
_CONTENT_QUESTION_MARKERS = (
    "guide", "artikel", "var kan jag läsa", "har ni skrivit", "länk", "lank",
    "var hittar jag",
)


_SIGNAL_CATEGORY_PRIORITY = ("BUSINESS_DISTRIBUTOR", "PRODUCT", "SCIENCE_HEALTH", "CONSUMER_DECISION", "CONTENT_QUESTION")


def classify_levnytt_signal(text: str) -> dict[str, Any]:
    """Classify one observed Facebook text into the NeoLife consumer taxonomy.

    Returns matched categories and a primary category. Text matching nothing is
    UNKNOWN (not actionable). A user statement is USER_CLAIM, never verified fact.

    Evidence-combination, not first-match-wins: BUSINESS_DISTRIBUTOR requires
    either one unambiguous strong marker or two or more independent weak
    (generic, ambiguous) markers together -- see
    _BUSINESS_DISTRIBUTOR_STRONG_MARKERS/_WEAK_MARKERS. The primary category
    is whichever matched category has the strongest evidence (most matched
    markers), not merely whichever fixed-priority category happened to match
    first -- so a handful of health markers correctly outweighs one
    borderline business-shaped word, while ties still fall back to the same
    priority order as before.
    """
    stripped = (text or "").strip()
    if not stripped:
        return {"signal_types": [], "primary_signal_type": "UNKNOWN", "is_actionable": False, "matched_markers": []}

    lowered = stripped.casefold()
    category_hits: dict[str, list[str]] = {}
    for category, marker_list in (
        ("PRODUCT", _PRODUCT_MARKERS),
        ("SCIENCE_HEALTH", _SCIENCE_HEALTH_MARKERS),
        ("CONSUMER_DECISION", _CONSUMER_DECISION_MARKERS),
        ("CONTENT_QUESTION", _CONTENT_QUESTION_MARKERS),
    ):
        hits = [m for m in marker_list if m in lowered]
        if hits:
            category_hits[category] = hits

    strong_hits = [m for m in _BUSINESS_DISTRIBUTOR_STRONG_MARKERS if m in lowered]
    weak_hits = [m for m in _BUSINESS_DISTRIBUTOR_WEAK_MARKERS if m in lowered]
    if strong_hits or len(weak_hits) >= 2:
        category_hits["BUSINESS_DISTRIBUTOR"] = strong_hits + weak_hits

    if not category_hits:
        return {"signal_types": [], "primary_signal_type": "UNKNOWN", "is_actionable": False, "matched_markers": []}

    matched = sorted(category_hits, key=_SIGNAL_CATEGORY_PRIORITY.index)
    primary = max(matched, key=lambda c: (len(category_hits[c]), -_SIGNAL_CATEGORY_PRIORITY.index(c)))
    markers = [m for c in matched for m in category_hits[c]]

    # A direct question is always actionable; otherwise only substantive matches are.
    is_question = "?" in stripped or lowered.startswith(("vad", "hur", "varför", "vilken", "vilket", "är", "hjälper", "kan"))
    return {
        "signal_types": matched,
        "primary_signal_type": primary,
        "is_actionable": is_question or bool(matched),
        "matched_markers": markers,
    }


# ── evidence routing (LevNytt research, never olsp_scout) ─────────
def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _slugify(value: str) -> str:
    slug = value.casefold().strip().replace("å", "a").replace("ä", "a").replace("ö", "o")
    return re.sub(r"[^a-z0-9]+", "-", slug).strip("-")[:80]


def _matching_keyword(text: str, runtime: Path) -> str | None:
    """Find the most specific known LevNytt keyword/topic present in the observed
    text (longest match wins), so the reply is grounded in existing project
    evidence rather than invented."""
    lowered = (text or "").casefold()
    candidates_path = runtime / "intelligence" / "keyword-candidates.json"
    candidates = _read_json(candidates_path).get("candidates", [])
    if not isinstance(candidates, list):
        candidates = []
    best: str | None = None
    for item in candidates:
        if not isinstance(item, dict):
            continue
        kw = str(item.get("keyword", "")).strip()
        if kw and kw.casefold() in lowered and (best is None or len(kw) > len(best)):
            best = kw
    if best:
        return best
    research_dir = runtime / "intelligence"
    for path in sorted(research_dir.glob("research-*.json")):
        packet = _read_json(path)
        topic = str(packet.get("topic", "")).strip()
        if topic and topic.casefold() in lowered and (best is None or len(topic) > len(best)):
            best = topic
    return best


def _tokens(value: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", _slugify(value)) if len(t) >= 3}


def _shared_grounding_facts(topic: str, runtime: Path) -> list[dict[str, Any]]:
    """Ground a reasoning draft in the one shared LevNytt evidence provider.

    This is the canonical LevNytt factual-evidence path
    (app.commander.levnytt_health_evidence), which reads the same research
    packets but applies the evidence-quality filter and the health/wellness
    claim-safety gate -- never the raw research packets directly, so a
    disease/treatment/dosage/weight-loss claim cannot become a draft merely
    because it exists in a packet. Facts are source-linked with provenance;
    nothing is synthesized.
    """
    from app.commander.levnytt_health_evidence import collect_evidence

    return collect_evidence(topic, runtime_directory=runtime)


# ── response proposal ─────────────────────────────────────────────
_LEVNYTT_DISCLOSURE = (
    "LevNytt är en oberoende NeoLife-distributörswebbplats (Sponsor-ID 41-830928)."
)


def propose_levnytt_response(
    candidate_text: str,
    classification: dict[str, Any],
    facts: list[dict[str, Any]],
) -> dict[str, Any]:
    """Propose a short Swedish, evidence-bound reply — or request research.

    Never proposes without a sourced fact. A science/health/product signal that
    has no grounded fact returns RESEARCH_REQUIRED instead of a fabricated
    answer. Business/distributor signals are answered only with a truthful
    non-promotional pointer, never an income promise.
    """
    if not classification.get("is_actionable"):
        return {"status": "NOT_PROPOSED", "reason": "Observed text did not match an actionable NeoLife consumer signal."}

    primary = str(classification.get("primary_signal_type", ""))
    usable = [f for f in facts if isinstance(f, dict) and str(f.get("claim", "")).strip()]

    if primary == "BUSINESS_DISTRIBUTOR":
        return {
            "status": "PROPOSED",
            "proposed_text": (
                "Tack för frågan. LevNytt förklarar direktförsäljningsmodellen utan "
                "inkomstlöften — vi ger fakta om hur återförsäljarskapet fungerar, men "
                "lovar aldrig en viss inkomst. Läs gärna vår sida om direktförsäljning: "
                "https://levnytt.se/direktforsaljning-fakta"
            ),
            "signal_type": primary,
            "responds_to": candidate_text[:300],
            "grounding_source": "levnytt.se (direktforsaljning-fakta)",
            "grounding_source_type": "NEOLIFE_FIRST_PARTY",
            "requires_policy_approval_before_sending": True,
        }

    if not usable:
        return {
            "status": "RESEARCH_REQUIRED",
            "reason": f"No sourced NeoLife evidence grounds a reply for signal {primary!r}.",
            "evidence_gap": primary,
        }

    fact = usable[0]
    is_first_party = fact.get("source_type") == "NEOLIFE_FIRST_PARTY"
    text = f"Tack för frågan. {fact['claim']}"
    if is_first_party:
        text += f" (Detta är NeoLifes egen information — inte oberoende forskning.)"
    if primary == "SCIENCE_HEALTH" and len(usable) > 1:
        # Prefer an independent source over first-party when both exist.
        independent = next((f for f in usable if f.get("source_type") != "NEOLIFE_FIRST_PARTY"), usable[0])
        text = f"Tack för frågan. {independent['claim']}"

    return {
        "status": "PROPOSED",
        "proposed_text": text,
        "signal_type": primary,
        "responds_to": candidate_text[:300],
        "grounding_evidence_id": fact.get("evidence_id", ""),
        "grounding_source": str(fact.get("source") or fact.get("source_title") or fact.get("source_reference") or ""),
        "grounding_source_type": str(fact.get("source_type", "")),
        "requires_policy_approval_before_sending": True,
    }


# ── persistence ───────────────────────────────────────────────────
def _community_store_path(runtime: Path) -> Path:
    return runtime / "community" / "knowledge.json"


def load_community_store(runtime: Path) -> dict[str, Any]:
    return _read_json(_community_store_path(runtime))


def save_community_store(runtime: Path, store: dict[str, Any]) -> None:
    path = _community_store_path(runtime)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")


def record_discovery(runtime: Path, items: list[dict[str, Any]]) -> int:
    """Append newly discovered read-only Community Intelligence items to the
    project-scoped store, deduped by URL. This is discovery evidence only --
    nothing in this module or its callers posts, replies, joins a group,
    sends a connection request, or messages anyone. A discovered item's
    ``recommended_action`` (NO_ACTION / OBSERVE / POSSIBLE_REPLY) is a
    reporting label for a human/Owner decision, never a trigger for
    automated action -- no code path consumes it to act.

    Returns the count of genuinely new (not previously seen) items this call
    added -- the caller uses this to tell a run that surfaced real new
    evidence apart from one that just rediscovered already-known items
    (DataForSEO's live SERP results fluctuate run to run even for the same
    fixed query list, so a nonzero raw result_count does not by itself mean
    anything new was actually found).

    Also appends a compact, bounded run-history entry (store["discovery_runs"],
    kept to the most recent 20) recording when a run happened and how many
    new items it actually contributed -- evidence._community_state reads this
    to warn Commander when the most recent run already found ~nothing new,
    the same "don't re-run something that just told you it has nothing new"
    principle already applied to measurement_freshness."""
    store = load_community_store(runtime)
    existing = store.get("discovery", [])
    if not isinstance(existing, list):
        existing = []
    seen_urls = {str(d.get("url", "")) for d in existing if isinstance(d, dict)}
    new_count = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url", ""))
        if not url or url in seen_urls:
            continue
        item["recorded_at"] = datetime.now(timezone.utc).isoformat()
        existing.append(item)
        seen_urls.add(url)
        new_count += 1
    store["discovery"] = existing
    now = datetime.now(timezone.utc).isoformat()
    runs = store.get("discovery_runs", [])
    if not isinstance(runs, list):
        runs = []
    runs.append({"at": now, "candidate_count": len(items), "new_item_count": new_count})
    store["discovery_runs"] = runs[-20:]
    store["updated_at"] = now
    save_community_store(runtime, store)
    return new_count


# Swedish-specific discussion platforms only. Facebook and Reddit discovery
# results are not filtered by locale anywhere upstream (community_intelligence's
# domain allowlist matches any facebook.com/reddit.com hit) -- confirmed
# during the intelligence audit that a Croatian-language r/hrvatska thread
# was matched by the same fixed Swedish query set. A global platform hit
# cannot be trusted as Swedish-market community demand for a Swedish-only
# site, so it is excluded from Scout promotion (though still retained as
# community_intelligence discovery evidence -- this filter narrows only what
# becomes a Scout candidate).
_SWEDISH_DISCUSSION_PLATFORMS = {"flashback_forum", "familjeliv_forum", "flexans_forum"}


# Allowlist, not a blocklist: keep only unicode word characters (letters incl.
# å/ä/ö, digits), spaces, and a small set of punctuation confirmed live
# against DataForSEO's own Google Ads keyword-volume endpoint (':', '/',
# quotes, '-' all accepted). Everything else becomes a space. Allowlisting is
# deliberate here -- a live commissioning cycle discovered DataForSEO rejects
# '?', ',', '(', ')', en dash ('kollagen – hud' -> "Invalid Field: keywords
# ... invalid characters or symbols") and fails the ENTIRE batch task for one
# bad keyword, not just that keyword's own lookup. A blocklist would have to
# anticipate every future forum-title character; this can't miss one.
_DATAFORSEO_UNSAFE_CHARS = re.compile(r"[^\w\s.:/'\"-]", re.UNICODE)


def dataforseo_safe_keyword(text: str, max_words: int = 10, max_chars: int = 80) -> str:
    """Sanitize and truncate a real question/topic string to something
    app.providers.dataforseo's keyword-volume endpoint will accept (see
    _DATAFORSEO_UNSAFE_CHARS; also enforces the endpoint's own <=10-word,
    <=80-char limits). Forum titles and audience questions are full
    sentences with real punctuation, not search-style keywords, so this is
    applied wherever a community-derived string becomes a
    keyword-candidates.json 'keyword' value. The untruncated, unsanitized
    original text is preserved separately (question_context) for
    provenance -- this function only ever shortens/cleans the
    DataForSEO-facing copy, never the evidence record."""
    cleaned = _DATAFORSEO_UNSAFE_CHARS.sub(" ", text)
    words = cleaned.split()[:max_words]
    value = " ".join(words)
    if len(value) > max_chars:
        value = value[:max_chars].rstrip()
    return value.strip(".-:'\"/ ")


def _delta_status(prior: dict[str, Any] | None) -> str:
    """NEW (never seen before) -> RECURRING (seen once before) ->
    STRENGTHENED (seen 2+ times before, then plateaus). Shared by every
    per-source-URL delta counter in this module (Scout promotion, Stage 2
    reasoning eligibility) so "new vs. known vs. strengthened" means the
    same thing everywhere, even though each consumer keeps its own
    independent counter store -- rerunning Scout's own seeding must not
    silently mark a candidate as already-reasoned-about, and vice versa."""
    if prior is None:
        return "NEW"
    if int(prior.get("times_seen", prior.get("times_promoted", 0))) >= 2:
        return "STRENGTHENED"
    return "RECURRING"


def _record_delta(counters: dict[str, Any], url: str, *, now: str) -> None:
    record = counters.get(url) if isinstance(counters.get(url), dict) else {}
    record["times_seen"] = int(record.get("times_seen", record.get("times_promoted", 0))) + 1
    record.setdefault("first_seen_at", now)
    record["last_seen_at"] = now
    counters[url] = record


def _qualifying_swedish_possible_reply_discoveries(store: dict[str, Any]) -> list[dict[str, Any]]:
    """The one shared eligibility filter both Scout promotion and Stage 2
    reasoning start from: recommended_action == POSSIBLE_REPLY (a real
    question on a topic LevNytt covers), a Swedish-specific discussion
    platform (excludes Facebook/Reddit -- confirmed cross-locale noise), and
    a non-empty title. This is an INITIAL filter only, never treated as the
    final engagement decision -- see reason_about_discovery_candidate for
    the real relevance/grounding/link reasoning that follows."""
    discovery = store.get("discovery", [])
    if not isinstance(discovery, list):
        return []
    qualifying = [
        item for item in discovery
        if isinstance(item, dict)
        and item.get("recommended_action") == "POSSIBLE_REPLY"
        and item.get("platform") in _SWEDISH_DISCUSSION_PLATFORMS
        and str(item.get("title", "")).strip()
    ]
    qualifying.sort(key=lambda item: str(item.get("observed_at", "")), reverse=True)
    return qualifying


def community_derived_candidates(runtime: Path, limit: int = 5) -> list[dict[str, Any]]:
    """Real third-party community discoveries that are sufficiently supported
    to become Scout demand-evidence inputs -- the Community Intelligence ->
    Scout join.

    Promotes only ``store["discovery"]`` items that are all of:
      - recommended_action == "POSSIBLE_REPLY" (community_intelligence's own
        heuristic for "the title/snippet contains a real question on a topic
        LevNytt covers" -- OBSERVE/NO_ACTION results are not demand evidence);
      - on a Swedish-specific discussion platform (see
        _SWEDISH_DISCUSSION_PLATFORMS above);
      - carry a non-empty title (the minimum usable topic context).

    Never invents search volume: every returned candidate carries only real
    observed community provenance (platform, source URL, retrieval time,
    the seed query, a confidence label, and question/context text) --
    no monthly_search_volume or similar figure is ever attached. Ranked
    freshest-first and deduplicated by topic text so one recurring thread
    does not occupy multiple candidate slots. community_demand_status marks
    whether this exact source URL is being promoted for the first time
    (NEW), has been promoted once before (RECURRING), or has now been
    promoted repeatedly (STRENGTHENED) -- see record_scout_promotions.
    """
    store = load_community_store(runtime)
    discovery = store.get("discovery", [])
    if not isinstance(discovery, list):
        return []
    promotions = store.get("scout_promotions", {})
    if not isinstance(promotions, dict):
        promotions = {}

    qualifying = [
        item for item in discovery
        if isinstance(item, dict)
        and item.get("recommended_action") == "POSSIBLE_REPLY"
        and item.get("platform") in _SWEDISH_DISCUSSION_PLATFORMS
        and str(item.get("title", "")).strip()
    ]
    qualifying.sort(key=lambda item: str(item.get("observed_at", "")), reverse=True)

    seen_topics: set[str] = set()
    candidates: list[dict[str, Any]] = []
    for item in qualifying:
        topic = str(item.get("title", "")).strip()
        topic_key = topic.casefold()
        if topic_key in seen_topics:
            continue
        seen_topics.add(topic_key)
        url = str(item.get("url", ""))
        prior = promotions.get(url) if isinstance(promotions.get(url), dict) else None
        if prior is None:
            status = "NEW"
        elif int(prior.get("times_promoted", 0)) >= 2:
            status = "STRENGTHENED"
        else:
            status = "RECURRING"
        candidates.append({
            "keyword": dataforseo_safe_keyword(topic),
            "evidence_type": "COMMUNITY_DEMAND",
            "community_demand_status": status,
            "source_platform": item.get("platform", ""),
            "source_url": url,
            "source_query": item.get("query", ""),
            "retrieved_at": item.get("observed_at", ""),
            "confidence": "MEDIUM",
            "question_context": str(item.get("snippet") or item.get("title", "")),
        })
        if len(candidates) >= limit:
            break
    return candidates


def record_scout_promotions(runtime: Path, candidates: list[dict[str, Any]]) -> None:
    """Update the small per-source-URL promotion counter that
    community_derived_candidates uses to compute community_demand_status.

    This is the smallest possible new/known/strengthened mechanism: one
    counter and two timestamps per source URL, not a historical analytics
    system. It exists specifically so a community-derived question that gets
    rediscovered every day is not reported to Scout/Commander as fresh
    intelligence every single cycle."""
    store = load_community_store(runtime)
    promotions = store.get("scout_promotions", {})
    if not isinstance(promotions, dict):
        promotions = {}
    now = datetime.now(timezone.utc).isoformat()
    for candidate in candidates:
        if not isinstance(candidate, dict) or candidate.get("evidence_type") != "COMMUNITY_DEMAND":
            continue
        url = str(candidate.get("source_url", ""))
        if not url:
            continue
        record = promotions.get(url) if isinstance(promotions.get(url), dict) else {}
        record["times_promoted"] = int(record.get("times_promoted", 0)) + 1
        record.setdefault("first_promoted_at", now)
        record["last_promoted_at"] = now
        promotions[url] = record
    store["scout_promotions"] = promotions
    save_community_store(runtime, store)


# ── Stage 2: bounded third-party READ -> REASON -> DRAFT ───────────
# This never constructs or authorizes a write. It reads persisted
# community_intelligence discoveries (already real, already deduplicated,
# already URL-canonicalized -- see procedure.py), reasons about each with
# its own, independent NEW/RECURRING/STRENGTHENED delta counter (kept
# separate from scout_promotions above -- Scout seeding and this reasoning
# pass are different consumers of the same discovery data and must not
# contaminate each other's "have I already looked at this" state), and
# produces evidence for Commander. Nothing here ever builds a
# community_engagement-shaped assignment or calls a Facebook interactor.

# A general, evidence-based positive-identification list of NeoLife's own
# real identifiers (brand name, actual product line names, the real
# Sponsor-ID) -- not a blacklist of competitors. Matching this list is
# strong, objective evidence a discussion is specifically about NeoLife;
# matching nothing here says nothing about any other company.
_NEOLIFE_SPECIFIC_MARKERS = (
    "neolife", "neolifeshop", "neolife.com",
    "carotenoid complex", "pro vitality", "pro-vitality", "tre en en", "tre-en-en",
    "formula iv", "elevate", "upbeet", "super 10", "golden home care",
    "41-830928", "sponsor-id",
)

# A bare domain/URL reference is the one general, structural, company-
# agnostic signal that a discussion centers on a specific OTHER site --
# unlike a bare capitalized name (e.g. "Amway"), a domain is unambiguous
# and requires no per-company enumeration to detect. This deliberately
# under-detects rather than guesses: a discussion naming a competitor only
# by bare name, with no domain/URL evidence, falls through to the more
# conservative GENERAL_MLM_DISCUSSION/GENERAL_TOPIC_DISCUSSION buckets
# instead of being (possibly wrongly) flagged as company-specific.
_NAMED_DOMAIN_PATTERN = re.compile(r"\b[a-z0-9][a-z0-9-]{1,60}\.(?:se|com|net|org|nu|info)\b")
_LEVNYTT_OWN_DOMAINS = ("levnytt.se", "neolife.com", "neolifeshop.com")
# The discussion platforms themselves are never "the other company" --
# real full-thread text (Stage 3) embeds the platform's own structural
# links (image CDNs, quote-reply permalinks, outbound-link redirect
# wrappers like flashback.org's leave.php?u=...) which otherwise
# domain-match and would wrongly flag the platform's own infrastructure as
# an unrelated named company. Confirmed live: a real fetched Flashback
# thread's embedded links matched "flashback.org" itself before this
# exclusion was added.
_SOURCE_PLATFORM_DOMAINS = ("flashback.org", "familjeliv.se", "reddit.com", "facebook.com", "flexans.se")

_ON_TOPIC_SIGNAL_TYPES = {"SCIENCE_HEALTH", "PRODUCT", "CONSUMER_DECISION", "CONTENT_QUESTION"}


def classify_topical_relevance(text: str) -> dict[str, str]:
    """Distinguish whether a real observed discussion is explicitly about
    NeoLife, a general direct-selling/topic discussion with no specific
    company named, a discussion centered on a specific, different, named
    company/site, or too unclear to tell. A general, evidence-based rule --
    see the module-level comments above on _NEOLIFE_SPECIFIC_MARKERS and
    _NAMED_DOMAIN_PATTERN for why neither list is a competitor blacklist."""
    lowered = (text or "").casefold()
    neolife_hits = sorted({m for m in _NEOLIFE_SPECIFIC_MARKERS if m in lowered})
    if neolife_hits:
        return {
            "relevance": "EXPLICITLY_NEOLIFE",
            "relevance_evidence": f"Matched NeoLife-specific identifier(s): {', '.join(neolife_hits)}.",
        }

    excluded_domains = _LEVNYTT_OWN_DOMAINS + _SOURCE_PLATFORM_DOMAINS
    domain_hits = sorted({m.group(0) for m in _NAMED_DOMAIN_PATTERN.finditer(lowered)})
    other_domains = [d for d in domain_hits if not any(d == own or d.endswith("." + own) for own in excluded_domains)]
    if other_domains:
        return {
            "relevance": "UNRELATED_NAMED_COMPANY",
            "relevance_evidence": f"References a specific, non-NeoLife domain/site: {', '.join(other_domains)}.",
        }

    classification = classify_levnytt_signal(text)
    primary = classification.get("primary_signal_type")
    if primary == "BUSINESS_DISTRIBUTOR":
        return {
            "relevance": "GENERAL_MLM_DISCUSSION",
            "relevance_evidence": "Matched general direct-selling/MLM vocabulary with no specific company identified.",
        }
    if primary in _ON_TOPIC_SIGNAL_TYPES:
        return {
            "relevance": "GENERAL_TOPIC_DISCUSSION",
            "relevance_evidence": f"Matched LevNytt's own editorial scope ({primary}) with no specific company identified.",
        }
    return {
        "relevance": "UNCLEAR_CONTEXT",
        "relevance_evidence": "No NeoLife-specific, other-company, or LevNytt-topical signal was matched.",
    }


_LEVNYTT_URL_PATTERN = re.compile(r"https?://\S*levnytt\.se\S*", re.IGNORECASE)
_LEVNYTT_LINK_LEADIN_PATTERN = re.compile(r"\s*L[äa]s g[äa]rna[^:]*:\s*$")


def _strip_levnytt_link(text: str) -> str:
    """Remove any LevNytt URL (and its immediate lead-in clause) from a
    drafted response. A draft returned for ANSWER_WITHOUT_LINK must never
    carry a LevNytt URL or promotional CTA -- this makes that mechanically
    true rather than relying on the response templates never adding one."""
    stripped = _LEVNYTT_URL_PATTERN.sub("", text)
    stripped = _LEVNYTT_LINK_LEADIN_PATTERN.sub("", stripped)
    return stripped.strip()


def _find_live_page_for_topic(working_repository: Path, topic: str) -> dict[str, str] | None:
    """Real, published-page evidence that LevNytt has directly relevant
    content for a topic -- not merely a research packet. Token-overlap
    matched against actual on-disk HTML files (the same kind of matching the
    shared evidence provider uses for research packets), never a fabricated
    URL."""
    topic_tokens = _tokens(topic)
    if not topic_tokens:
        return None
    candidates = list(working_repository.glob("*.html"))
    articles_dir = working_repository / "content" / "articles"
    if articles_dir.is_dir():
        candidates += list(articles_dir.rglob("*.html"))
    best_path: Path | None = None
    best_overlap = 0
    for path in candidates:
        overlap = len(topic_tokens & _tokens(path.stem))
        if overlap > best_overlap:
            best_overlap = overlap
            best_path = path
    if best_path is None or best_overlap < max(1, len(topic_tokens) // 2):
        return None
    relative = best_path.relative_to(working_repository)
    return {"url": f"https://levnytt.se/{relative.stem}", "path": str(relative)}


def _possible_relevant_content(classification: dict[str, Any], topic: str | None, working_repository: Path) -> dict[str, str] | None:
    if classification.get("primary_signal_type") == "BUSINESS_DISTRIBUTOR":
        page = working_repository / "direktforsaljning-fakta.html"
        if page.is_file():
            return {"url": "https://levnytt.se/direktforsaljning-fakta", "path": "direktforsaljning-fakta.html"}
        return None
    if not topic:
        return None
    return _find_live_page_for_topic(working_repository, topic)


def reason_about_discovery_candidate(
    item: dict[str, Any],
    runtime: Path,
    working_repository: Path,
    *,
    thread_context: str | None = None,
) -> dict[str, Any]:
    """READ (one already-persisted, already real discovery item -- SERP
    title+snippet by default, or real fetched full-thread text when
    thread_context is supplied by Stage 3) -> REASON -> DRAFT where evidence
    justifies it. Returns a full evidence record for Commander -- never
    constructs or authorizes a write; community_engagement (owned-page only)
    is a wholly separate path this never reaches.

    Outcome is always exactly one of: NO_ACTION, OBSERVE, ANSWER_WITHOUT_LINK,
    POSSIBLE_VALUE_ADDING_LINK, INSUFFICIENT_CONTEXT. None of these
    authorizes execution -- they are reasoning results only. Factual
    grounding rules are unchanged regardless of evidence_basis: thread text
    tells us what people said, never that it is true.
    """
    url = str(item.get("url", ""))
    title = str(item.get("title", "")).strip()
    snippet = str(item.get("snippet", "")).strip()
    text = " ".join(part for part in (title, snippet, thread_context) if part).strip()

    relevance = classify_topical_relevance(text)
    record: dict[str, Any] = {
        "source_platform": item.get("platform", ""),
        "source_url": url,
        "source_query": item.get("query", ""),
        "observed_at": item.get("observed_at", ""),
        "question_context": text,
        "community_demand_status": item.get("community_demand_status"),
        "relevance": relevance["relevance"],
        "relevance_evidence": relevance["relevance_evidence"],
        "reasoned_at": datetime.now(timezone.utc).isoformat(),
        "evidence_basis": "FULL_THREAD" if thread_context else "SERP_SNIPPET",
    }

    if relevance["relevance"] == "UNRELATED_NAMED_COMPANY":
        return {
            **record,
            "outcome": "NO_ACTION",
            "outcome_reason": "This discussion is centered on a specific, different, named company/site; LevNytt has no basis to insert itself or its NeoLife content.",
            "draft": None,
            "possible_relevant_content": None,
        }

    if relevance["relevance"] == "UNCLEAR_CONTEXT":
        return {
            **record,
            "outcome": "OBSERVE",
            "outcome_reason": "The discussion did not clearly match a NeoLife-specific, general direct-selling, or LevNytt-topical signal.",
            "draft": None,
            "possible_relevant_content": None,
        }

    classification = classify_levnytt_signal(text)
    topic = _matching_keyword(text, runtime)
    # Grounding uses the one shared LevNytt evidence provider (which applies
    # evidence-quality and health/wellness claim-safety gates), never the raw
    # research packets directly: GSC_DEMAND/COMMUNITY_DEMAND prove a question
    # exists, not that any claim about it is true, and a disease/dosage/
    # weight-loss claim must not become a draft merely because it exists in a
    # research packet.
    facts = _shared_grounding_facts(topic, runtime) if topic else []
    proposal = propose_levnytt_response(text, classification, facts)

    if proposal.get("status") != "PROPOSED":
        return {
            **record,
            "outcome": "INSUFFICIENT_CONTEXT",
            "outcome_reason": proposal.get("reason", "No sourced evidence grounds an answer for this signal; refusing to improvise."),
            "draft": None,
            "possible_relevant_content": None,
        }

    draft_text = _strip_levnytt_link(str(proposal.get("proposed_text", "")))
    possible_link = _possible_relevant_content(classification, topic, working_repository)

    if possible_link is not None:
        return {
            **record,
            "outcome": "POSSIBLE_VALUE_ADDING_LINK",
            "outcome_reason": "A grounded answer is possible, and LevNytt has a directly relevant, published page that adds material value beyond it. This is a reasoning classification only -- it does not authorize posting the link.",
            "draft": draft_text,
            "possible_relevant_content": possible_link,
        }
    return {
        **record,
        "outcome": "ANSWER_WITHOUT_LINK",
        "outcome_reason": "A grounded answer is possible, but no directly relevant, published LevNytt page was found to add material value beyond it. A useful answer does not by itself justify self-promotion.",
        "draft": draft_text,
        "possible_relevant_content": None,
    }


def community_reasoning_eligible_candidates(runtime: Path, limit: int = 5) -> list[dict[str, Any]]:
    """The candidates Stage 2 reasoning should spend effort on this cycle:
    the same initial POSSIBLE_REPLY/Swedish-platform filter
    community_derived_candidates uses (a starting filter, never trusted as
    the final engagement decision -- reason_about_discovery_candidate does
    the real work), restricted to NEW or STRENGTHENED per this reasoning
    pass's own delta counter. An unchanged RECURRING discovery is skipped:
    it was already reasoned about last time and nothing changed, so
    reprocessing it would be expensive busywork, not new intelligence."""
    store = load_community_store(runtime)
    reasoning_history = store.get("community_reasoning_history", {})
    if not isinstance(reasoning_history, dict):
        reasoning_history = {}

    seen_topics: set[str] = set()
    eligible: list[dict[str, Any]] = []
    for item in _qualifying_swedish_possible_reply_discoveries(store):
        topic_key = str(item.get("title", "")).strip().casefold()
        if topic_key in seen_topics:
            continue
        seen_topics.add(topic_key)
        url = str(item.get("url", ""))
        prior = reasoning_history.get(url) if isinstance(reasoning_history.get(url), dict) else None
        status = _delta_status(prior)
        if status == "RECURRING":
            continue
        eligible.append({**item, "community_demand_status": status})
        if len(eligible) >= limit:
            break
    return eligible


def record_community_reasoning(runtime: Path, results: list[dict[str, Any]]) -> None:
    """Update the small per-source-URL counter community_reasoning_eligible_
    candidates uses -- kept entirely separate from scout_promotions (Stage
    2 reasoning and Scout candidate seeding are different consumers of the
    same discovery data and must not contaminate each other's delta
    state)."""
    store = load_community_store(runtime)
    reasoning_history = store.get("community_reasoning_history", {})
    if not isinstance(reasoning_history, dict):
        reasoning_history = {}
    now = datetime.now(timezone.utc).isoformat()
    for result in results:
        if not isinstance(result, dict):
            continue
        url = str(result.get("source_url", ""))
        if not url:
            continue
        _record_delta(reasoning_history, url, now=now)
    store["community_reasoning_history"] = reasoning_history
    save_community_store(runtime, store)


def record_reasoning_results(runtime: Path, results: list[dict[str, Any]]) -> None:
    """Persist Stage 2's reasoning evidence for Commander visibility,
    bounded the same way discovery_runs is (most recent 20)."""
    if not results:
        return
    store = load_community_store(runtime)
    existing = store.get("reasoning", [])
    if not isinstance(existing, list):
        existing = []
    existing.extend(results)
    store["reasoning"] = existing[-20:]
    store["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_community_store(runtime, store)


# ── Stage 3: bounded full-thread fetching ───────────────────────────
# Adds only FULL THREAD CONTEXT before any future engagement decision --
# still never constructs or authorizes a write. Fetchability was verified
# for real (live fetches + robots.txt) during the Stage 3 audit:
#   - flashback.org: robots.txt allows general crawling (Crawl-delay: 5);
#     real fetch returns rich, individually-attributed posts (author,
#     timestamp, post number).
#   - familjeliv.se: robots.txt allows general crawling for a generic
#     user-agent; real fetch returns the original post reliably, but
#     individual replies are only loosely delimited and per-reply
#     author/timestamp is not reliably available (only quoted replies show
#     an author + timestamp).
#   - reddit.com: robots.txt explicitly disallows all crawling
#     ("User-agent: * / Disallow: /"); a real fetch returned HTTP 403.
#   - facebook.com: robots.txt explicitly prohibits automated collection
#     without permission; a real fetch returned HTTP 403.
#   - flexans.se (present in the discussion-domain allowlist, but with zero
#     real discoveries so far): the domain does not resolve at all.
# Reddit, Facebook, and flexans.se are therefore excluded from fetch
# eligibility entirely, not merely best-effort-attempted.
_FETCHABLE_PLATFORMS = {"flashback_forum", "familjeliv_forum"}
_MAX_THREAD_FETCHES_PER_RUN = 3
_THREAD_FETCH_TIMEOUT_SECONDS = 30


def find_discovery_item(runtime: Path, url: str) -> dict[str, Any] | None:
    """Look up one persisted SERP discovery record by URL -- used to recover
    the original title/snippet before re-reasoning with thread context,
    without ever overwriting the original discovery record itself."""
    store = load_community_store(runtime)
    discovery = store.get("discovery", [])
    if not isinstance(discovery, list):
        return None
    for item in discovery:
        if isinstance(item, dict) and str(item.get("url", "")) == url:
            return item
    return None


_FLASHBACK_POST_HEADER = re.compile(
    r"# \[\*\*(?P<number>\d+)\*\*\]\([^)]+\)\s*\n\s*\n\[(?P<username>[^\]]+)\]\([^)]+\)"
)
_FLASHBACK_TIMESTAMP_LINE = re.compile(r"^\d{4}-\d{2}-\d{2}, \d{2}:\d{2}$")
_FLASHBACK_BOILERPLATE_LINE = re.compile(
    r"^(- .*|Medlem|Reg: .*|Inl[äa]gg: .*|\[Citera\]\(.*\)|\[!\[.*\]\(.*\)\]\(.*\)|Spoiler)$"
)


def _parse_flashback_thread(markdown: str) -> dict[str, Any]:
    """Best-effort structural extraction, verified against real fetched
    Flashback threads: post headers ('# [**N**](url)') reliably delimit
    individually-attributed posts (author, timestamp, text). No evidence of
    multi-page pagination markup was observed in the real threads fetched
    during the audit -- reported honestly as single-page rather than assumed."""
    matches = list(_FLASHBACK_POST_HEADER.finditer(markdown))
    posts: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        body = markdown[start:end]
        timestamp = None
        lines: list[str] = []
        for raw_line in body.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if _FLASHBACK_TIMESTAMP_LINE.match(line):
                timestamp = line.replace(",", "")
                continue
            if _FLASHBACK_BOILERPLATE_LINE.match(line):
                continue
            lines.append(line)
        posts.append({
            "post_number": int(match.group("number")),
            "author": match.group("username"),
            "timestamp": timestamp,
            "text": "\n".join(lines).strip(),
        })
    return {
        "posts": posts,
        "original_post": posts[0]["text"] if posts else None,
        "pagination": {"pages_observed": 1, "additional_pages_detected": False},
    }


_FAMILJELIV_PAGINATION = re.compile(r"^Sida (?P<current>\d+) av (?P<total>\d+)$")
_FAMILJELIV_REPLY_HEADER = re.compile(r"^Svar på tråden .*$")
_FAMILJELIV_QUOTE_ATTRIBUTION = re.compile(
    r"^(?P<author>.+?) skrev (?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) följande:$"
)
_FAMILJELIV_TITLE_HEADING = re.compile(r"^(?:-\s*)*#\s+(?P<title>.+)$")
_FAMILJELIV_NAV_BULLET = re.compile(r"^(?:-\s*)*\[.*\]\(.*\)$")


def _parse_familjeliv_thread(markdown: str) -> dict[str, Any]:
    """Best-effort structural extraction, verified against a real fetched
    Familjeliv thread. The original post is reliably distinguishable (the
    first heading not naming the site itself, up to the first navigation/
    pagination marker). Individual replies are only loosely delimited by
    blank lines and are NOT reliably attributed to an author or timestamp --
    only a reply that quotes an earlier one reveals an author + timestamp.
    This limitation is real, not a parsing gap to be perfected here."""
    lines = [line.strip() for line in markdown.splitlines()]
    title_idx = None
    title = None
    for index, line in enumerate(lines):
        match = _FAMILJELIV_TITLE_HEADING.match(line)
        if match and "familjeliv" not in match.group("title").casefold():
            title_idx = index
            title = match.group("title")
            break
    if title_idx is None:
        return {"title": None, "original_post": None, "replies": [], "quoted_authors": [], "pagination": None}

    # Pagination ("Sida X av Y") is detected as a standalone full-text search,
    # not tied to the original-post loop below: the real markdown places one
    # or more plain navigation-arrow bullets (e.g. "- - [«](...)") BEFORE the
    # "Sida X av Y" text on the same nav line group, so a loop that stops at
    # the first nav-bullet-shaped line would otherwise never reach it.
    pagination = None
    for line in lines:
        page_match = _FAMILJELIV_PAGINATION.match(line.lstrip("- ").strip())
        if page_match:
            pagination = {"current_page": int(page_match.group("current")), "total_pages": int(page_match.group("total"))}
            break

    original_post_lines: list[str] = []
    cursor = title_idx + 1
    while cursor < len(lines):
        candidate = lines[cursor].lstrip("- ").strip()
        if _FAMILJELIV_PAGINATION.match(candidate) or _FAMILJELIV_NAV_BULLET.match(lines[cursor]):
            break
        if lines[cursor]:
            original_post_lines.append(lines[cursor])
        cursor += 1
    original_post = "\n".join(original_post_lines).strip()

    reply_start = None
    for index in range(cursor, len(lines)):
        if _FAMILJELIV_REPLY_HEADER.match(lines[index]):
            reply_start = index + 1
            break

    replies: list[str] = []
    quoted_authors: list[dict[str, str]] = []
    if reply_start is not None:
        current: list[str] = []
        for line in lines[reply_start:]:
            candidate = line.lstrip("- ").strip()
            if _FAMILJELIV_PAGINATION.match(candidate) or line.startswith("[Svara i tråden]"):
                break
            quote_match = _FAMILJELIV_QUOTE_ATTRIBUTION.match(candidate)
            if quote_match:
                quoted_authors.append({"author": quote_match.group("author"), "timestamp": quote_match.group("timestamp")})
            if not candidate:
                if current:
                    replies.append("\n".join(current).strip())
                    current = []
                continue
            current.append(candidate)
        if current:
            replies.append("\n".join(current).strip())
    replies = [reply for reply in replies if reply]

    return {
        "title": title,
        "original_post": original_post or None,
        "replies": replies,
        "quoted_authors": quoted_authors,
        "pagination": pagination,
    }


def fetch_thread_context(url: str, platform: str, *, scrape) -> dict[str, Any]:
    """One bounded, read-only fetch of a single third-party discussion
    thread's first page, via the existing Firecrawl provider Scout already
    uses (no second web-fetch stack). Read-only by construction: this
    function only ever calls scrape() (Firecrawl's GET-equivalent) and
    returns a structured evidence record -- it never constructs an
    interaction, never calls FacebookCommunityInteractor, and never submits
    anything. A failed or unsupported fetch is reported, never raised, so
    one bad thread can never block a Community Intelligence cycle."""
    now = datetime.now(timezone.utc).isoformat()
    if platform not in _FETCHABLE_PLATFORMS:
        return {
            "fetch_status": "UNSUPPORTED_SOURCE", "url": url, "platform": platform,
            "fetched_at": now, "provider": "none",
            "limitations": [f"{platform!r} is not a supported full-thread-fetch source (see the Stage 3 fetchability audit)."],
        }
    try:
        data = scrape(url, formats=("markdown",), timeout=_THREAD_FETCH_TIMEOUT_SECONDS)
    except Exception as error:
        return {
            "fetch_status": "FAILED", "url": url, "platform": platform,
            "fetched_at": now, "provider": "Firecrawl",
            "error": f"{type(error).__name__}: {error}",
        }
    markdown = str(data.get("markdown") or "")
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    if not markdown.strip():
        return {
            "fetch_status": "EMPTY", "url": url, "platform": platform,
            "fetched_at": now, "provider": "Firecrawl", "page_title": metadata.get("title", ""),
        }

    if platform == "flashback_forum":
        parsed = _parse_flashback_thread(markdown)
        confidence = "HIGH" if parsed["posts"] else "LOW"
        limitations = [] if parsed["posts"] else ["No individually-attributed posts were recognized in the fetched content."]
    else:
        parsed = _parse_familjeliv_thread(markdown)
        confidence = "MEDIUM" if parsed["original_post"] else "LOW"
        limitations = ["Per-reply author/timestamp attribution is not reliably available for this source; only quoted replies reveal an author/timestamp."]
        if not parsed["original_post"]:
            limitations.append("The original post could not be confidently distinguished from surrounding content.")

    result = {
        "fetch_status": "COMPLETE",
        "url": url,
        "platform": platform,
        "fetched_at": now,
        "provider": "Firecrawl",
        "page_title": metadata.get("title", ""),
        "thread_title": parsed.get("title") or metadata.get("title", ""),
        "original_post": parsed.get("original_post"),
        "posts": parsed.get("posts", []),
        "replies": parsed.get("replies", []),
        "quoted_authors": parsed.get("quoted_authors", []),
        "pagination": parsed.get("pagination"),
        "extraction_confidence": confidence,
        "limitations": limitations,
        "raw_markdown_length": len(markdown),
    }
    # Stage 4.5 item 2: freshness fields recorded explicitly and separately
    # from the raw post list, where the source exposes real timestamps --
    # thread creation date (earliest extracted timestamp), latest meaningful
    # reply date (reused from Stage 4's own staleness check), and age at
    # discovery, all real, never fabricated when timestamps are unavailable.
    created_at = _earliest_post_timestamp(result)
    latest_at = _latest_post_timestamp(result)
    result["thread_created_at"] = created_at.isoformat() if created_at else None
    result["latest_reply_at"] = latest_at.isoformat() if latest_at else None
    result["age_at_discovery_days"] = (datetime.now(timezone.utc) - created_at).days if created_at else None
    return result


def thread_context_text(fetch: dict[str, Any], *, max_chars: int = 3000) -> str | None:
    """Flatten one fetch_thread_context() result into bounded plain text
    suitable as reasoning context. Never fabricates structure that wasn't
    extracted -- an EMPTY/FAILED/UNSUPPORTED fetch returns None, and
    reasoning falls back to SERP snippet alone."""
    if fetch.get("fetch_status") != "COMPLETE":
        return None
    parts: list[str] = []
    if fetch.get("original_post"):
        parts.append(str(fetch["original_post"]))
    for post in fetch.get("posts", [])[1:]:
        if isinstance(post, dict) and post.get("text"):
            parts.append(str(post["text"]))
    for reply in fetch.get("replies", []):
        if reply:
            parts.append(str(reply))
    text = "\n".join(parts).strip()
    if not text:
        return None
    return text[:max_chars]


def thread_fetch_eligible_candidates(runtime: Path, limit: int = _MAX_THREAD_FETCHES_PER_RUN) -> list[dict[str, Any]]:
    """Candidates for bounded full-thread fetching this cycle: already
    reasoned about by Stage 2, not already resolved as NO_ACTION, on a
    source Stage 3 can actually fetch (_FETCHABLE_PLATFORMS), and NEW or
    STRENGTHENED per this stage's own delta counter -- kept independent of
    both scout_promotions and community_reasoning_history, so seeding
    Scout, Stage 2 reasoning, and Stage 3 fetching never contaminate each
    other's "have I already done this" state. An unchanged RECURRING
    candidate is skipped: it was already fetched and nothing has changed."""
    store = load_community_store(runtime)
    reasoning = store.get("reasoning", [])
    if not isinstance(reasoning, list):
        return []
    fetch_history = store.get("thread_fetch_history", {})
    if not isinstance(fetch_history, dict):
        fetch_history = {}
    # Stage 4.5: use known platform policy before spending an expensive
    # fetch. Only a cache read (scrape=None) -- never a live fetch just to
    # decide eligibility. Skips only platforms with a KNOWN prohibition;
    # UNKNOWN never blocks bounded read-only fetching, since reading a
    # thread doesn't itself violate anything -- only a future write would,
    # and write remains impossible regardless.
    prohibited_platforms = {
        platform for platform in _FETCHABLE_PLATFORMS
        if platform_policy_state(platform, runtime, scrape=None).get("overall_state") == "PROHIBITED"
    }

    seen_urls: set[str] = set()
    eligible: list[dict[str, Any]] = []
    for result in reversed(reasoning):  # most recent reasoning per URL wins
        if not isinstance(result, dict):
            continue
        url = str(result.get("source_url", ""))
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        if result.get("outcome") == "NO_ACTION":
            continue
        if result.get("source_platform") not in _FETCHABLE_PLATFORMS:
            continue
        if result.get("source_platform") in prohibited_platforms:
            continue
        prior = fetch_history.get(url) if isinstance(fetch_history.get(url), dict) else None
        status = _delta_status(prior)
        if status == "RECURRING":
            continue
        eligible.append({**result, "thread_fetch_status": status})
        if len(eligible) >= limit:
            break
    return eligible


def record_thread_fetch(runtime: Path, urls: list[str]) -> None:
    """Update Stage 3's own per-source-URL delta counter."""
    store = load_community_store(runtime)
    fetch_history = store.get("thread_fetch_history", {})
    if not isinstance(fetch_history, dict):
        fetch_history = {}
    now = datetime.now(timezone.utc).isoformat()
    for url in urls:
        if url:
            _record_delta(fetch_history, url, now=now)
    store["thread_fetch_history"] = fetch_history
    save_community_store(runtime, store)


def record_thread_evidence(runtime: Path, records: list[dict[str, Any]]) -> None:
    """Persist full-thread evidence SEPARATELY from the original SERP
    discovery record (store['thread_evidence'], never store['discovery']) --
    the original discovery record is never overwritten."""
    if not records:
        return
    store = load_community_store(runtime)
    existing = store.get("thread_evidence", [])
    if not isinstance(existing, list):
        existing = []
    existing.extend(records)
    store["thread_evidence"] = existing[-20:]
    store["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_community_store(runtime, store)


# ── Stage 4: community rules + engagement policy ─────────────────────
# Answers a separate question from Stages 2-3: even if LevNytt can help,
# would participation be appropriate and permitted? Nothing here authorizes
# a write -- every function returns a recommendation only, and
# write_authorized is always False. See evaluate_engagement for the single
# entry point that ties the four dimensions (RELEVANCE/GROUNDING are
# already Stage 2/3's job; this stage adds PLATFORM POLICY and SOCIAL
# APPROPRIATENESS) into one recommendation.

# Real, first-party rule pages, resolved and read live -- not guessed.
# Reddit and Facebook are deliberately absent: Stage 3 already proved both
# structurally unavailable for this mechanism (robots.txt disallows/
# prohibits automated collection; both returned real HTTP 403), and this
# phase does not attempt to bypass that.
#
# Familjeliv (Stage 4.5): the Stage 4 audit only reached /sakerhet-och-regler,
# a client-side-rendered table of contents with zero real <a href> links
# (confirmed live: Firecrawl's own "links" format returned an empty list for
# it -- the page's "Läs mer om..." sections are JS expand-in-place, not
# navigable sub-pages). A bounded, first-party investigation this session
# found the actual rule text lives at a real, separately-resolving URL,
# /medlemsvillkor (verified: plain HTTP 200, not linked from the rendered
# page, discovered by trying the platform's own common URL naming pattern --
# not guessed at the rule-text level, the URL was found first and then read).
_PLATFORM_RULES_URLS = {
    "flashback_forum": "https://www.flashback.org/regler",
    "familjeliv_forum": "https://www.familjeliv.se/medlemsvillkor",
}
# Rules change far less often than individual threads -- one authoritative
# fetch per platform is reused for every candidate on that platform until
# stale, rather than re-fetched per discussion.
_RULES_FRESHNESS_DAYS = 30


def fetch_platform_rules(platform: str, *, scrape) -> dict[str, Any]:
    """One bounded, read-only fetch of a platform's own first-party rules
    page, via the same Firecrawl provider Stage 3 already uses. A failed or
    unsupported fetch is reported, never raised."""
    now = datetime.now(timezone.utc).isoformat()
    url = _PLATFORM_RULES_URLS.get(platform)
    if not url:
        return {"fetch_status": "UNSUPPORTED_SOURCE", "platform": platform, "url": None, "fetched_at": now}
    try:
        data = scrape(url, formats=("markdown",), timeout=_THREAD_FETCH_TIMEOUT_SECONDS)
    except Exception as error:
        return {"fetch_status": "FAILED", "platform": platform, "url": url, "fetched_at": now, "error": f"{type(error).__name__}: {error}"}
    markdown = str(data.get("markdown") or "")
    if not markdown.strip():
        return {"fetch_status": "EMPTY", "platform": platform, "url": url, "fetched_at": now}
    return {
        "fetch_status": "COMPLETE", "platform": platform, "url": url, "fetched_at": now,
        "provider": "Firecrawl", "raw_text": markdown, "raw_text_length": len(markdown),
    }


def _extract_platform_policy_facts(platform: str, raw_text: str) -> list[dict[str, Any]]:
    """Bounded, deterministic extraction of specific rule facts from a
    platform's real, freshly-fetched rules text. Only recognizes exact
    phrases this session verified appear in the real, live rules page --
    never infers a rule from absence, never fabricates rule text beyond
    what the fetch actually contains.

    Flashback's real rules page (verified live, rule 1.01 "Reklam och
    annonsering") is unambiguous and directly relevant to LevNytt's own
    situation: independent tips/links and consumer questions ARE
    permitted, but "referallänkar" (referral links) and marketing for
    "egen eller andras verksamhet" (one's own or others' business) are
    explicitly PROHIBITED -- and a levnytt.se link is exactly a referral
    link for LevNytt's own declared NeoLife commercial relationship.

    Familjeliv's real /medlemsvillkor page (found and verified live during
    Stage 4.5, after the Stage 4 audit only reached a client-side-rendered
    table of contents with no real links) has genuine, authoritative rule
    text in section 3.3: members may not post links to sites that "har
    kommersiella intressen" (have commercial interests) -- with the exact
    same "gäller ej oberoende tips" (does not apply to independent tips)
    exception Flashback's own rules use. A levnytt.se link is exactly a
    commercial-interest link given LevNytt's declared NeoLife relationship.
    """
    lowered = raw_text.casefold()
    facts: list[dict[str, Any]] = []

    def _add(scope: str, state: str, phrase: str, rule_reference: str) -> None:
        if phrase.casefold() in lowered:
            facts.append({"scope": scope, "state": state, "evidence_phrase": phrase, "rule_reference": rule_reference})

    if platform == "flashback_forum":
        _add("referral_link", "PROHIBITED", "referallänkar är förbjudna", "1.01 Reklam och annonsering")
        _add(
            "self_promotion", "PROHIBITED",
            "inte tillåtet att använda forumet för att skapa eller sprida marknadsföring för egen eller andras verksamhet",
            "1.01 Reklam och annonsering",
        )
        _add("independent_tips", "PERMITTED", "det är tillåtet att tipsa och länka till innehåll", "1.01 Reklam och annonsering")
        _add("consumer_questions", "PERMITTED", "det är tillåtet att ställa konsumentfrågor", "1.01 Reklam och annonsering")
    elif platform == "familjeliv_forum":
        _add("referral_link", "PROHIBITED", "har kommersiella intressen", "Medlemsvillkor 3.3")
        _add("independent_tips", "PERMITTED", "gäller ej oberoende tips", "Medlemsvillkor 3.3")
    return facts


def _aggregate_policy_state(facts: list[dict[str, Any]]) -> str:
    """Absence of evidence is UNKNOWN, never PERMITTED -- fail closed."""
    if not facts:
        return "UNKNOWN"
    scopes = {fact["scope"]: fact["state"] for fact in facts}
    link_prohibited = scopes.get("referral_link") == "PROHIBITED" or scopes.get("self_promotion") == "PROHIBITED"
    discussion_permitted = scopes.get("independent_tips") == "PERMITTED" or scopes.get("consumer_questions") == "PERMITTED"
    if link_prohibited and discussion_permitted:
        return "PERMITTED_WITHOUT_LINK"
    if link_prohibited:
        return "PROHIBITED"
    if discussion_permitted:
        return "PERMITTED"
    return "REQUIRES_REVIEW"


def _is_rules_cache_fresh(cached: dict[str, Any] | None) -> bool:
    if not cached or not cached.get("retrieved_at"):
        return False
    try:
        retrieved = datetime.fromisoformat(str(cached["retrieved_at"]))
    except ValueError:
        return False
    if retrieved.tzinfo is None:
        retrieved = retrieved.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - retrieved).days < _RULES_FRESHNESS_DAYS


def platform_policy_state(platform: str, runtime: Path, *, scrape=None) -> dict[str, Any]:
    """Cached, freshness-aware platform rules lookup -- one authoritative
    fetch per platform (bounded to _RULES_FRESHNESS_DAYS) supports every
    candidate on that platform, never a fetch per discussion. Returns
    overall_state UNKNOWN whenever no rules evidence exists and none can be
    fetched right now; never infers PERMITTED from an empty cache."""
    store = load_community_store(runtime)
    cache = store.get("platform_rules", {})
    if not isinstance(cache, dict):
        cache = {}
    cached = cache.get(platform)
    fresh = _is_rules_cache_fresh(cached)

    if not fresh and scrape is not None:
        fetch = fetch_platform_rules(platform, scrape=scrape)
        if fetch.get("fetch_status") == "COMPLETE":
            facts = _extract_platform_policy_facts(platform, fetch["raw_text"])
            cached = {
                "platform": platform,
                "source_url": fetch["url"],
                "retrieved_at": fetch["fetched_at"],
                "facts": facts,
                "overall_state": _aggregate_policy_state(facts),
                "confidence": "HIGH" if facts else "LOW",
                "raw_text_length": fetch.get("raw_text_length"),
            }
            cache[platform] = cached
            store["platform_rules"] = cache
            save_community_store(runtime, store)
            fresh = True
        elif cached is None:
            return {
                "platform": platform, "overall_state": "UNKNOWN", "facts": [], "source_url": fetch.get("url"),
                "retrieved_at": None, "confidence": "NONE", "cache_fresh": False,
                "note": f"Rules fetch did not complete ({fetch.get('fetch_status')}); no cached rules exist for this platform.",
            }

    if cached is None:
        return {
            "platform": platform, "overall_state": "UNKNOWN", "facts": [], "source_url": None,
            "retrieved_at": None, "confidence": "NONE", "cache_fresh": False,
            "note": "No rules evidence has been fetched for this platform yet.",
        }
    return {**cached, "cache_fresh": fresh}


_THREAD_STALE_DAYS = 365
# A small, explicitly heuristic marker set -- absence never asserts "not
# hostile," only "not detected." A deterministic keyword check cannot
# reliably judge tone; this is used only to lower confidence, never to
# confidently clear a thread as friendly.
_HOSTILITY_MARKERS = ("idiot", "dum i huvudet", "håll käften", "dra åt helvete", "fan ta dig", "håll tyst")


def _extracted_timestamps(fetch: dict[str, Any]) -> list[datetime]:
    timestamps: list[datetime] = []
    for post in fetch.get("posts", []) or []:
        raw = post.get("timestamp") if isinstance(post, dict) else None
        if not raw:
            continue
        try:
            timestamps.append(datetime.strptime(raw, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc))
        except ValueError:
            continue
    for quote in fetch.get("quoted_authors", []) or []:
        raw = quote.get("timestamp") if isinstance(quote, dict) else None
        if not raw:
            continue
        try:
            timestamps.append(datetime.strptime(raw, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc))
        except ValueError:
            continue
    return timestamps


def _latest_post_timestamp(fetch: dict[str, Any]) -> datetime | None:
    timestamps = _extracted_timestamps(fetch)
    return max(timestamps) if timestamps else None


def _earliest_post_timestamp(fetch: dict[str, Any]) -> datetime | None:
    timestamps = _extracted_timestamps(fetch)
    return min(timestamps) if timestamps else None


def _reply_count(fetch: dict[str, Any]) -> int:
    if fetch.get("posts"):
        return max(0, len(fetch["posts"]) - 1)  # exclude the original post
    return len(fetch.get("replies", []) or [])


def _combined_thread_text(fetch: dict[str, Any]) -> str:
    parts = [str(fetch.get("original_post") or "")]
    parts += [str(post.get("text", "")) for post in fetch.get("posts", []) or [] if isinstance(post, dict)]
    parts += [str(reply) for reply in fetch.get("replies", []) or []]
    return " ".join(parts)


def assess_social_appropriateness(fetch: dict[str, Any] | None, reasoning: dict[str, Any]) -> dict[str, Any]:
    """A separate, deterministic judgment of whether participation would
    actually be useful -- distinct from whether it is technically permitted
    or grounded. Optimizes for useful participation, not reply volume.
    Every factor is a real, checkable signal from fetched evidence; nothing
    reliably assessable from available evidence returns UNKNOWN/reduced
    confidence rather than a guessed confident answer."""
    outcome = reasoning.get("outcome")
    if outcome in {"NO_ACTION", "OBSERVE", "INSUFFICIENT_CONTEXT"} or fetch is None:
        return {
            "social_value": "NOT_APPLICABLE",
            "thread_is_stale": None, "reply_count": None, "hostility_detected": None,
            "has_commercial_interest": None, "addresses_question": None,
            "reasons": ["No draft exists at this reasoning outcome; social value is not applicable."],
            "concerns": [],
        }

    reasons: list[str] = []
    concerns: list[str] = []

    latest = _latest_post_timestamp(fetch)
    thread_is_stale = None
    if latest is not None:
        age_days = (datetime.now(timezone.utc) - latest).days
        thread_is_stale = age_days > _THREAD_STALE_DAYS
        reasons.append(f"Latest observed reply was {age_days} day(s) ago.")
        if thread_is_stale:
            concerns.append("No thread activity in over a year; reviving it may read as necroposting.")
    else:
        reasons.append("No reliable reply timestamp was extracted; thread recency is unknown.")

    reply_count = _reply_count(fetch)
    reasons.append(f"{reply_count} real reply/replies observed in the fetched thread.")

    hostility_hits = [m for m in _HOSTILITY_MARKERS if m in _combined_thread_text(fetch).casefold()]
    if hostility_hits:
        concerns.append(f"Hostile/dismissive language observed: {', '.join(hostility_hits)}.")

    has_commercial_interest = reasoning.get("relevance") == "EXPLICITLY_NEOLIFE" or "BUSINESS_DISTRIBUTOR" in str(reasoning.get("relevance", ""))
    addresses_question = bool(reasoning.get("draft"))

    if hostility_hits:
        social_value = "LOW"
    elif thread_is_stale:
        social_value = "LOW"
    elif not addresses_question:
        social_value = "LOW"
        concerns.append("No draft text was actually produced for this candidate.")
    elif thread_is_stale is None:
        social_value = "MEDIUM"
        reasons.append("Thread recency could not be established, so social value is capped at MEDIUM.")
    else:
        social_value = "HIGH"

    return {
        "social_value": social_value,
        "thread_is_stale": thread_is_stale,
        "reply_count": reply_count,
        "hostility_detected": bool(hostility_hits),
        "has_commercial_interest": has_commercial_interest,
        "addresses_question": addresses_question,
        "reasons": reasons,
        "concerns": concerns,
    }


def assess_disclosure_requirement(reasoning: dict[str, Any]) -> dict[str, Any]:
    """Whether a proposed response requires LevNytt's commercial-relationship
    disclosure -- kept separate from platform rules. Never invents a legal
    conclusion; returns REQUIRES_REVIEW where confidence is insufficient."""
    outcome = reasoning.get("outcome")
    if outcome in {"NO_ACTION", "OBSERVE", "INSUFFICIENT_CONTEXT"}:
        return {"disclosure_state": "NOT_APPLICABLE", "reasons": ["No response is proposed at this outcome."]}

    draft = str(reasoning.get("draft") or "")
    discusses_neolife = reasoning.get("relevance") == "EXPLICITLY_NEOLIFE" or "neolife" in draft.casefold()
    links_levnytt = reasoning.get("possible_relevant_content") is not None
    could_be_commercial_recommendation = outcome == "POSSIBLE_VALUE_ADDING_LINK"

    if discusses_neolife or links_levnytt or could_be_commercial_recommendation:
        reasons = [
            reason for reason, present in (
                ("The response discusses NeoLife specifically.", discusses_neolife),
                ("The response identifies LevNytt content as a possible resource.", links_levnytt),
                ("The outcome could reasonably be read as a commercial recommendation.", could_be_commercial_recommendation),
            ) if present
        ]
        return {"disclosure_state": "DISCLOSURE_REQUIRED", "reasons": reasons, "existing_disclosure_text": _LEVNYTT_DISCLOSURE}

    if outcome == "ANSWER_WITHOUT_LINK":
        return {
            "disclosure_state": "NOT_REQUIRED",
            "reasons": ["The proposed response does not discuss NeoLife, does not link LevNytt content, and is not a commercial recommendation."],
        }
    return {"disclosure_state": "REQUIRES_REVIEW", "reasons": ["The commercial character of this specific response could not be confidently established."]}


def combine_engagement_recommendation(
    reasoning: dict[str, Any],
    policy: dict[str, Any],
    social: dict[str, Any],
    disclosure: dict[str, Any],
) -> dict[str, Any]:
    """Combine RELEVANCE/GROUNDING (Stage 2/3's existing outcome),
    PLATFORM POLICY, and SOCIAL APPROPRIATENESS into one recommendation.
    write_authorized is always False -- none of these outcomes may invoke
    an interactor. Enriches the existing Stage 2/3 outcome; never replaces
    it."""
    outcome = reasoning.get("outcome")

    if outcome == "NO_ACTION":
        recommendation = "DO_NOT_ENGAGE"
    elif outcome in {"OBSERVE", "INSUFFICIENT_CONTEXT"}:
        recommendation = "OBSERVE"
    else:
        policy_state = policy.get("overall_state")
        social_value = social.get("social_value")
        disclosure_state = disclosure.get("disclosure_state")

        # Fail closed first: a prohibited or unproven platform policy state
        # ends the decision here regardless of how favorable grounding or
        # social value are -- e.g. POSSIBLE_VALUE_ADDING_LINK + UNKNOWN must
        # never "magically become permission."
        if policy_state == "PROHIBITED":
            recommendation = "DO_NOT_ENGAGE"
        elif policy_state in {"UNKNOWN", "REQUIRES_REVIEW"}:
            recommendation = "REQUIRES_OWNER_REVIEW"
        elif social_value in {"LOW", None}:
            recommendation = "DRAFT_ONLY"
        elif outcome == "ANSWER_WITHOUT_LINK":
            # policy_state is PERMITTED or PERMITTED_WITHOUT_LINK here --
            # either way a link-free answer is allowed.
            recommendation = "POTENTIALLY_ENGAGE_WITHOUT_LINK" if social_value == "HIGH" else "DRAFT_ONLY"
        else:  # POSSIBLE_VALUE_ADDING_LINK
            if policy_state == "PERMITTED_WITHOUT_LINK":
                # Real evidence-grounded downgrade: the platform permits
                # discussion but explicitly prohibits the link itself.
                recommendation = "POTENTIALLY_ENGAGE_WITHOUT_LINK" if social_value == "HIGH" else "DRAFT_ONLY"
            elif policy_state == "PERMITTED" and disclosure_state == "DISCLOSURE_REQUIRED" and social_value == "HIGH":
                recommendation = "POTENTIALLY_ENGAGE_WITH_DISCLOSED_LINK"
            else:
                recommendation = "REQUIRES_OWNER_REVIEW"

    return {"engagement_recommendation": recommendation, "write_authorized": False}


def evaluate_engagement(
    item: dict[str, Any],
    fetch: dict[str, Any] | None,
    reasoning: dict[str, Any],
    runtime: Path,
    *,
    scrape=None,
) -> dict[str, Any]:
    """The complete Stage 4 decision packet for one candidate: existing
    Stage 2/3 reasoning, platform policy, social appropriateness,
    disclosure, and a final recommendation. Never authorizes a write --
    write_authorized is always False, structurally, regardless of input."""
    platform = str(reasoning.get("source_platform") or item.get("platform") or "")
    policy = platform_policy_state(platform, runtime, scrape=scrape)
    social = assess_social_appropriateness(fetch, reasoning)
    disclosure = assess_disclosure_requirement(reasoning)
    decision = combine_engagement_recommendation(reasoning, policy, social, disclosure)

    return {
        "source_platform": platform,
        "source_url": reasoning.get("source_url"),
        "thread_context_status": (fetch or {}).get("fetch_status", "NOT_FETCHED"),
        "relevance": reasoning.get("relevance"),
        "grounding_sufficiency": "GROUNDED" if reasoning.get("draft") else "INSUFFICIENT",
        "reasoning_outcome": reasoning.get("outcome"),
        "draft": reasoning.get("draft"),
        "possible_relevant_content": reasoning.get("possible_relevant_content"),
        "platform_policy": policy,
        "social_appropriateness": social,
        "disclosure": disclosure,
        "engagement_recommendation": decision["engagement_recommendation"],
        "write_authorized": decision["write_authorized"],
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }


def record_engagement_evaluations(runtime: Path, evaluations: list[dict[str, Any]]) -> None:
    """Persist Stage 4 decision packets for Commander visibility, bounded
    the same way every other list in this store is (most recent 20)."""
    if not evaluations:
        return
    store = load_community_store(runtime)
    existing = store.get("engagement_evaluations", [])
    if not isinstance(existing, list):
        existing = []
    existing.extend(evaluations)
    store["engagement_evaluations"] = existing[-20:]
    store["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_community_store(runtime, store)
