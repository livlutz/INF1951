document.addEventListener('DOMContentLoaded', function () {
    buildAtivosAfetadosCheckboxes();
    initAtivosAfetadosSearch();
    initAtivosAfetadosActions();
});

function buildAtivosAfetadosCheckboxes() {
    const select = document.querySelector('select[name="ativos_afetados"]');
    const container = document.getElementById('ativos-afetados-checkbox-list');
    if (!select || !container) return;

    container.innerHTML = '';

    Array.from(select.options).forEach(function (option) {
        const item = document.createElement('label');
        item.className = 'checkbox-item';
        item.dataset.label = option.text.toLowerCase();

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = option.value;
        checkbox.className = 'asset-cb';
        checkbox.checked = option.selected;

        checkbox.addEventListener('change', function () {
            option.selected = this.checked;
            item.classList.toggle('is-selected', this.checked);
            updateSummary();
        });

        const label = document.createElement('span');
        label.className = 'asset-cb-label';
        label.textContent = option.text;

        item.appendChild(checkbox);
        item.appendChild(label);
        item.classList.toggle('is-selected', option.selected);
        container.appendChild(item);
    });

    updateSummary();
}

function initAtivosAfetadosSearch() {
    const input = document.getElementById('ativos-afetados-search');
    const container = document.getElementById('ativos-afetados-checkbox-list');
    if (!input || !container) return;

    input.addEventListener('input', function () {
        const term = this.value.toLowerCase().trim();
        container.querySelectorAll('.checkbox-item').forEach(function (item) {
            const isMatch = !term || item.dataset.label.includes(term);
            item.style.display = isMatch ? '' : 'none';
            const label = item.querySelector('.asset-cb-label');
            if (label) {
                label.innerHTML = highlightMatch(label.textContent, term);
            }
        });
    });
}

function initAtivosAfetadosActions() {
    const selectAllButton = document.getElementById('ativos-afetados-select-all');
    const clearButton = document.getElementById('ativos-afetados-clear');
    const container = document.getElementById('ativos-afetados-checkbox-list');
    const select = document.querySelector('select[name="ativos_afetados"]');

    if (selectAllButton && container && select) {
        selectAllButton.addEventListener('click', function () {
            container.querySelectorAll('.asset-cb').forEach(function (checkbox, index) {
                checkbox.checked = true;
                select.options[index].selected = true;
                checkbox.closest('.checkbox-item')?.classList.add('is-selected');
            });
            updateSummary();
        });
    }

    if (clearButton && container && select) {
        clearButton.addEventListener('click', function () {
            container.querySelectorAll('.asset-cb').forEach(function (checkbox, index) {
                checkbox.checked = false;
                select.options[index].selected = false;
                checkbox.closest('.checkbox-item')?.classList.remove('is-selected');
            });
            updateSummary();
        });
    }
}

function highlightMatch(text, term) {
    if (!term) {
        return escapeHtml(text);
    }

    const escapedTerm = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const pattern = new RegExp(`(${escapedTerm})`, 'ig');
    return escapeHtml(text).replace(pattern, '<span class="match-highlight">$1</span>');
}

function escapeHtml(text) {
    return text
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

function updateSummary() {
    const countEl = document.getElementById('ativos-afetados-count');
    if (countEl) {
        countEl.textContent = document.querySelectorAll('#ativos-afetados-checkbox-list .asset-cb:checked').length;
    }
}