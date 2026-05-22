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

  // CSS
// ============================================================
var style = document.createElement('style');
style.textContent = '\
  .scroll-top{position:fixed;bottom:80px;right:24px;width:44px;height:44px;background:#2D6A4F;border-radius:50%;display:none;justify-content:center;align-items:center;z-index:9999;transition:all 0.3s ease;cursor:pointer;}\
  .scroll-top:hover{background:#1B4332;}\
  .scroll-top.visible{display:flex;}\
  .scroll-top svg{width:20px;height:20px;stroke:#fff;fill:none;stroke-width:2;}\
';
document.head.appendChild(style);
