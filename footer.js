(function() {
  document.querySelectorAll('footer').forEach(function(f) { f.remove(); });

  var html = `
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

<footer class="site-footer" role="contentinfo">
  <div class="footer-container">

    <!-- ── TOP GRID ──────────────────────────────────────────────── -->
    <div class="footer-grid">

      <!-- Column 1: Brand -->
      <div class="footer-brand">
        <a href="https://levnytt.se" class="footer-logo">Lev<span>Nytt</span></a>
        <p class="footer-brand-desc">Oberoende konsumentutbildning om NeoLife-produkter och hälsa. Vi förklarar — du bestämmer.</p>
      </div>

      <!-- Column 2: Forskning -->
      <div class="footer-col">
        <p class="footer-col-heading">Forskning</p>
        <ul class="footer-nav">
          <li><a href="https://levnytt.se/neolife-historia">Historia</a></li>
          <li><a href="https://levnytt.se/neolife-vetenskap">Vetenskap</a></li>
          <li><a href="https://levnytt.se/neolife-hallbarhet">Hållbarhet</a></li>
          <li><a href="https://levnytt.se/direktforsaljning-fakta">Direktförsäljning</a></li>
          <li><a href="https://levnytt.se/neolife-affarsmojlighet">Affärsmöjlighet</a></li>
        </ul>
      </div>

      <!-- Column 3: Produkter -->
      <div class="footer-col">
        <p class="footer-col-heading">Produkter</p>
        <ul class="footer-nav">
          <li><a href="https://levnytt.se/neolife-kosttillskott">Kosttillskott</a></li>
          <li><a href="https://levnytt.se/personlig-vard">Personlig Vård</a></li>
          <li><a href="https://levnytt.se/golden-home-care">Golden Home Care</a></li>
          <li><a href="https://levnytt.se/neolife-pro-vitality">Pro Vitality+</a></li>
          <li><a href="https://levnytt.se/neolife-carotenoid-complex">Carotenoid Complex</a></li>
          <li><a href="https://levnytt.se/neolife-omega-3-plus">Omega-3 Plus</a></li>
        </ul>
      </div>

      <!-- Column 4: Om LevNytt -->
      <div class="footer-col">
        <p class="footer-col-heading">Om LevNytt</p>
        <ul class="footer-nav">
          <li><a href="https://levnytt.se/om-oss">Om Oss</a></li>
          <li><a href="https://levnytt.se/den-fundersamma-mannen">Den Fundersamma Mannen</a></li>
          <!-- Activate when /var-metod is published -->
          <li><span class="footer-link-inactive">Vår Metod</span></li>
          <!-- Activate when /forsknings-faq is published -->
          <li><span class="footer-link-inactive">Forsknings-FAQ</span></li>
          <!-- Activate when /levnytt-principer is published -->
          <li><span class="footer-link-inactive">LevNytt Principer</span></li>
        </ul>
      </div>

    </div><!-- /footer-grid -->

    <!-- ── LEVNYTTS PRINCIPER ──────────────────────────────────── -->
    <div class="footer-principles">
      <p class="footer-principles-label">LevNytts Principer</p>
      <div class="footer-principles-body">
        <p>Informationen på LevNytt bygger, så långt det är möjligt, på forskning, myndighetskällor, dokumenterade fakta och praktisk erfarenhet. Vårt mål är att hjälpa läsare att fatta mer informerade beslut – inte att tala om för dem vad de ska välja.</p>
        <p>LevNytt ger inte medicinska, juridiska eller ekonomiska råd. Resultat inom hälsa, livsstil och affärsverksamhet varierar mellan individer.</p>
        <p>LevNytt skriver om NeoLife-produkter och NeoLife-affärsmöjligheten. Eventuella kommersiella relationer redovisas öppet.</p>
      </div>
    </div>

    <!-- ── CLOSING STATEMENT ───────────────────────────────────── -->
    <div class="footer-closing">
      <div class="footer-closing-lines">
        <span class="footer-closing-line">Fakta före hype.</span>
        <span class="footer-closing-line">Värde före pris.</span>
        <span class="footer-closing-line">Förstå först. Bestäm sedan.</span>
      </div>
    </div>

    <!-- ── LEGAL STRIP ─────────────────────────────────────────── -->
    <div class="footer-legal">
      <p class="footer-copyright">
        &copy; 2026 LevNytt. Alla rättigheter förbehållna.<br>
        NeoLife&reg; är ett registrerat varumärke tillhörande NeoLife International, LLC. LevNytt är inte en officiell NeoLife-webbplats.
      </p>
      <nav class="footer-legal-links" aria-label="Juridiska sidor">
        <a href="https://levnytt.se/integritetspolicy">Integritetspolicy</a>
      </nav>
    </div>

  </div><!-- /footer-container -->
</footer>
`;

  document.body.insertAdjacentHTML('beforeend', html);
})();
