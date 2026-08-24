(function () {
  'use strict';
  function number(value, decimals) { return new Intl.NumberFormat('sv-SE', { minimumFractionDigits: decimals, maximumFractionDigits: decimals }).format(value); }
  var ldcInput = document.getElementById('ldc-price');
  var ldcResult = document.getElementById('ldc-result');
  var superInput = document.getElementById('super10-price');
  var superResult = document.getElementById('super10-result');
  function calculateProducts() {
    [[ldcInput, ldcResult, 6], [superInput, superResult, 11]].forEach(function (entry) {
      if (!entry[0] || !entry[1]) return;
      var value = Number(entry[0].value);
      var valid = Number.isFinite(value) && value >= 0;
      entry[0].setAttribute('aria-invalid', String(!valid));
      entry[1].textContent = valid ? number(value / entry[2], 2) : '—';
    });
  }
  [ldcInput, superInput].forEach(function (input) { if (input) input.addEventListener('input', calculateProducts); });
  calculateProducts();
  var slider = document.getElementById('monthly-purchase');
  var purchase = document.getElementById('purchase-display');
  var monthly = document.getElementById('monthly-savings');
  var annual = document.getElementById('annual-savings');
  function calculateMembership() {
    if (!slider || !purchase || !monthly || !annual) return;
    var value = Number(slider.value);
    purchase.textContent = number(value, 0);
    monthly.textContent = number(value * 0.2, 0);
    annual.textContent = number(value * 0.2 * 12, 0);
  }
  if (slider) slider.addEventListener('input', calculateMembership);
  calculateMembership();
}());
