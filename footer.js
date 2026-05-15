(function() {
  // Poista vanhat footer-elementit
  document.querySelectorAll('footer').forEach(function(f) { f.remove(); });

  var html = `
<style>
  #levnytt-footer{background:#1A1A1A;color:rgba(255,255,255,0.6);padding:56px 0 32px;font-family:'Inter',-apple-system,sans-serif;}
  .lf-grid{max-width:1200px;margin:0 auto;padding:0 24px;display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:48px;margin-bottom:48px;}
  .lf-brand{font-family:'Playfair Display',Georgia,serif;font-weight:700;font-size:1.2rem;color:#fff;margin-bottom:12px;}
  .lf-brand span{color:#E8C870;}
  .lf-tagline{font-size:0.85rem;line-height:1.6;max-width:280px;color:rgba(255,255,255,0.6);}
  .lf-col h5{color:#fff;font-size:0.82rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:16px;}
  .lf-col a{display:block;color:rgba(255,255,255,0.55);text-decoration:none;font-size:0.88rem;padding:4px 0;transition:color 0.2s;}
  .lf-col a:hover{color:#E8C870;}
  .lf-bottom{max-width:1200px;margin:0 auto;padding:24px 24px 0;border-top:1px solid rgba(255,255,255,0.08);font-size:0.78rem;color:rgba(255,255,255,0.6);}
  .lf-disclaimer{margin-top:16px;font-size:0.72rem;color:rgba(255,255,255,0.35);line-height:1.6;}
  @media(max-width:900px){.lf-grid{grid-template-columns:1fr 1fr;gap:32px;}}
  @media(max-width:600px){.lf-grid{grid-template-columns:1fr;}}
</style>
<footer id="levnytt-footer">
  <div class="lf-grid">
    <div>
      <div class="lf-brand">Lev<span>Nytt</span></div>
      <p class="lf-tagline">Oberoende NeoLife-distributör. Vetenskapligt baserade kosttillskott och biologiskt nedbrytbar städning sedan 1958. Uppdaterad maj 2026. Sponsor-ID: 41-830928.</p>
    </div>
    <div class="lf-col">
      <h5>Forskning</h5>
      <a href="/neolife-historia/">Historia</a>
      <a href="/neolife-vetenskap/">Vetenskap</a>
      <a href="/neolife-hallbarhet/">Hållbarhet</a>
      <a href="/direktforsaljning-fakta/">Direktförsäljning</a>
      <a href="/neolife-affarsmojlighet/">Affärsmöjlighet</a>
    </div>
    <div class="lf-col">
      <h5>Produkter</h5>
      <a href="/neolife-kosttillskott/">Kosttillskott</a>
      <a href="/personlig-vard/">Personlig vård</a>
      <a href="/golden-home-care/">Golden Home Care</a>
      <a href="/neolife-pro-vitality/">Pro Vitality+</a>
      <a href="/neolife-carotenoid-complex/">Carotenoid Complex</a>
      <a href="/neolife-omega-3-plus/">Omega-3 Plus</a>
    </div>
    <div class="lf-col">
      <h5>Shoppa</h5>
      <a href="https://se.neolifeshop.com/i/shop.html?sponsor=41-830928" target="_blank" rel="noopener">Kundshop</a>
      <a href="https://se.neolifeshop.com/i/registration.html?type=reseller&sponsor=41-830928" target="_blank" rel="noopener">Bli distributör</a>
      <a href="/integritetspolicy">Integritetspolicy</a>
      <a href="/om-oss">Om oss</a>
    </div>
  </div>
  <div class="lf-bottom">
    <p>&copy; ${new Date().getFullYear()} LevNytt.se &mdash; Oberoende NeoLife-distributör &mdash; Sponsor-ID: 41-830928</p>
    <p class="lf-disclaimer">LevNytt.se är en oberoende NeoLife-distributörswebbplats. Informationen är avsedd för utbildningssyfte och har inte utvärderats av Livsmedelsverket. Produkterna är inte avsedda att diagnostisera, behandla, bota eller förebygga några sjukdomar. Individuella resultat kan variera. Vissa länkar på den här webbplatsen är affiliatelänkar. NeoLife&reg; är ett registrerat varumärke tillhörande NeoLife International. Den här webbplatsen ägs inte av och är inte kopplad till NeoLife International AB.</p>
  </div>
</footer>`;

  document.body.insertAdjacentHTML('beforeend', html);
})();
