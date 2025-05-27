// This script handles the client-side logic for the PTO request form,
// including fetching dropdown data and submitting the form data.
// It leverages a smartFetch function to handle JWT token refreshes
// in conjunction with the Django middleware, ensuring a smooth user experience.

document.addEventListener('DOMContentLoaded', function() {
    // Get references to DOM elements
    const departmentSelect = document.getElementById('department_name');
    const payTypeSelect = document.getElementById('pay_types');
    const form = document.getElementById('ptoRequestForm');
    const submitButton = document.getElementById('submitButton');
    const submitButtonText = document.getElementById('submitButtonText');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const clearFormButton = document.getElementById('clearFormButton');


    /**
     * smartFetch is a robust wrapper around the native Fetch API.
     * It automatically retries an API request exactly once if the initial attempt
     * returns a 401 Unauthorized status. This is designed to work seamlessly
     * with a Django backend middleware that handles JWT token refreshing
     * via HTTP-only cookies. If the middleware successfully refreshes the access token,
     * the retry attempt will use the newly set valid cookie.
     *
     * @param {string} url The URL to send the request to.
     * @param {RequestInit} options Configuration options for the fetch request
     * (e.g., method, headers, body, credentials).
     * @param {boolean} [isRetry=false] Internal flag to prevent infinite retry loops.
     * @returns {Promise<Response>} A promise that resolves with the Fetch API Response object.
     * @throws {Error} Throws an error if a network issue occurs or if the request
     * fails after the retry attempt (and is not a 401 leading to redirect).
     */
    async function smartFetch(url, options = {}, isRetry = false) {
        try {
            // Execute the first fetch attempt
            const response = await fetch(url, options);

            // If a 401 Unauthorized status is received and it's not already a retry attempt,
            // assume the access token has expired and the Django middleware has refreshed it.
            if (response.status === 401 && !isRetry) {
                console.warn(`[smartFetch] Received 401 for ${url}. Retrying with potentially new token.`);
                // Recursively call smartFetch for a single retry
                return await smartFetch(url, options, true);
            }
            
            return response; // Return the original or retried response

        } catch (error) {
            // Catch and log any network or other unexpected fetch errors
            console.error(`[smartFetch] Network or other fetch error for ${url}:`, error);
            // Re-throw the error to be handled by the calling function
            throw error;
        }
    }

    /**
     * Displays a styled notification pop-up.
     * @param {string} message The message to display.
     * @param {'success'|'error'|'warning'} type The type of notification.
     */
    function showNotification(message, type = 'success') {
        // Remove any existing notifications to prevent stacking
        const existingNotification = document.getElementById('global-notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        const notification = document.createElement('div');
        notification.id = 'global-notification';
        notification.className = `
            fixed top-10 right-4 z-50
            px-6 py-4 rounded-lg shadow-xl
            flex items-center space-x-2 animate-slide-in
        `;

        let bgColorClass = '';
        let iconSvg = '';

        if (type === 'success') {
            bgColorClass = 'bg-green-600';
            iconSvg = `
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
            `;
        } else if (type === 'error') {
            bgColorClass = 'bg-red-600';
            iconSvg = `
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
            `;
        } else if (type === 'warning') {
            bgColorClass = 'bg-yellow-500';
            iconSvg = `
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.332 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
            `;
        }

        notification.classList.add(bgColorClass, 'text-white', 'font-medium');
        notification.innerHTML = `
            ${iconSvg}
            <span>${message}</span>
        `;
        document.body.appendChild(notification);

        // Remove after 5 seconds with a fade-out animation
        setTimeout(() => {
            notification.classList.remove('animate-slide-in');
            notification.classList.add('animate-fade-out');
            notification.addEventListener('animationend', () => {
                notification.remove();
            }, { once: true }); // Ensure listener is removed after first use
        }, 5000);
    }


    /**
     * Clears all existing field-specific error messages.
     */
    function clearFieldErrors() {
        document.querySelectorAll('.field-errors').forEach(errorDiv => {
            errorDiv.textContent = ''; // Clear text content
        });
    }

    /**
     * Shows the loading spinner and disables the submit button.
     */
    function showLoadingState() {
        submitButton.disabled = true;
        submitButtonText.classList.add('hidden');
        loadingSpinner.classList.remove('hidden');
    }

    /**
     * Hides the loading spinner and enables the submit button.
     */
    function hideLoadingState() {
        submitButton.disabled = false;
        submitButtonText.classList.remove('hidden');
        loadingSpinner.classList.add('hidden');
    }

    /**
     * Fetches data from a specified API endpoint and uses it to populate
     * a given HTML <select> element. It handles loading states and errors.
     * This function uses smartFetch for API calls to benefit from token retry logic.
     *
     * @param {string} url The API endpoint to fetch data from.
     * @param {HTMLSelectElement} selectElement The <select> DOM element to populate.
     * @param {string} defaultOptionText The text for the initial disabled option (e.g., "Select a Department").
     * @param {string} valueKey The key in the API response object representing the option's value.
     * @param {string} labelKey The key in the API response object representing the option's display text.
     */
    async function fetchAndPopulateDropdown(url, selectElement, defaultOptionText, valueKey, labelKey) {
        try {
            // Retrieve the CSRF token from the hidden input field.
            // This is needed for Django's CSRF protection on API requests.
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            // Make the API call using smartFetch, including necessary headers and credentials.
            const response = await smartFetch(url, {
                method: 'GET',
                // credentials: 'include' ensures HTTP-only cookies (like JWT) are sent.
                credentials: 'include',
                headers: {
                    'X-CSRFToken': csrftoken, // Send the CSRF token for Django's validation
                    'Content-Type': 'application/json'
                }
            });

            // Check if the response was successful (status 2xx)
            if (!response.ok) {
                // If a 401 persists after smartFetch's retry, it means the refresh token is also invalid.
                // In this case, redirect the user to the login page.
                if (response.status === 401) {
                    console.error(`[Dropdown Fetch] Refresh token invalid for ${url}. Redirecting to login.`);
                    window.location.href = '/auth/login/';
                    return; // Stop execution
                }
                // For any other non-OK status, throw an Error.
                const errorData = await response.json(); // Try to get error details
                throw new Error(`Failed to load ${defaultOptionText}. Status: ${response.status}. Error: ${JSON.stringify(errorData)}`);
            }

            // Parse the JSON data from the response
            const data = await response.json();
            
            // Clear existing options and add the default placeholder option
            selectElement.innerHTML = `<option value="" disabled selected>${defaultOptionText}</option>`;

            // Populate the dropdown with data from the API response
            data.forEach(item => {
                const option = document.createElement('option');
                option.value = item[valueKey];       // Set the option's value
                option.textContent = item[labelKey]; // Set the option's display text
                selectElement.appendChild(option);   // Add the option to the select element
            });
        } catch (error) {
            // Log and display an error message if population fails
            console.error(`[Dropdown Fetch] Error populating ${defaultOptionText} dropdown:`, error);
            selectElement.innerHTML = `<option value="" disabled selected>Error loading ${defaultOptionText}</option>`;
            showNotification(`Error loading ${defaultOptionText}. Please try refreshing the page.`, 'error');
        }
    }

    // --- Initial Data Loading ---
    // Fetch and populate the Department dropdown when the page loads
    fetchAndPopulateDropdown('/api/department/', departmentSelect, 'Select your Department', 'id', 'name');
    // Fetch and populate the Pay Type dropdown when the page loads
    fetchAndPopulateDropdown('/api/departmentpaytype/', payTypeSelect, 'Select Pay Type', 'id', 'name');

    // --- Form Submission Handling ---
    form.addEventListener('submit', async function(event) {
        event.preventDefault(); // Prevent the browser's default form submission behavior

        clearFieldErrors(); // Clear previous field errors
        showLoadingState(); // Show loading spinner and disable button

        // Retrieve the CSRF token for the POST request
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Gather all form data into a payload object
        const payload = {
            department_name: form.department_name.value,
            pay_types: form.pay_types.value,
            start_date_time: form.start_date_time.value,
            end_date_time: form.end_date_time.value,
            reason: form.reason.value
        };

        try {
            // Submit the form data to the API using smartFetch
            const response = await smartFetch('/api/pto-requests/', { // Adjust API endpoint as needed
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json', // Specify content type for JSON payload
                    'X-CSRFToken': csrftoken // Include the CSRF token for server-side validation
                },
                credentials: 'include', // Ensures HTTP-only cookies (like JWT) are sent with the request
                body: JSON.stringify(payload) // Convert the payload object to a JSON string
            });

            // Handle response based on status
            if (response.ok) {
                // Success: Display global success notification, reset form
                const data = await response.json(); // Get JSON response if available
                showNotification('Your time off request was successfully submitted!', 'success');
                form.reset();
                console.log("[Form Submission] PTO request submitted successfully:", data);
            } else if (response.status === 400) {
                // Bad Request: Display inline field errors and global error notification
                const errorData = await response.json();
                console.error('[Form Submission] Validation Errors:', errorData);

                Object.keys(errorData).forEach(field => {
                    const fieldElement = form.querySelector(`[name="${field}"]`);
                    if (fieldElement) {
                        const errorDiv = fieldElement.nextElementSibling; // Assuming field-errors div is next sibling
                        if (errorDiv && errorDiv.classList.contains('field-errors')) {
                            // Join array errors with space, or just use string error
                            errorDiv.textContent = Array.isArray(errorData[field]) ? errorData[field].join(' ') : errorData[field];
                        }
                    } else if (field === 'non_field_errors' || field === 'detail') {
                        // Handle non-field errors or general API errors
                        const errorMessageText = Array.isArray(errorData[field]) ? errorData[field].join(' ') : errorData[field];
                        showNotification(`Submission failed: ${errorMessageText}`, 'error');
                    }
                });
                showNotification('Please correct the errors in the form.', 'error');
            } else if (response.status === 401) {
                // Unauthorized: Redirect to login (smartFetch should handle this, but as a fallback)
                console.error("[Form Submission] Unauthorized. Redirecting to login.");
                window.location.href = '/auth/login/';
            } else {
                // Other HTTP errors: Display generic error notification
                const errorText = await response.text(); // Get raw text for unexpected errors
                console.error(`[Form Submission] Server Error (${response.status}):`, errorText);
                showNotification(`An unexpected error occurred (${response.status}). Please try again.`, 'error');
            }
        } catch (err) {
            // Network or unhandled JavaScript errors: Display generic error notification
            console.error('[Form Submission] Network or unknown error during submission:', err);
            showNotification('Network error, please check your internet connection and try again.', 'error');
        } finally {
            hideLoadingState(); // Always hide loading spinner and enable button
        }
    });

    // --- Clear Form Button Handling ---
    clearFormButton.addEventListener('click', function() {
        form.reset();
        clearFieldErrors(); // Clear any existing errors
        showNotification('Form cleared!', 'warning');
    });
});