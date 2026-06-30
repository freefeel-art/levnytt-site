#!/usr/bin/env python3
"""
Editorial Sync Engine V1.0
Generates canonical editorial state from repository sources.
Always safe to run. Deterministic output. No external dependencies.
"""

import json
import os
import re
import time
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

OUTPUTS = {
    "production_status": REPO_ROOT / "docs/editorial-backlog/production-status.md",
    "repository_inventory": REPO_ROOT / "docs/reports/repository-inventory.md",
    "drift_detection": REPO_ROOT / "docs/reports/drift-detection.md",
    "publication_queue": REPO_ROOT / "docs/reports/publication-queue.md",
}

CANONICAL = {
    "root_html": REPO_ROOT,
    "source_articles": REPO_ROOT / "content/articles",
    "gap_reports": REPO_ROOT / "docs/editorial-backlog",
    "authority_research": REPO_ROOT / "docs/authority-research",
    "entities": REPO_ROOT / "content/products/entities",
    "price_db": REPO_ROOT / "docs/databank/LEVNYTT-PRICE-DATABASE.md",
    "brand_assets": REPO_ROOT / "assets/brand",
    "categories": REPO_ROOT / "content/products/categories.json",
}

EXCLUDED_ROOT_PAGES = {
    "index.html", "404.html", "integritetspolicy.html",
    "levnytt-se-master-template.html",
}

BRAND_ASSETS_REQUIRED = [
    "logo.svg", "logo-light.svg", "logo-dark.svg", "favicon.svg",
    "apple-touch-icon.png", "author-avatar.svg", "hero-watermark.svg",
    "og-brand.png",
]

AUTHORITY_TO_GAP_MAP = {
    "omega-3": ["omega-3"],
    "direct-selling": ["mlm", "direct-selling"],
    "direct-selling-associations": ["mlm", "direct-selling"],
    "network-marketing": ["mlm"],
    "pyramid-schemes": ["mlm"],
    "mlm-compensation-plans": ["mlm"],
    "income-disclosure-statements": ["mlm"],
    "ftc-mlm-regulation": ["mlm"],
    "eu-consumer-protection": ["mlm"],
    "swedish-consumer-protection": ["mlm"],
    "supplement-safety": ["kosttillskott"],
    "supplement-need-assessment": ["kosttillskott"],
}

# topic keywords → slug patterns for matching gap clusters to root pages
TOPIC_SLUG_MAP = {
    "multivitamin": "multivitamin",
    "magnesium": "magnesium",
    "probiotika": "probiotika",
    "vitamin d": "d-vitamin",
    "fiber": "fiber",
    "omega-3": "omega-3",
}


def get_git_commit():
    try:
        import subprocess
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=REPO_ROOT, timeout=5
        )
        return r.stdout.strip() if r.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def calculate_business_impact(cluster, published_slugs, entities):
    """
    Calculate Business Impact score (0-100) based on long-term strategic value.
    
    Factors:
    - Pillar/cornerstone content (25 points)
    - Search demand potential (20 points) 
    - Internal linking value (20 points)
    - Commercial relevance (15 points)
    - Evergreen value (10 points)
    - Product Entity coverage (10 points)
    
    Returns: (score, rating_stars)
    """
    score = 0
    topic = cluster["topic"].lower()
    gap_file = cluster.get("gap_file", "")
    priority = cluster.get("priority", "C")
    
    # 1. Pillar/Cornerstone Content (25 points)
    pillar_keywords = [
        "komplett guide", "evidensbaserad guide", "portal", "komplett",
        "allt du behöver veta", "kompletta guiden"
    ]
    if any(kw in topic for kw in pillar_keywords):
        score += 25
    elif topic.endswith("guide") or "guide" in topic:
        score += 20
    elif priority == "A":
        score += 15  # A-priority suggests cornerstone value
    elif priority == "B":
        score += 10
    else:  # Priority C
        score += 5
    
    # 2. Search Demand Potential (20 points)
    # Based on gap report type and cluster priority
    high_demand_topics = [
        "multivitamin", "magnesium", "probiotika", "vitamin d", "kostfiber",
        "omega-3", "kosttillskott"
    ]
    if any(keyword in topic for keyword in high_demand_topics):
        if priority == "A":
            score += 20
        elif priority == "B":
            score += 15
        else:
            score += 10
    else:
        if priority == "A":
            score += 15
        elif priority == "B":
            score += 10
        else:
            score += 5
    
    # 3. Internal Linking Value (20 points)
    # Portal articles and foundational content have high linking value
    if "portal" in gap_file or "global-batch" in gap_file:
        score += 20
    elif any(word in topic for word in ["komplett", "guide", "vad är", "behöver jag"]):
        score += 15
    elif priority == "A":
        score += 12
    else:
        score += 8
    
    # 4. Commercial Relevance (15 points)
    # How well does this support product sales or business model
    commercial_topics = [
        "kosttillskott", "neolife", "direktförsäljning", "mlm", 
        "behöver jag", "farligt", "säkerhet", "kvalitet", "bäst"
    ]
    if any(word in topic for word in commercial_topics):
        score += 15
    elif "mlm" in gap_file or "kosttillskott" in gap_file:
        score += 12
    else:
        score += 8
    
    # 5. Evergreen Value (10 points)
    # Scientific, educational, and regulatory content ages well
    evergreen_indicators = [
        "forskning", "vetenskap", "evidens", "vad är", "hur fungerar",
        "säkerhet", "risker", "kvalitet", "dosering"
    ]
    if any(indicator in topic for indicator in evergreen_indicators):
        score += 10
    elif priority in ["A", "B"]:
        score += 8
    else:
        score += 6
    
    # 6. Product Entity Coverage (10 points)
    # Articles that can support multiple product entities
    relevant_entities = 0
    entity_keywords = [
        "multivitamin", "magnesium", "probiotika", "vitamin", "omega",
        "fiber", "kosttillskott", "supplement"
    ]
    
    # Count how many product categories this article could support
    for keyword in entity_keywords:
        if keyword in topic:
            relevant_entities += 1
    
    if relevant_entities >= 3:
        score += 10
    elif relevant_entities >= 2:
        score += 8
    elif relevant_entities >= 1:
        score += 6
    else:
        score += 3
    
    # Ensure score is within bounds
    score = min(100, max(0, score))
    
    # Convert to star rating
    if score >= 90:
        rating = "★★★★★"
    elif score >= 75:
        rating = "★★★★☆"
    elif score >= 60:
        rating = "★★★☆☆"
    elif score >= 40:
        rating = "★★☆☆☆"
    else:
        rating = "★☆☆☆☆"
    
    return score, rating


