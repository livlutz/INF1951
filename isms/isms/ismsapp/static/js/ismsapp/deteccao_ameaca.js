/**
 * Deteccao de Ameaca - Threat Detection
 *
 * Handles interactions for the threat detection page:
 * - Asset multi-select dropdown
 * - Form validation
 * - Dynamic feedback
 * - Modal for threats display
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
  const ativosField = form.querySelector('[name="ativos"]');
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

  ativosField.addEventListener('change', function() {
    if (!this.value || this.selectedOptions.length === 0) {
      showFieldError(this, 'Selecione um ativo afetado');
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

/**
 * Open threats modal
 */
function openThreatsModal() {
  const modal = document.getElementById('threatsModal');
  if (modal) {
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
}

/**
 * Close threats modal
 */
function closeThreatsModal() {
  const modal = document.getElementById('threatsModal');
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
  }
}

/**
 * Initialize modal event listeners
 */
function initializeModal() {
  const modal = document.getElementById('threatsModal');
  if (modal) {
    modal.addEventListener('click', function(e) {
      if (e.target === modal) {
        closeThreatsModal();
      }
    });
  }

  // Close modal with Escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      closeThreatsModal();
    }
  });
}
