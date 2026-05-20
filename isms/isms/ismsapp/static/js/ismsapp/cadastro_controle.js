document.addEventListener('DOMContentLoaded', function() {
    const selectAllBtn = document.getElementById('select-all');
    const clearAllBtn = document.getElementById('clear-all');
    const searchInput = document.getElementById('category-search');
    const container = document.querySelector('.categorias-container');
    const countEl = document.getElementById('cat-count');
    const form = document.querySelector('.cadastro-form');

    function getCheckboxes() {
        return Array.from(container.querySelectorAll('input[type="checkbox"]'));
    }

    function updateCount() {
        const checked = getCheckboxes().filter(cb => cb.checked).length;
        if (countEl) countEl.textContent = String(checked);
    }

    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => {
            getCheckboxes().forEach(cb => cb.checked = true);
            updateCount();
        });
    }

    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', () => {
            getCheckboxes().forEach(cb => cb.checked = false);
            updateCount();
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', () => {
            const term = searchInput.value.toLowerCase().trim();
            const items = Array.from(container.querySelectorAll('.categoria-checkbox'));
            items.forEach(item => {
                const label = item.textContent.toLowerCase();
                item.style.display = term && !label.includes(term) ? 'none' : '';
            });
        });
    }

    // Update count on any checkbox change
    container.addEventListener('change', (e) => {
        if (e.target && e.target.matches('input[type="checkbox"]')) {
            updateCount();
        }
    });

    // Initial count
    updateCount();

    // Optional: prevent submit if none selected
    if (form) {
        form.addEventListener('submit', (e) => {
            const anyChecked = getCheckboxes().some(cb => cb.checked);
            if (!anyChecked) {
                e.preventDefault();
                alert('Selecione pelo menos uma categoria.');
            }
        });
    }
});
