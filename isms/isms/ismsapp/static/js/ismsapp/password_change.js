document.addEventListener('DOMContentLoaded', function() {
    // Toggle password visibility for old password
    const oldPasswordToggle = document.getElementById('oldPasswordToggle');
    if (oldPasswordToggle) {
        oldPasswordToggle.addEventListener('click', function(e) {
            e.preventDefault();
            const oldPasswordInput = document.getElementById('id_old_password');
            const icon = this.querySelector('i');

            if (oldPasswordInput.type === 'password') {
                oldPasswordInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                oldPasswordInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    }

    // Toggle password visibility for new password
    const newPasswordToggle = document.getElementById('newPasswordToggle');
    if (newPasswordToggle) {
        newPasswordToggle.addEventListener('click', function(e) {
            e.preventDefault();
            const newPasswordInput = document.getElementById('id_new_password1');
            const icon = this.querySelector('i');

            if (newPasswordInput.type === 'password') {
                newPasswordInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                newPasswordInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    }

    // Toggle password visibility for confirm password
    const confirmPasswordToggle = document.getElementById('confirmPasswordToggle');
    if (confirmPasswordToggle) {
        confirmPasswordToggle.addEventListener('click', function(e) {
            e.preventDefault();
            const confirmPasswordInput = document.getElementById('id_new_password2');
            const icon = this.querySelector('i');

            if (confirmPasswordInput.type === 'password') {
                confirmPasswordInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                confirmPasswordInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    }
});
