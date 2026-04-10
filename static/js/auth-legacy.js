document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('subscribeForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const submitBtn = document.getElementById('submitBtn');

    // Email validation regex
    const emailRegex = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;

    // Clear error messages on input
    emailInput.addEventListener('input', () => clearError('emailError'));
    passwordInput.addEventListener('input', () => {
        clearError('passwordError');
        checkPasswordStrength();
        checkPasswordMatch();
    });
    confirmPasswordInput.addEventListener('input', () => {
        clearError('confirmPasswordError');
        checkPasswordMatch();
    });

    // Real-time password strength check
    function checkPasswordStrength() {
        const password = passwordInput.value;
        const strengthDiv = document.getElementById('passwordStrength');
        
        if (password.length === 0) {
            strengthDiv.innerHTML = '';
            return;
        }

        let strength = 0;
        if (password.length >= 8) strength++;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^a-zA-Z0-9]/.test(password)) strength++;

        const strengthClasses = ['', 'strength-weak', 'strength-fair', 'strength-good', 'strength-good'];
        strengthDiv.innerHTML = `<div class="password-strength-bar ${strengthClasses[strength]}"></div>`;
    }

    // Check if passwords match
    function checkPasswordMatch() {
        if (passwordInput.value && confirmPasswordInput.value && passwordInput.value !== confirmPasswordInput.value) {
            showError('confirmPasswordError', 'Passwords do not match');
        }
    }

    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Clear previous errors
        document.getElementById('emailError').textContent = '';
        document.getElementById('passwordError').textContent = '';
        document.getElementById('confirmPasswordError').textContent = '';

        // Validate email
        const email = emailInput.value.trim().toLowerCase();
        if (!email) {
            showError('emailError', 'Email is required');
            return;
        }
        if (!emailRegex.test(email)) {
            showError('emailError', 'Invalid email address');
            return;
        }

        // Validate password
        const password = passwordInput.value.trim();
        if (!password) {
            showError('passwordError', 'Password is required');
            return;
        }
        if (password.length < 8) {
            showError('passwordError', 'Password must be at least 8 characters');
            return;
        }
        if (password.length > 64) {
            showError('passwordError', 'Password must not exceed 64 characters');
            return;
        }

        // Validate confirm password
        const confirmPassword = confirmPasswordInput.value.trim();
        if (!confirmPassword) {
            showError('confirmPasswordError', 'Confirm password is required');
            return;
        }
        if (password !== confirmPassword) {
            showError('confirmPasswordError', 'Passwords do not match');
            return;
        }

        // All validations passed - submit form
        submitBtn.disabled = true;
        document.querySelector('.btn-text').style.display = 'none';
        document.querySelector('.btn-loader').style.display = 'inline-block';

        // Let the form submit normally (server-side handles the rest)
        setTimeout(() => {
            form.submit();
        }, 300);
    });

    function showError(elementId, message) {
        document.getElementById(elementId).textContent = message;
    }

function clearError(elementId) {
        document.getElementById(elementId).textContent = '';
    }

    // Login form validation (new)
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        const loginEmailInput = document.querySelector('#loginForm #email');
        const loginPasswordInput = document.querySelector('#loginForm #password');
        const loginSubmitBtn = document.querySelector('#loginForm #submitBtn');

        // Clear errors on input
        loginEmailInput.addEventListener('input', () => clearError('emailError'));
        loginPasswordInput.addEventListener('input', () => clearError('passwordError'));

        // Login form submission
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            // Clear previous errors
            document.getElementById('emailError').textContent = '';
            document.getElementById('passwordError').textContent = '';

            // Validate email
            const email = loginEmailInput.value.trim().toLowerCase();
            if (!email) {
                showError('emailError', 'Email is required');
                return;
            }
            if (!emailRegex.test(email)) {
                showError('emailError', 'Invalid email address');
                return;
            }

            // Validate password
            const password = loginPasswordInput.value.trim();
            if (!password) {
                showError('passwordError', 'Password is required');
                return;
            }
            if (password.length < 8) {
                showError('passwordError', 'Password must be at least 8 characters');
                return;
            }
            if (password.length > 64) {
                showError('passwordError', 'Password must not exceed 64 characters');
                return;
            }

            // All good - submit with loading
            loginSubmitBtn.disabled = true;
            document.querySelector('#loginForm .btn-text').style.display = 'none';
            document.querySelector('#loginForm .btn-loader').style.display = 'inline-block';

            setTimeout(() => {
                loginForm.submit();
            }, 300);
        });
    }
});
