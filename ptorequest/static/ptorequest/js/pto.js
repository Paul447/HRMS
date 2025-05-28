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

    // --- Confirmation Modal Elements ---
    const confirmationModal = document.getElementById('confirmationModal');
    const confirmSubmitButton = document.getElementById('confirmSubmitButton');
    const confirmCancelButton = document.getElementById('confirmCancelButton');
    // --- END NEW ---

    // --- NEW: Elements for Update Mode ---
    const pageTitle = document.getElementById('page_title'); // Assuming you have an ID for the page title H2
    const formHeading = form.querySelector('h2'); // The main form heading within the template
    const formParagraph = form.querySelector('p'); // The descriptive paragraph
    let ptoRequestId = null; // Variable to store PTO request ID if in update mode
    // --- END NEW ---

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
            const response = await fetch(url, options);

            if (response.status === 401 && !isRetry) {
                console.warn(`[smartFetch] Received 401 for ${url}. Retrying with potentially new token.`);
                return await smartFetch(url, options, true);
            }

            return response;

        } catch (error) {
            console.error(`[smartFetch] Network or other fetch error for ${url}:`, error);
            throw error;
        }
    }

    /**
     * Displays a styled notification pop-up.
     * @param {string} message The message to display.
     * @param {'success'|'error'|'warning'} type The type of notification.
     */
    function showNotification(message, type = 'success') {
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

        setTimeout(() => {
            notification.classList.remove('animate-slide-in');
            notification.classList.add('animate-fade-out');
            notification.addEventListener('animationend', () => {
                notification.remove();
            }, { once: true });
        }, 5000);
    }

    /**
     * Clears all existing field-specific error messages.
     */
    function clearFieldErrors() {
        document.querySelectorAll('.field-errors').forEach(errorDiv => {
            errorDiv.textContent = '';
        });
    }

    /**
     * Shows the loading spinner and disables the submit button.
     * @param {string} buttonText The text to display on the button.
     */
    function showLoadingState(buttonText = 'Processing...') {
        submitButton.disabled = true;
        submitButtonText.innerHTML = buttonText;
        submitButtonText.classList.remove('inline-block'); // Ensure it's hidden properly if it was inline-block
        submitButtonText.classList.add('hidden');
        loadingSpinner.classList.remove('hidden');
    }

    /**
     * Hides the loading spinner and enables the submit button.
     * @param {string} originalText The original text for the button.
     */
    function hideLoadingState(originalText = 'Submit Request') {
        submitButton.disabled = false;
        submitButtonText.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 inline-block" viewBox="0 0 20 20" fill="currentColor">
                                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                                      </svg>${originalText}`;
        submitButtonText.classList.remove('hidden');
        submitButtonText.classList.add('inline-block');
        loadingSpinner.classList.add('hidden');
    }

    /**
     * Fetches data from a specified API endpoint and uses it to populate
     * a given HTML <select> element.
     */
    async function fetchAndPopulateDropdown(url, selectElement, defaultOptionText, valueKey, labelKey) {
        try {
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const response = await smartFetch(url, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    console.error(`[Dropdown Fetch] Refresh token invalid for ${url}. Redirecting to login.`);
                    window.location.href = '/auth/login/';
                    return;
                }
                const errorData = await response.json();
                throw new Error(`Failed to load ${defaultOptionText}. Status: ${response.status}. Error: ${JSON.stringify(errorData)}`);
            }

            const data = await response.json();

            selectElement.innerHTML = `<option value="" disabled selected>${defaultOptionText}</option>`;

            data.forEach(item => {
                const option = document.createElement('option');
                option.value = item[valueKey];
                option.textContent = item[labelKey];
                selectElement.appendChild(option);
            });
        } catch (error) {
            console.error(`[Dropdown Fetch] Error populating ${defaultOptionText} dropdown:`, error);
            selectElement.innerHTML = `<option value="" disabled selected>Error loading ${defaultOptionText}</option>`;
            showNotification(`Error loading ${defaultOptionText}. Please try refreshing the page.`, 'error');
        }
    }

    // --- Confirmation Modal Functions ---
    function showConfirmationModal() {
        confirmationModal.classList.remove('hidden');
        confirmationModal.classList.remove('animate-fade-out-modal');
        confirmationModal.querySelector('.confirm-modal-content').classList.remove('animate-fade-out-modal');
        confirmationModal.querySelector('.confirm-modal-content').classList.add('animate-scale-in');
    }

    function hideConfirmationModal(animate = true) {
        if (animate) {
            confirmationModal.classList.add('animate-fade-out-modal');
            confirmationModal.querySelector('.confirm-modal-content').classList.remove('animate-scale-in');
            confirmationModal.querySelector('.confirm-modal-content').classList.add('animate-fade-out-modal');
            confirmationModal.addEventListener('animationend', () => {
                confirmationModal.classList.add('hidden');
                confirmationModal.classList.remove('animate-fade-out-modal');
                confirmationModal.querySelector('.confirm-modal-content').classList.remove('animate-fade-out-modal');
            }, { once: true });
        } else {
            confirmationModal.classList.add('hidden');
        }
    }

    let confirmPromiseResolve;

    function askForConfirmation() {
        return new Promise(resolve => {
            confirmPromiseResolve = resolve;
            showConfirmationModal();
        });
    }

    // Add event listeners for the modal buttons
    confirmSubmitButton.addEventListener('click', () => {
        hideConfirmationModal();
        confirmPromiseResolve(true);
    });

    confirmCancelButton.addEventListener('click', () => {
        hideConfirmationModal();
        confirmPromiseResolve(false);
    });

    // --- NEW: Populate Form for Update ---
    /**
     * Fetches a single PTO request by ID and populates the form fields.
     * @param {string} id The ID of the PTO request to fetch.
     */
    async function populateFormForUpdate(id) {
        showLoadingState('Loading Data...');
        try {
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const response = await smartFetch(`/api/pto-requests/${id}/`, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/auth/login/';
                    return;
                }
                const errorData = await response.json();
                throw new Error(`Failed to load PTO request for update. Status: ${response.status}. Error: ${JSON.stringify(errorData)}`);
            }

            const ptoRequest = await response.json();
            console.log("PTO Request Data for Update:", ptoRequest);

            // Populate form fields
            // Ensure dropdowns are populated first before setting their values
            await Promise.all([
                fetchAndPopulateDropdown('/api/department/', departmentSelect, 'Select your Department', 'id', 'name'),
                fetchAndPopulateDropdown('/api/departmentpaytype/', payTypeSelect, 'Select Pay Type', 'id', 'name')
            ]);

            form.department_name.value = ptoRequest.department_name; // Should be the ID
            form.pay_types.value = ptoRequest.pay_types; // Should be the ID

            // Format datetime-local fields
            // API returns ISO format, which is directly compatible with datetime-local
            // If it returns a Z-timezone, we need to strip it for local datetime-local input
            form.start_date_time.value = ptoRequest.start_date_time ? ptoRequest.start_date_time.slice(0, 16) : '';
            form.end_date_time.value = ptoRequest.end_date_time ? ptoRequest.end_date_time.slice(0, 16) : '';
            form.reason.value = ptoRequest.reason || '';

            // Update UI for update mode
            submitButtonText.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 inline-block" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>Update Request
            `;
            // Update page title and form heading
            if (pageTitle) pageTitle.textContent = 'Edit Time Off Request';
            if (formHeading) formHeading.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" class="h-9 w-9 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Edit Your Time Off Request
            `;
            if (formParagraph) formParagraph.textContent = 'Modify the details of your time off request and submit the updates.';
            clearFormButton.textContent = 'Reset Form'; // Change button text

            showNotification('Form loaded for update.', 'success');
        } catch (error) {
            console.error('[Update Load] Error loading PTO request for update:', error);
            showNotification('Failed to load request details. Please try again.', 'error');
            // Consider redirecting back to the list if loading fails critically
            // window.location.href = '/ptorequest/';
        } finally {
            hideLoadingState('Submit Request'); // Reset button text to default
        }
    }

    // --- Initial Data Loading & Mode Check ---
    // Extract PTO ID from URL if present (e.g., /ptorequest/submit/?id=123)
    const urlParams = new URLSearchParams(window.location.search);
    ptoRequestId = urlParams.get('id');

    if (ptoRequestId) {
        populateFormForUpdate(ptoRequestId);
    } else {
        // Only fetch and populate dropdowns if not in update mode,
        // as populateFormForUpdate already handles this.
        fetchAndPopulateDropdown('/api/department/', departmentSelect, 'Select your Department', 'id', 'name');
        fetchAndPopulateDropdown('/api/departmentpaytype/', payTypeSelect, 'Select Pay Type', 'id', 'name');
    }

    // --- Form Submission Handling ---
    form.addEventListener('submit', async function(event) {
        event.preventDefault();

        const confirmSubmission = await askForConfirmation();
        if (!confirmSubmission) {
            showNotification('PTO request submission cancelled.', 'warning');
            return;
        }

        clearFieldErrors();
        showLoadingState(ptoRequestId ? 'Updating...' : 'Submitting...'); // Dynamic loading text

        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const payload = {
            department_name: form.department_name.value,
            pay_types: form.pay_types.value,
            start_date_time: form.start_date_time.value,
            end_date_time: form.end_date_time.value,
            reason: form.reason.value
        };

        let method = 'POST';
        let url = '/api/pto-requests/';
        let successMessage = 'Your time off request was successfully submitted!'; // Default message

        if (ptoRequestId) {
            // If ptoRequestId exists, it's an update operation
            method = 'PUT'; // Or PATCH, depending on your API design (PUT for full replacement, PATCH for partial)
            url = `/api/pto-requests/${ptoRequestId}/`;
            successMessage = 'Your time off request was successfully updated!'; // Update message
            showNotification('Attempting to update request...', 'warning'); // Provide immediate feedback
        } else {
            showNotification('Attempting to submit new request...', 'warning');
        }

        try {
            const response = await smartFetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                credentials: 'include',
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                const data = await response.json();
                // Pass the success message via URL query parameter
                window.location.href = `/auth/ptorequest/details/?message=${encodeURIComponent(successMessage)}&type=success`;
                console.log("[Form Submission] PTO request processed successfully:", data);
            } else if (response.status === 400) {
                const errorData = await response.json();
                console.error('[Form Submission] Validation Errors:', errorData);

                Object.keys(errorData).forEach(field => {
                    const fieldElement = form.querySelector(`[name="${field}"]`);
                    if (fieldElement) {
                        const errorDiv = fieldElement.nextElementSibling;
                        if (errorDiv && errorDiv.classList.contains('field-errors')) {
                            errorDiv.textContent = Array.isArray(errorData[field]) ? errorData[field].join(' ') : errorData[field];
                        }
                    } else if (field === 'non_field_errors' || field === 'detail') {
                        const errorMessageText = Array.isArray(errorData[field]) ? errorData[field].join(' ') : errorData[field];
                        showNotification(`Submission failed: ${errorMessageText}`, 'error');
                    }
                });
                showNotification('Please correct the errors in the form.', 'error');
            } else if (response.status === 401) {
                console.error("[Form Submission] Unauthorized. Redirecting to login.");
                window.location.href = '/auth/login/';
            } else {
                const errorText = await response.text();
                console.error(`[Form Submission] Server Error (${response.status}):`, errorText);
                showNotification(`An unexpected error occurred (${response.status}). Please try again.`, 'error');
            }
        } catch (err) {
            console.error('[Form Submission] Network or unknown error during submission:', err);
            showNotification('Network error, please check your internet connection and try again.', 'error');
        } finally {
            hideLoadingState(ptoRequestId ? 'Update Request' : 'Submit Request'); // Dynamic button text reset
        }
    });

    // --- Clear/Reset Form Button Handling ---
    clearFormButton.addEventListener('click', function() {
        form.reset();
        clearFieldErrors();
        if (ptoRequestId) { // If in update mode, allow option to revert to original data or clear entirely
            // Optionally, reload original data or just clear
            // For now, it will simply clear the form fields
            showNotification('Form cleared. To revert, refresh the page.', 'warning');
        } else {
            showNotification('Form cleared!', 'warning');
        }
    });
});