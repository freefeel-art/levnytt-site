(function () {
  'use strict';
  var search = document.getElementById('idx-search');
  var chips = Array.prototype.slice.call(document.querySelectorAll('#js-chips .idx-chip'));
  var cards = Array.prototype.slice.call(document.querySelectorAll('.idx-card'));
  var sections = Array.prototype.slice.call(document.querySelectorAll('.idx-cat'));
  var count = document.getElementById('idx-count');
  if (!search || !cards.length || !count) return;
  var activeCategory = 'alla';
  function normalise(value) { return value.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); }
  function filter() {
    var term = normalise(search.value.trim());
    var visible = 0;
    cards.forEach(function (card) {
      var categoryMatch = activeCategory === 'alla' || card.dataset.cat === activeCategory;
      var searchMatch = !term || normalise((card.dataset.search || '') + ' ' + card.textContent).indexOf(term) !== -1;
      var show = categoryMatch && searchMatch;
      card.hidden = !show;
      if (show) visible += 1;
    });
    sections.forEach(function (section) { section.hidden = !section.querySelector('.idx-card:not([hidden])'); });
    count.textContent = visible === 1 ? '1 artikel' : visible + ' artiklar';
    var empty = document.getElementById('js-empty');
    if (empty) empty.hidden = visible !== 0;
  }
  search.addEventListener('input', filter);
  chips.forEach(function (chip) {
    chip.type = 'button';
    chip.setAttribute('aria-pressed', String(chip.classList.contains('active')));
    chip.addEventListener('click', function () {
      activeCategory = chip.dataset.cat || 'alla';
      chips.forEach(function (item) {
        var selected = item === chip;
        item.classList.toggle('active', selected);
        item.setAttribute('aria-pressed', String(selected));
      });
      filter();
    });
  });
  filter();
}());
