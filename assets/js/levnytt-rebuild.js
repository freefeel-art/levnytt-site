(function () {
  const toggle = document.querySelector('.ln-menu-toggle');
  const nav = document.querySelector('.ln-primary-nav');
  if (!toggle || !nav) return;
  toggle.addEventListener('click', function () {
    const open = nav.classList.toggle('is-open');
    toggle.setAttribute('aria-expanded', String(open));
  });
}());
