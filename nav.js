(function() {
  var current = window.location.pathname;

  function isActive(path) {
    return current === path || current.startsWith(path) ? ' nav-active' : '';
  }

  var html = `
<style>
  #levnytt-nav{position:sticky;top:0;z-index:100;background:rgba(251,248,240,0.92);backdrop-filter:blur(12px);border-bottom:1px solid #E0D8C8;font-family:'Inter',-apple-system,sans-serif;}
  .lnav-inner{max-width:1200px;margin:0 auto;padding:0 24px;display:flex;align-items:center;justify-content:space-between;height:64px;}
  .lnav-brand{font-family:'Playfair Display',Georgia,serif;font-weight:700;font-size:1.25rem;color:#C9A84C;text-decoration:none;}
  .lnav-brand span{color:#2D6A4F;}
  .lnav-links{display:flex;gap:4px;align-items:center;}
  .lnav-links a{font-size:0.85rem;font-weight:500;color:#1B4332;text-decoration:none;padding:6px 12px;border-radius:6px;transition:all 0.2s;white-space:nowrap;}
  .lnav-links a:hover{color:#1A1A1A;background:#F0EBDD;}
  .lnav-links a.nav-active{color:#C9A84C;font-weight:700;}
  .lnav-dropdown{position:relative;}
  .lnav-dropdown-btn{font-size:0.85rem;font-weight:500;color:#1B4332;background:none;border:none;cursor:pointer;padding:6px 12px;border-radius:6px;display:flex;align-items:center;gap:4px;transition:all 0.2s;font-family:'Inter',-apple-system,sans-serif;}
  .lnav-dropdown-btn:hover{color:#1A1A1A;background:#F0EBDD;}
  .lnav-dropdown-btn.nav-active{color:#C9A84C;font-weight:700;}
  .lnav-dropdown-btn svg{width:14px;height:14px;stroke:currentColor;transition:transform 0.2s;}
  .lnav-dropdown-btn.open svg{transform:rotate(180deg);}
  .lnav-dropdown-menu{position:absolute;top:calc(100% + 8px);left:0;background:#fff;border:1px solid #E0D8C8;border-radius:10px;box-shadow:0 8px 32px rgba(0,0,0,0.12);min-width:220px;padding:8px;display:none;z-index:200;}
  .lnav-dropdown-menu.open{display:block;}
  .lnav-dropdown-menu a{display:block;font-size:0.85rem;font-weight:500;color:#1B4332;text-decoration:none;padding:8px 14px;border-radius:6px;transition:all 0.2s;}
  .lnav-dropdown-menu a:hover{color:#1A1A1A;background:#F0EBDD;}
  .lnav-dropdown-menu a.nav-active{color:#C9A84C;font-weight:700;}
  .lnav-dropdown-divider{height:1px;background:#E0D8C8;margin:4px 0;}
  .lnav-dropdown-label{font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#888;padding:6px 14px 2px;}
  .lnav-cta{background:#2D6A4F!important;color:#fff!important;font-weight:600!important;padding:8px 18px!important;}
  .lnav-cta:hover{background:#1B4332!important;color:#fff!important;}
  .lnav-savings{background:#D4A017!important;color:#111!important;}
  .lnav-savings:hover{background:#B8860B!important;color:#111!important;}

  .lnav-hamburger{display:none;background:none;border:none;cursor:pointer;padding:8px;}
  .lnav-hamburger svg{width:24px;height:24px;stroke:#1A1A1A;}
  @media(max-width:900px){
    .lnav-links{display:none;}
    .lnav-hamburger{display:block;}
    .lnav-links.open{display:flex;flex-direction:column;align-items:stretch;position:absolute;top:64px;left:0;right:0;background:#FBF8F0;border-bottom:1px solid #E0D8C8;padding:12px 24px;box-shadow:0 8px 32px rgba(0,0,0,0.12);}
    .lnav-dropdown-menu{position:static;box-shadow:none;border:none;border-left:2px solid #E0D8C8;border-radius:0;padding:4px 0 4px 12px;margin:4px 0;}
    .lnav-dropdown-btn{justify-content:space-between;width:100%;}
  }
</style>
<nav id="levnytt-nav">
  <div class="lnav-inner">
    <a href="/" class="lnav-brand">Lev<span>Nytt</span></a>
    <button class="lnav-hamburger" id="lnavHamburger" aria-label="Meny">
      <svg fill="none" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" d="M4 6h16M4 12h16M4 18h16"/></svg>
    </button>
    <div class="lnav-links" id="lnavLinks">
      <a href="/"${isActive('/')}>Hem</a>

      <a href="/neolife-historia/"${isActive('/neolife-historia/')}>Historia</a>
      <a href="/neolife-vetenskap/"${isActive('/neolife-vetenskap/')}>Vetenskap</a>

      <div class="lnav-dropdown" id="lnavDropdown">
        <button class="lnav-dropdown-btn${isActive('/neolife-kosttillskott/') || isActive('/personlig-vard/') || isActive('/golden-home-care/') || isActive('/nutriance-organic/') ? ' nav-active' : ''}" id="lnavDropBtn">
          Produkter
          <svg fill="none" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
        </button>
        <div class="lnav-dropdown-menu" id="lnavDropMenu">
          <p class="lnav-dropdown-label">Kosttillskott</p>
          <a href="/neolife-pro-vitality/"${isActive('/neolife-pro-vitality/')}>Pro Vitality+</a>
          <a href="/multivitamin-kvinnor-over-40/"${isActive('/multivitamin-kvinnor-over-40/')}>Multivitamin för kvinnor över 40</a>
          <a href="/neolife-kosttillskott/"${isActive('/neolife-kosttillskott/')}>Alla kosttillskott</a>
          <div class="lnav-dropdown-divider"></div>
          <p class="lnav-dropdown-label">Personlig vård</p>
          <a href="/personlig-vard/"${isActive('/personlig-vard/')}>Personlig vård — översikt</a>
          <a href="/personlig-vard.html"${isActive('/personlig-vard.html')}>Personlig vård</a>
          <div class="lnav-dropdown-divider"></div>
          <p class="lnav-dropdown-label">Hem & Städning</p>
          <a href="/golden-home-care/"${isActive('/golden-home-care/')}>Golden Home Care</a>
        </div>
      </div>

      <a href="/neolife-affarsmojlighet/"${isActive('/neolife-affarsmojlighet/')}>Affärsmöjlighet</a>
      <a href="https://se.neolifeshop.com/i/shop.html?sponsor=41-830928" class="lnav-cta" target="_blank" rel="noopener">Handla NeoLife &rarr;</a>
      <a href="/finns-det-billigare-alternativ/" class="lnav-cta lnav-savings">Spara Pengar?</a>
    </div>
  </div>
</nav>`;

  var existing = document.getElementById('levnytt-nav');
  if (existing) existing.remove();

  var existingNavs = document.querySelectorAll('nav');
  existingNavs.forEach(function(n) { n.remove(); });

  document.body.insertAdjacentHTML('afterbegin', html);

  document.getElementById('lnavHamburger').addEventListener('click', function() {
    document.getElementById('lnavLinks').classList.toggle('open');
  });

  document.getElementById('lnavDropBtn').addEventListener('click', function(e) {
    e.stopPropagation();
    this.classList.toggle('open');
    document.getElementById('lnavDropMenu').classList.toggle('open');
  });

  document.addEventListener('click', function() {
    document.getElementById('lnavDropBtn').classList.remove('open');
    document.getElementById('lnavDropMenu').classList.remove('open');
  });
})();