def categorize_page(slug):
    if slug.startswith("neolife-"):
        return "product"
    if slug.endswith("-komplett-guide"):
        return "portal"
    if slug in {"om-oss", "neolife-vetenskap", "neolife-historia",
                 "neolife-affarsmojlighet", "den-fundersamma-mannen",
                 "var-metod", "levnytt-principer", "forsknings-faq",
                 "direktforsaljning-fakta", "hur-fungerar-natverksmarknadsforing-egentligen",
                 "golden-home-care", "personlig-vard", "neolife-hallbarhet",
                 "ekologisk-stadning-greenwashing"}:
        return "pillar"
    if slug in ("artiklar", "404", "index", "integritetspolicy", "levnytt-se-master-template"):
        return "utility"
    return "informational"


def parse_gap_clusters(filepath):
    text = filepath.read_text(encoding="utf-8")
    filename = filepath.name
    clusters = []
    lines = text.split("\n")
    i = 0
    n = len(lines)

    # Detect format: table-based (global-batch) vs heading-based (all others)
    table_format = "| Field | Value |" in text

    if table_format:
        return _parse_table_format(lines, filename)
    else:
        return _parse_heading_format(lines, filename)


def _parse_table_format(lines, filename):
    clusters = []
    current = None
    for line in lines:
        m = re.match(r"^###\s+(\d+)\.\s+(.+)", line)
        if m:
            if current and current.get("topic"):
                clusters.append(current)
            heading_topic = m.group(2).strip()
            current = {
                "cluster_num": int(m.group(1)),
                "topic": heading_topic,  # use full heading as topic initially
                "heading_topic": heading_topic,
                "priority": "C",
                "score": None,
                "recommendation": "",
                "gap_file": filename,
            }
        elif current and current.get("topic"):
            tm = re.match(r"^\|\s*Topic\s*\|\s*(.+?)\s*\|", line)
            if tm:
                # Keep heading_topic for matching, short tag is just metadata
                current["topic_tag"] = tm.group(1).strip()
            pm = re.match(r"^\|\s*Priority\s*\|\s*(.+?)\s*\|", line)
            if pm:
                current["priority"] = pm.group(1).strip()
            sm = re.match(r"^\|\s*Publication Score\s*\|\s*(\d+)", line)
            if sm:
                current["score"] = int(sm.group(1))
            rm = re.match(r"^\|\s*Recommendation\s*\|\s*(.+?)\s*\|", line)
            if rm:
                current["recommendation"] = rm.group(1).strip()
    if current and current.get("topic"):
        clusters.append(current)
    return clusters


