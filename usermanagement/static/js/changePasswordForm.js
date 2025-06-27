// static/js/changePasswordForm.js

import { NotificationService } from './notificationService.js'; // Import your notification service

document.addEventListener('DOMContentLoaded', () => {
    // Get references to all necessary DOM elements
    const changePasswordForm = document.getElementById('changePasswordForm');
    const oldPasswordInput = document.getElementById('old_password');
    const newPasswordInput = document.getElementById('new_password');
    const confirmNewPasswordInput = document.getElementById('confirm_new_password');
    const submitButton = document.getElementById('submitButton');

    // References for displaying client-side error messages
    const oldPasswordError = document.getElementById('old_password_error');
    const newPasswordError = document.getElementById('new_password_error');
    const confirmNewPasswordError = document.getElementById('confirm_new_password_error');

    /**
     * Clears all displayed client-side validation error messages.
     */
    function clearErrors() {
        oldPasswordError.textContent = '';
        newPasswordError.textContent = '';
        confirmNewPasswordError.textContent = '';
        oldPasswordError.classList.add('hidden');
        newPasswordError.classList.add('hidden');
        confirmNewPasswordError.classList.add('hidden');
    }

    /**
     * Displays a client-side validation error message for a specific input field.
     * @param {HTMLElement} errorElement - The <p> element to display the error message in.
     * @param {string} message - The error message text.
     */
    function displayError(errorElement, message) {
        errorElement.textContent = message;
        errorElement.classList.remove('hidden');
    }

    /**
     * Performs comprehensive client-side validation for the password change form.
     * This provides immediate feedback to the user before sending data to the server.
     * @returns {boolean} True if all form fields pass client-side validation, false otherwise.
     */
    function validateForm() {
        clearErrors(); // Always clear previous errors at the start of validation
        let isValid = true; // Flag to track overall form validity

        const oldPassword = oldPasswordInput.value.trim();
        const newPassword = newPasswordInput.value.trim();
        const confirmNewPassword = confirmNewPasswordInput.value.trim();

        // 1. Check for empty fields
        if (oldPassword === '') {
            displayError(oldPasswordError, 'Current password is required.');
            isValid = false;
        }

        if (newPassword === '') {
            displayError(newPasswordError, 'New password is required.');
            isValid = false;
        }

        if (confirmNewPassword === '') {
            displayError(confirmNewPasswordError, 'Confirm new password is required.');
            isValid = false;
        }

        // 2. Check if new passwords match
        if (newPassword !== '' && confirmNewPassword !== '' && newPassword !== confirmNewPassword) {
            displayError(confirmNewPasswordError, 'New passwords do not match.');
            isValid = false;
        }

        // 3. Client-side password strength validation (align with Django's AUTH_PASSWORD_VALIDATORS)
        // Adjust these regular expressions and messages to match your Django backend's rules
        if (newPassword.length > 0) { // Only validate if new password is not empty
            if (newPassword.length < 8) { // MinimumLengthValidator
                displayError(newPasswordError, 'New password must be at least 8 characters long.');
                isValid = false;
            }
            // Example of other common password strength checks:
            if (!/[A-Z]/.test(newPassword)) { // Requires uppercase letter
                displayError(newPasswordError, 'New password must contain at least one uppercase letter.');
                isValid = false;
            }
            if (!/[a-z]/.test(newPassword)) { // Requires lowercase letter
                displayError(newPasswordError, 'New password must contain at least one lowercase letter.');
                isValid = false;
            }
            if (!/[0-9]/.test(newPassword)) { // Requires a number
                displayError(newPasswordError, 'New password must contain at least one digit.');
                isValid = false;
            }
            if (!/[^A-Za-z0-9]/.test(newPassword)) { // Requires a special character
                displayError(newPasswordError, 'New password must contain at least one special character (e.g., !@#$%^&*).');
                isValid = false;
            }
            // You could also add checks for UserAttributeSimilarityValidator (e.g., not containing username/email)
            // though this is often better left to the server for security.
        }

        return isValid;
    }

    // Add event listener for form submission
    changePasswordForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Stop the default form submission (prevents page reload)

        // Perform client-side validation first
        if (!validateForm()) {
            NotificationService.showNotification('Please correct the errors in the form.', 'warning');
            return; // Stop execution if validation fails
        }

        // Disable button and show loading state
        submitButton.disabled = true;
        submitButton.textContent = 'Changing...';
        submitButton.classList.add('opacity-50', 'cursor-not-allowed');

        // Prepare the data to be sent to the API
        const formData = {
            old_password: oldPasswordInput.value,
            new_password: newPasswordInput.value,
            confirm_new_password: confirmNewPasswordInput.value
        };

        try {
            // Get CSRF token from the hidden input generated by {% csrf_token %}
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // Make the API call to your DRF endpoint
            const response = await fetch('/api/change-password/', { // <--- **IMPORTANT:** Ensure this matches your DRF URL
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken, // Mandatory for Django's CSRF protection
                    // Include Authorization header if you are using Token or JWT authentication
                    // Example for Token Authentication:
                    // 'Authorization': `Token ${localStorage.getItem('token')}` // Adjust this line based on your auth method
                    // For Session Authentication, the browser automatically sends the session cookie,
                    // and 'X-CSRFToken' is sufficient.
                },
                body: JSON.stringify(formData) // Send data as JSON
            });

            const responseData = await response.json(); // Parse the JSON response from the server

            if (response.ok) { // Check if the response status is 2xx (success)
                NotificationService.showNotification(responseData.detail || 'Password changed successfully!', 'success');
                // Clear the form fields after successful submission
                // consoles.log('Password change successful:', responseData);
                changePasswordForm.reset();
                clearErrors(); // Also clear any displayed error messages
            } else {
                // Handle API errors (e.g., validation errors, authentication errors)
                if (response.status === 400) { // Bad Request, often validation errors
                    // Display specific field errors returned by DRF serializer
                    for (const field in responseData) {
                        const errorMessages = responseData[field];
                        if (Array.isArray(errorMessages) && errorMessages.length > 0) {
                            const errorMessage = errorMessages.join(' '); // Join multiple messages if a field has many
                            if (field === 'old_password') {
                                displayError(oldPasswordError, errorMessage);
                            } else if (field === 'new_password') {
                                displayError(newPasswordError, errorMessage);
                            } else if (field === 'confirm_new_password') {
                                displayError(confirmNewPasswordError, errorMessage);
                            } else {
                                // For non-field errors or other unexpected messages from DRF
                                NotificationService.showNotification(`${field}: ${errorMessage}`, 'error');
                            }
                        }
                    }
                    NotificationService.showNotification('Please correct the form errors.', 'error');
                } else if (response.status === 401 || response.status === 403) { // Unauthorized or Forbidden
                    NotificationService.showNotification('Authentication failed. Please log in again.', 'error');
                    // Optionally, redirect to the login page after a short delay
                    // setTimeout(() => window.location.href = '/login/', 2000);
                } else {
                    // Catch-all for other HTTP error statuses
                    NotificationService.showNotification(responseData.detail || 'An unexpected error occurred. Please try again.', 'error');
                }
            }
        } catch (error) {
            // Handle network errors (e.g., server unreachable)
            console.error('Error changing password:', error);
            NotificationService.showNotification('Network error or server unavailable. Please try again later.', 'error');
        } finally {
            // Re-enable the submit button and reset its text/style
            submitButton.disabled = false;
            submitButton.textContent = 'Change Password';
            submitButton.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    });

    // Optional: Add event listeners to clear specific error messages when input fields are changed
    // This provides a smoother user experience
    oldPasswordInput.addEventListener('input', () => oldPasswordError.classList.add('hidden'));
    newPasswordInput.addEventListener('input', () => newPasswordError.classList.add('hidden'));
    confirmNewPasswordInput.addEventListener('input', () => confirmNewPasswordError.classList.add('hidden'));
});