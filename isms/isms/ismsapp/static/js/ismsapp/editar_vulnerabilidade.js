document.addEventListener('DOMContentLoaded', function () {
  buildAmeacasCheckboxes();
  initAmeacasSearch();
  initAtivoSearch();
  initSubmitLoadingState();
});

function initAtivoSearch() {
  const filters = document.querySelectorAll('.searchable-filter');

  filters.forEach(function (filterInput) {
    const targetId = filterInput.dataset.targetSelect;
    const select = document.getElementById(targetId);

    if (!select) return;

    const options = Array.from(select.options);

    filterInput.addEventListener('input', function () {
      const term = this.value.toLowerCase().trim();

      select.innerHTML = '';

      let matchesFound = false;

      options.forEach(function (option) {
        const matches = option.text.toLowerCase().includes(term);

        if (matches || option.selected) {
          select.appendChild(option);
          matchesFound = true;
        }
      });

      if (!matchesFound) {
        const emptyOption = document.createElement('option');
        emptyOption.text = 'Nenhum ativo encontrado';
        emptyOption.disabled = true;
        emptyOption.selected = true;
        select.appendChild(emptyOption);
      }
    });
  });
}

function buildAmeacasCheckboxes() {
  const select = document.querySelector('select[name="ameacas"]');
  const container = document.getElementById('ameacas-checkbox-list');
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

function initAmeacasSearch() {
  const input = document.getElementById('ameacas-search');
  const container = document.getElementById('ameacas-checkbox-list');
  if (!input || !container) return;

  input.addEventListener('input', function () {
    const term = this.value.toLowerCase().trim();
    container.querySelectorAll('.checkbox-asset-item').forEach(function (item) {
      item.style.display = (!term || item.dataset.label.includes(term)) ? '' : 'none';
    });
  });
}

function updateSummary() {
  const countEl = document.getElementById('ameacas-count');
  if (countEl) {
    countEl.textContent = document.querySelectorAll('#ameacas-checkbox-list .asset-cb:checked').length;
  }
}

function initSubmitLoadingState() {
  const form = document.querySelector('form');
  if (!form) return;

  form.addEventListener('submit', function () {
    const button = this.querySelector('.btn-confirm');
    if (!button) return;

    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Salvando...';
  });
}
