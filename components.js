// LevNytt.se — Global components
// Brand system + scroll-to-top + sponsor-ID automaatio

(function() {

  var SPONSOR = '41-830928';
  var SHOP_BASE = 'https://se.neolifeshop.com';

  // ============================================================
  // BRAND SYSTEM — favicon, apple-touch-icon, OG image
  // ============================================================
  function injectBrandMeta() {
    if (document.querySelector('link[rel="icon"][href*="favicon"]')) return;

    var frag = document.createDocumentFragment();

    var favicon = document.createElement('link');
    favicon.rel = 'icon';
    favicon.type = 'image/svg+xml';
    favicon.href = '/assets/brand/favicon.svg';
    frag.appendChild(favicon);

    var apple = document.createElement('link');
    apple.rel = 'apple-touch-icon';
    apple.href = '/assets/brand/apple-touch-icon.png';
    frag.appendChild(apple);

    document.head.insertBefore(frag, document.head.firstChild);
  }

  // ============================================================
  // BRAND WATERMARK — inject hero-watermark.svg into .hero
  // ============================================================
  function injectHeroWatermark() {
    var hero = document.querySelector('.hero');
    if (!hero || hero.querySelector('.lv-watermark')) return;

    var wm = document.createElement('img');
    wm.className = 'lv-watermark';
    wm.src = '/assets/brand/hero-watermark.svg';
    wm.alt = '';
    wm.setAttribute('aria-hidden', 'true');
    wm.style.cssText = 'position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:80%;height:80%;pointer-events:none;z-index:1;';
    hero.style.position = 'relative';
    hero.style.overflow = 'hidden';
    hero.insertBefore(wm, hero.firstChild);
  }

  // ============================================================
  // BRAND AUTHOR AVATAR — replace initials with LV Mark SVG
  // ============================================================
  function injectBrandAvatar() {
    document.querySelectorAll('.ia-author-avatar').forEach(function(el) {
      if (el.querySelector('svg')) return;
      el.textContent = '';
      el.style.cssText = 'background:#1B4332;display:flex;align-items:center;justify-content:center;';
      var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('viewBox', '0 0 28 28');
      svg.setAttribute('width', '20');
      svg.setAttribute('height', '20');
      svg.setAttribute('fill', 'none');
      svg.innerHTML = '<rect x="5" y="4" width="4" height="18" rx="1" fill="#E8C870"/>' +
        '<rect x="5" y="18" width="11" height="3" rx="1" fill="#E8C870"/>' +
        '<rect x="16" y="4" width="3" height="18" rx="1" fill="#E8C870" transform="rotate(14 17.5 4)"/>' +
        '<rect x="24" y="4" width="3" height="18" rx="1" fill="#E8C870" transform="rotate(-14 25.5 4)"/>';
      el.appendChild(svg);
    });
  }

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

  // ============================================================
  // INIT — run on DOMContentLoaded
  // ============================================================
  function init() {
    fixLinks();
    injectBrandMeta();
    injectHeroWatermark();
    injectBrandAvatar();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
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
