(function() {
  var existing = document.querySelector('footer');
  if (existing) existing.remove();

  var html = `
<style>
.lfoot{background:var(--ln-color-brand-green,#1B4332);color:rgba(255,255,255,0.75);padding:28px 0 0;font-size:14px;line-height:1.7;font-family:var(--ln-font-body,'Inter',-apple-system,sans-serif);}
.lfoot-inner{max-width:var(--ln-width-shell,1200px);margin:0 auto;padding:0 24px;}
.lfoot-top{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px 40px;padding-bottom:18px;border-bottom:1px solid rgba(255,255,255,0.12);}
.lfoot-logo{background:var(--ln-color-surface,#F9F6EF);border-radius:var(--ln-radius-sm,6px);padding:4px 8px;text-decoration:none;display:inline-flex;align-items:center;}
.lfoot-logo img{display:block;height:24px;width:auto;}
.lfoot-nav{display:flex;flex-wrap:wrap;gap:8px 22px;align-items:center;}
.lfoot-nav a{color:rgba(255,255,255,0.72);text-decoration:none;font-size:12.5px;transition:color 0.18s;}
.lfoot-nav a:hover{color:var(--ln-color-brand-gold,#E8C870);}
.lfoot-closing{padding:16px 0;border-bottom:1px solid rgba(255,255,255,0.12);}
.lfoot-lines{display:flex;gap:6px 28px;flex-wrap:wrap;margin-bottom:8px;}
.lfoot-line{font-family:'Playfair Display',Georgia,serif;font-size:13px;font-weight:600;color:rgba(255,255,255,0.50);font-style:italic;white-space:nowrap;}
.lfoot-line::before{content:'— ';color:var(--ln-color-brand-gold,#E8C870);font-style:normal;}
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
      <a href="https://levnytt.se" class="lfoot-logo" target="_blank" rel="noopener noreferrer" aria-label="LevNytt — Hem">
        <img src="/assets/brand/header-logo.svg" alt="LevNytt">
      </a>
      <nav class="lfoot-nav" aria-label="Sidfot navigation">
        <a href="https://levnytt.se/neolife-historia" target="_blank" rel="noopener noreferrer">Historia</a>
        <a href="https://levnytt.se/neolife-vetenskap" target="_blank" rel="noopener noreferrer">Vetenskap</a>
        <a href="https://levnytt.se/neolife-hallbarhet/" target="_blank" rel="noopener noreferrer">Hållbarhet</a>
        <a href="https://levnytt.se/direktforsaljning-fakta" target="_blank" rel="noopener noreferrer">Direktförsäljning</a>
        <a href="https://levnytt.se/neolife-affarsmojlighet" target="_blank" rel="noopener noreferrer">Affärsmöjlighet</a>
        <a href="https://levnytt.se/neolife-kosttillskott" target="_blank" rel="noopener noreferrer">Kosttillskott</a>
        <a href="https://levnytt.se/personlig-vard" target="_blank" rel="noopener noreferrer">Personlig Vård</a>
        <a href="https://levnytt.se/golden-home-care/" target="_blank" rel="noopener noreferrer">Golden Home Care</a>
        <a href="https://levnytt.se/neolife-pro-vitality" target="_blank" rel="noopener noreferrer">Pro Vitality+</a>
        <a href="https://levnytt.se/neolife-carotenoid-complex" target="_blank" rel="noopener noreferrer">Carotenoid Complex</a>
        <a href="https://levnytt.se/neolife-omega-3-plus" target="_blank" rel="noopener noreferrer">Omega-3 Plus</a>
        <a href="https://levnytt.se/om-oss" target="_blank" rel="noopener noreferrer">Om Oss</a>
        <a href="https://levnytt.se/artiklar" target="_blank" rel="noopener noreferrer">Alla artiklar</a>
        <a href="https://levnytt.se/den-fundersamma-mannen" target="_blank" rel="noopener noreferrer">Jarmo Halonen</a>
        <a href="https://levnytt.se/var-metod" target="_blank" rel="noopener noreferrer">Vår Metod</a>
        <a href="https://levnytt.se/forsknings-faq" target="_blank" rel="noopener noreferrer">Forsknings-FAQ</a>
        <a href="https://levnytt.se/levnytt-principer" target="_blank" rel="noopener noreferrer">LevNytt Principer</a>
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
        <a href="https://levnytt.se/integritetspolicy" target="_blank" rel="noopener noreferrer">Integritetspolicy</a>
      </nav>
    </div>
  </div>
</footer>`;

  document.body.insertAdjacentHTML('beforeend', html);
})();
