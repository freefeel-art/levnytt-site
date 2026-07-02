// LevNytt.se — Product Entity Data Module
// Single source of truth for product prices, shop URLs, and entity lookups.
// Replaces the hardcoded productMap in components.js.
// Load with: <script src="/content/products/product-data.js" defer></script>
// API: window.LevNyttProductData

(function () {
  var SPONSOR = '41-830928';
  var SHOP_BASE = 'https://se.neolifeshop.com';

  // ============================================================
  // PRICE DATA — all 57 products from LEVNYTT-PRICE-DATABASE.md
  // Indexed by NeoLife product code.
  // ============================================================
  var prices = {
    16: { name: 'Super 10', packaging: '1 l', customer: 254, distr: 200, savings_sek: 54, savings_pct: 21.3, cat: 'home_care' },
    17: { name: 'Super 10', packaging: '5 l', customer: 1034, distr: 816, savings_sek: 218, savings_pct: 21.1, cat: 'home_care' },
    18: { name: 'Super 10', packaging: '10 l', customer: 1993, distr: 1495, savings_sek: 498, savings_pct: 25.0, cat: 'home_care' },
    19: { name: 'Super 10', packaging: '25 l', customer: 4519, distr: 3389, savings_sek: 1130, savings_pct: 25.0, cat: 'home_care' },
    21: { name: 'LDC', packaging: '1 l', customer: 268, distr: 211, savings_sek: 57, savings_pct: 21.3, cat: 'home_care' },
    25: { name: 'LDC', packaging: '5 l', customer: 1091, distr: 861, savings_sek: 230, savings_pct: 21.1, cat: 'home_care' },
    42: { name: 'Soft', packaging: '1 l', customer: 255, distr: 201, savings_sek: 54, savings_pct: 21.2, cat: 'home_care' },
    144: { name: 'G1', packaging: '5 kg', customer: 729, distr: 575, savings_sek: 154, savings_pct: 21.1, cat: 'home_care' },
    303: { name: 'Handsprayflaska', packaging: '500 ml', customer: 29, distr: null, cat: 'accessories' },
    308: { name: 'Blandflaska', packaging: '500 ml', customer: 24, distr: null, cat: 'accessories' },
    310: { name: 'Rich Revitalizing Shampoo', packaging: '250 ml', customer: 166, distr: 131, savings_sek: 35, savings_pct: 21.1, cat: 'personal_care' },
    311: { name: 'Mild Revitalizing Shampoo', packaging: '250 ml', customer: 166, distr: 131, savings_sek: 35, savings_pct: 21.1, cat: 'personal_care' },
    312: { name: 'Enriching Conditioner', packaging: '250 ml', customer: 158, distr: 125, savings_sek: 33, savings_pct: 20.9, cat: 'personal_care' },
    314: { name: 'Refreshing Bath & Shower Gel', packaging: '250 ml', customer: 208, distr: 164, savings_sek: 44, savings_pct: 21.2, cat: 'personal_care' },
    315: { name: 'Moisturizing Hand & Body Lotion', packaging: '250 ml', customer: 167, distr: 131, savings_sek: 36, savings_pct: 21.6, cat: 'personal_care' },
    316: { name: 'Aloe Vera Gel', packaging: '100 ml', customer: 207, distr: 164, savings_sek: 43, savings_pct: 20.8, cat: 'personal_care' },
    360: { name: 'Balancing Tonic', packaging: '100 ml', customer: 321, distr: 252, savings_sek: 69, savings_pct: 21.5, cat: 'skin_care' },
    361: { name: 'Cleansing Milk', packaging: '150 ml', customer: 397, distr: 312, savings_sek: 85, savings_pct: 21.4, cat: 'skin_care' },
    362: { name: 'Cleansing Gel', packaging: '150 ml', customer: 397, distr: 312, savings_sek: 85, savings_pct: 21.4, cat: 'skin_care' },
    364: { name: 'Moisturizing Cream', packaging: '75 ml', customer: 490, distr: 386, savings_sek: 104, savings_pct: 21.2, cat: 'skin_care' },
    365: { name: 'Ultra Moisturizing Cream', packaging: '75 ml', customer: 490, distr: 386, savings_sek: 104, savings_pct: 21.2, cat: 'skin_care' },
    366: { name: 'Hydrating Serum', packaging: '30 ml', customer: 650, distr: 511, savings_sek: 139, savings_pct: 21.4, cat: 'skin_care' },
    367: { name: 'Ultra Hydrating Serum', packaging: '30 ml', customer: 650, distr: 511, savings_sek: 139, savings_pct: 21.4, cat: 'skin_care' },
    368: { name: 'Insta-Lift Eye Gel', packaging: '15 ml', customer: 304, distr: 239, savings_sek: 65, savings_pct: 21.4, cat: 'skin_care' },
    369: { name: 'Rejuvenating Rich Cream', packaging: '50 ml', customer: 588, distr: 462, savings_sek: 126, savings_pct: 21.4, cat: 'skin_care' },
    551: { name: 'Sustained Release Vitamin C', packaging: '120 tab', customer: 358, distr: 282, savings_sek: 76, savings_pct: 21.2, cat: 'supplements' },
    552: { name: 'All C', packaging: '120 tab', customer: 259, distr: 205, savings_sek: 54, savings_pct: 20.8, cat: 'supplements' },
    555: { name: 'Garlic Allium Complex', packaging: '60 tab', customer: 235, distr: 184, savings_sek: 51, savings_pct: 21.7, cat: 'supplements' },
    560: { name: 'Acidophilus Plus', packaging: '60 kaps', customer: 520, distr: 409, savings_sek: 111, savings_pct: 21.3, cat: 'supplements' },
    562: { name: 'Vitamin E', packaging: '100 kaps', customer: 387, distr: 305, savings_sek: 82, savings_pct: 21.2, cat: 'supplements' },
    566: { name: 'Carotenoid Complex', packaging: '90 kaps', customer: 736, distr: 579, savings_sek: 157, savings_pct: 21.3, cat: 'supplements' },
    576: { name: 'Formula IV', packaging: '100 kaps', customer: 539, distr: 424, savings_sek: 115, savings_pct: 21.3, cat: 'supplements' },
    590: { name: 'Multi', packaging: '60 tab', customer: 249, distr: 196, savings_sek: 53, savings_pct: 21.3, cat: 'supplements' },
    608: { name: 'NeoLife Shaker', packaging: '1 st', customer: 41, distr: null, cat: 'accessories' },
    691: { name: 'Formula IV Plus', packaging: '60 tab/kaps', customer: 486, distr: 383, savings_sek: 103, savings_pct: 21.2, cat: 'supplements' },
    724: { name: 'Kal-Mag Plus D', packaging: '180 tab', customer: 240, distr: 190, savings_sek: 50, savings_pct: 20.8, cat: 'supplements' },
    731: { name: 'Aloe Vera Plus', packaging: '1 l', customer: 224, distr: 176, savings_sek: 48, savings_pct: 21.4, cat: 'supplements' },
    735: { name: 'Tre', packaging: '750 ml', customer: 492, distr: 387, savings_sek: 105, savings_pct: 21.3, cat: 'supplements' },
    740: { name: 'Vita Squares', packaging: '180 tuggtab', customer: 355, distr: 280, savings_sek: 75, savings_pct: 21.1, cat: 'supplements' },
    789: { name: 'Beta Guard', packaging: '90 tab', customer: 354, distr: 279, savings_sek: 75, savings_pct: 21.2, cat: 'supplements' },
    790: { name: 'Flavonoid Complex', packaging: '60 tab', customer: 284, distr: 224, savings_sek: 60, savings_pct: 21.1, cat: 'supplements' },
    800: { name: 'Botanical Balance', packaging: '120 tab', customer: 704, distr: 554, savings_sek: 150, savings_pct: 21.3, cat: 'supplements' },
    805: { name: 'Magnesium Complex', packaging: '60 tab', customer: 231, distr: 182, savings_sek: 49, savings_pct: 21.2, cat: 'supplements' },
    820: { name: 'Resp-X', packaging: '90 tab', customer: 268, distr: 211, savings_sek: 57, savings_pct: 21.3, cat: 'supplements' },
    830: { name: 'Chelated Zinc', packaging: '90 tab', customer: 213, distr: 167, savings_sek: 46, savings_pct: 21.6, cat: 'supplements' },
    840: { name: 'UpBeet', packaging: '30 port', customer: 818, distr: 643, savings_sek: 175, savings_pct: 21.4, cat: 'supplements' },
    850: { name: 'Fibre Tablets', packaging: '120 tab', customer: 244, distr: 192, savings_sek: 52, savings_pct: 21.3, cat: 'supplements' },
    860: { name: 'Elevate', packaging: '30 port', customer: 661, distr: 520, savings_sek: 141, savings_pct: 21.3, cat: 'supplements' },
    865: { name: 'Vegan D', packaging: '120 tab', customer: 210, distr: 165, savings_sek: 45, savings_pct: 21.4, cat: 'supplements' },
    892: { name: 'Cruciferous Plus', packaging: '60 tab', customer: 301, distr: 236, savings_sek: 65, savings_pct: 21.6, cat: 'supplements' },
    915: { name: 'NeoLifeShake (Vanilj)', packaging: '15 sachet', customer: 776, distr: 612, savings_sek: 164, savings_pct: 21.1, cat: 'weight_management' },
    916: { name: 'NeoLifeShake (Choklad)', packaging: '15 sachet', customer: 776, distr: 612, savings_sek: 164, savings_pct: 21.1, cat: 'weight_management' },
    917: { name: 'NeoLifeShake (Bär)', packaging: '15 sachet', customer: 776, distr: 612, savings_sek: 164, savings_pct: 21.1, cat: 'weight_management' },
    920: { name: 'NeoLifeTea', packaging: '30 portioner', customer: 415, distr: 328, savings_sek: 87, savings_pct: 21.0, cat: 'weight_management' },
    927: { name: 'Tre-en-en', packaging: '120 kaps', customer: 562, distr: 442, savings_sek: 120, savings_pct: 21.4, cat: 'supplements' },
    929: { name: 'Omega-3 Plus', packaging: '90 kaps', customer: 422, distr: 332, savings_sek: 90, savings_pct: 21.3, cat: 'supplements' },
    930: { name: 'CoQ10', packaging: '60 kaps', customer: 586, distr: 461, savings_sek: 125, savings_pct: 21.3, cat: 'supplements' },
    935: { name: 'Bio-Tone', packaging: '120 tab', customer: 527, distr: 416, savings_sek: 111, savings_pct: 21.1, cat: 'supplements' },
    942: { name: 'Pro Vitality+', packaging: '30 sachet', customer: 647, distr: 509, savings_sek: 138, savings_pct: 21.3, cat: 'supplements' },
    950: { name: 'NeoLifeBar', packaging: '15 st', customer: 465, distr: 404, savings_sek: 61, savings_pct: 13.1, cat: 'weight_management' },
    1573: { name: 'Pump 1L', packaging: '1 st', customer: 42, distr: null, cat: 'accessories' },
    1583: { name: 'Pump 250 ml', packaging: '1 st', customer: 15, distr: null, cat: 'accessories' },
    1584: { name: 'Dunkpump Super 10 5L', packaging: '1 st', customer: 133, distr: null, cat: 'accessories' },
    1585: { name: 'Dunkpump Super 10 10L', packaging: '1 st', customer: 60, distr: null, cat: 'accessories' },
    1586: { name: 'Dunkpump LDC 5L', packaging: '1 st', customer: 86, distr: null, cat: 'accessories' },
    1650: { name: 'Vitamin box', packaging: '1 st', customer: 32, distr: null, cat: 'accessories' },
    5001: { name: 'Vitamin box (stor)', packaging: '1 st', customer: 38, distr: null, cat: 'accessories' }
  };

  // ============================================================
  // PAGE SLUG TO ENTITY MAP
  // Maps the site's URL slugs to primary NeoLife product codes.
  // This is the replacement for components.js productMap.
  // ============================================================
  var slugIndex = {
    '/golden-home-care/': { code: 21, name: 'LDC', shop: '/i/shop/home-care/ldc.html' },
    '/super-10/': { code: 16, name: 'Super 10', shop: '/i/shop/home-care/super-10.html' },
    '/neolife-pro-vitality/': { code: 942, name: 'Pro Vitality+', shop: '/i/shop/nutrition/pro-vitality-plus.html' },
    '/neolife-carotenoid-complex/': { code: 566, name: 'Carotenoid Complex', shop: '/i/shop/nutrition/carotenoid-complex.html' },
    '/neolife-omega-3-plus/': { code: 929, name: 'Omega-3 Plus', shop: '/i/shop/nutrition/omega-3-plus.html' },
    '/neolife-tre-en-en/': { code: 927, name: 'Tre-en-en', shop: '/i/shop/nutrition/tre-en-en.html' },
    '/neolife-viktkontroll/': { code: 915, name: 'NeoLifeShake', shop: '/i/shop/weight-management/neolifeshake.html' },
    '/neolife-acidophilus-plus/': { code: 560, name: 'Acidophilus Plus', shop: '/i/shop/nutrition/acidophilus-plus.html' },
    '/neolife-betaguard/': { code: 789, name: 'Beta Guard', shop: '/i/shop/nutrition/beta-guard.html' },
    '/neolife-coq10/': { code: 930, name: 'CoQ10', shop: '/i/shop/nutrition/coq10.html' },
    '/neolife-elevate/': { code: 860, name: 'Elevate', shop: '/i/shop/nutrition/elevate.html' },
    '/neolife-flavonoid-complex/': { code: 790, name: 'Flavonoid Complex', shop: '/i/shop/nutrition/flavonoid-complex.html' },
    '/neolife-formula-iv/': { code: 576, name: 'Formula IV', shop: '/i/shop/nutrition/formula-iv.html' },
    '/neolife-vitamin-d/': { code: 865, name: 'Vegan D', shop: '/i/shop/nutrition/vitamin-d.html' },
    '/neolife-vitamin-e/': { code: 562, name: 'Vitamin E', shop: '/i/shop/nutrition/wheat-germ-oil-vitamin-e.html' },
    '/neolife-magnesium-complex/': { code: 805, name: 'Magnesium Complex', shop: '/i/shop/nutrition/magnesium-complex.html' },
    '/neolife-chelated-zinc/': { code: 830, name: 'Chelated Zinc', shop: '/i/shop/nutrition/chelated-zinc.html' },
    '/neolife-upbeet/': { code: 840, name: 'UpBeet', shop: '/i/shop/nutrition/upbeet.html' },
    '/neolife-resp-x/': { code: 820, name: 'Resp-X', shop: '/i/shop/nutrition/resp-x.html' },
    '/neolife-garlic-allium-complex/': { code: 555, name: 'Garlic Allium Complex', shop: '/i/shop/nutrition/garlic-allium-complex.html' },
    '/neolife-cruciferous-plus/': { code: 892, name: 'Cruciferous Plus', shop: '/i/shop/nutrition/cruciferous-plus.html' },
    '/neolife-botanical-balance/': { code: 800, name: 'Botanical Balance', shop: '/i/shop/nutrition/botanical-balance.html' },
    '/neolife-kalmag-plus-d/': { code: 724, name: 'Kal-Mag Plus D', shop: '/i/shop/nutrition/kal-mag-plus-d.html' },
    '/neolife-shake-bar-tea/': { code: 915, name: 'NeoLifeShake', shop: '/i/shop/weight-management/neolifeshake.html' },
    '/neolife-formula-iv-plus/': { code: 691, name: 'Formula IV Plus', shop: '/i/shop/nutrition/formula-iv-plus.html' },
    '/neolife-sustained-vitamin-c/': { code: 551, name: 'Sustained Release Vitamin C', shop: '/i/shop/nutrition/sustained-release-vitamin-c.html' },
    '/neolife-fibre-tablets/': { code: 850, name: 'Fibre Tablets', shop: '/i/shop/nutrition/fibre-tablets.html' },
    '/neolife-aloe-vera-plus/': { code: 731, name: 'Aloe Vera Plus', shop: '/i/shop/nutrition/aloe-vera-plus.html' },
    '/neolife-g1/': { code: 144, name: 'G1', shop: '/i/shop/home-care/g1.html' },
    '/neolife-soft/': { code: 42, name: 'Soft', shop: '/i/shop/home-care/soft.html' },
    '/personlig-vard/': { code: 310, name: 'Rich Revitalizing Shampoo', shop: '/i/shop/personal-care/rich-shampoo.html' }
  };

  // ============================================================
  // PRICE DATA LOOKUPS
  // ============================================================

  function getPrice(code) {
    return prices[code] || null;
  }

  function getProductBySlug(slug) {
    var entry = slugIndex[slug];
    if (!entry) return null;
    var price = getPrice(entry.code);
    return {
      code: entry.code,
      name: entry.name,
      shopPath: entry.shop,
      price: price,
      shopUrl: SHOP_BASE + entry.shop + '?sponsor=' + SPONSOR
    };
  }

  function getShopUrl(slug) {
    var entry = slugIndex[slug];
    if (!entry) return null;
    return SHOP_BASE + entry.shop + '?sponsor=' + SPONSOR;
  }

  function formatPrice(sek) {
    if (sek === null || sek === undefined) return '';
    return sek.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ':-';
  }

  function formatPriceRange(min, max) {
    return formatPrice(min) + ' – ' + formatPrice(max);
  }

  function getPriceByCode(code) {
    return getPrice(code);
  }

  // ============================================================
  // SPONSOR LINK FIXING — replaces components.js fixLinks()
  // Uses slugIndex instead of hardcoded productMap.
  // ============================================================
  function fixLinks() {
    var currentPath = window.location.pathname.replace(/\/$/, '') + '/';
    var productEntry = slugIndex[currentPath];

    var links = document.querySelectorAll('a[href*="neolifeshop.com"]');
    links.forEach(function (link) {
      var href = link.getAttribute('href');

      if (href && href.indexOf('sponsor=') === -1 && href.indexOf('sponsorId=') === -1) {
        var separator = href.indexOf('?') !== -1 ? '&' : '?';
        link.setAttribute('href', href + separator + 'sponsor=' + SPONSOR);
      }

      if (productEntry && href && href.indexOf('registration') === -1 && href.indexOf('enrollment') === -1) {
        link.setAttribute('href', SHOP_BASE + productEntry.shop + '?sponsor=' + SPONSOR);
      }
    });
  }

  // ============================================================
  // INIT
  // ============================================================
  function init() {
    fixLinks();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // ============================================================
  // PUBLIC API
  // ============================================================
  window.LevNyttProductData = {
    getPrice: getPriceByCode,
    getProduct: getProductBySlug,
    getShopUrl: getShopUrl,
    formatPrice: formatPrice,
    formatPriceRange: formatPriceRange,
    slugIndex: slugIndex,
    fixLinks: fixLinks
  };

})();
