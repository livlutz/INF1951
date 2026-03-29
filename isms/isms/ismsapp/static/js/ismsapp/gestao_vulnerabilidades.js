/**
 * Gestão de Vulnerabilidades - Vulnerability Management
 *
 * Handles interactions for the vulnerability management page:
 * - Form validation
 * - Dynamic feedback
 * - Severity and priority highlighting
 */

document.addEventListener('DOMContentLoaded', function() {
  initializeFormValidation();
});

/**
 * Initialize form validation
 */
function initializeFormValidation() {
  const form = document.querySelector('.vulnerability-form');
  if (!form) return;

  // Get form fields
  const ativoField = form.querySelector('[name="ativo"]');
  const descricaoField = form.querySelector('[name="descricao"]');
  const severidadeField = form.querySelector('[name="nivel_severidade"]');
  const prioridadeField = form.querySelector('[name="prioridade_correcao"]');
  const submitBtn = form.querySelector('button[type="submit"]');

  // Add form submit validation
  form.addEventListener('submit', function(e) {
    let isValid = true;

    // Validate required fields
    if (!ativoField.value) {
      showFieldError(ativoField, 'Ativo afetado é obrigatório');
      isValid = false;
    } else {
      clearFieldError(ativoField);
    }

    if (!descricaoField.value.trim()) {
      showFieldError(descricaoField, 'Descrição da vulnerabilidade é obrigatória');
      isValid = false;
    } else {
      clearFieldError(descricaoField);
    }

    if (!severidadeField.value) {
      showFieldError(severidadeField, 'Selecione o nível de severidade');
      isValid = false;
    } else {
      clearFieldError(severidadeField);
    }

    if (!prioridadeField.value) {
      showFieldError(prioridadeField, 'Selecione a prioridade de correção');
      isValid = false;
    } else {
      clearFieldError(prioridadeField);
    }

    if (!isValid) {
      e.preventDefault();
    }
  });

  // Real-time validation on input
  ativoField.addEventListener('change', function() {
    if (this.value) {
      clearFieldError(this);
    }
  });

  descricaoField.addEventListener('blur', function() {
    if (!this.value.trim()) {
      showFieldError(this, 'Descrição da vulnerabilidade é obrigatória');
    } else {
      clearFieldError(this);
    }
  });

  severidadeField.addEventListener('change', function() {
    if (this.value) {
      clearFieldError(this);
    }
  });

  prioridadeField.addEventListener('change', function() {
    if (this.value) {
      clearFieldError(this);
    }
  });
}

/**
 * Show field error message
 */
function showFieldError(field, message) {
  clearFieldError(field);

  const errorElement = document.createElement('p');
  errorElement.className = 'field-error';
  errorElement.style.cssText = 'color:#f87171;font-size:.73rem;margin-top:.4rem;';
  errorElement.textContent = message;

  field.after(errorElement);
  field.style.borderColor = '#f87171';
}

/**
 * Clear field error message
 */
function clearFieldError(field) {
  const errorElement = field.nextElementSibling;
  if (errorElement && errorElement.className === 'field-error') {
    errorElement.remove();
  }
  field.style.borderColor = '';
}
