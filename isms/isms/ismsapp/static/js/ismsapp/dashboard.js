/**
 * Toggle module card expansion/collapse
 */
function toggleModule(headerElement) {
    const moduleCard = headerElement.parentElement;

    moduleCard.classList.toggle('expanded');
}

/**
 * Initialize dashboard on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    // Add keyboard support - expand/collapse on Enter or Space
    const moduleHeaders = document.querySelectorAll('.module-card-header');
    moduleHeaders.forEach(header => {
        header.setAttribute('role', 'button');
        header.setAttribute('tabindex', '0');

        header.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                toggleModule(this);
            }
        });
    });

    const searchInput = document.getElementById('dashboardSearch');
    const moduleCards = document.querySelectorAll('.acc');

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.trim().toLowerCase();

            moduleCards.forEach(card => {
                const title = (card.dataset.title || card.querySelector('.module-title')?.textContent || '').toLowerCase();
                card.style.display = title.includes(query) ? '' : 'none';
            });
        });
    }
});
