/* Compatibility loader for legacy pages outside the canonical rebuild. */
(function () {
  'use strict';
  var language = document.documentElement.lang && document.documentElement.lang.toLowerCase().indexOf('no') === 0 ? 'no' : 'sv';
  fetch('/assets/fragments/header-' + language + '.html')
    .then(function (response) { if (!response.ok) throw new Error('header unavailable'); return response.text(); })
    .then(function (markup) {
      var old = document.querySelector('#site-nav, #levnytt-nav, .ln-site-header');
      if (old) old.outerHTML = markup;
      else document.body.insertAdjacentHTML('afterbegin', markup);
      var current = window.location.pathname.replace(/\/$/, '') || '/';
      document.querySelectorAll('.ln-primary-nav a[href^="/"]').forEach(function (link) {
        var path = new URL(link.href, window.location.origin).pathname.replace(/\/$/, '') || '/';
        if (path === current) link.setAttribute('aria-current', 'page');
      });
      if (!document.querySelector('script[src="/assets/js/levnytt-rebuild.js"]')) {
        var script = document.createElement('script');
        script.src = '/assets/js/levnytt-rebuild.js';
        script.defer = true;
        document.head.appendChild(script);
      }
    })
    .catch(function () { /* Content remains usable without the enhancement. */ });
}());
