document.addEventListener('DOMContentLoaded', function() {
    // 1. Identify the original select element
    const originalSelect = document.querySelector('.asset-selection-container select');
    if (!originalSelect) return;

    // 2. Hide the original select
    originalSelect.style.display = 'none';

    // 3. Create a container for the checkboxes
    const checkboxContainer = document.createElement('div');
    checkboxContainer.className = 'checkbox-list-container';

    // 4. Loop through options and create checkboxes
    Array.from(originalSelect.options).forEach((option, index) => {
        const wrapper = document.createElement('div');
        wrapper.className = 'checkbox-item';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `asset_${index}`;
        checkbox.value = option.value;
        checkbox.checked = option.selected;
        checkbox.className = 'form-check-input';

        const label = document.createElement('label');
        label.htmlFor = `asset_${index}`;
        label.textContent = option.text;
        label.className = 'form-check-label';

        // 5. Sync checkbox state back to the original select
        checkbox.addEventListener('change', function() {
            option.selected = this.checked;
            // Trigger a change event in case other scripts are listening
            originalSelect.dispatchEvent(new Event('change'));

            // Optional: Toggle a 'selected' class for styling
            wrapper.classList.toggle('is-selected', this.checked);
        });

        wrapper.appendChild(checkbox);
        wrapper.appendChild(label);
        checkboxContainer.appendChild(wrapper);
    });

    // 6. Insert the new UI into the DOM
    originalSelect.parentNode.appendChild(checkboxContainer);
});