document.addEventListener('DOMContentLoaded', function () {
  buildAtivosCheckboxes();
  initAtivosSearch();
});

function buildAtivosCheckboxes() {
  const select = document.querySelector('select[name="ativos"]');
  const container = document.getElementById('ativos-checkbox-list');
  if (!select || !container) return;

  container.innerHTML = '';

  Array.from(select.options).forEach(function (option) {
    const item = document.createElement('label');
    item.className = 'checkbox-asset-item';
    item.dataset.label = option.text.toLowerCase();

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.value = option.value;
    checkbox.className = 'asset-cb';
    checkbox.checked = option.selected;

    checkbox.addEventListener('change', function () {
      option.selected = this.checked;
      updateSummary();
    });

    const label = document.createElement('span');
    label.className = 'asset-cb-label';
    label.textContent = option.text;

    item.appendChild(checkbox);
    item.appendChild(label);
    container.appendChild(item);
  });

  updateSummary();
}

function initAtivosSearch() {
  const input = document.getElementById('ativos-search');
  const container = document.getElementById('ativos-checkbox-list');
  if (!input || !container) return;

  input.addEventListener('input', function () {
    const term = this.value.toLowerCase().trim();
    container.querySelectorAll('.checkbox-asset-item').forEach(function (item) {
      item.style.display = (!term || item.dataset.label.includes(term)) ? '' : 'none';
    });
  });
}

function updateSummary() {
  const countEl = document.getElementById('ativos-count');
  if (countEl) {
    countEl.textContent = document.querySelectorAll('#ativos-checkbox-list .asset-cb:checked').length;
  }
}
