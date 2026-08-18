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
_BUSINESS_DISTRIBUTOR_MARKERS = (
    "återförsäljare", "aterforsaljare", "distributör", "distributor", "tjäna pengar",
    "tjana pengar", "inkomst", "sponsor", "registrera", "registrera sig",
    "affärsmöjlighet", "affarsmojlighet", "sälja", "salja", "pyramidspel", "mlm",
)
_CONSUMER_DECISION_MARKERS = (
    "värt", "vart", "billigare", "pris", "kostar", "vilket ska jag", "jämför",
    "jamfor", "köpa", "kopa", "rekommendera", "värt det", "vart det",
)
_CONTENT_QUESTION_MARKERS = (
    "guide", "artikel", "var kan jag läsa", "har ni skrivit", "länk", "lank",
    "var hittar jag",
)


def classify_levnytt_signal(text: str) -> dict[str, Any]:
    """Classify one observed Facebook text into the NeoLife consumer taxonomy.

    Returns matched categories and a primary category. Text matching nothing is
    UNKNOWN (not actionable). A user statement is USER_CLAIM, never verified fact.
    """
    stripped = (text or "").strip()
    if not stripped:
        return {"signal_types": [], "primary_signal_type": "UNKNOWN", "is_actionable": False, "matched_markers": []}

    lowered = stripped.casefold()
    matched: list[str] = []
    markers: list[str] = []
    for category, marker_list in (
        ("BUSINESS_DISTRIBUTOR", _BUSINESS_DISTRIBUTOR_MARKERS),
        ("PRODUCT", _PRODUCT_MARKERS),
        ("SCIENCE_HEALTH", _SCIENCE_HEALTH_MARKERS),
        ("CONSUMER_DECISION", _CONSUMER_DECISION_MARKERS),
        ("CONTENT_QUESTION", _CONTENT_QUESTION_MARKERS),
    ):
        hits = [m for m in marker_list if m in lowered]
        if hits:
            matched.append(category)
            markers.extend(hits)

    if not matched:
        return {"signal_types": [], "primary_signal_type": "UNKNOWN", "is_actionable": False, "matched_markers": []}

    # A direct question is always actionable; otherwise only substantive matches are.
    is_question = "?" in stripped or lowered.startswith(("vad", "hur", "varför", "vilken", "vilket", "är", "hjälper", "kan"))
    return {
        "signal_types": matched,
        "primary_signal_type": matched[0],
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


def levnytt_grounding_facts(topic: str, runtime: Path) -> list[dict[str, Any]]:
    """Return sourced factual claims from a LevNytt research packet for a topic,
    each with source provenance. Falls back to token-overlap matching across all
    research packets when the exact slug has no packet. Never synthesizes facts."""
    slug = _slugify(topic)
    packet = _read_json(runtime / "intelligence" / f"research-{slug}.json")
    if not packet.get("claims"):
        topic_tokens = _tokens(topic)
        best_packet: dict[str, Any] = {}
        best_overlap = 0
        for path in sorted((runtime / "intelligence").glob("research-*.json")):
            candidate = _read_json(path)
            candidate_tokens = _tokens(str(candidate.get("topic", "")))
            overlap = len(topic_tokens & candidate_tokens)
            if overlap > best_overlap:
                best_overlap = overlap
                best_packet = candidate
        if best_overlap > 0:
            packet = best_packet
    claims = packet.get("claims", []) if isinstance(packet.get("claims"), list) else []
    facts: list[dict[str, Any]] = []
    for c in claims:
        if not isinstance(c, dict):
            continue
        claim = str(c.get("claim", "")).strip()
        if not claim:
            continue
        facts.append({
            "evidence_id": str(c.get("evidence_id", f"levnytt-{slug}")),
            "claim": claim,
            "source": str(c.get("source_title") or c.get("source_reference") or ""),
            "source_type": str(c.get("source_type", "")),
            "source_url": str(c.get("source_url", "")),
        })
    return facts


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
        "grounding_source": str(fact.get("source", "")),
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


def record_signals(runtime: Path, signals: list[dict[str, Any]]) -> None:
    """Append newly observed signals to the project-scoped store, deduped by
    observed text so a handled comment is not re-processed every run."""
    store = load_community_store(runtime)
    existing = store.get("signals", [])
    if not isinstance(existing, list):
        existing = []
    seen_texts = {str(s.get("text", "")) for s in existing if isinstance(s, dict)}
    for signal in signals:
        if not isinstance(signal, dict):
            continue
        text = str(signal.get("text", ""))
        if not text or text in seen_texts:
            continue
        signal["recorded_at"] = datetime.now(timezone.utc).isoformat()
        existing.append(signal)
        seen_texts.add(text)
    store["signals"] = existing
    store["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_community_store(runtime, store)


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


def record_research_gaps(runtime: Path, gaps: list[str]) -> None:
    store = load_community_store(runtime)
    existing = store.get("research_gaps", [])
    if not isinstance(existing, list):
        existing = []
    for gap in gaps:
        if gap not in existing:
            existing.append(gap)
    store["research_gaps"] = existing
    save_community_store(runtime, store)


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

    domain_hits = sorted({m.group(0) for m in _NAMED_DOMAIN_PATTERN.finditer(lowered)})
    other_domains = [d for d in domain_hits if not any(d == own or d.endswith("." + own) for own in _LEVNYTT_OWN_DOMAINS)]
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
    matched against actual on-disk HTML files (the same kind of matching
    levnytt_grounding_facts already uses for research packets), never a
    fabricated URL."""
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


def reason_about_discovery_candidate(item: dict[str, Any], runtime: Path, working_repository: Path) -> dict[str, Any]:
    """READ (one already-persisted, already real discovery item) -> REASON
    -> DRAFT where evidence justifies it. Returns a full evidence record for
    Commander -- never constructs or authorizes a write; community_engagement
    (owned-page only) is a wholly separate path this never reaches.

    Outcome is always exactly one of: NO_ACTION, OBSERVE, ANSWER_WITHOUT_LINK,
    POSSIBLE_VALUE_ADDING_LINK, INSUFFICIENT_CONTEXT. None of these
    authorizes execution -- they are reasoning results only.
    """
    url = str(item.get("url", ""))
    title = str(item.get("title", "")).strip()
    snippet = str(item.get("snippet", "")).strip()
    text = f"{title} {snippet}".strip()

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
    # Facts and search-demand evidence are never treated as claim evidence
    # here: GSC_DEMAND/COMMUNITY_DEMAND prove a question exists, not that
    # any claim about it is true (see levnytt_grounding_facts, which only
    # ever returns sourced AUTHORITY/GENERAL_SCIENCE/NEOLIFE_FIRST_PARTY
    # claims from real research packets).
    facts = levnytt_grounding_facts(topic, runtime) if topic else []
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


def recurring_questions(runtime: Path, limit: int = 10) -> list[dict[str, Any]]:
    """Recurring consumer questions recorded as audience-demand evidence for the
    SEO/content opportunity loop. A question is 'recurring' when its observed
    text appears more than once."""
    store = load_community_store(runtime)
    signals = store.get("signals", []) if isinstance(store.get("signals"), list) else []
    counts: dict[str, int] = {}
    for s in signals:
        if not isinstance(s, dict):
            continue
        text = str(s.get("text", "")).strip()
        if text and s.get("classification", {}).get("is_actionable") if isinstance(s.get("classification"), dict) else False:
            counts[text] = counts.get(text, 0) + 1
    return [{"question": t, "count": c} for t, c in sorted(counts.items(), key=lambda kv: -kv[1]) if c >= 1][:limit]
