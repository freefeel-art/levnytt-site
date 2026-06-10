(function() {
  document.querySelectorAll('footer').forEach(function(f) { f.remove(); });

  var html = `
<style> block into the site master template.

  URL verification status (against LEVNYTT-URL-MAP.md, 2026-06-10):
  ✅ Active links  — verified in URL map
  ⬜ Inactive       — page not yet published; rendered as non-linking text

  Column 2 — Forskning:
    Historia            → /neolife-historia           ✅
    Vetenskap           → /neolife-vetenskap           ✅
    Hållbarhet          → /neolife-hallbarhet          ✅
    Direktförsäljning   → /direktforsaljning-fakta     ✅
    Affärsmöjlighet     → /neolife-affarsmojlighet     ✅

  Column 3 — Produkter:
    Kosttillskott       → /neolife-kosttillskott       ✅
    Personlig Vård      → /personlig-vard              ✅
    Golden Home Care    → /golden-home-care            ✅
    Pro Vitality+       → /neolife-pro-vitality        ✅
    Carotenoid Complex  → /neolife-carotenoid-complex  ✅
    Omega-3 Plus        → /neolife-omega-3-plus        ✅

  Column 4 — Om LevNytt:
    Om Oss              → /om-oss                      ✅
    Den Fundersamma M.  → /den-fundersamma-mannen      ✅
    Vår Metod           → /var-metod                   ⬜ (not yet published)
    Forsknings-FAQ      → /forsknings-faq              ⬜ (not yet published)
    LevNytt Principer   → /levnytt-principer           ⬜ (not yet published)

  When ⬜ pages are published:
    1. Add the URL to LEVNYTT-URL-MAP.md
    2. Replace the <span class="footer-link-inactive"> with a live <a> tag
-->

<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LevNytt — Footer V2 Preview</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">

<style>
/* ── DESIGN TOKENS (mirror from master template) ────────────────── */
:root {
  --gold:        #B8960C;
  --gold-light:  #F5E6A3;
  --gold-dark:   #8A6E08;
  --green:       #2D6A4F;
  --green-light: #D8F3DC;
  --green-dark:  #1B4332;
  --cream:       #FAF7F0;
  --cream-dark:  #EDE8DC;
  --white:       #FFFFFF;
  --ink:         #1A1A1A;
  --ink-muted:   #555550;
  --border:      #DDD8CE;
  --max-width:   820px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Inter', sans-serif;
  background: var(--cream);
  color: var(--ink);
}

/* ── FOOTER ──────────────────────────────────────────────────────── */

.site-footer {
  background: var(--green-dark);
  color: rgba(255, 255, 255, 0.75);
  padding: 64px 0 0;
  font-size: 14px;
  line-height: 1.7;
}

.footer-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
}

/* ── TOP GRID: 4 columns ─────────────────────────────────────────── */

.footer-grid {
  display: grid;
  grid-template-columns: 1.6fr 1fr 1fr 1fr;
  gap: 40px 48px;
  padding-bottom: 48px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}

@media (max-width: 860px) {
  .footer-grid {
    grid-template-columns: 1fr 1fr;
    gap: 36px 32px;
  }
}

@media (max-width: 540px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 32px;
  }
}

/* Column 1 — Brand */
.footer-brand {}

.footer-logo {
  font-family: 'Playfair Display', serif;
  font-size: 22px;
  font-weight: 700;
  color: var(--white);
  letter-spacing: -0.01em;
  margin-bottom: 14px;
  display: block;
  text-decoration: none;
}

.footer-logo span {
  color: var(--gold);
}

.footer-brand-desc {
  font-size: 13.5px;
  color: rgba(255, 255, 255, 0.65);
  line-height: 1.7;
  max-width: 280px;
}

/* Columns 2–4 — Nav */
.footer-col {}

.footer-col-heading {
  font-family: 'Inter', sans-serif;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--gold-light);
  margin-bottom: 16px;
}

.footer-nav {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 9px;
}

.footer-nav li {}

.footer-nav a {
  color: rgba(255, 255, 255, 0.72);
  text-decoration: none;
  font-size: 13.5px;
  transition: color 0.18s;
}

.footer-nav a:hover {
  color: var(--gold-light);
}

/* Inactive nav items — pages not yet published */
.footer-link-inactive {
  color: rgba(255, 255, 255, 0.32);
  font-size: 13.5px;
  cursor: default;
  display: inline-block;
}

/* ── PRINCIPLES BLOCK ────────────────────────────────────────────── */

.footer-principles {
  padding: 40px 0 36px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}

.footer-principles-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 20px;
}

.footer-principles-body {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0 48px;
}

@media (max-width: 720px) {
  .footer-principles-body {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

.footer-principles-body p {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.7;
}

/* ── CLOSING STATEMENT ───────────────────────────────────────────── */

.footer-closing {
  padding: 32px 0 40px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}

.footer-closing-lines {
  display: flex;
  gap: 0 40px;
  flex-wrap: wrap;
}

.footer-closing-line {
  font-family: 'Playfair Display', serif;
  font-size: 15px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.55);
  font-style: italic;
  line-height: 1.5;
}

.footer-closing-line::before {
  content: '— ';
  color: var(--gold);
  font-style: normal;
}

@media (max-width: 600px) {
  .footer-closing-lines {
    flex-direction: column;
    gap: 10px;
  }
}

/* ── LEGAL STRIP ─────────────────────────────────────────────────── */

.footer-legal {
  padding: 24px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.footer-copyright {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.38);
  line-height: 1.6;
}

.footer-legal-links {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.footer-legal-links a {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.38);
  text-decoration: none;
  transition: color 0.18s;
}

.footer-legal-links a:hover {
  color: rgba(255, 255, 255, 0.65);
}

@media (max-width: 540px) {
  .footer-legal {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
<footer> element and the
  accompanying <style> block into the site master template.

  URL verification status (against LEVNYTT-URL-MAP.md, 2026-06-10):
  ✅ Active links  — verified in URL map
  ⬜ Inactive       — page not yet published; rendered as non-linking text

  Column 2 — Forskning:
    Historia            → /neolife-historia           ✅
    Vetenskap           → /neolife-vetenskap           ✅
    Hållbarhet          → /neolife-hallbarhet          ✅
    Direktförsäljning   → /direktforsaljning-fakta     ✅
    Affärsmöjlighet     → /neolife-affarsmojlighet     ✅

  Column 3 — Produkter:
    Kosttillskott       → /neolife-kosttillskott       ✅
    Personlig Vård      → /personlig-vard              ✅
    Golden Home Care    → /golden-home-care            ✅
    Pro Vitality+       → /neolife-pro-vitality        ✅
    Carotenoid Complex  → /neolife-carotenoid-complex  ✅
    Omega-3 Plus        → /neolife-omega-3-plus        ✅

  Column 4 — Om LevNytt:
    Om Oss              → /om-oss                      ✅
    Den Fundersamma M.  → /den-fundersamma-mannen      ✅
    Vår Metod           → /var-metod                   ⬜ (not yet published)
    Forsknings-FAQ      → /forsknings-faq              ⬜ (not yet published)
    LevNytt Principer   → /levnytt-principer           ⬜ (not yet published)

  When ⬜ pages are published:
    1. Add the URL to LEVNYTT-URL-MAP.md
    2. Replace the <span class="footer-link-inactive"> with a live <a> tag
-->

<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LevNytt — Footer V2 Preview</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">

<style>
/* ── DESIGN TOKENS (mirror from master template) ────────────────── */
:root {
  --gold:        #B8960C;
  --gold-light:  #F5E6A3;
  --gold-dark:   #8A6E08;
  --green:       #2D6A4F;
  --green-light: #D8F3DC;
  --green-dark:  #1B4332;
  --cream:       #FAF7F0;
  --cream-dark:  #EDE8DC;
  --white:       #FFFFFF;
  --ink:         #1A1A1A;
  --ink-muted:   #555550;
  --border:      #DDD8CE;
  --max-width:   820px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Inter', sans-serif;
  background: var(--cream);
  color: var(--ink);
}

/* ── FOOTER ──────────────────────────────────────────────────────── */

.site-footer {
  background: var(--green-dark);
  color: rgba(255, 255, 255, 0.75);
  padding: 64px 0 0;
  font-size: 14px;
  line-height: 1.7;
}

.footer-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
}

/* ── TOP GRID: 4 columns ─────────────────────────────────────────── */

.footer-grid {
  display: grid;
  grid-template-columns: 1.6fr 1fr 1fr 1fr;
  gap: 40px 48px;
  padding-bottom: 48px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}

@media (max-width: 860px) {
  .footer-grid {
    grid-template-columns: 1fr 1fr;
    gap: 36px 32px;
  }
}

@media (max-width: 540px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 32px;
  }
}

/* Column 1 — Brand */
.footer-brand {}

.footer-logo {
  font-family: 'Playfair Display', serif;
  font-size: 22px;
  font-weight: 700;
  color: var(--white);
  letter-spacing: -0.01em;
  margin-bottom: 14px;
  display: block;
  text-decoration: none;
}

.footer-logo span {
  color: var(--gold);
}

.footer-brand-desc {
  font-size: 13.5px;
  color: rgba(255, 255, 255, 0.65);
  line-height: 1.7;
  max-width: 280px;
}

/* Columns 2–4 — Nav */
.footer-col {}

.footer-col-heading {
  font-family: 'Inter', sans-serif;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--gold-light);
  margin-bottom: 16px;
}

.footer-nav {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 9px;
}

.footer-nav li {}

.footer-nav a {
  color: rgba(255, 255, 255, 0.72);
  text-decoration: none;
  font-size: 13.5px;
  transition: color 0.18s;
}

.footer-nav a:hover {
  color: var(--gold-light);
}

/* Inactive nav items — pages not yet published */
.footer-link-inactive {
  color: rgba(255, 255, 255, 0.32);
  font-size: 13.5px;
  cursor: default;
  display: inline-block;
}

/* ── PRINCIPLES BLOCK ────────────────────────────────────────────── */

.footer-principles {
  padding: 40px 0 36px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}

.footer-principles-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 20px;
}

.footer-principles-body {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0 48px;
}

@media (max-width: 720px) {
  .footer-principles-body {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

.footer-principles-body p {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.7;
}

/* ── CLOSING STATEMENT ───────────────────────────────────────────── */

.footer-closing {
  padding: 32px 0 40px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}

.footer-closing-lines {
  display: flex;
  gap: 0 40px;
  flex-wrap: wrap;
}

.footer-closing-line {
  font-family: 'Playfair Display', serif;
  font-size: 15px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.55);
  font-style: italic;
  line-height: 1.5;
}

.footer-closing-line::before {
  content: '— ';
  color: var(--gold);
  font-style: normal;
}

@media (max-width: 600px) {
  .footer-closing-lines {
    flex-direction: column;
    gap: 10px;
  }
}

/* ── LEGAL STRIP ─────────────────────────────────────────────────── */

.footer-legal {
  padding: 24px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.footer-copyright {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.38);
  line-height: 1.6;
}

.footer-legal-links {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.footer-legal-links a {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.38);
  text-decoration: none;
  transition: color 0.18s;
}

.footer-legal-links a:hover {
  color: rgba(255, 255, 255, 0.65);
}

@media (max-width: 540px) {
  .footer-legal {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
</head>

<body>

<!-- ════════════════════════════════════════════════════════════════
     LEVNYTT FOOTER V2
     Paste from <footer> to </footer>
`;

  document.body.insertAdjacentHTML('beforeend', html);
})();
