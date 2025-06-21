
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

// Global variables for DOM elements
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
    console.log('Error data received:', errorData); // Debug log

    let errorMessages = [];

    // Handle global errors
    if (errorData.detail) {
        errorMessages.push(errorData.detail);
    }

    // Handle non-field errors
    if (errorData.non_field_errors) {
        errorMessages.push(errorData.non_field_errors.join(' '));
    }

    // Handle all field-specific and logical errors
    Object.keys(errorData).forEach(field => {
        const fieldElement = formElement.querySelector(`[name="${field}"]`);
        if (fieldElement) {
            // Field-specific errors tied to form inputs
            const errorDiv = fieldElement.closest('div').querySelector('.field-errors');
            if (errorDiv) {
                errorDiv.textContent = Array.isArray(errorData[field]) ? errorData[field].join(' ') : errorData[field];
                errorMessages.push(`${field}: ${errorData[field]}`);
            }
        } else {
            // Logical errors not tied to form fields (e.g., unverified_sick_balance)
            errorMessages.push(errorData[field]);
        }
    });

    // Display all collected error messages
    if (errorMessages.length > 0) {
        showNotification(errorMessages.join('\n'), 'error');
    } else {
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
        return;
    }

    // Ask for confirmation
    const confirmed = await askForConfirmation(dom.confirmationModal, dom.confirmSubmitButton, dom.confirmCancelButton);
    if (!confirmed) {
        showNotification('PTO request submission cancelled.', 'warning');
        return;
    }

    clearFieldErrors();
    showLoadingState(dom.submitButton, dom.submitButtonText, dom.loadingSpinner, ptoRequestId ? 'Updating...' : 'Submitting...');

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const formData = new FormData(dom.form);

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
            window.location.href = `/auth/ptorequest/details/?message=${encodeURIComponent(successMessage)}&type=success`;
        } else if (response.status === 400) {
            const errorData = await response.json();
            console.log('Validation errors:', errorData); // Debug log
            handleFormErrors(errorData, dom.form);
        } else if (response.status === 401) {
            showNotification('Your session has expired. Please log in again.', 'error');
            window.location.href = '/auth/login/';
        } else {
            const errorText = await response.text();
            console.error('Server error:', errorText);
            showNotification(`An unexpected error occurred (${response.status}). Please try again.`, 'error');
        }
    } catch (err) {
        console.error('Fetch error:', err);
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
    toggleMedicalDocumentField();
    dom.medicalDocumentInput.value = '';

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
    const mandatoryDocumentLeaveTypes = ['FVSL', 'VSL'];
    const optionalDocumentLeaveTypes = ['Sick Leave', 'Medical Leave', 'Disability'];

    let isMandatory = false;
    let isOptionalButShown = false;

    if (mandatoryDocumentLeaveTypes.includes(selectedLeaveTypeName)) {
        isMandatory = true;
        isOptionalButShown = true;
    } else if (optionalDocumentLeaveTypes.includes(selectedLeaveTypeName)) {
        isOptionalButShown = true;
    }

    if (isOptionalButShown) {
        dom.medicalDocumentField.classList.remove('hidden');
        if (isMandatory) {
            dom.medicalDocumentInput.setAttribute('required', 'required');
            dom.medicalDocumentRequiredStar.classList.remove('hidden');
        } else {
            dom.medicalDocumentInput.removeAttribute('required');
            dom.medicalDocumentRequiredStar.classList.add('hidden');
        }
    } else {
        dom.medicalDocumentField.classList.add('hidden');
        dom.medicalDocumentInput.removeAttribute('required');
        dom.medicalDocumentRequiredStar.classList.add('hidden');
        dom.medicalDocumentInput.value = '';
    }
}

// --- Main DOMContentLoaded Event Listener ---
document.addEventListener('DOMContentLoaded', async function() {
    dom = getDomElements();
    dom.medicalDocumentField = document.getElementById('medicalDocumentField');
    dom.medicalDocumentInput = document.getElementById('medical_document');
    dom.medicalDocumentRequiredStar = document.getElementById('medicalDocumentRequiredStar');
    dom.medicalDocumentFieldErrors = dom.medicalDocumentInput ? dom.medicalDocumentInput.closest('div').querySelector('.field-errors') : null;

    initializeConfirmationModalListeners(dom.confirmationModal, dom.confirmSubmitButton, dom.confirmCancelButton);

    const urlParams = new URLSearchParams(window.location.search);
    ptoRequestId = urlParams.get('id');

    if (ptoRequestId) {
        await fetchAndPopulateDropdown('/api/department/', dom.departmentSelect, 'Select your Department', 'id', 'name');
        await fetchAndPopulateDropdown('/api/departmentleavetype/', dom.leaveTypeSelect, 'Select Leave Type', 'id', 'name');
        await populateFormForUpdate(ptoRequestId, dom.form, dom.pageTitle, dom.formHeading, dom.formParagraph, dom.submitButtonText, dom.clearFormButton, showLoadingState, hideLoadingState, showNotification);
        updateUIMode(ptoRequestId, dom.pageTitle, dom.formHeading, dom.formParagraph, dom.submitButtonText, dom.clearFormButton);
        toggleMedicalDocumentField();
    } else {
        fetchAndPopulateDropdown('/api/department/', dom.departmentSelect, 'Select your Department', 'id', 'name');
        fetchAndPopulateDropdown('/api/departmentleavetype/', dom.leaveTypeSelect, 'Select Leave Type', 'id', 'name');
        toggleMedicalDocumentField();
    }

    dom.form.addEventListener('submit', handleFormSubmission);
    dom.clearFormButton.addEventListener('click', handleClearForm);
    dom.leaveTypeSelect.addEventListener('change', toggleMedicalDocumentField);
});
