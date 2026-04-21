/**
 * Deteccao de Ameaca - Threat Detection
 *
 * Handles interactions for the threat detection page:
 * - Checkbox list built from hidden Django <select multiple> for ativos
 * - Live search filter over checkbox items
 * - Selection counter summary
 * - Form validation
 * - Modal for threats display
 */

document.addEventListener('DOMContentLoaded', function () {
  buildAtivosCheckboxes();
  initAtivosSearch();
  initializeFormValidation();
  initializeModal();
});

/* ── Checkbox builder ─────────────────────────────────────────────── */

/**
 * Reads every <option> from the hidden Django-rendered <select name="ativos">
 * and creates a matching visible checkbox for each one.
 * On tick/untick, the hidden select's option.selected is kept in sync,
 * so Django form submission works unchanged.
 */
function buildAtivosCheckboxes() {
  const select = document.querySelector('select[name="ativos"]');
  const container = document.getElementById('ativos-checkbox-list');
  if (!select || !container) return;

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
      // Clear validation error on the checkbox list when a box is ticked
      if (this.checked) {
        clearFieldError(document.getElementById('ativos-checkbox-list'));
      }
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

/* ── Live search filter ───────────────────────────────────────────── */

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

/* ── Selection counter ────────────────────────────────────────────── */

function updateSummary() {
  const countEl = document.getElementById('ativos-count');
  if (countEl) {
    countEl.textContent = document.querySelectorAll('.asset-cb:checked').length;
  }
}

/* ── Form validation ──────────────────────────────────────────────── */

function initializeFormValidation() {
  const form = document.querySelector('.threat-form');
  if (!form) return;

  const nomeField   = form.querySelector('[name="nome"]');
  // The hidden select holds the actual submitted values — validate against it
  const ativosField = form.querySelector('select[name="ativos"]');

  form.addEventListener('submit', function (e) {
    let isValid = true;

    if (!nomeField.value.trim()) {
      showFieldError(nomeField, 'Nome da ameaça é obrigatório');
      isValid = false;
    } else {
      clearFieldError(nomeField);
    }

    const noneSelected = !ativosField ||
      Array.from(ativosField.options).every(function (o) { return !o.selected; });

    // Attach the error to the visible checkbox list, not the hidden select
    const errorAnchor = document.getElementById('ativos-checkbox-list') || ativosField;
    if (noneSelected) {
      showFieldError(errorAnchor, 'Selecione pelo menos um ativo afetado');
      isValid = false;
    } else {
      clearFieldError(errorAnchor);
    }

    if (!isValid) e.preventDefault();
  });

  // Real-time: clear nome error on blur once filled
  if (nomeField) {
    nomeField.addEventListener('blur', function () {
      if (!this.value.trim()) {
        showFieldError(this, 'Nome da ameaça é obrigatório');
      } else {
        clearFieldError(this);
      }
    });
  }
}

/* ── Error helpers ────────────────────────────────────────────────── */

function showFieldError(field, message) {
  if (!field) return;
  field.style.borderColor     = '#ef4444';
  field.style.backgroundColor = 'rgba(239, 68, 68, 0.05)';

  clearFieldError(field); // remove any pre-existing error first

  const errorMsg = document.createElement('p');
  errorMsg.style.cssText = 'color:#f87171;font-size:.73rem;margin-top:.4rem';
  errorMsg.textContent = message;
  field.parentNode.insertBefore(errorMsg, field.nextSibling);
}

function clearFieldError(field) {
  if (!field) return;
  field.style.borderColor     = '';
  field.style.backgroundColor = '';

  const next = field.nextElementSibling;
  if (next && next.tagName === 'P' && next.style.color === 'rgb(248, 113, 113)') {
    next.remove();
  }
}

/* ── Modal ────────────────────────────────────────────────────────── */

function openThreatsModal() {
  const modal = document.getElementById('threatsModal');
  if (modal) {
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
}

function closeThreatsModal() {
  const modal = document.getElementById('threatsModal');
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
  }
}

function initializeModal() {
  const modal = document.getElementById('threatsModal');
  if (modal) {
    modal.addEventListener('click', function (e) {
      if (e.target === modal) closeThreatsModal();
    });
  }

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeThreatsModal();
  });
}