// Signup Form Validation and Interactions
document.addEventListener('DOMContentLoaded', function() {
    // Add any custom form validations or interactions here

    // Example: Real-time password confirmation check
    const passwordField = document.getElementById('id_password');
    const confirmPasswordField = document.getElementById('id_password_confirm');

    if (confirmPasswordField) {
        confirmPasswordField.addEventListener('blur', function() {
            if (passwordField.value !== confirmPasswordField.value) {
                confirmPasswordField.style.borderColor = '#ff6b6b';
            } else {
                confirmPasswordField.style.borderColor = 'rgba(255, 255, 255, 0.15)';
            }
        });
    }
});