def _parse_heading_format(lines, filename):
    clusters = []
    current = None
    in_cluster = False
    cluster_num = 0
    topic_lines = []
    inline_topic_mode = False

    for line in lines:
        cm = re.match(r"^## Cluster (\d+)(?::\s*(.+))?", line)
        if cm:
            if current:
                if not inline_topic_mode:
                    topic = _derive_topic(topic_lines, current)
                    if topic:
                        current["topic"] = topic
                clusters.append(current)
            cluster_num = int(cm.group(1))
            inline_topic = cm.group(2)
            inline_topic_mode = bool(inline_topic)
            current = {
                "cluster_num": cluster_num,
                "topic": inline_topic.strip() if inline_topic else "",
                "priority": "C",
                "score": None,
                "recommendation": "",
                "gap_file": filename,
            }
            in_cluster = True
            topic_lines = []
            if inline_topic_mode:
                continue

        if in_cluster and current:
            topic_lines.append(line)
            pm = re.match(r"^### Priority\s*$", line)
            if pm:
                # priority is on next non-empty line
                pass
            elif current.get("priority") == "C" and re.match(r"^[ABC]$", line.strip()):
                current["priority"] = line.strip()
            psm = re.match(r"^### Publication Score\s*$", line)
            if psm:
                current["_expecting_score"] = True
                continue
            if current.get("_expecting_score"):
                # next non-empty line should contain the score
                stripped_score = line.strip()
                if stripped_score:
                    scm = re.search(r"(\d+)\s*/\s*100", stripped_score)
                    if scm:
                        current["score"] = int(scm.group(1))
                    current["_expecting_score"] = False
                continue
            rm = re.match(r"^### Recommendation\s*$", line)
            if rm:
                current["_expecting_rec"] = True
                continue
            if current.pop("_expecting_rec", None):
                rec = line.strip().strip("*")
                if rec:
                    current["recommendation"] = rec
                continue

    if current:
        if not current.get("topic") or current["topic"].startswith("Cluster "):
            topic = _derive_topic(topic_lines, current)
            if topic:
                current["topic"] = topic
        clusters.append(current)

    return clusters


def _derive_topic(topic_lines, current):
    found_questions = False
    topic_candidates = []

    for i, line in enumerate(topic_lines):
        stripped = line.strip()

        # ### Sub-heading that could be the topic
        h3m = re.match(r"^###\s+(.+)", stripped)
        if h3m:
            h3_text = h3m.group(1).strip()
            if h3_text != "Questions" and not h3_text.startswith("Priority") \
               and not h3_text.startswith("Publication Score") \
               and not h3_text.startswith("Search") and not h3_text.startswith("Why") \
               and not h3_text.startswith("Existing") and not h3_text.startswith("Suggested") \
               and not h3_text.startswith("Strategic") and not h3_text.startswith("Recommended") \
               and not h3_text.startswith("Recommendation"):
                topic_candidates.append(h3_text)

        if stripped == "### Questions":
            found_questions = True
            break

    if topic_candidates:
        return topic_candidates[-1]  # the last H3 before Questions (usually the topic)

    if not found_questions:
        # Try first significant non-heading line
        for line in topic_lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("---"):
                return stripped

    if current.get("cluster_num"):
        return f"Cluster {current['cluster_num']}"
    return "Unknown"


def collect_published_pages():
    pages = []
    for f in sorted(CANONICAL["root_html"].glob("*.html")):
        slug = f.stem
        if slug in EXCLUDED_ROOT_PAGES:
            continue
        category = categorize_page(slug)
        pages.append({
            "slug": slug,
            "category": category,
            "path": str(f.relative_to(REPO_ROOT)),
        })
    return pages


def collect_source_articles():
    articles = []
    for f in sorted(CANONICAL["source_articles"].glob("*.html")):
        slug = f.stem
        articles.append({
            "slug": slug,
            "path": str(f.relative_to(REPO_ROOT)),
        })
    return articles


def collect_authority_research():
    files = []
    for f in sorted(CANONICAL["authority_research"].glob("*.md")):
        name = f.stem.replace("-authority-research", "")
        files.append({
            "filename": f.name,
            "stem": name,
            "path": str(f.relative_to(REPO_ROOT)),
        })
    return files


def collect_entities():
    entities = []
    for d in sorted(CANONICAL["entities"].iterdir()):
        jf = d / "sv.json"
        if jf.exists():
            with open(jf) as f:
                data = json.load(f)
            entities.append({
                "canonical_id": data.get("canonical_id", d.name),
                "name": data.get("name", {}).get("sv", ""),
                "category": data.get("category", "unknown"),
                "subcategory": data.get("subcategory", ""),
                "has_variants": bool(data.get("variants")),
                "status": data.get("status", "active"),
                "neolife_code": data.get("neoLife_code"),
                "path": str(jf.relative_to(REPO_ROOT)),
            })
    return entities


