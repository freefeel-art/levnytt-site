#!/usr/bin/env python3
"""
Fix internal recommendation links in existing articles.

Adds target="_blank" rel="noopener noreferrer" to links inside:
- ia-related blocks (Fortsätt läsa)
- journey-block / journey-card grids
- cta-block CTA buttons
- callout boxes containing "Relaterade sidor"
- Paragraphs containing "Relaterad läsning:"
- Paragraphs/divs containing "Läs vidare:"
- related-section / related-card

Does NOT modify inline contextual links in body prose.
"""

import glob
import os
import re
import sys

ARTICLES_DIR = "content/articles"

# ── Balancing div matcher ──────────────────────────────────────────

def balanced_div_end(html: str, start: int) -> int:
    """
    Find the position of the closing </div> that matches the <div> at `start`.
    Handles nested divs by counting depth.
    Returns position right after the matching </div>.
    """
    depth = 0
    i = start
    while i < len(html):
        # Check for opening <div (but not </div)
        dm = re.match(r'<div\b', html[i:])
        if dm:
            depth += 1
            i += dm.end()
            continue
        # Check for closing </div>
        cm = re.match(r'</div>', html[i:])
        if cm:
            depth -= 1
            i += cm.end()
            if depth == 0:
                return i
            continue
        i += 1
    return len(html)


def extract_container(html: str, open_tag_pattern: str) -> list[tuple[int, int]]:
    """Find all containers matching the open tag pattern and return (start, end) spans."""
    spans = []
    for m in re.finditer(open_tag_pattern, html):
        start = m.start()
        end = balanced_div_end(html, start)
        spans.append((start, end))
    return spans


# ── Link fixing ────────────────────────────────────────────────────

def add_target_to_internal_links(html: str) -> str:
    """Add target/_blank/rel to internal <a> tags that don't already have target."""

    def fix_link(m):
        pre = m.group(1)   # anything before href
        href = m.group(2)
        after = m.group(3) # anything after href before >
        content = m.group(4)

        # Skip if already has target
        if 'target=' in pre or 'target=' in after:
            return m.group(0)

        # Only fix internal links
        if not (href.startswith('/') or href.startswith('https://levnytt.se') or href.startswith('https://www.levnytt.se')):
            return m.group(0)

        # Build replacement with attrs inserted before >
        attrs = pre + after
        if attrs.strip():
            new_attrs = f'{attrs} target="_blank" rel="noopener noreferrer"'
        else:
            new_attrs = f'target="_blank" rel="noopener noreferrer"'

        return f'<a {new_attrs} href="{href}">{content}</a>'

    return re.sub(
        r'<a\s*((?:[^>]*\s+)?)href="([^"]*)"((?:\s+[^>]*)?)\s*>(.*?)</a>',
        fix_link,
        html,
        flags=re.DOTALL,
    )


def fix_file(filepath: str) -> bool:
    """Apply all recommendation link fixes to a file. Returns True if modified."""
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    original = html
    name = os.path.basename(filepath)
    changes = []

    # Patterns to find: (label, open_tag_regex)
    patterns = [
        ("ia-related", r'<div[^>]*class="[^"]*ia-related[^"]*"[^>]*>'),
        ("journey-block", r'<div[^>]*class="[^"]*journey-block[^"]*"[^>]*>'),
        ("cta-block", r'<div[^>]*class="[^"]*cta-block[^"]*"[^>]*>'),
        ("callout (Relaterade sidor)", r'<div[^>]*class="[^"]*callout[^"]*"[^>]*>'),
        ("related-section", r'<div[^>]*class="[^"]*related-section[^"]*"[^>]*>'),
    ]

    for label, pat in patterns:
        spans = extract_container(html, pat)
        # For callout, further filter to only those containing "Relaterade sidor"
        if label == "callout (Relaterade sidor)":
            spans = [(s, e) for s, e in spans if "Relaterade sidor" in html[s:e]]
        # Process spans in reverse to preserve positions
        for start, end in reversed(spans):
            old_section = html[start:end]
            new_section = add_target_to_internal_links(old_section)
            if new_section != old_section:
                html = html[:start] + new_section + html[end:]
                changes.append(label)

    # Text-based patterns (no div balancing needed)
    text_patterns = [
        ("Relaterad läsning", r'(<(?:p|div)[^>]*>.*?Relaterad läsning:.*?</(?:p|div)>)'),
        ("Läs vidare", r'(<(?:p|div)[^>]*>.*?Läs vidare:.*?</(?:p|div)>)'),
    ]

    for label, pat in text_patterns:
        def repl(m, lbl=label):
            old = m.group(0)
            new = add_target_to_internal_links(old)
            if new != old:
                changes.append(lbl)
            return new
        html = re.sub(pat, repl, html, flags=re.DOTALL | re.IGNORECASE)

    if html != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        for c in sorted(set(changes)):
            print(f"    Fixed links in <{c}>")
        return True
    return False


def main():
    files = sorted(glob.glob(os.path.join(ARTICLES_DIR, "*.html")))
    modified = 0
    total_links_fixed = 0

    for fpath in files:
        name = os.path.basename(fpath)
        if fix_file(fpath):
            modified += 1
            print(f"  ✓ {name}")
        else:
            print(f"  - {name} (no changes)")

    print(f"\n{modified}/{len(files)} files modified")


if __name__ == "__main__":
    main()
