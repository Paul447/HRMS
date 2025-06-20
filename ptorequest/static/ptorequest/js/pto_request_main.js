// static/ptorequest/js/pto_request_main.js

import { smartFetch } from './modules/ptorequest/apiService.js';
import { showNotification } from './modules/ptorequest/notificationService.js';
import {
    getDomElements,
    showLoadingState,
    hideLoadingState,
    clearFieldErrors,
    populateFormForUpdate,
    updateUIMode
} from './modules/ptorequest/formHandler.js';
import {
    showConfirmationModal,
    hideConfirmationModal,
    askForConfirmation
} from './modules/ptorequest/confirmationModal.js';
import { fetchAndPopulateDropdown } from './modules/ptorequest/dropdownHandler.js';

// Global variables for DOM elements (or pass them around as needed)
let dom = {};
let ptoRequestId = null;

// --- Helper Functions ---

/**
 * Initializes confirmation modal event listeners.
 * @param {HTMLElement} confirmationModal
 * @param {HTMLElement} confirmSubmitButton
 * @param {HTMLElement} confirmCancelButton
 */
function initializeConfirmationModalListeners(confirmationModal, confirmSubmitButton, confirmCancelButton) {
    confirmSubmitButton.addEventListener('click', () => {
        hideConfirmationModal(confirmationModal);
    });

    confirmCancelButton.addEventListener('click', () => {
        hideConfirmationModal(confirmationModal);
    });

    confirmationModal.addEventListener('click', function(event) {
        if (event.target === confirmationModal) {
            hideConfirmationModal(confirmationModal);
        }
    });
}

/**
 * Handles client-side validation for medical document requirement.
 * @param {HTMLSelectElement} leaveTypeSelectElement
 * @param {HTMLInputElement} medicalDocumentInput
 * @param {HTMLElement} medicalDocumentFieldErrors
 * @returns {boolean} True if validation passes, false otherwise.
 */
function validateMedicalDocument(leaveTypeSelectElement, medicalDocumentInput, medicalDocumentFieldErrors) {
    const selectedLeaveTypeName = leaveTypeSelectElement.options[leaveTypeSelectElement.selectedIndex]?.text;
    const mandatoryDocumentLeaveTypes = ['FVSL', 'VSL'];

    if (mandatoryDocumentLeaveTypes.includes(selectedLeaveTypeName) && (!medicalDocumentInput || medicalDocumentInput.files.length === 0)) {
        showNotification('Medical document is required for this leave type (FVSL/VSL).', 'error');
        if (medicalDocumentFieldErrors) {
            medicalDocumentFieldErrors.textContent = 'This field is required.';
        }
        return false;
    }
    return true;
}

/**
 * Displays validation errors on the form.
 * @param {Object} errorData - The error data received from the API.
 * @param {HTMLFormElement} formElement - The form element.
 */
function handleFormErrors(errorData, formElement) {
    if (errorData.detail) {
        // Global error (e.g., "No active pay period")
        showNotification(`Submission failed: ${errorData.detail}`, 'error');
    } else if (errorData.non_field_errors) {
        // General non-field errors
        showNotification(`Submission failed: ${errorData.non_field_errors.join(' ')}`, 'error');
    } else {
        // Field-specific errors
        Object.keys(errorData).forEach(field => {
            const fieldElement = formElement.querySelector(`[name="${field}"]`);
            if (fieldElement) {
                const errorDiv = fieldElement.closest('div').querySelector('.field-errors');
                if (errorDiv) {
                    errorDiv.textContent = Array.isArray(errorData[field]) ? errorData[field].join(' ') : errorData[field];
                }
            }
        });
        showNotification('Please correct the errors in the form.', 'error');
    }
}

/**
 * Handles the form submission process.
 * @param {Event} event - The submit event.
 */
async function handleFormSubmission(event) {
    event.preventDefault();

    // Client-side validation for medical document
    if (!validateMedicalDocument(dom.leaveTypeSelect, dom.medicalDocumentInput, dom.medicalDocumentFieldErrors)) {
        return; // Stop submission if validation fails
    }

    // Ask for confirmation
    const confirmed = await askForConfirmation(dom.confirmationModal, dom.confirmSubmitButton, dom.confirmCancelButton);
    if (!confirmed) {
        showNotification('PTO request submission cancelled.', 'warning');
        return;
    }

    clearFieldErrors(); // Clear all existing field errors
    showLoadingState(dom.submitButton, dom.submitButtonText, dom.loadingSpinner, ptoRequestId ? 'Updating...' : 'Submitting...');

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const formData = new FormData(dom.form); // 'dom.form' is the form element

    let headers = {
        'X-CSRFToken': csrftoken
    };

    let method = 'POST';
    let url = '/api/pto-requests/';
    let successMessage = 'Your time off request was successfully submitted!';

    if (ptoRequestId) {
        method = 'PUT';
        url = `/api/pto-requests/${ptoRequestId}/`;
        successMessage = 'Your time off request was successfully updated!';
        showNotification('Attempting to update request...', 'warning');
    } else {
        showNotification('Attempting to submit new request...', 'warning');
    }

    try {
        const response = await smartFetch(url, {
            method: method,
            headers: headers,
            credentials: 'include',
            body: formData
        });

        if (response.ok) {
            // Success
            window.location.href = `/auth/ptorequest/details/?message=${encodeURIComponent(successMessage)}&type=success`;
        } else if (response.status === 400) {
            // Bad Request (Validation Errors)
            const errorData = await response.json();
            handleFormErrors(errorData, dom.form); // Pass form element to helper
        } else if (response.status === 401) {
            // Unauthorized
            showNotification('Your session has expired. Please log in again.', 'error');
            window.location.href = '/auth/login/';
        } else {
            // Other server errors
            const errorText = await response.text();
            showNotification(`An unexpected error occurred (${response.status}). Please try again.`, 'error');
            console.error("Server error:", errorText);
        }
    } catch (err) {
        // Network or unexpected client-side errors
        console.error("Fetch error:", err);
        showNotification('Network error, please check your internet connection and try again.', 'error');
    } finally {
        hideLoadingState(dom.submitButton, dom.submitButtonText, dom.loadingSpinner, ptoRequestId ? 'Update Request' : 'Submit Request');
    }
}