def slug_matches_topic_keywords(slug, topic):
    tl = topic.lower()
    sl = slug.lower().replace("-", " ")

    STOP_WORDS = {"komplett", "guide", "och", "för", "mot", "hur", "vad", "är",
                   "en", "ett", "det", "som", "att", "till", "med", "den",
                   "hjälper", "varför", "behöver", "från", "bästa", "mycket",
                   "skillnad", "samband", "egentligen", "funktion", "riktigt",
                   "sverige", "världen"}

    # 1. Exact slug-in-topic check
    if slug.replace("-", " ") in tl or slug in tl:
        return True

    # 2. Multi-word topic matching — prioritize portal guides for main topics
    topic_guide_map = {
        "multivitamin": "multivitamin-komplett-guide",
        "magnesium": "magnesium-komplett-guide",
        "probiotika": "probiotika-komplett-guide",
        "vitamin d": "d-vitamin",
        "fiber": "kostfiber-komplett-guide",
        "kostfiber": "kostfiber-komplett-guide",
    }
    for word, expected_slug in topic_guide_map.items():
        if word in tl:
            if expected_slug in slug:
                return True
            if word in sl:
                return True

    # 3. Specific multi-word match for MLM/direct-sales pages
    mlm_slug_map = {
        "direktforsaljning-fakta": ["direktförsäljning fakta", "direktförsäljning"],
        "hur-fungerar-natverksmarknadsforing-egentligen": ["nätverksmarknadsföring", "fungerar"],
        "neolife-affarsmojlighet": ["neolife", "affärsmöjlighet"],
    }
    for mlm_slug, keywords in mlm_slug_map.items():
        if slug == mlm_slug:
            for kw in keywords:
                if kw in tl:
                    # Only match if the keyword is a significant multi-char word
                    # in a non-MLM-generic context
                    if kw in tl.split():
                        return True

    # 4. Significant-word matching (must be specific to topic, not generic)
    topic_words = set()
    for word in tl.split():
        w = word.strip("-,.()")
        if len(w) > 3 and w not in STOP_WORDS:
            topic_words.add(w)

    slug_words = set(sl.split())

    # Require at least one significant topic word that appears in the slug
    matched_words = topic_words & slug_words
    if matched_words:
        return True

    return False


def compute_published_slug_set(published_pages):
    return {p["slug"] for p in published_pages}


def compute_source_slug_set(source_articles):
    return {a["slug"] for a in source_articles}


def match_cluster_to_published(cluster, published_slugs):
    topic = cluster["topic"]
    for slug in published_slugs:
        if slug_matches_topic_keywords(slug, topic):
            return slug
    return None


def match_cluster_to_source(cluster, source_slugs):
    topic = cluster["topic"]
    for slug in source_slugs:
        if slug_matches_topic_keywords(slug, topic):
            return slug
    return None


def find_authority_for_cluster(cluster, authority_files):
    topic = cluster["topic"].lower()
    gap_file = cluster["gap_file"].replace("-gap.md", "").replace("docs/editorial-backlog/", "")

    for af in authority_files:
        # match by gap report name
        mapped_gaps = AUTHORITY_TO_GAP_MAP.get(af["stem"], [])
        if gap_file in mapped_gaps:
            return af
        # match by keyword in topic
        for kw in mapped_gaps:
            if kw in topic:
                return af
    return None


def classify_cluster(cluster, published_slugs, source_slugs):
    rec = cluster["recommendation"].lower().strip()
    if rec == "skip":
        return "Skipped", None, None

    pub_slug = match_cluster_to_published(cluster, published_slugs)
    src_slug = match_cluster_to_source(cluster, source_slugs)

    if pub_slug:
        return "Published", pub_slug, None
    if src_slug:
        return "Generated", None, src_slug
    if "update existing" in rec or "update" in rec:
        return "Update Existing", None, None
    return "New Article", None, None


