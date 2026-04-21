/**
 * Gestão de Vulnerabilidades - Vulnerability Management
 *
 * - Checkbox list built from hidden Django <select multiple> for ameacas
 * - Live search filter over checkbox items
 * - Selection counter summary
 * - Form validation for all fields
 */

document.addEventListener('DOMContentLoaded', function () {
  buildAmeacasCheckboxes();
  initAmeacasSearch();
  initializeFormValidation();
});

/* ── Checkbox builder ─────────────────────────────────────────────── */

/**
 * Reads every <option> from the hidden Django-rendered <select name="ameacas">
 * and creates a matching visible checkbox for each one.
 * Keeps the hidden select in sync so Django form submission works unchanged.
 */
function buildAmeacasCheckboxes() {
  const select    = document.querySelector('select[name="ameacas"]');
  const container = document.getElementById('ameacas-checkbox-list');
  if (!select || !container) return;

  Array.from(select.options).forEach(function (option) {
    const item       = document.createElement('label');
    item.className   = 'checkbox-asset-item';
    item.dataset.label = option.text.toLowerCase();

    const checkbox     = document.createElement('input');
    checkbox.type      = 'checkbox';
    checkbox.value     = option.value;
    checkbox.className = 'asset-cb';
    checkbox.checked   = option.selected;

    checkbox.addEventListener('change', function () {
      option.selected = this.checked;
      updateSummary();
      if (this.checked) clearAmeacasError();
    });

    const label       = document.createElement('span');
    label.className   = 'asset-cb-label';
    label.textContent = option.text;

    item.appendChild(checkbox);
    item.appendChild(label);
    container.appendChild(item);
  });

  updateSummary();
}

/* ── Live search ──────────────────────────────────────────────────── */

function initAmeacasSearch() {
  const input     = document.getElementById('ameacas-search');
  const container = document.getElementById('ameacas-checkbox-list');
  if (!input || !container) return;

  input.addEventListener('input', function () {
    const term = this.value.toLowerCase().trim();
    container.querySelectorAll('.checkbox-asset-item').forEach(function (item) {
      item.style.display = (!term || item.dataset.label.includes(term)) ? '' : 'none';
    });
  });
}

/* ── Selection counter ────────────────────────────────────────────── */

function updateSummary() {
  const countEl = document.getElementById('ameacas-count');
  if (countEl) countEl.textContent = document.querySelectorAll('.asset-cb:checked').length;
}

/* ── Ameacas error helpers ────────────────────────────────────────── */

function showAmeacasError(message) {
  const container = document.getElementById('ameacas-checkbox-list');
  if (container) container.style.borderColor = '#f87171';

  let errorEl = document.getElementById('ameacas-error');
  if (!errorEl) {
    errorEl    = document.createElement('p');
    errorEl.id = 'ameacas-error';
    errorEl.style.cssText = 'color:#f87171;font-size:.73rem;margin-top:.4rem;';
    const anchor = container || document.querySelector('select[name="ameacas"]');
    if (anchor) anchor.parentNode.insertBefore(errorEl, anchor.nextSibling);
  }
  errorEl.textContent  = message;
  errorEl.style.display = '';
}

function clearAmeacasError() {
  const container = document.getElementById('ameacas-checkbox-list');
  if (container) container.style.borderColor = '';

  const errorEl = document.getElementById('ameacas-error');
  if (errorEl) errorEl.style.display = 'none';
}

/* ── Form validation ──────────────────────────────────────────────── */

function initializeFormValidation() {
  const form = document.querySelector('.vulnerability-form');
  if (!form) return;

  const nomeField       = form.querySelector('[name="nome"]');
  const ameacasField    = form.querySelector('select[name="ameacas"]');
  const ativoField      = form.querySelector('[name="ativo"]');
  const descricaoField  = form.querySelector('[name="descricao"]');
  const severidadeField = form.querySelector('[name="nivel_severidade"]');
  const prioridadeField = form.querySelector('[name="prioridade_correcao"]');

  form.addEventListener('submit', function (e) {
    let isValid = true;

    // nome
    if (nomeField && !nomeField.value.trim()) {
      showFieldError(nomeField, 'Nome da vulnerabilidade é obrigatório');
      isValid = false;
    } else if (nomeField) {
      clearFieldError(nomeField);
    }

    // ameacas — validate via hidden select
    const noneSelected = !ameacasField ||
      Array.from(ameacasField.options).every(function (o) { return !o.selected; });
    if (noneSelected) {
      showAmeacasError('Selecione pelo menos uma ameaça associada');
      isValid = false;
    } else {
      clearAmeacasError();
    }

    // ativo
    if (ativoField && !ativoField.value) {
      showFieldError(ativoField, 'Ativo afetado é obrigatório');
      isValid = false;
    } else if (ativoField) {
      clearFieldError(ativoField);
    }

    // descricao (optional field — only validate if it exists in this form variant)
    if (descricaoField && !descricaoField.value.trim()) {
      showFieldError(descricaoField, 'Descrição da vulnerabilidade é obrigatória');
      isValid = false;
    } else if (descricaoField) {
      clearFieldError(descricaoField);
    }

    // nivel_severidade
    if (severidadeField && !severidadeField.value) {
      showFieldError(severidadeField, 'Selecione o nível de severidade');
      isValid = false;
    } else if (severidadeField) {
      clearFieldError(severidadeField);
    }

    // prioridade_correcao
    if (prioridadeField && !prioridadeField.value) {
      showFieldError(prioridadeField, 'Selecione a prioridade de correção');
      isValid = false;
    } else if (prioridadeField) {
      clearFieldError(prioridadeField);
    }

    if (!isValid) e.preventDefault();
  });

  // Real-time listeners
  if (nomeField) {
    nomeField.addEventListener('blur', function () {
      if (!this.value.trim()) showFieldError(this, 'Nome da vulnerabilidade é obrigatório');
      else clearFieldError(this);
    });
  }

  if (ativoField) {
    ativoField.addEventListener('change', function () {
      if (this.value) clearFieldError(this);
    });
  }

  if (descricaoField) {
    descricaoField.addEventListener('blur', function () {
      if (!this.value.trim()) showFieldError(this, 'Descrição da vulnerabilidade é obrigatória');
      else clearFieldError(this);
    });
  }

  if (severidadeField) {
    severidadeField.addEventListener('change', function () {
      if (this.value) clearFieldError(this);
    });
  }

  if (prioridadeField) {
    prioridadeField.addEventListener('change', function () {
      if (this.value) clearFieldError(this);
    });
  }
}

/* ── Generic field error helpers ─────────────────────────────────── */

function showFieldError(field, message) {
  clearFieldError(field);

  const errorEl       = document.createElement('p');
  errorEl.className   = 'field-error';
  errorEl.style.cssText = 'color:#f87171;font-size:.73rem;margin-top:.4rem;';
  errorEl.textContent = message;

  field.after(errorEl);
  field.style.borderColor = '#f87171';
}

function clearFieldError(field) {
  if (!field) return;
  const next = field.nextElementSibling;
  if (next && next.className === 'field-error') next.remove();
  field.style.borderColor = '';
}