/**
 * Resets the form and its error states.
 */
function handleClearForm() {
    dom.form.reset();
    clearFieldErrors();
    // Manually reset the medical document field's visibility and required status
    // This calls the same logic as toggleMedicalDocumentField to ensure state consistency
    toggleMedicalDocumentField(); // Resets to default hidden state
    dom.medicalDocumentInput.value = ''; // Clear selected file content
    
    if (ptoRequestId) {
        showNotification('Form cleared. To revert, refresh the page.', 'warning');
    } else {
        showNotification('Form cleared!', 'warning');
    }
}

/**
 * Toggles the visibility and required attribute of the medical document field
 * based on the selected leave type.
 */
function toggleMedicalDocumentField() {
    const selectedLeaveTypeName = dom.leaveTypeSelect.options[dom.leaveTypeSelect.selectedIndex]?.text;

    // Define leave types where the document is MANDATORY
    const mandatoryDocumentLeaveTypes = ['FVSL', 'VSL']; // Family Verified Sick Leave, Verified Sick Leave
    // Define other medical leave types where the document is OPTIONAL but shown
    const optionalDocumentLeaveTypes = ['Sick Leave', 'Medical Leave', 'Disability'];

    let isMandatory = false;
    let isOptionalButShown = false;

    if (mandatoryDocumentLeaveTypes.includes(selectedLeaveTypeName)) {
        isMandatory = true;
        isOptionalButShown = true; // If mandatory, it's also shown
    } else if (optionalDocumentLeaveTypes.includes(selectedLeaveTypeName)) {
        isOptionalButShown = true;
    }

    if (isOptionalButShown) {
        dom.medicalDocumentField.classList.remove('hidden');
        if (isMandatory) {
            dom.medicalDocumentInput.setAttribute('required', 'required');
            dom.medicalDocumentRequiredStar.classList.remove('hidden'); // Show the star
        } else {
            dom.medicalDocumentInput.removeAttribute('required');
            dom.medicalDocumentRequiredStar.classList.add('hidden'); // Hide the star
        }
    } else {
        dom.medicalDocumentField.classList.add('hidden');
        dom.medicalDocumentInput.removeAttribute('required');
        dom.medicalDocumentRequiredStar.classList.add('hidden'); // Ensure star is hidden
        dom.medicalDocumentInput.value = ''; // Clear selected file when hidden
    }
}


// --- Main DOMContentLoaded Event Listener ---
document.addEventListener('DOMContentLoaded', async function() {
    dom = getDomElements(); // Populate dom object with all elements

    // Get specific medical document elements after general DOM elements are fetched
    // Ensure these are directly assigned to 'dom' for consistency
    dom.medicalDocumentField = document.getElementById('medicalDocumentField');
    dom.medicalDocumentInput = document.getElementById('medical_document');
    dom.medicalDocumentRequiredStar = document.getElementById('medicalDocumentRequiredStar');
    dom.medicalDocumentFieldErrors = dom.medicalDocumentInput ? dom.medicalDocumentInput.closest('div').querySelector('.field-errors') : null;


    // Initialize Confirmation Modal Listeners
    initializeConfirmationModalListeners(dom.confirmationModal, dom.confirmSubmitButton, dom.confirmCancelButton);

    // --- Initial Data Loading & Mode Check ---
    const urlParams = new URLSearchParams(window.location.search);
    ptoRequestId = urlParams.get('id');

    if (ptoRequestId) {
        // In update mode, populate dropdowns and then form data
        await fetchAndPopulateDropdown('/api/department/', dom.departmentSelect, 'Select your Department', 'id', 'name');
        await fetchAndPopulateDropdown('/api/departmentleavetype/', dom.leaveTypeSelect, 'Select Leave Type', 'id', 'name');
        await populateFormForUpdate(ptoRequestId, dom.form, dom.pageTitle, dom.formHeading, dom.formParagraph, dom.submitButtonText, dom.clearFormButton, showLoadingState, hideLoadingState, showNotification);
        updateUIMode(ptoRequestId, dom.pageTitle, dom.formHeading, dom.formParagraph, dom.submitButtonText, dom.clearFormButton);
        // Important: Call toggleMedicalDocumentField after populating form for update
        // to ensure its state is correct based on loaded data.
        toggleMedicalDocumentField();
    } else {
        // In create mode, just populate dropdowns
        fetchAndPopulateDropdown('/api/department/', dom.departmentSelect, 'Select your Department', 'id', 'name');
        fetchAndPopulateDropdown('/api/departmentleavetype/', dom.leaveTypeSelect, 'Select Leave Type', 'id', 'name');
        // Call initially for create mode to set default state
        toggleMedicalDocumentField();
    }

    // --- Event Listeners ---
    dom.form.addEventListener('submit', handleFormSubmission);
    dom.clearFormButton.addEventListener('click', handleClearForm);
    dom.leaveTypeSelect.addEventListener('change', toggleMedicalDocumentField); // Add this listener here
});