def main():
    t0 = time.time()

    published = collect_published_pages()
    source_articles = collect_source_articles()
    authority_files = collect_authority_research()
    entities = collect_entities()

    published_slugs = compute_published_slug_set(published)
    source_slugs = compute_source_slug_set(source_articles)

    # Parse gap reports
    gap_files = sorted(CANONICAL["gap_reports"].glob("*-gap.md"))
    all_clusters = []
    gap_report_summary = {}

    for gf in gap_files:
        clusters = parse_gap_clusters(gf)
        all_clusters.extend(clusters)

        report_name = gf.stem
        total = len(clusters)
        published_count = 0
        generated_count = 0
        new_count = 0
        update_count = 0
        skipped_count = 0

        for c in clusters:
            status, _, _ = classify_cluster(c, published_slugs, source_slugs)
            if status == "Published":
                published_count += 1
            elif status == "Generated":
                generated_count += 1
            elif status == "Update Existing":
                update_count += 1
            elif status == "Skipped":
                skipped_count += 1
            else:
                new_count += 1

        gap_report_summary[report_name] = {
            "total": total,
            "published": published_count,
            "generated": generated_count,
            "new": new_count,
            "update_existing": update_count,
            "skipped": skipped_count,
        }

    # Compute production status for each cluster
    production_rows = []
    for idx, cluster in enumerate(all_clusters, 1):
        status, pub_slug, src_slug = classify_cluster(
            cluster, published_slugs, source_slugs
        )
        auth = find_authority_for_cluster(cluster, authority_files)
        authority_status = "CLEARED" if auth else "BLOCKED"
        authority_file = auth["filename"] if auth else "—"
        
        # Calculate Business Impact
        business_impact, business_rating = calculate_business_impact(
            cluster, published_slugs, entities
        )

        file_field = ""
        if status == "Published" and pub_slug:
            file_field = f"{pub_slug}.html"
        elif status == "Generated" and src_slug:
            file_field = f"{src_slug}.html"
        elif status == "Update Existing":
            # find if we have any existing page matching this topic
            existing = match_cluster_to_published(cluster, published_slugs)
            if existing:
                file_field = f"{existing}.html"
            else:
                file_field = "—"

        gap_file_short = cluster["gap_file"].replace("-gap.md", "")

        production_rows.append({
            "num": idx,
            "cluster": cluster["topic"],
            "gap_report": gap_file_short,
            "gap_filename": cluster["gap_file"],
            "cluster_num": cluster["cluster_num"],
            "priority": cluster["priority"],
            "score": cluster["score"],
            "business_impact": business_impact,
            "business_rating": business_rating,
            "status": status,
            "file": file_field,
            "authority": authority_status,
            "authority_file": authority_file,
            "recommendation": cluster["recommendation"],
        })

    # Publication queue
    ready_to_write = []
    blocked = []
    ready_to_publish = []
    update_existing = []

    for row in production_rows:
        if row["status"] == "Skipped":
            continue
        if row["status"] == "Published":
            continue

        entry = {
            "topic": row["cluster"],
            "priority": row["priority"],
            "score": row["score"],
            "business_impact": row["business_impact"],
            "business_rating": row["business_rating"],
            "gap_report": row["gap_report"],
            "authority": row["authority"],
            "authority_file": row["authority_file"],
        }

        if row["status"] == "Generated":
            ready_to_publish.append(entry)
        elif row["status"] == "Update Existing":
            update_existing.append(entry)
        elif row["authority"] == "CLEARED":
            ready_to_write.append(entry)
        else:
            blocked.append(entry)

    def sort_key(e):
        pri = {"A": 0, "B": 1, "C": 2}.get(e["priority"], 3)
        bi = -(e["business_impact"] or 0)  # Business Impact descending
        sc = -(e["score"] or 0)  # Original score descending
        return (pri, bi, sc)

    ready_to_write.sort(key=sort_key)
    blocked.sort(key=sort_key)
    ready_to_publish.sort(key=lambda e: -(e["business_impact"] or 0))
    update_existing.sort(key=lambda e: (
        {"A": 0, "B": 1, "C": 2}.get(e["priority"], 3),
        -(e["business_impact"] or 0),
        -(e["score"] or 0)
    ))

    # Drift detection
    drifts = []
    undocumented_pages = []
    stale_clusters = []

    # Undocumented pages — only flag informational pages, not products/pillars/utilities
    for p in published:
        if p["category"] in ("product", "pillar", "landing", "utility"):
            continue
        found = False
        for cluster in all_clusters:
            if slug_matches_topic_keywords(p["slug"], cluster["topic"]):
                found = True
                break
        if not found:
            undocumented_pages.append(p["slug"])
            drifts.append({
                "type": "Undocumented page",
                "detail": f"Root page `{p['slug']}.html` has no matching gap report cluster.",
                "severity": "AMBER",
            })

    # Stale clusters — but exclude global-batch (86 the exhausted backlog)
    for row in production_rows:
        if row["status"] == "Published" and row["recommendation"].lower() == "write now":
            if row["gap_filename"] == "global-batch-2026-06-29-gap.md":
                continue  # exhausted backlog, not stale
            stale_clusters.append(row)
            drifts.append({
                "type": "Stale gap cluster",
                "detail": (f"`{row['gap_filename']}` Cluster {row['cluster_num']} "
                           f"recommends 'Write now' but `{row['file']}` already published."),
                "severity": "AMBER",
            })

    # Source article → no gap report (skip published duplicates)
    for a in source_articles:
        if a["slug"] in published_slugs:
            continue
        found = False
        for cluster in all_clusters:
            if slug_matches_topic_keywords(a["slug"], cluster["topic"]):
                found = True
                break
        if not found:
            drifts.append({
                "type": "Orphan source article",
                "detail": f"`{a['path']}` has no matching gap report cluster.",
                "severity": "AMBER",
            })

    # Authority CLEARED but not in production queue (no gap report cluster)
    authority_mapped_topics = set()
    for cluster in all_clusters:
        for af in authority_files:
            mapped = AUTHORITY_TO_GAP_MAP.get(af["stem"], [])
            gap_file = cluster["gap_file"].replace("-gap.md", "")
            if gap_file in mapped:
                authority_mapped_topics.add(af["stem"])

    for af in authority_files:
        if af["stem"] not in authority_mapped_topics:
            drifts.append({
                "type": "Unused authority research",
                "detail": (f"`{af['filename']}` exists but no gap report cluster references "
                           f"it. Consider creating a gap report or linking it."),
                "severity": "GREEN",
            })

    # Gap report → stale authority status
    for cluster in all_clusters:
        auth = find_authority_for_cluster(cluster, authority_files)
        if auth:
            # check if any production row for this cluster shows it as blocked
            matching_rows = [r for r in production_rows
                             if r["cluster"] == cluster["topic"]
                             and r["gap_report"] == cluster["gap_file"].replace("-gap.md", "")]
            for r in matching_rows:
                if r["authority"] == "CLEARED" and r["status"] == "New Article":
                    pass  # this is the desired state - no drift

    # Brand assets
    missing_brand = []
    for asset in BRAND_ASSETS_REQUIRED:
        if not (CANONICAL["brand_assets"] / asset).exists():
            missing_brand.append(asset)
    if missing_brand:
        drifts.append({
            "type": "Missing brand assets",
            "detail": f"Missing from assets/brand/: {', '.join(missing_brand)}",
            "severity": "RED",
        })

    # Repository health
    health = "GREEN"
    for d in drifts:
        if d["severity"] == "RED":
            health = "RED"
            break
        if d["severity"] == "AMBER":
            health = "AMBER"

    commit = get_git_commit()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today = date.today().isoformat()

    # Entity stats
    entity_categories = {}
    entity_with_product_pages = 0
    entity_without = 0
    entity_with_variants = 0
    entity_inactive = 0

    for e in entities:
        cat = e["category"]
        entity_categories[cat] = entity_categories.get(cat, 0) + 1
        has_page = any(
            p["slug"] == f"neolife-{e['canonical_id'].replace('entity_', '')}"
            for p in published
        )
        if has_page:
            entity_with_product_pages += 1
        else:
            entity_without += 1
        if e["has_variants"]:
            entity_with_variants += 1
        if e["status"] != "active":
            entity_inactive += 1

    # Published page category counts
    cat_counts = {}
    for p in published:
        cat_counts[p["category"]] = cat_counts.get(p["category"], 0) + 1

    # Source article stats
    source_published_dupes = sum(
        1 for a in source_articles if a["slug"] in published_slugs
    )
    source_unique = len(source_articles) - source_published_dupes
    source_orphans = sum(
        1 for a in source_articles if not any(
            slug_matches_topic_keywords(a["slug"], c["topic"])
            for c in all_clusters
        )
    )

    # Published by gap report
    published_by_gap = {}
    for row in production_rows:
        if row["status"] == "Published":
            gr = row["gap_report"]
            published_by_gap[gr] = published_by_gap.get(gr, 0) + 1

    # ================================================================
    # WRITE OUTPUT FILES
    # ================================================================

    # 1. production-status.md
    lines = [
        "# Production Status — Auto-Generated",
        "",
        f"**Generated:** {now}",
        f"**Commit:** {commit}",
        f"**Source:** Editorial Sync Engine V1.0",
        "",
        "> AUTO-GENERATED — DO NOT EDIT. Run `python3 scripts/sync-editorial-state.py` to regenerate.",
        "",
        "## Full Backlog",
        "",
        "| # | Cluster | Gap Report | Priority | Score | Business Impact | Status | File | Authority |",
        "|---|---------|------------|----------|-------|----------------|--------|------|-----------|",
    ]

    for row in production_rows:
        if row["status"] == "Skipped":
            continue
        score_str = str(row["score"]) if row["score"] else "—"
        business_impact_str = f"{row['business_impact']} {row['business_rating']}"
        status_emoji = {
            "Published": "Published",
            "Generated": "Generated",
            "New Article": "**New Article**",
            "Update Existing": "Update Existing",
        }.get(row["status"], row["status"])

        lines.append(
            f"| {row['num']} | {row['cluster']} | {row['gap_report']} | "
            f"{row['priority']} | {score_str} | {business_impact_str} | {status_emoji} | "
            f"{row['file']} | {row['authority']} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Production Status Summary",
        "",
        f"**Total clusters tracked:** {len(production_rows)}",
        f"**Published:** {sum(1 for r in production_rows if r['status'] == 'Published')}",
        f"**Generated (source ready):** {sum(1 for r in production_rows if r['status'] == 'Generated')}",
        f"**New Article (unwritten):** {sum(1 for r in production_rows if r['status'] == 'New Article')}",
        f"**Update Existing:** {sum(1 for r in production_rows if r['status'] == 'Update Existing')}",
        f"**Skipped:** {sum(1 for r in production_rows if r['status'] == 'Skipped')}",
        "",
        f"**Authority CLEARED:** {sum(1 for r in production_rows if r['authority'] == 'CLEARED' and r['status'] not in ('Published', 'Skipped'))}",
        f"**Authority BLOCKED:** {sum(1 for r in production_rows if r['authority'] == 'BLOCKED' and r['status'] not in ('Published', 'Skipped'))}",
    ])

    OUTPUTS["production_status"].parent.mkdir(parents=True, exist_ok=True)
    OUTPUTS["production_status"].write_text("\n".join(lines) + "\n", encoding="utf-8")

    # 2. repository-inventory.md
    lines = [
        "# Repository Inventory — Auto-Generated",
        "",
        f"**Generated:** {now}",
        f"**Commit:** {commit}",
        "",
        "> AUTO-GENERATED — DO NOT EDIT. Run `python3 scripts/sync-editorial-state.py` to regenerate.",
        "",
        "## Published Pages",
        "",
        f"**Total:** {len(published)}",
        "",
        "### By Category",
    ]
    for cat in ["product", "pillar", "informational", "portal", "landing", "utility"]:
        count = cat_counts.get(cat, 0)
        if count:
            lines.append(f"- **{cat.capitalize()}:** {count}")
    lines.append("")
    lines.append("### By Source Gap Report")
    for gr, cnt in sorted(published_by_gap.items()):
        lines.append(f"- **{gr}:** {cnt}")
    lines.append(f"- **Undocumented (no gap report):** {len(undocumented_pages)}")
    if undocumented_pages:
        lines.append("")
        for slug in sorted(undocumented_pages):
            lines.append(f"  - `{slug}.html`")

    lines.extend([
        "",
        "## Source Articles",
        "",
        f"**Total:** {len(source_articles)}",
        f"**Published duplicates (root exists):** {source_published_dupes}",
        f"**Unique source-only (rewrite):** {source_unique}",
        f"**Orphan (no gap report):** {source_orphans}",
        "",
        "## Product Entities",
        "",
        f"**Total:** {len(entities)}",
        f"**With product pages:** {entity_with_product_pages}",
        f"**Without product pages:** {entity_without}",
        f"**With variants:** {entity_with_variants}",
        f"**Inactive:** {entity_inactive}",
        "",
    ])
    for cat, cnt in sorted(entity_categories.items()):
        lines.append(f"- **{cat}:** {cnt}")

    lines.extend([
        "",
        "## Authority Research",
        "",
        f"**Total files:** {len(authority_files)}",
        f"**Total topic domains:** {len(set(a['stem'] for a in authority_files))}",
        "",
        "### Coverage by Gap Report",
    ])
    for gr_name, gr_data in sorted(gap_report_summary.items()):
        # count authority files mapped to this gap report
        gap_short = gr_name.replace("-gap", "")
        auth_count = sum(
            1 for a in authority_files
            if gap_short in AUTHORITY_TO_GAP_MAP.get(a["stem"], [])
        )
        lines.append(f"- **{gr_name}:** {auth_count} research files")

    lines.extend([
        "",
        "### Per-Cluster Authority Status",
        "",
        f"- **CLEARED:** {sum(1 for r in production_rows if r['authority'] == 'CLEARED')} clusters",
        f"- **BLOCKED:** {sum(1 for r in production_rows if r['authority'] == 'BLOCKED')} clusters",
        "",
        "## Gap Reports",
        "",
        f"**Total gap reports:** {len(gap_files)}",
        "",
        "| Report | Total | Published | Generated | New | Update | Skipped |",
        "|--------|-------|-----------|-----------|-----|--------|---------|",
    ])
    for gr_name, gr_data in sorted(gap_report_summary.items()):
        lines.append(
            f"| {gr_name} | {gr_data['total']} | {gr_data['published']} | "
            f"{gr_data['generated']} | {gr_data['new']} | "
            f"{gr_data['update_existing']} | {gr_data['skipped']} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Repository Health",
        "",
        f"**Overall:** {health}",
    ])
    if drifts:
        lines.append("")
        for d in drifts:
            lines.append(f"- **[**{d['severity']}**]** {d['detail']}")
    else:
        lines.append("- No drifts detected.")

    OUTPUTS["repository_inventory"].parent.mkdir(parents=True, exist_ok=True)
    OUTPUTS["repository_inventory"].write_text("\n".join(lines) + "\n", encoding="utf-8")

    # 3. drift-detection.md
    lines = [
        "# Drift Detection — Auto-Generated",
        "",
        f"**Generated:** {now}",
        f"**Commit:** {commit}",
        "",
        "> AUTO-GENERATED — DO NOT EDIT. Run `python3 scripts/sync-editorial-state.py` to regenerate.",
        "",
        f"**Drifts found:** {len(drifts)}",
        "",
    ]
    if drifts:
        lines.append("| Type | Detail | Severity |")
        lines.append("|------|--------|----------|")
        for d in drifts:
            lines.append(f"| {d['type']} | {d['detail']} | **{d['severity']}** |")
    else:
        lines.append("No drifts detected. Repository state is consistent.")

    OUTPUTS["drift_detection"].parent.mkdir(parents=True, exist_ok=True)
    OUTPUTS["drift_detection"].write_text("\n".join(lines) + "\n", encoding="utf-8")

    # 4. publication-queue.md
    lines = [
        "# Publication Queue — Auto-Generated",
        "",
        f"**Generated:** {now}",
        f"**Commit:** {commit}",
        "",
        "> AUTO-GENERATED — DO NOT EDIT. Run `python3 scripts/sync-editorial-state.py` to regenerate.",
        "",
        "## Ready to Write (Authority CLEARED)",
        "",
    ]
    if ready_to_write:
        lines.append("| Rank | Topic | Priority | Score | Business Impact | Gap Report | Authority File |")
        lines.append("|------|-------|----------|-------|----------------|------------|----------------|")
        for i, item in enumerate(ready_to_write, 1):
            sc = str(item["score"]) if item["score"] else "—"
            bi = f"{item['business_impact']} {item['business_rating']}"
            lines.append(
                f"| {i} | {item['topic']} | {item['priority']} | {sc} | {bi} | "
                f"{item['gap_report']} | {item['authority_file']} |"
            )
    else:
        lines.append("*No items.*")
    lines.append("")
    lines.append("## Blocked (Needs Authority Research)")
    lines.append("")
    if blocked:
        lines.append("| Rank | Topic | Priority | Score | Business Impact | Gap Report |")
        lines.append("|------|-------|----------|-------|----------------|------------|")
        for i, item in enumerate(blocked, 1):
            sc = str(item["score"]) if item["score"] else "—"
            bi = f"{item['business_impact']} {item['business_rating']}"
            lines.append(
                f"| {i} | {item['topic']} | {item['priority']} | {sc} | {bi} | {item['gap_report']} |"
            )
    else:
        lines.append("*No items.*")
    lines.append("")
    lines.append("## Ready to Publish (Source File Exists)")
    lines.append("")
    if ready_to_publish:
        lines.append("| Rank | Topic | Score | Business Impact | Gap Report |")
        lines.append("|------|-------|-------|----------------|------------|")
        for i, item in enumerate(ready_to_publish, 1):
            sc = str(item["score"]) if item["score"] else "—"
            bi = f"{item['business_impact']} {item['business_rating']}"
            lines.append(
                f"| {i} | {item['topic']} | {sc} | {bi} | {item['gap_report']} |"
            )
    else:
        lines.append("*No items.*")
    lines.append("")
    lines.append("## Update Existing")
    lines.append("")
    if update_existing:
        lines.append("| Rank | Topic | Priority | Business Impact | Gap Report |")
        lines.append("|------|-------|----------|----------------|------------|")
        for i, item in enumerate(update_existing, 1):
            bi = f"{item['business_impact']} {item['business_rating']}"
            lines.append(
                f"| {i} | {item['topic']} | {item['priority']} | {bi} | {item['gap_report']} |"
            )
    else:
        lines.append("*No items.*")

    OUTPUTS["publication_queue"].parent.mkdir(parents=True, exist_ok=True)
    OUTPUTS["publication_queue"].write_text("\n".join(lines) + "\n", encoding="utf-8")

    elapsed = time.time() - t0

    # Print summary to terminal
    print(f"✅ Editorial Sync Engine V1.0 — {now}")
    print(f"   Commit: {commit}")
    print(f"   Duration: {elapsed:.2f}s")
    print(f"   Health: {health}")
    print(f"")
    print(f"📊 Published pages: {len(published)}")
    print(f"📄 Source articles: {len(source_articles)} ({source_unique} unique)")
    print(f"🔬 Authority research: {len(authority_files)} files")
    print(f"📦 Product entities: {len(entities)}")
    print(f"📋 Gap report clusters: {len(all_clusters)}")
    print(f"")
    print(f"📋 Production status: {OUTPUTS['production_status']}")
    print(f"📋 Repository inventory: {OUTPUTS['repository_inventory']}")
    print(f"📋 Drift detection: {OUTPUTS['drift_detection']}")
    print(f"📋 Publication queue: {OUTPUTS['publication_queue']}")
    print(f"")
    print(f"🚨 Drifts: {len(drifts)}")
    for d in drifts:
        print(f"   [{d['severity']}] {d['type']}: {d['detail']}")
    print(f"")
    print(f"✍️  Ready to write: {len(ready_to_write)}")
    for item in ready_to_write:
        print(f"   - {item['topic']} ({item['priority']}, {item['score'] or '—'})")
    print(f"🔒 Blocked: {len(blocked)}")
    print(f"📤 Ready to publish: {len(ready_to_publish)}")


if __name__ == "__main__":
    main()
