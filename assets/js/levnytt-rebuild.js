(function () {
  'use strict';

  function initialiseMenu() {
    var toggle = document.querySelector('.ln-menu-toggle');
    var nav = document.querySelector('.ln-primary-nav');
    if (!toggle || !nav) return;
    function closeMenu(returnFocus) {
      nav.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', document.documentElement.lang === 'no' ? 'Åpne meny' : 'Öppna meny');
      if (returnFocus) toggle.focus();
    }
    toggle.addEventListener('click', function () {
      var open = !nav.classList.contains('is-open');
      nav.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? (document.documentElement.lang === 'no' ? 'Lukk meny' : 'Stäng meny') : (document.documentElement.lang === 'no' ? 'Åpne meny' : 'Öppna meny'));
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && nav.classList.contains('is-open')) closeMenu(true);
    });
    nav.addEventListener('click', function (event) {
      if (event.target.closest('a') && window.matchMedia('(max-width: 67rem)').matches) closeMenu(false);
    });
    window.addEventListener('resize', function () {
      if (!window.matchMedia('(max-width: 67rem)').matches) closeMenu(false);
    });
  }

  function initialiseLegacyFaq() {
    document.querySelectorAll('.faq-question').forEach(function (button, index) {
      var item = button.closest('.faq-item');
      var answer = item && item.querySelector('.faq-answer');
      if (!item || !answer) return;
      var answerId = answer.id || 'ln-faq-answer-' + index;
      answer.id = answerId;
      button.type = 'button';
      button.setAttribute('aria-controls', answerId);
      button.setAttribute('aria-expanded', String(item.classList.contains('active')));
      answer.hidden = !item.classList.contains('active');
      button.addEventListener('click', function () {
        var open = button.getAttribute('aria-expanded') !== 'true';
        item.classList.toggle('active', open);
        button.setAttribute('aria-expanded', String(open));
        answer.hidden = !open;
      });
    });
  }

  function ensureSponsorAttribution() {
    document.querySelectorAll('a[href*="neolifeshop.com"]').forEach(function (link) {
      var url;
      try { url = new URL(link.href); } catch (error) { return; }
      if (!url.searchParams.has('sponsor') && !url.searchParams.has('sponsorId')) {
        url.searchParams.set('sponsor', '41-830928');
        link.href = url.toString();
      }
      link.target = '_blank';
      ['nofollow', 'sponsored', 'noopener', 'noreferrer'].forEach(function (value) { link.relList.add(value); });
    });
  }

  function trackNeoLifeClicks() {
    document.addEventListener('click', function (event) {
      var link = event.target.closest && event.target.closest('a[href*="neolifeshop.com"]');
      if (!link || !/41-830928/.test(link.href) || !navigator.sendBeacon) return;
      var payload = {
        cta_id: link.href.indexOf('registration') !== -1 ? 'levnytt-neolife-registration' : 'levnytt-neolife-shop',
        page_path: window.location.pathname,
        destination: link.href
      };
      try { navigator.sendBeacon('/events/cta-click', new Blob([JSON.stringify(payload)], { type: 'application/json' })); } catch (error) { /* best effort */ }
    });
  }

  function initialiseGeoDismiss() {
    var button = document.querySelector('[data-dismiss-geo]');
    if (!button) return;
    button.addEventListener('click', function () {
      var banner = button.closest('.ln-geo-banner');
      if (banner) banner.remove();
    });
  }

  function init() {
    initialiseMenu();
    initialiseLegacyFaq();
    ensureSponsorAttribution();
    trackNeoLifeClicks();
    initialiseGeoDismiss();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
}());
