// LevNytt.se — Global components
// Translate + scroll-to-top + sponsor-ID automaatio

(function() {

  var SPONSOR = '41-830928';
  var SHOP_BASE = 'https://se.neolifeshop.com';

  // ============================================================
  // TUOTESIVUKARTTA — sivu → suora tuote-URL sponsori-ID:llä
  // ============================================================
  var productMap = {
    '/super-10/':                      SHOP_BASE + '/i/shop/home-care/super-10.html?sponsor=' + SPONSOR,
    '/golden-home-care/':              SHOP_BASE + '/i/shop/home-care/ldc.html?sponsor=' + SPONSOR,
    '/neolife-pro-vitality/':          SHOP_BASE + '/i/shop/nutrition/pro-vitality-plus.html?sponsor=' + SPONSOR,
    '/neolife-carotenoid-complex/':    SHOP_BASE + '/i/shop/nutrition/carotenoid-complex.html?sponsor=' + SPONSOR,
    '/neolife-omega-3-plus/':          SHOP_BASE + '/i/shop/nutrition/omega-3-plus.html?sponsor=' + SPONSOR,
    '/neolife-tre-en-en/':             SHOP_BASE + '/i/shop/nutrition/tre-en-en.html?sponsor=' + SPONSOR,
    '/neolife-viktkontroll/':          SHOP_BASE + '/i/shop/nutrition/neolife-shake.html?sponsor=' + SPONSOR,
    '/nutriance-organic/':             SHOP_BASE + '/i/shop/personal-care/nutriance-organic.html?sponsor=' + SPONSOR,
    '/neolife-acidophilus-plus/':      SHOP_BASE + '/i/shop/nutrition/acidophilus-plus.html?sponsor=' + SPONSOR,
    '/neolife-betaguard/':             SHOP_BASE + '/i/shop/nutrition/betaguard.html?sponsor=' + SPONSOR,
    '/neolife-coq10/':                 SHOP_BASE + '/i/shop/nutrition/coq10.html?sponsor=' + SPONSOR,
    '/neolife-elevate/':               SHOP_BASE + '/i/shop/nutrition/elevate.html?sponsor=' + SPONSOR,
    '/neolife-flavonoid-complex/':     SHOP_BASE + '/i/shop/nutrition/flavonoid-complex.html?sponsor=' + SPONSOR,
    '/neolife-formula-iv/':            SHOP_BASE + '/i/shop/nutrition/formula-iv.html?sponsor=' + SPONSOR,
    '/neolife-vitamin-d/':             SHOP_BASE + '/i/shop/nutrition/vitamin-d.html?sponsor=' + SPONSOR,
    '/neolife-vitamin-e/':             SHOP_BASE + '/i/shop/nutrition/vitamin-e.html?sponsor=' + SPONSOR,
    '/neolife-magnesium-complex/':     SHOP_BASE + '/i/shop/nutrition/magnesium-complex.html?sponsor=' + SPONSOR,
    '/neolife-chelated-zinc/':         SHOP_BASE + '/i/shop/nutrition/chelated-zinc.html?sponsor=' + SPONSOR,
    '/neolife-upbeet/':                SHOP_BASE + '/i/shop/nutrition/upbeet.html?sponsor=' + SPONSOR,
    '/neolife-resp-x/':                SHOP_BASE + '/i/shop/nutrition/resp-x.html?sponsor=' + SPONSOR,
    '/neolife-garlic-allium-complex/': SHOP_BASE + '/i/shop/nutrition/garlic-allium-complex.html?sponsor=' + SPONSOR,
    '/neolife-cruciferous-plus/':      SHOP_BASE + '/i/shop/nutrition/cruciferous-plus.html?sponsor=' + SPONSOR,
    '/neolife-botanical-balance/':     SHOP_BASE + '/i/shop/nutrition/botanical-balance.html?sponsor=' + SPONSOR,
    '/neolife-kalmag-plus-d/':         SHOP_BASE + '/i/shop/nutrition/kal-mag-plus-d.html?sponsor=' + SPONSOR,
    '/neolife-shake-bar-tea/':         SHOP_BASE + '/i/shop/nutrition/neolife-shake.html?sponsor=' + SPONSOR,
  };

  // ============================================================
  // SPONSOR-ID AUTOMAATIO
  // ============================================================
  function fixLinks() {
    var currentPath = window.location.pathname;
    var directProductUrl = productMap[currentPath];

    var links = document.querySelectorAll('a[href*="neolifeshop.com"]');
    links.forEach(function(link) {
      var href = link.href;

      // Jos ollaan tuotesivulla → ohjaa suoraan tuotteeseen
      if (directProductUrl && !href.includes('registration') && !href.includes('enrollment')) {
        link.href = directProductUrl;
        return;
      }

      // Lisää sponsor= jos puuttuu
      if (!href.includes('sponsor=') && !href.includes('sponsorId=')) {
        var separator = href.includes('?') ? '&' : '?';
        link.href = href + separator + 'sponsor=' + SPONSOR;
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fixLinks);
  } else {
    fixLinks();
  }

  // ============================================================
  // CSS
  // ============================================================
  var style = document.createElement('style');
  style.textContent = '\
    .scroll-top{position:fixed;bottom:80px;right:24px;width:44px;height:44px;background:#2D6A4F;border:none;border-radius:50%;cursor:pointer;display:none;align-items:center;justify-content:center;box-shadow:0 4px 16px rgba(0,0,0,0.2);z-index:9999;transition:all 0.25s;}\
    .scroll-top:hover{background:#1B4332;}\
    .scroll-top.visible{display:flex;}\
    .scroll-top svg{width:20px;height:20px;stroke:#fff;fill:none;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round;}\
    .translator-wrap{position:fixed;bottom:24px;right:24px;z-index:9999;}\
    .translator-btn{background:#fff;border:1px solid #E0D8C8;border-radius:24px;padding:8px 16px;font-size:0.82rem;font-weight:600;color:#555;cursor:pointer;box-shadow:0 4px 16px rgba(0,0,0,0.12);display:flex;align-items:center;gap:6px;font-family:inherit;transition:all 0.25s;}\
    .translator-btn:hover{border-color:#2D6A4F;color:#2D6A4F;}\
    #goog-translate-wrap{display:none;position:absolute;bottom:48px;right:0;background:#fff;border:1px solid #E0D8C8;border-radius:8px;padding:8px;box-shadow:0 8px 32px rgba(0,0,0,0.15);min-width:180px;}\
    #goog-translate-wrap.open{display:block;}\
    .goog-te-gadget{font-size:0!important;}\
    .goog-te-gadget .goog-te-combo{font-size:0.9rem;padding:6px 8px;border:1px solid #E0D8C8;border-radius:6px;width:100%;cursor:pointer;}\
  ';
  document.head.appendChild(style);

  // ============================================================
  // YLÖS-NUOLI
  // ============================================================
  var btn = document.createElement('button');
  btn.className = 'scroll-top';
  btn.id = 'scrollTop';
  btn.setAttribute('aria-label', 'Tillbaka till toppen');
  btn.innerHTML = '<svg viewBox="0 0 24 24"><polyline points="18 15 12 9 6 15"/></svg>';
  btn.onclick = function(){ window.scrollTo({top:0, behavior:'smooth'}); };
  document.body.appendChild(btn);

  window.addEventListener('scroll', function(){
    btn.classList.toggle('visible', window.scrollY > 400);
  });

  // ============================================================
  // TRANSLATOR
  // ============================================================
  var wrap = document.createElement('div');
  wrap.className = 'translator-wrap';
  wrap.innerHTML = '<button class="translator-btn" onclick="document.getElementById(\'goog-translate-wrap\').classList.toggle(\'open\')" aria-label="Translate">&#127760; Translate</button><div id="goog-translate-wrap"><div id="google_translate_element"></div></div>';
  document.body.appendChild(wrap);

  window.googleTranslateElementInit = function() {
    new google.translate.TranslateElement({
      pageLanguage: 'sv',
      includedLanguages: 'en,fi,no,da,de,fr,es,ar,zh-CN,fa',
      layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
      autoDisplay: false
    }, 'google_translate_element');
  };

  var gtScript = document.createElement('script');
  gtScript.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
  document.body.appendChild(gtScript);

})();
