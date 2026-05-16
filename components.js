// LevNytt.se — Global components
// Translate + scroll-to-top för alla sidor

(function() {

  // CSS
  var style = document.createElement('style');
  style.textContent = `
    .scroll-top{position:fixed;bottom:80px;right:24px;width:44px;height:44px;background:#2D6A4F;border:none;border-radius:50%;cursor:pointer;display:none;align-items:center;justify-content:center;box-shadow:0 4px 16px rgba(0,0,0,0.2);z-index:9999;transition:all 0.25s;}
    .scroll-top:hover{background:#1B4332;}
    .scroll-top.visible{display:flex;}
    .scroll-top svg{width:20px;height:20px;stroke:#fff;fill:none;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round;}
    .translator-wrap{position:fixed;bottom:24px;right:24px;z-index:9999;}
    .translator-btn{background:#fff;border:1px solid #E0D8C8;border-radius:24px;padding:8px 16px;font-size:0.82rem;font-weight:600;color:#555;cursor:pointer;box-shadow:0 4px 16px rgba(0,0,0,0.12);display:flex;align-items:center;gap:6px;font-family:inherit;transition:all 0.25s;}
    .translator-btn:hover{border-color:#2D6A4F;color:#2D6A4F;}
    #goog-translate-wrap{display:none;position:absolute;bottom:48px;right:0;background:#fff;border:1px solid #E0D8C8;border-radius:8px;padding:8px;box-shadow:0 8px 32px rgba(0,0,0,0.15);min-width:180px;}
    #goog-translate-wrap.open{display:block;}
    .goog-te-gadget{font-size:0!important;}
    .goog-te-gadget .goog-te-combo{font-size:0.9rem;padding:6px 8px;border:1px solid #E0D8C8;border-radius:6px;width:100%;cursor:pointer;}
  `;
  document.head.appendChild(style);

  // Ylös-nuoli
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

  // Translator
  var wrap = document.createElement('div');
  wrap.className = 'translator-wrap';
  wrap.innerHTML = `
    <button class="translator-btn" onclick="document.getElementById('goog-translate-wrap').classList.toggle('open')" aria-label="Translate">
      &#127760; Translate
    </button>
    <div id="goog-translate-wrap">
      <div id="google_translate_element"></div>
    </div>
  `;
  document.body.appendChild(wrap);

  // Google Translate init
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
