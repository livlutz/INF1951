// Delete Account Form Validation

document.addEventListener('DOMContentLoaded', function() {
    const usernameInput = document.getElementById('username');
    const deleteBtn = document.getElementById('deleteBtn');
    const deleteForm = document.querySelector('.delete-form');

    // Get the expected username from the input's placeholder attribute
    const expectedUsername = usernameInput.getAttribute('placeholder');

    /**
     * Check if the form is valid and enable/disable the delete button
     */
    function checkFormValidity() {
        const isUsernamePassed = usernameInput.value === expectedUsername;
        deleteBtn.disabled = !isUsernamePassed;
    }

    // Attach event listeners
    usernameInput.addEventListener('input', checkFormValidity);

    /**
     * Prevent form submission if username doesn't match
     */
    deleteForm.addEventListener('submit', function(e) {
        if (usernameInput.value !== expectedUsername) {
            e.preventDefault();
            alert('Username não corresponde!');
            return false;
        }
    });
});
