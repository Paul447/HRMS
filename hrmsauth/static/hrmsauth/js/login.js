/**
 * login.js
 *
 * This script handles the client-side validation and submission
 * of the login form, providing real-time feedback and a loading state.
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Element References ---
    // Get references to all necessary DOM elements once the document is loaded.
    const loginForm = document.getElementById('login-form');
    const submitButton = document.getElementById('submit-btn');
    const buttonText = document.getElementById('btn-text');
    const buttonSpinner = document.getElementById('btn-spinner');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const usernameErrorDisplay = document.getElementById('username-error');
    const passwordErrorDisplay = document.getElementById('password-error');

    // --- Event Listeners ---
    // Attach event listeners for real-time validation as the user types.
    if (usernameInput) {
        usernameInput.addEventListener('input', () => validateField(usernameInput, usernameErrorDisplay, validateUsername));
    }
    if (passwordInput) {
        passwordInput.addEventListener('input', () => validateField(passwordInput, passwordErrorDisplay, validatePassword));
    }

    // Attach event listener for form submission.
    if (loginForm) {
        loginForm.addEventListener('submit', handleFormSubmission);
    }

    // --- Validation Functions ---

    /**
     * Validates the username input field.
     * @returns {boolean} True if the username is valid, false otherwise.
     */
    function validateUsername() {
        const value = usernameInput.value.trim();
        if (!value) {
            return { isValid: false, message: 'Employee ID is required.' };
        }
        if (value.length < 3) {
            return { isValid: false, message: 'Employee ID must be at least 3 characters long.' };
        }
        return { isValid: true, message: '' };
    }

    /**
     * Validates the password input field.
     * @returns {boolean} True if the password is valid, false otherwise.
     */
    function validatePassword() {
        const value = passwordInput.value; // No trim for password
        if (!value) {
            return { isValid: false, message: 'Password is required.' };
        }
        if (value.length < 6) {
            return { isValid: false, message: 'Password must be at least 6 characters long.' };
        }
        return { isValid: true, message: '' };
    }

    /**
     * Generic function to validate a field and display/hide errors.
     * @param {HTMLElement} inputElement The input field element.
     * @param {HTMLElement} errorDisplayElement The element to display error messages.
     * @param {Function} validationFunction The specific validation function for the field.
     * @returns {boolean} True if the field is valid, false otherwise.
     */
    function validateField(inputElement, errorDisplayElement, validationFunction) {
        const { isValid, message } = validationFunction();
        if (!isValid) {
            showError(errorDisplayElement, message);
            inputElement.classList.add('border-danger-500'); // Add error styling
            return false;
        } else {
            hideError(errorDisplayElement);
            inputElement.classList.remove('border-danger-500'); // Remove error styling
            return true;
        }
    }

    // --- Error Display Helpers ---

    /**
     * Displays an error message in the specified element.
     * @param {HTMLElement} element The DOM element to display the message in.
     * @param {string} message The error message to display.
     */
    function showError(element, message) {
        if (element) {
            element.textContent = message;
            element.classList.add('text-danger-500', 'font-medium'); // Ensure error styling is applied
            element.setAttribute('aria-live', 'polite'); // Announce changes to screen readers
        }
    }

    /**
     * Hides the error message from the specified element.
     * @param {HTMLElement} element The DOM element to clear.
     */
    function hideError(element) {
        if (element) {
            element.textContent = '';
            element.classList.remove('text-danger-500', 'font-medium');
            element.removeAttribute('aria-live');
        }
    }

    // --- Form Submission Handler ---

    /**
     * Handles the form submission event.
     * Prevents default submission if validation fails, otherwise shows loading state.
     * @param {Event} event The submit event object.
     */
    function handleFormSubmission(event) {
        // Perform a final validation check for both fields before submission.
        const isUsernameValid = validateField(usernameInput, usernameErrorDisplay, validateUsername);
        const isPasswordValid = validateField(passwordInput, passwordErrorDisplay, validatePassword);

        // If any field is invalid, prevent the form from submitting.
        if (!isUsernameValid || !isPasswordValid) {
            event.preventDefault();
            return;
        }

        // If validation passes, show the loading state on the button.
        setLoadingState(true);
    }

    /**
     * Sets the loading state of the submit button.
     * @param {boolean} isLoading True to show loading state, false to hide.
     */
    function setLoadingState(isLoading) {
        if (submitButton && buttonText && buttonSpinner) {
            submitButton.disabled = isLoading;
            if (isLoading) {
                buttonText.classList.add('hidden');
                buttonSpinner.classList.remove('hidden');
            } else {
                buttonText.classList.remove('hidden');
                buttonSpinner.classList.add('hidden');
            }
        }
    }

    // Optional: If you want to hide the spinner on page load (e.g., after a failed submission redirect)
    // This ensures the button is in its default state when the page loads.
    setLoadingState(false);
});
