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
});

function updateFieldsVisibility() {
    const checkbox = document.querySelector('input[name="nao_conformidades_identificadas"]');
    const nonConformityTextarea = document.querySelector('textarea[name="nao_conformidades"]');
    const actionPlanTextarea = document.querySelector('textarea[name="plano_acao"]');

    if (checkbox && nonConformityTextarea && actionPlanTextarea) {

        const nonConformityField = nonConformityTextarea.closest('.form-group');
        const actionPlanField = actionPlanTextarea.closest('.form-group');

        if (nonConformityField && actionPlanField) {

            if (checkbox.checked) {

                // Non-conformities identified -> show fields
                nonConformityField.style.display = 'block';
                actionPlanField.style.display = 'block';

            } else {

                // No non-conformities -> hide fields
                nonConformityField.style.display = 'none';
                actionPlanField.style.display = 'none';

                // Clear hidden values
                nonConformityTextarea.value = '';
                actionPlanTextarea.value = '';
            }
        }
    }
}
