/**
 * Avaliação de Riscos — avaliacao_riscos.js
 * Handles interactive features for risk evaluation
 */

document.addEventListener('DOMContentLoaded', function () {
  initializeRiskSearch();
  initializeDecisionOptions();
  initializeFormValidation();
  highlightSelectedRisk();
  autoPreselectDecision();
});

/**
 * Highlight the currently selected risk in the list view (if any).
 * Driven by the ?risco_id= query param so it survives a page refresh.
 */
function highlightSelectedRisk() {
  const params = new URLSearchParams(window.location.search);
  const selectedId = params.get('risco_id');
  if (!selectedId) return;

  const item = document.querySelector(`.risk-list-item[data-risk-id="${selectedId}"]`);
  if (item) {
    item.classList.add('selected');
    item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

/**
 * Live search/filter across risk cards in the list view.
 * Searches both the risk name and asset name.
 * Shows a "no results" message when nothing matches.
 */
function initializeRiskSearch() {
  const input = document.getElementById('riskSearch');
  if (!input) return;

  const noResults = document.getElementById('noResults');

  input.addEventListener('input', function () {
    const query = this.value.toLowerCase().trim();
    const items = document.querySelectorAll('.risk-list-item');
    let visible = 0;

    items.forEach(function (item) {
      const text = item.textContent.toLowerCase();
      const match = !query || text.includes(query);
      item.style.display = match ? '' : 'none';
      if (match) visible++;
    });

    if (noResults) {
      noResults.style.display = visible === 0 ? 'block' : 'none';
    }
  });
}

/**
 * Visual feedback when a decision radio is selected.
 * The heavy lifting is done by CSS, but we keep the handler for
 * any future additional logic (analytics, warnings, etc.).
 */
function initializeDecisionOptions() {
  const radios = document.querySelectorAll('input[name="decisao"]');
  radios.forEach(function (radio) {
    radio.addEventListener('change', function () {
      // Future hook: show confirmation prompt for "aceitar" on high-risk items
    });
  });
}

/**
 * Pre-select the recommended decision radio based on the badge already
 * rendered by the server.  This is a progressive-enhancement fallback:
 * the template already sets `checked` via Django, but this guards against
 * edge cases where neither was checked (e.g. borderline risk).
 */
function autoPreselectDecision() {
  const anyChecked = document.querySelector('input[name="decisao"]:checked');
  if (anyChecked) return; // already set server-side

  // Check whether the status badge says "ACEITÁVEL"
  const statusBadge = document.querySelector('.criteria-item .badge-success');
  if (statusBadge) {
    const radio = document.querySelector('input[name="decisao"][value="aceitar"]');
    if (radio) radio.checked = true;
  }
}

/**
 * Form validation — prevent submission without a decision.
 */
function initializeFormValidation() {
  const form = document.querySelector('form');
  if (!form) return;

  form.addEventListener('submit', function (e) {
    const checked = this.querySelector('input[name="decisao"]:checked');
    if (!checked) {
      e.preventDefault();
      showValidationError('Por favor, selecione uma decisão antes de confirmar a avaliação.');
    }
  });
}

/**
 * Show an inline validation error rather than a browser alert.
 * Inserts a dismissible banner above the decision section.
 */
function showValidationError(message) {
  // Remove existing error if any
  const existing = document.getElementById('validation-error');
  if (existing) existing.remove();

  const banner = document.createElement('div');
  banner.id = 'validation-error';
  banner.className = 'alert alert-error';
  banner.style.cssText = 'margin-bottom:1rem; animation: fadeIn .2s ease;';
  banner.textContent = message;

  const decisionSection = document.querySelector('.decision-options');
  if (decisionSection) {
    decisionSection.parentElement.insertBefore(banner, decisionSection);
    banner.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  // Auto-dismiss after 5 s
  setTimeout(function () { banner.remove(); }, 5000);
}