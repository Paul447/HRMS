// static/ptorequest/js/modules/ptorequest/formHandler.js

import { smartFetch } from './apiService.js';
import { showNotification } from './notificationService.js';
import { fetchAndPopulateDropdown } from './dropdownHandler.js';

/**
 * Gets references to all necessary DOM elements for the PTO request form.
 * @returns {Object} An object containing references to DOM elements.
 */
export function getDomElements() {
    return {
        departmentSelect: document.getElementById('department_name'),
        payTypeSelect: document.getElementById('pay_types'),
        form: document.getElementById('ptoRequestForm'),
        submitButton: document.getElementById('submitButton'),
        submitButtonText: document.getElementById('submitButtonText'),
        loadingSpinner: document.getElementById('loadingSpinner'),
        clearFormButton: document.getElementById('clearFormButton'),
        confirmationModal: document.getElementById('confirmationModal'),
        confirmSubmitButton: document.getElementById('confirmSubmitButton'),
        confirmCancelButton: document.getElementById('confirmCancelButton'),
        pageTitle: document.getElementById('page_title'),
        formHeading: document.getElementById('ptoRequestForm').querySelector('h4'), // Changed from h2 to h4
        formParagraph: document.getElementById('ptoRequestForm').querySelector('p') // Added to handle p tag
    };
}

/**
 * Clears all existing field-specific error messages.
 */
export function clearFieldErrors() {
    document.querySelectorAll('.field-errors').forEach(errorDiv => {
        errorDiv.textContent = '';
    });
    console.log('[FormHandler] All field errors cleared.');
}

/**
 * Shows the loading spinner and disables the submit button.
 * @param {HTMLElement} submitButton The submit button element.
 * @param {HTMLElement} submitButtonText The text element within the submit button.
 * @param {HTMLElement} loadingSpinner The loading spinner element.
 * @param {string} buttonText The text to display on the button.
 */
export function showLoadingState(submitButton, submitButtonText, loadingSpinner, buttonText = 'Processing...') {
    submitButton.disabled = true;
    submitButtonText.innerHTML = buttonText;
    submitButtonText.classList.remove('inline-block');
    submitButtonText.classList.add('hidden');
    loadingSpinner.classList.remove('hidden');
    console.log(`[FormHandler] Loading state activated: "${buttonText}"`);
}

/**
 * Hides the loading spinner and enables the submit button.
 * @param {HTMLElement} submitButton The submit button element.
 * @param {HTMLElement} submitButtonText The text element within the submit button.
 * @param {HTMLElement} loadingSpinner The loading spinner element.
 * @param {string} originalText The original text for the button.
 */
export function hideLoadingState(submitButton, submitButtonText, loadingSpinner, originalText = 'Submit Request') {
    submitButton.disabled = false;
    submitButtonText.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2 inline-block align-text-bottom" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                                  </svg>${originalText}`;
    submitButtonText.classList.remove('hidden');
    submitButtonText.classList.add('inline-block');
    loadingSpinner.classList.add('hidden');
    console.log(`[FormHandler] Loading state deactivated. Button text: "${originalText}"`);
}

/**
 * Populates the form fields with data fetched from an existing PTO request.
 * This is used when the form is in "update" mode.
 * @param {string} id The ID of the PTO request to fetch.
 * @param {HTMLFormElement} form The form element.
 * @param {HTMLElement} pageTitle The page title element.
 * @param {HTMLElement} formHeading The form heading element.
 * @param {HTMLElement} formParagraph The form paragraph element.
 * @param {HTMLElement} submitButtonText The submit button text element.
 * @param {HTMLElement} clearFormButton The clear form button element.
 * @param {Function} showLoadingStateFn Function to show loading state.
 * @param {Function} hideLoadingStateFn Function to hide loading state.
 * @param {Function} showNotificationFn Function to display notifications.
 */
export async function populateFormForUpdate(id, form, pageTitle, formHeading, formParagraph, submitButtonText, clearFormButton, showLoadingStateFn, hideLoadingStateFn, showNotificationFn) {
    showLoadingStateFn(form.querySelector('#submitButton'), submitButtonText, form.querySelector('#loadingSpinner'), 'Loading Data...');
    console.log(`[FormHandler] Attempting to load form data for PTO ID: ${id}`);
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
                console.error('[FormHandler] 401 Unauthorized during form data load. Redirecting to login.');
                window.location.href = '/auth/login/';
                return;
            }
            const errorData = await response.json();
            throw new Error(`Failed to load PTO request for update. Status: ${response.status}. Error: ${JSON.stringify(errorData)}`);
        }

        const ptoRequest = await response.json();
        console.log('[FormHandler] PTO Request data fetched:', ptoRequest);

        // Populate form fields
        form.department_name.value = ptoRequest.department_name;
        form.pay_types.value = ptoRequest.pay_types;
        form.start_date_time.value = ptoRequest.start_date_time ? ptoRequest.start_date_time.slice(0, 16) : '';
        form.end_date_time.value = ptoRequest.end_date_time ? ptoRequest.end_date_time.slice(0, 16) : '';
        form.reason.value = ptoRequest.reason || '';

        showNotificationFn('Form loaded for update.', 'success');
    } catch (error) {
        console.error('[FormHandler] Error loading PTO request for update:', error);
        showNotificationFn('Failed to load request details. Please try again.', 'error');
    } finally {
        hideLoadingStateFn(form.querySelector('#submitButton'), submitButtonText, form.querySelector('#loadingSpinner'), 'Submit Request');
    }
}

/**
 * Updates the UI elements (titles, button text) based on whether the form is in
 * create or update mode.
 * @param {string|null} ptoRequestId The ID of the PTO request if in update mode, null otherwise.
 * @param {HTMLElement} pageTitle The page title element.
 * @param {HTMLElement} formHeading The form heading element.
 * @param {HTMLElement} formParagraph The form paragraph element.
 * @param {HTMLElement} submitButtonText The submit button text element.
 * @param {HTMLElement} clearFormButton The clear form button element.
 */
export function updateUIMode(ptoRequestId, pageTitle, formHeading, formParagraph, submitButtonText, clearFormButton) {
    if (ptoRequestId) {
        submitButtonText.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2 inline-block align-text-bottom" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>Update Request
        `;
        if (pageTitle) pageTitle.textContent = 'Edit Time Off Request';
        if (formHeading) formHeading.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Edit Your Time Off Request
        `;
        if (formParagraph) formParagraph.textContent = 'Modify the details of your time off request and submit the updates.';
        clearFormButton.textContent = 'Reset Form';
        console.log('[FormHandler] UI updated to "update" mode.');
    } else {
        submitButtonText.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2 inline-block align-text-bottom" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>Submit
        `;
        if (pageTitle) pageTitle.textContent = 'Submit New Time Off Request';
        if (formHeading) formHeading.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Request Time Off
        `;
        if (formParagraph) formParagraph.textContent = 'Fill out the form below to submit a new time off request.';
        clearFormButton.textContent = 'Clear';
        console.log('[FormHandler] UI updated to "create" mode.');
    }
}