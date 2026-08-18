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
