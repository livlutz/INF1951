// Identificacao Riscos JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    const form = document.querySelector('form');

    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
            }
        });
    }
});

/**
 * Validate the form before submission
 */
function validateForm() {
    const nome = document.querySelector('[name="nome"]');
    const descricao = document.querySelector('[name="descricao"]');
    const ativo = document.querySelector('[name="ativo"]');

    // Check if risk name is filled
    if (!nome || !nome.value.trim()) {
        showError(nome, 'Por favor, insira um nome para o risco.');
        return false;
    }

    // Check if description is filled
    if (!descricao || !descricao.value.trim()) {
        showError(descricao, 'Por favor, descreva o risco identificado.');
        return false;
    }

    // Check if asset is selected
    if (!ativo || !ativo.value) {
        showError(ativo, 'Por favor, selecione um ativo associado.');
        return false;
    }

    return true;
}

/**
 * Show error message for a field
 */
function showError(input, message) {
    if (!input) return;

    // Remove existing error
    const existingError = input.parentElement.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }

    // Add new error
    const errorDiv = document.createElement('p');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = 'color:#fca5a5;font-size:.73rem;margin-top:.4rem;padding:0.5rem 0.75rem;background:rgba(220, 38, 38, 0.1);border-left:3px solid #dc2626;border-radius:4px;';
    errorDiv.textContent = message;

    input.parentElement.insertBefore(errorDiv, input.nextSibling);

    // Clear error on input
    input.addEventListener('input', function() {
        const err = input.parentElement.querySelector('.error-message');
        if (err) err.remove();
    }, { once: true });
}
