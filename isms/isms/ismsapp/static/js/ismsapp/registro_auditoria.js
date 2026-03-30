// Audit Registration Page Script

document.addEventListener('DOMContentLoaded', function() {
    // Handle checkbox change to conditionally show/hide non-conformity fields
    const checkboxField = document.querySelector('input[name="nao_conformidades_identificadas"]');

    if (checkboxField) {
        checkboxField.addEventListener('change', function() {
            updateFieldsVisibility();
        });

        // Initialize on load
        updateFieldsVisibility();
    }

    // Handle status tab switching
    const statusTabs = document.querySelectorAll('.status-tab');
    statusTabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();

            // Remove active class from all tabs
            statusTabs.forEach(t => t.classList.remove('active'));

            // Add active class to clicked tab
            this.classList.add('active');
        });
    });
});

function updateFieldsVisibility() {
    const checkbox = document.querySelector('input[name="nao_conformidades_identificadas"]');
    const nonConformityField = document.querySelector('textarea[name="nao_conformidades"]').closest('.form-group');
    const actionPlanField = document.querySelector('textarea[name="plano_acao"]').closest('.form-group');

    if (checkbox && nonConformityField && actionPlanField) {
        if (checkbox.checked) {
            // Non-conformities were NOT found, hide the fields
            nonConformityField.style.display = 'none';
            actionPlanField.style.display = 'none';
        } else {
            // Non-conformities WERE found, show the fields
            nonConformityField.style.display = 'block';
            actionPlanField.style.display = 'block';
        }
    }
