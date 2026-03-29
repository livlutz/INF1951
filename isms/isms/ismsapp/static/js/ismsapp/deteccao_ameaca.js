/**
 * Deteccao de Ameaca - Threat Detection
 *
 * Handles interactions for the threat detection page:
 * - Asset multi-select dropdown
 * - Form validation
 * - Dynamic feedback
 */

document.addEventListener('DOMContentLoaded', function() {
  initializeFormValidation();
});

/**
 * Initialize form validation
 */
function initializeFormValidation() {
  const form = document.querySelector('.threat-form');
  if (!form) return;

  // Get form fields
  const nomeField = form.querySelector('[name="nome"]');
  const origemField = form.querySelector('[name="origem"]');
  const ativosField = form.querySelector('[name="ativos"]');
  const descricaoField = form.querySelector('[name="descricao"]');
  const submitBtn = form.querySelector('button[type="submit"]');

  // Add form submit validation
  form.addEventListener('submit', function(e) {
    let isValid = true;

    // Validate required fields
    if (!nomeField.value.trim()) {
      showFieldError(nomeField, 'Nome da ameaça é obrigatório');
      isValid = false;
    } else {
      clearFieldError(nomeField);
    }

    if (!ativosField.value || ativosField.selectedOptions.length === 0) {
      showFieldError(ativosField, 'Selecione pelo menos um ativo afetado');
      isValid = false;
    } else {
      clearFieldError(ativosField);
    }

    if (!descricaoField.value.trim()) {
      showFieldError(descricaoField, 'Descrição da ameaça é obrigatória');
      isValid = false;
    } else {
      clearFieldError(descricaoField);
    }

    if (!origemField.value) {
      showFieldError(origemField, 'Selecione a origem da ameaça');
      isValid = false;
    } else {
      clearFieldError(origemField);
    }

    if (!isValid) {
      e.preventDefault();
    }
  });

  // Real-time validation on input
  nomeField.addEventListener('blur', function() {
    if (!this.value.trim()) {
      showFieldError(this, 'Nome da ameaça é obrigatório');
    } else {
      clearFieldError(this);
    }
  });

  descricaoField.addEventListener('blur', function() {
    if (!this.value.trim()) {
      showFieldError(this, 'Descrição da ameaça é obrigatória');
    } else {
      clearFieldError(this);
    }
  });


  ativoField.addEventListener('change', function() {
    if (!this.value) {
      showFieldError(this, 'Selecione um ativo afetado');
    } else {
      clearFieldError(this);
    }
  });

  origemField.addEventListener('change', function() {
    if (!this.value) {
      showFieldError(this, 'Selecione a origem da ameaça');
    } else {
      clearFieldError(this);
    }
  });
}

/**
 * Show field error styling
 */
function showFieldError(field, message) {
  field.style.borderColor = '#ef4444';
  field.style.backgroundColor = 'rgba(239, 68, 68, 0.05)';

  // Remove existing error message if present
  clearFieldError(field);

  // Add error message
  const errorMsg = document.createElement('p');
  errorMsg.style.cssText = 'color:#f87171;font-size:.73rem;margin-top:.4rem';
  errorMsg.textContent = message;
  field.parentNode.insertBefore(errorMsg, field.nextSibling);
}

/**
 * Clear field error styling
 */
function clearFieldError(field) {
  field.style.borderColor = '';
  field.style.backgroundColor = '';

  // Remove error message if present
  const nextEl = field.nextElementSibling;
  if (nextEl && nextEl.tagName === 'P' && nextEl.style.color === 'rgb(248, 113, 113)') {
    nextEl.remove();
  }
}
