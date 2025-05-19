    document.addEventListener('DOMContentLoaded', () => {
      const form = document.getElementById('login-form');
      const submitBtn = document.getElementById('submit-btn');
      const btnText = document.getElementById('btn-text');
      const btnSpinner = document.getElementById('btn-spinner');
      const usernameInput = document.getElementById('username');
      const passwordInput = document.getElementById('password');
      const usernameError = document.getElementById('username-error');
      const passwordError = document.getElementById('password-error');

      // Real-time validation
      usernameInput.addEventListener('input', validateUsername);
      passwordInput.addEventListener('input', validatePassword);
      
      // Form submission handler
      form.addEventListener('submit', (e) => {
        const isUsernameValid = validateUsername();
        const isPasswordValid = validatePassword();
        
        if (!isUsernameValid || !isPasswordValid) {
          e.preventDefault();
          return;
        }

        // Show loading state
        submitBtn.disabled = true;
        btnText.classList.add('hidden');
        btnSpinner.classList.remove('hidden');
      });

      function validateUsername() {
        const value = usernameInput.value.trim();
        if (!value) {
          showError(usernameError, 'Employee ID is required');
          return false;
        }
        if (value.length < 3) {
          showError(usernameError, 'ID must be at least 3 characters');
          return false;
        }
        hideError(usernameError);
        return true;
      }

      function validatePassword() {
        const value = passwordInput.value;
        if (!value) {
          showError(passwordError, 'Password is required');
          return false;
        }
        if (value.length < 6) {
          showError(passwordError, 'Password must be at least 6 characters');
          return false;
        }
        hideError(passwordError);
        return true;
      }


        function showError(element, message) {
          element.textContent = message;
          element.classList.add('active');
        }

        function hideError(element) {
          element.textContent = '';
          element.classList.remove('active');
        }

    });