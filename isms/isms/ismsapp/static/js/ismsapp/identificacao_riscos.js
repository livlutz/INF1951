// Identificacao Riscos JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const searchInput = document.getElementById('ativo-search');
    const dropdown = document.getElementById('ativo-dropdown');
    const hiddenInput = document.getElementById('ativo-hidden');
    const clearButton = document.getElementById('ativo-clear');

    if (searchInput && dropdown && hiddenInput) {
        const options = Array.from(dropdown.querySelectorAll('.option-item'));

        const renderOptions = (query) => {
            const normalized = query.toLowerCase().trim();

            options.forEach((option) => {
                const rawText = option.dataset.label || option.textContent.trim();
                const text = rawText.toLowerCase();
                const matches = text.includes(normalized);

                option.style.display = matches ? 'block' : 'none';
                option.classList.toggle('selected', option.dataset.value === hiddenInput.value);

                if (!normalized) {
                    option.innerHTML = rawText;
                } else if (matches) {
                    const escaped = rawText.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&');
                    const highlighted = rawText.replace(new RegExp(normalized.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&'), 'gi'), match => `<mark>${match}</mark>`);
                    option.innerHTML = highlighted || escaped;
                } else {
                    option.innerHTML = rawText;
                }
            });
        };

        const openDropdown = () => {
            dropdown.style.display = 'block';
            renderOptions(searchInput.value);
        };

        const closeDropdown = () => {
            dropdown.style.display = 'none';
        };

        searchInput.addEventListener('input', function() {
            renderOptions(this.value);
            openDropdown();
        });

        searchInput.addEventListener('focus', openDropdown);

        options.forEach((option) => {
            const label = option.textContent.trim();
            option.dataset.label = label;

            option.addEventListener('click', function() {
                searchInput.value = label;
                hiddenInput.value = this.dataset.value;
                options.forEach(opt => opt.classList.remove('selected'));
                this.classList.add('selected');
                closeDropdown();
            });
        });

        if (clearButton) {
            clearButton.addEventListener('click', function() {
                searchInput.value = '';
                hiddenInput.value = '';
                options.forEach(opt => {
                    opt.style.display = 'block';
                    opt.classList.remove('selected');
                    opt.innerHTML = opt.dataset.label || opt.textContent.trim();
                });
                searchInput.focus();
                openDropdown();
            });
        }

        document.addEventListener('click', function(e) {
            if (!e.target.closest('.search-select')) {
                closeDropdown();
            }
        });

        // Initialize from hidden value if editing an existing record.
        if (hiddenInput.value) {
            const selected = options.find(opt => opt.dataset.value === hiddenInput.value);
            if (selected) {
                searchInput.value = selected.dataset.label || selected.textContent.trim();
                selected.classList.add('selected');
            }
        }
    }

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
    const ativo = document.getElementById('ativo-hidden') || document.querySelector('[name="ativo"]');

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
