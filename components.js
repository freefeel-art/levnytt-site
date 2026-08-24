/* Compatibility attribution guard. Canonical pages use levnytt-rebuild.js. */
(function () {
  'use strict';
  document.querySelectorAll('a[href*="neolifeshop.com"]').forEach(function (link) {
    var url;
    try { url = new URL(link.href); } catch (error) { return; }
    if (!url.searchParams.has('sponsor') && !url.searchParams.has('sponsorId')) url.searchParams.set('sponsor', '41-830928');
    link.href = url.toString();
    link.target = '_blank';
    ['nofollow', 'sponsored', 'noopener', 'noreferrer'].forEach(function (value) { link.relList.add(value); });
  });
}());
