// Login Form Interactions
document.addEventListener('DOMContentLoaded', function() {
    // Password visibility toggle
    const passwordToggle = document.getElementById('passwordToggle');
    const passwordField = document.getElementById('id_password');

    if (passwordToggle && passwordField) {
        passwordToggle.addEventListener('click', function(e) {
            e.preventDefault();

            const isPassword = passwordField.type === 'password';
            passwordField.type = isPassword ? 'text' : 'password';

            // Update icon
            const icon = passwordToggle.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-eye');
                icon.classList.toggle('fa-eye-slash');
            }
        });
    }

    // Form submission handling
    const loginForm = document.querySelector('form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            // You can add custom validation here if needed
            console.log('Login form submitted');
        });
    }
});
