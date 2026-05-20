/**
 * Avaliação de Riscos JavaScript
 * Handles interactive features for risk evaluation
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize interactive elements
  initializeRiskSelection();
  initializeRiskSearch();
  initializeDecisionOptions();
  initializeFormValidation();
});

/**
 * Initialize risk selection functionality
 */
function initializeRiskSelection() {
  const riskItems = document.querySelectorAll('.risk-list-item');
  const params = new URLSearchParams(window.location.search);
  const selectedRiskId = params.get('risco_id');

  riskItems.forEach(item => {
    const itemRiskId = item.dataset.riskId;
    if (selectedRiskId && itemRiskId === selectedRiskId) {
      item.classList.add('selected');
    }

    item.addEventListener('click', function(e) {
      e.preventDefault();
      const url = this.getAttribute('href');
      if (url) {
        window.location.href = url;
      }
    });
  });
}

/**
 * Initialize quick search across risk cards
 */
function initializeRiskSearch() {
  const input = document.getElementById('riskSearch');
  if (!input) return;

  input.addEventListener('input', function() {
    const query = this.value.toLowerCase();
    const items = document.querySelectorAll('.risk-list-item');

    items.forEach(item => {
      const text = item.textContent.toLowerCase();
      item.style.display = text.includes(query) ? 'flex' : 'none';
    });
  });
}

/**
 * Initialize decision option radio buttons
 */
function initializeDecisionOptions() {
  const radioButtons = document.querySelectorAll('input[name="decisao"]');

  radioButtons.forEach(radio => {
    radio.addEventListener('change', function() {
      // Visual feedback is handled by CSS, but we can add additional logic here
      const decisionValue = this.value;
      console.log('Risk decision selected:', decisionValue);
    });
  });
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
  const form = document.querySelector('form');

  if (form) {
    form.addEventListener('submit', function(e) {
      const decisaoInput = this.querySelector('input[name="decisao"]:checked');

      if (!decisaoInput) {
        e.preventDefault();
        alert('Selecione uma decisão (Aceitar ou Tratar).');
        return false;
      }

      return true;
    });
  }
}

/**
 * Format risk value for display
 * @param {number} value - The risk value
 * @returns {string} Formatted risk value
 */
function formatRiskValue(value) {
  return Math.round(value).toString();
}

/**
 * Get risk level color based on value
 * @param {number} value - The risk value
 * @returns {string} CSS color class
 */
function getRiskLevelColor(value) {
  if (value <= 3) return 'green';
  if (value <= 8) return 'yellow';
  if (value <= 15) return 'orange';
  return 'red';
}

/**
 * Toggle risk details visibility
 * @param {Element} element - The risk element to toggle
 */
function toggleRiskDetails(element) {
  element.classList.toggle('active');
}

/**
 * Handle risk acceptance
 */
function handleRiskAcceptance() {
  const decisaoInput = document.querySelector('input[name="decisao"][value="aceitar"]');
  if (decisaoInput) {
    decisaoInput.checked = true;
    decisaoInput.dispatchEvent(new Event('change', { bubbles: true }));
  }
}

/**
 * Handle risk treatment
 */
function handleRiskTreatment() {
  const decisaoInput = document.querySelector('input[name="decisao"][value="tratar"]');
  if (decisaoInput) {
    decisaoInput.checked = true;
    decisaoInput.dispatchEvent(new Event('change', { bubbles: true }));
  }
}

/**
 * Export risk evaluation for reporting
 */
function exportRiskEvaluation() {
  const riskName = document.querySelector('.risk-name-eval') ? document.querySelector('.risk-name-eval').textContent : 'Risk';
  const riskValue = document.querySelector('.value-number') ? document.querySelector('.value-number').textContent : '0';
  const decision = document.querySelector('input[name="decisao"]:checked') ? document.querySelector('input[name="decisao"]:checked').value : 'Not selected';

  const data = {
    riskName: riskName,
    riskValue: riskValue,
    decision: decision,
    timestamp: new Date().toISOString()
  };

  console.log('Risk Evaluation Data:', data);
  return data;
}

/**
 * Print risk evaluation report
 */
function printRiskEvaluation() {
  window.print();
}
