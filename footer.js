(function() {
  var existing = document.querySelector('footer');
  if (existing) existing.remove();

  var html = `
<style>
.lfoot{background:#1B4332;color:rgba(255,255,255,0.75);padding:28px 0 0;font-size:14px;line-height:1.7;font-family:'Inter',-apple-system,sans-serif;}
.lfoot-inner{max-width:1200px;margin:0 auto;padding:0 24px;}
.lfoot-top{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px 40px;padding-bottom:18px;border-bottom:1px solid rgba(255,255,255,0.12);}
.lfoot-logo{font-family:'Playfair Display',Georgia,serif;font-size:26px;font-weight:700;color:#fff;letter-spacing:-0.01em;text-decoration:none;white-space:nowrap;}
.lfoot-logo span{color:#B8960C;}
.lfoot-nav{display:flex;flex-wrap:wrap;gap:8px 22px;align-items:center;}
.lfoot-nav a{color:rgba(255,255,255,0.72);text-decoration:none;font-size:12.5px;transition:color 0.18s;}
.lfoot-nav a:hover{color:#F5E6A3;}
.lfoot-closing{padding:16px 0;border-bottom:1px solid rgba(255,255,255,0.12);}
.lfoot-lines{display:flex;gap:6px 28px;flex-wrap:wrap;margin-bottom:8px;}
.lfoot-line{font-family:'Playfair Display',Georgia,serif;font-size:13px;font-weight:600;color:rgba(255,255,255,0.50);font-style:italic;white-space:nowrap;}
.lfoot-line::before{content:'— ';color:#B8960C;font-style:normal;}
.lfoot-note{font-size:11px;font-style:italic;color:rgba(255,255,255,0.45);line-height:1.5;margin:0;max-width:560px;}
.lfoot-legal{padding:12px 0 20px;display:flex;justify-content:space-between;align-items:center;gap:8px 20px;flex-wrap:wrap;}
.lfoot-copy{font-size:10.5px;color:rgba(255,255,255,0.35);line-height:1.5;max-width:480px;margin:0;}
.lfoot-legal-links{display:flex;gap:20px;}
.lfoot-legal-links a{font-size:10.5px;color:rgba(255,255,255,0.35);text-decoration:none;transition:color 0.18s;white-space:nowrap;}
.lfoot-legal-links a:hover{color:rgba(255,255,255,0.65);}
@media(max-width:540px){
  .lfoot-top{flex-direction:column;align-items:flex-start;}
  .lfoot-legal{flex-direction:column;align-items:flex-start;}
}
</style>
<footer class="lfoot" role="contentinfo">
  <div class="lfoot-inner">
    <div class="lfoot-top">
      <a href="https://levnytt.se" class="lfoot-logo">Lev<span>Nytt</span></a>
      <nav class="lfoot-nav" aria-label="Sidfot navigation">
        <a href="https://levnytt.se/neolife-historia">Historia</a>
        <a href="https://levnytt.se/neolife-vetenskap">Vetenskap</a>
        <a href="https://levnytt.se/neolife-hallbarhet">Hållbarhet</a>
        <a href="https://levnytt.se/direktforsaljning-fakta">Direktförsäljning</a>
        <a href="https://levnytt.se/neolife-affarsmojlighet">Affärsmöjlighet</a>
        <a href="https://levnytt.se/neolife-kosttillskott">Kosttillskott</a>
        <a href="https://levnytt.se/personlig-vard">Personlig Vård</a>
        <a href="https://levnytt.se/golden-home-care">Golden Home Care</a>
        <a href="https://levnytt.se/neolife-pro-vitality">Pro Vitality+</a>
        <a href="https://levnytt.se/neolife-carotenoid-complex">Carotenoid Complex</a>
        <a href="https://levnytt.se/neolife-omega-3-plus">Omega-3 Plus</a>
        <a href="https://levnytt.se/om-oss">Om Oss</a>
        <a href="https://levnytt.se/den-fundersamma-mannen">Den Fundersamma Mannen</a>
        <a href="https://levnytt.se/var-metod">Vår Metod</a>
        <a href="https://levnytt.se/forsknings-faq">Forsknings-FAQ</a>
        <a href="https://levnytt.se/levnytt-principer">LevNytt Principer</a>
      </nav>
    </div>
    <div class="lfoot-closing">
      <div class="lfoot-lines">
        <span class="lfoot-line">Fakta före hype.</span>
        <span class="lfoot-line">Värde före pris.</span>
        <span class="lfoot-line">Förstå först. Bestäm sedan.</span>
      </div>
      <p class="lfoot-note">
        Resultaten är inte typiska och kan inte garanteras.<br>
        Frågan är egentligen: vad händer när ett beprövat system tillämpas konsekvent under tillräckligt lång tid?<br>
        Det vet de som gör jobbet.
      </p>
    </div>
    <div class="lfoot-legal">
      <p class="lfoot-copy">
        &copy; 2026 LevNytt. Alla rättigheter förbehållna.<br>
        NeoLife&reg; är ett registrerat varumärke tillhörande NeoLife International, LLC. LevNytt är inte en officiell NeoLife-webbplats.
      </p>
      <nav class="lfoot-legal-links" aria-label="Juridiska sidor">
        <a href="https://levnytt.se/integritetspolicy">Integritetspolicy</a>
      </nav>
    </div>
  </div>
</footer>`;

  document.body.insertAdjacentHTML('beforeend', html);
})();
