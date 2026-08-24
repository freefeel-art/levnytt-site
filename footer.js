/* Compatibility loader for legacy pages outside the canonical rebuild. */
(function () {
  'use strict';
  var language = document.documentElement.lang && document.documentElement.lang.toLowerCase().indexOf('no') === 0 ? 'no' : 'sv';
  fetch('/assets/fragments/footer-' + language + '.html')
    .then(function (response) { if (!response.ok) throw new Error('footer unavailable'); return response.text(); })
    .then(function (markup) {
      var old = document.querySelector('footer');
      if (old) old.outerHTML = markup;
      else document.body.insertAdjacentHTML('beforeend', markup);
    })
    .catch(function () { /* Content remains usable without the enhancement. */ });
}());
