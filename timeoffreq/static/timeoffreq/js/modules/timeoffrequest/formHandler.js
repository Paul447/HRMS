/**
 * formHandler.js
 *
 * This module encapsulates all client-side logic for the time off request form.
 * It handles DOM element retrieval, form validation, loading states, API interaction,
 * and displaying feedback through the notification and confirmation services.
 */

import { ApiService } from './apiService.js';
import { NotificationService } from './notificationService.js'; // Use the modularized service
import { askForConfirmation } from './confirmationModal.js'; // Use the modularized function
import { formatDateTimeForAPI } from './utils.js';
import { DropdownHandler } from './dropdownHandler.js'; // Use the modularized dropdown handler

export const FormHandler = (function() {
    // Defines and retrieves all necessary DOM elements for the form.
    // This centralizes DOM access and makes it easier to manage.
    function getDomElements() {
        return {
            leaveTypeSelect: document.getElementById('leave_type'),
            form: document.getElementById('timeOffRequestForm'),
            startDateInput: document.getElementById('start_date_time'),
            endDateInput: document.getElementById('end_date_time'),
            reasonTextarea: document.getElementById('reason'),
            medicalDocumentInput: document.getElementById('medical_document'),
            medicalDocumentField: document.getElementById('medicalDocumentField'),
            medicalDocumentRequiredStar: document.getElementById('medicalDocumentRequiredStar'),
            medicalDocumentUploadLabel: document.getElementById('medicalDocumentUploadLabel'),
            medicalFileNameDisplay: document.getElementById('medicalFileNameDisplay'),
            submitButton: document.getElementById('submitButton'),
            submitButtonText: document.getElementById('submitButtonText'),
            loadingSpinner: document.getElementById('loadingSpinner'),
            clearFormButton: document.getElementById('clearFormButton'),
            // Confirmation modal elements are now managed by the ConfirmationModal module internally
            // but we keep their IDs here if we need to pass the main modal container.
            confirmationModal: document.getElementById('confirmationModal'), // Main modal container
            // Error display divs
            leaveTypeErrors: document.getElementById('leaveTypeErrors'),
            startDateErrors: document.getElementById('startDateErrors'),
            endDateErrors: document.getElementById('endDateErrors'),
            reasonErrors: document.getElementById('reasonErrors'),
            documentProofErrors: document.getElementById('documentProofErrors'),
            // UI mode elements for update/create distinction
            pageTitle: document.getElementById('page_title'),
            formHeading: document.getElementById('form_heading'),
            formParagraph: document.getElementById('form_paragraph')
        };
    }

    /**
     * Clears all validation error messages displayed on the form.
     */
    function clearFieldErrors() {
        document.querySelectorAll('.field-errors').forEach(errorDiv => {
            errorDiv.textContent = '';
        });
    }

    /**
     * Activates the loading state on the submit button.
     * Disables the button, hides text, and shows a spinner.
     * @param {HTMLElement} submitButton - The submit button element.
     * @param {HTMLElement} submitButtonText - The text span within the submit button.
     * @param {HTMLElement} loadingSpinner - The loading spinner element.
     * @param {string} buttonText - The text to display next to the spinner (e.g., 'Processing...').
     */
    function showLoadingState(submitButton, submitButtonText, loadingSpinner, buttonText = 'Processing...') {
        submitButton.disabled = true;
        submitButton.classList.add('opacity-50', 'cursor-not-allowed');
        submitButtonText.classList.add('hidden');
        loadingSpinner.classList.remove('hidden');
    }

    /**
     * Deactivates the loading state, re-enables the submit button, and restores its original text.
     * @param {HTMLElement} submitButton - The submit button element.
     * @param {HTMLElement} submitButtonText - The text span within the submit button.
     * @param {HTMLElement} loadingSpinner - The loading spinner element.
     * @param {string} originalText - The original text to restore on the button.
     */
    function hideLoadingState(submitButton, submitButtonText, loadingSpinner, originalText = 'Submit Request') {
        submitButton.disabled = false;
        submitButton.classList.remove('opacity-50', 'cursor-not-allowed');
        // Restore the button text with its SVG icon
        submitButtonText.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                                      </svg>${originalText}`;
        submitButtonText.classList.remove('hidden');
        loadingSpinner.classList.add('hidden');
    }

    /**
     * Fetches existing time off request data and populates the form for editing.
     * Includes error handling and loading indicators.
     * @param {string} id - The ID of the time off request to load.
     * @param {object} domElements - Object containing references to DOM elements.
     * @param {function} showLoadingStateFn - Function to show loading state.
     * @param {function} hideLoadingStateFn - Function to hide loading state.
     * @param {function} showNotificationFn - Function to show global notifications.
     */
    async function populateFormForUpdate(id, domElements, showLoadingStateFn, hideLoadingStateFn, showNotificationFn) {
        // Assume API_ENDPOINTS is available in the scope (from timeOffReq.js)
        const API_ENDPOINTS = {
            LEAVE_TYPES: '/api/leave-type-dropdown/',
            SUBMIT_REQUEST: '/api/timeoffrequests/'
        };

        showLoadingStateFn(domElements.submitButton, domElements.submitButtonText, domElements.loadingSpinner, 'Loading Data...');
        
        try {
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const response = await ApiService.smartFetch(`${API_ENDPOINTS.SUBMIT_REQUEST}${id}/`, {
                method: 'GET',
                credentials: 'include', // Ensure cookies (like CSRF) are sent
                headers: { 'X-CSRFToken': csrftoken, 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    showNotificationFn('Your session has expired. Please log in again.', 'error');
                    // Optionally redirect to login page
                    // window.location.href = '/login';
                    return;
                }
                const errorData = await response.json(); // Attempt to parse error details
                throw new Error(`Failed to load Time Off request for update. Status: ${response.status}. Error: ${JSON.stringify(errorData)}`);
            }

            const timeOffRequest = await response.json();
            
            // Re-populate dropdown to ensure all options are available
            await DropdownHandler.fetchAndPopulateDropdown(
                API_ENDPOINTS.LEAVE_TYPES,
                domElements.leaveTypeSelect,
                'Select Leave Type',
                'id',
                'display_name'
            );

            // Populate form fields
            domElements.leaveTypeSelect.value = timeOffRequest.requested_leave_type_details.id;
            // Slice to 16 characters to match datetime-local format 'YYYY-MM-DDTHH:MM'
            domElements.startDateInput.value = timeOffRequest.start_date_time ? timeOffRequest.start_date_time.slice(0, 16) : '';
            domElements.endDateInput.value = timeOffRequest.end_date_time ? timeOffRequest.end_date_time.slice(0, 16) : '';
            domElements.reasonTextarea.value = timeOffRequest.employee_leave_reason || '';

            // Handle existing document proof display
            if (timeOffRequest.document_proof) {
                const fileName = timeOffRequest.document_proof.split('/').pop();
                domElements.medicalFileNameDisplay.textContent = `Existing file: ${fileName}`;
                domElements.medicalDocumentUploadLabel.classList.add('custom-file-upload-selected');
            } else {
                domElements.medicalFileNameDisplay.textContent = 'No file chosen';
                domElements.medicalDocumentUploadLabel.classList.remove('custom-file-upload-selected');
            }
            
            // Trigger change event on leave type to update medical document field visibility
            const changeEvent = new Event('change');
            domElements.leaveTypeSelect.dispatchEvent(changeEvent);

            showNotificationFn('Form loaded for update.', 'success');
        } catch (error) {
            showNotificationFn('Failed to load request details. Please try again.', 'error');
            console.error('[FormHandler] Error populating form for update:', error);
        } finally {
            // Ensure button text reverts to "Update Request" after loading
            hideLoadingStateFn(domElements.submitButton, domElements.submitButtonText, domElements.loadingSpinner, 'Update Request');
        }
    }

    /**
     * Updates UI text and button labels based on whether the form is in 'create' or 'update' mode.
     * @param {string|null} timeOffRequestId - The ID of the time off request if in update mode, otherwise null.
     * @param {object} domElements - Object containing references to DOM elements.
     */
    function updateUIMode(timeOffRequestId, domElements) {
        if (timeOffRequestId) {
            domElements.submitButtonText.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                                                      </svg>Update Request`;
            // Optional: update header text if elements exist
            if (domElements.pageTitle) domElements.pageTitle.textContent = 'Edit Time Off Request';
            if (domElements.formHeading) domElements.formHeading.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>Edit Your Time Off Request`;
            if (domElements.formParagraph) domElements.formParagraph.textContent = 'Modify the details of your time off request and submit the updates.';
            domElements.clearFormButton.textContent = 'Reset Form';
        } else {
            domElements.submitButtonText.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                                                      </svg>Submit Request`;
            if (domElements.pageTitle) domElements.pageTitle.textContent = 'Submit New Time Off Request';
            if (domElements.formHeading) domElements.formHeading.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>Request Time Off`;
            if (domElements.formParagraph) domElements.formParagraph.textContent = 'Effortlessly request time off with our intuitive form. Please fill in all the required details.';
            domElements.clearFormButton.textContent = 'Clear Form'; // Changed from 'Clear' for clarity
        }
    }

    /**
     * Validates if a medical document is required for the selected leave type.
     * This is a client-side pre-check; server-side validation is still essential.
     * @param {HTMLElement} leaveTypeSelectElement - The select element for leave type.
     * @param {HTMLElement} medicalDocumentInput - The file input for the medical document.
     * @param {HTMLElement} medicalDocumentFieldErrors - The div to display document proof errors.
     * @returns {boolean} True if validation passes, false otherwise.
     */
    function validateMedicalDocument(leaveTypeSelectElement, medicalDocumentInput, medicalDocumentFieldErrors) {
        const selectedOption = leaveTypeSelectElement.options[leaveTypeSelectElement.selectedIndex];
        // Ensure we get the text content of the *selected* option
        const selectedLeaveTypeText = selectedOption ? selectedOption.textContent.trim() : '';

        // IMPORTANT: Configure these based on the exact `display_name` returned by your backend API
        // for 'FVSL' and 'VSL' leave types. If your Django `leave_type.name` is "FVSL" and "VSL",
        // then these values are correct. If it's something like "Family Medical Leave" or "Vacation Sick Leave",
        // then update this array accordingly.
        const mandatoryDocumentLeaveTypes = ['FVSL', 'VSL'];
        // Example: if 'Sick Leave' also requires a document, add it: ['Sick Leave', 'FVSL', 'VSL']

        if (mandatoryDocumentLeaveTypes.includes(selectedLeaveTypeText) && medicalDocumentInput.files.length === 0) {
            NotificationService.showNotification('Document proof is required for this leave type.', 'error');
            if (medicalDocumentFieldErrors) {
                medicalDocumentFieldErrors.textContent = 'This field is required.';
            }
            return false;
        }

        // Also perform file type and size validation if a file is selected
        if (medicalDocumentInput.files.length > 0) {
            const file = medicalDocumentInput.files[0];
            const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
            const maxSize = 5 * 1024 * 1024; // 5MB

            if (!allowedTypes.includes(file.type)) {
                NotificationService.showNotification('Invalid file type. Only PDF, JPG, JPEG, PNG are allowed.', 'error');
                if (medicalDocumentFieldErrors) {
                    medicalDocumentFieldErrors.textContent = 'Invalid file type.';
                }
                return false;
            }
            if (file.size > maxSize) {
                NotificationService.showNotification('File size exceeds 5MB limit (Max 5MB).', 'error');
                if (medicalDocumentFieldErrors) {
                    medicalDocumentFieldErrors.textContent = 'File size exceeds 5MB.';
                }
                return false;
            }
        }
        return true;
    }


    /**
     * Displays backend validation errors on the form.
     * @param {object} errorData - The error object received from the backend API.
     * @param {object} domElements - Object containing references to DOM elements.
     */
    function handleFormErrors(errorData, domElements) {
        clearFieldErrors(); // Clear all existing errors first

        let generalErrorMessages = [];

        // Check for common non-field errors
        if (errorData.detail) {
            generalErrorMessages.push(errorData.detail);
        }
        if (errorData.non_field_errors) {
            generalErrorMessages.push(errorData.non_field_errors.join(' '));
        }

        // Iterate through specific field errors
        for (const fieldName in errorData) {
            if (errorData.hasOwnProperty(fieldName)) {
                // Ensure errorMessages is an array and join them, or use as is
                const errorMessages = Array.isArray(errorData[fieldName]) ? errorData[fieldName].join(', ') : errorData[fieldName];
                let targetErrorDiv = null;

                // Map backend field names to frontend error div IDs
                switch (fieldName) {
                    case 'requested_leave_type': targetErrorDiv = domElements.leaveTypeErrors; break;
                    case 'start_date_time': targetErrorDiv = domElements.startDateErrors; break;
                    case 'end_date_time': targetErrorDiv = domElements.endDateErrors; break;
                    case 'employee_leave_reason': targetErrorDiv = domElements.reasonErrors; break;
                    case 'document_proof': targetErrorDiv = domElements.documentProofErrors; break;
                    // Add other field cases as needed, e.g., 'reference_pay_period' if you want to display it somewhere
                    case 'reference_pay_period':
                        // This error might not have a specific div, so add to general messages
                        generalErrorMessages.push(`Pay Period Error: ${errorMessages}`);
                        break;
                    default:
                        // Collect any unhandled field errors into general messages
                        if (fieldName !== 'detail' && fieldName !== 'non_field_errors') {
                            generalErrorMessages.push(`${errorMessages}`);
                        }
                        break;
                }

                // Display error in the specific div if found
                if (targetErrorDiv) {
                    targetErrorDiv.textContent = errorMessages;
                }
            }
        }

        // Display a general notification if there are aggregated errors or no specific field errors
        if (generalErrorMessages.length > 0) {
            NotificationService.showNotification(generalErrorMessages.join('. '), 'error');
        } else {
            // Fallback general error message if no specific details are available
            NotificationService.showNotification('Please correct the errors in the form.', 'error');
        }
    }

    /**
     * Handles the form submission process, including client-side validation,
     * confirmation, API request, and response handling.
     * @param {Event} event - The form submission event.
     * @param {object} dom - Object containing references to DOM elements.
     * @param {string|null} timeOffRequestId - ID if updating, null if creating.
     * @param {object} apiEndpoints - Object with API endpoint URLs.
     */
    async function handleFormSubmission(event, dom, timeOffRequestId, apiEndpoints) {
        event.preventDefault(); // Prevent default browser form submission

        // Perform client-side medical document validation first
        if (!validateMedicalDocument(dom.leaveTypeSelect, dom.medicalDocumentInput, dom.documentProofErrors)) {
            // If client-side validation fails, a notification and error message are already shown.
            return;
        }

        // Ask for user confirmation using the ConfirmationModal module
        const confirmed = await askForConfirmation(); // Only pass the modal container, module handles buttons
        if (!confirmed) {
            NotificationService.showNotification('Time off request submission cancelled.', 'warning');
            return; // Exit if user cancels
        }

        clearFieldErrors(); // Clear any previous errors before showing loading state
        showLoadingState(dom.submitButton, dom.submitButtonText, dom.loadingSpinner, timeOffRequestId ? 'Updating...' : 'Submitting...');

        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const formData = new FormData();
        
        // Append form data fields
        formData.append('requested_leave_type', dom.leaveTypeSelect.value);
        
        // Format dates for API consumption
        const formattedStartDate = formatDateTimeForAPI(dom.startDateInput.value);
        const formattedEndDate = formatDateTimeForAPI(dom.endDateInput.value);

        if (!formattedStartDate || !formattedEndDate) {
            NotificationService.showNotification('Invalid date/time input. Please check your entries.', 'error');
            hideLoadingState(dom.submitButton, dom.submitButtonText, dom.loadingSpinner, timeOffRequestId ? 'Update Request' : 'Submit Request');
            return;
        }
        formData.append('start_date_time', formattedStartDate);
        formData.append('end_date_time', formattedEndDate);
        formData.append('employee_leave_reason', dom.reasonTextarea.value);

        // Only append document_proof if a file is selected (not if it's just an existing file from update mode)
        if (dom.medicalDocumentInput.files.length > 0) {
            formData.append('document_proof', dom.medicalDocumentInput.files[0]);
        }
        // Important: For PUT requests, if document_proof is not changed, DO NOT send it again,
        // or send null if you want to clear it. DRF's `partial=True` in ViewSet.update
        // means missing fields aren't updated, which is often desired. If you send a file, it's replaced.

        let method = 'POST';
        let url = apiEndpoints.SUBMIT_REQUEST;
        let successMessage = 'Your time off request was successfully submitted!';

        if (timeOffRequestId) {
            method = 'PUT'; // Use PUT for updates
            url = `${apiEndpoints.SUBMIT_REQUEST}${timeOffRequestId}/`; // Append ID for update URL
            successMessage = 'Your time off request was successfully updated!';
            NotificationService.showNotification('Attempting to update request...', 'warning');
        } else {
            NotificationService.showNotification('Attempting to submit new request...', 'warning');
        }

        try {
            const response = await ApiService.smartFetch(url, {
                method: method,
                // Do NOT set Content-Type header manually for FormData.
                // The browser sets it correctly with boundary.
                headers: { 'X-CSRFToken': csrftoken },
                credentials: 'include',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                NotificationService.showNotification(successMessage, 'success');
                dom.form.reset(); // Clear the form
                // Reset file input display and hidden field
                dom.medicalDocumentInput.value = ''; // Important for clearing the file input
                dom.medicalFileNameDisplay.textContent = 'No file chosen';
                dom.medicalDocumentUploadLabel.classList.remove('custom-file-upload-selected');
                dom.medicalDocumentField.classList.add('hidden'); // Hide the field
                dom.medicalDocumentRequiredStar.classList.add('hidden');
                dom.medicalDocumentInput.required = false; // Ensure 'required' attribute is removed
                dom.leaveTypeSelect.value = ''; // Reset leave type select

                 // Reset date/time inputs' value to empty strings for full clear
                dom.startDateInput.value = '';
                dom.endDateInput.value = '';

            } else if (response.status === 400) {
                // Handle validation errors from the backend (DRF serializer errors)
                const errorData = await response.json();
                console.error('Validation errors:', errorData);
                handleFormErrors(errorData, dom); // Display specific field errors
            } else if (response.status === 401) {
                // Handle unauthorized access
                NotificationService.showNotification('Your session has expired. Please log in again.', 'error');
                // Consider redirecting to login page
                // window.location.href = '/login';
            } else {
                // Handle other server errors (5xx) or unexpected responses
                const errorText = await response.text(); // Get raw error text for debugging
                console.error('Server error:', response.status, errorText);
                NotificationService.showNotification(`An unexpected error occurred (${response.status}). Please try again.`, 'error');
            }
        } catch (err) {
            // Handle network errors (e.g., no internet connection)
            console.error('Fetch error:', err);
            NotificationService.showNotification('Network error, please check your internet connection and try again.', 'error');
        } finally {
            // Always hide loading state, regardless of success or failure
            hideLoadingState(dom.submitButton, dom.submitButtonText, dom.loadingSpinner, timeOffRequestId ? 'Update Request' : 'Submit Request');
        }
    }

    /**
     * Resets the form to its initial state, clearing all inputs and errors.
     * @param {object} dom - Object containing references to DOM elements.
     * @param {string|null} timeOffRequestId - ID if in update mode, null if creating.
     */
    function handleClearForm(dom, timeOffRequestId) {
        dom.form.reset(); // Resets all form inputs
        clearFieldErrors(); // Clears error messages
        
        // Manually reset file input and display
        dom.medicalDocumentInput.value = '';
        dom.medicalFileNameDisplay.textContent = 'No file chosen';
        dom.medicalDocumentUploadLabel.classList.remove('custom-file-upload-selected');
        
        // Hide medical document field and remove required attribute
        dom.medicalDocumentField.classList.add('hidden');
        dom.medicalDocumentRequiredStar.classList.add('hidden');
        dom.medicalDocumentInput.required = false;

        dom.leaveTypeSelect.value = ''; // Reset leave type select

        // Reset date/time inputs' value to empty strings for full clear
        dom.startDateInput.value = '';
        dom.endDateInput.value = '';

        NotificationService.showNotification('Form cleared!', 'info'); // Changed from warning to info
        updateUIMode(timeOffRequestId, dom); // Re-apply UI mode if needed (e.g., clear button text)
    }

    /**
     * Toggles the visibility and 'required' attribute of the medical document field
     * based on the selected leave type.
     * @param {object} dom - Object containing references to DOM elements.
     */
    function toggleMedicalDocumentField(dom) {
        const selectedOption = dom.leaveTypeSelect.options[dom.leaveTypeSelect.selectedIndex];
        const selectedLeaveTypeText = selectedOption ? selectedOption.textContent.trim() : null;

        // UPDATED: Configure these based on the exact `display_name` returned by your backend API
        // for 'FVSL' and 'VSL' leave types. This assumes their `leave_type.name` attribute
        // in Django is exactly "FVSL" and "VSL" respectively.
        const mandatoryDocumentLeaveTypes = ['FVSL', 'VSL'];
        // Add 'Sick Leave' here if it also requires a document:
        // const mandatoryDocumentLeaveTypes = ['Sick Leave', 'FVSL', 'VSL'];

        const optionalDocumentLeaveTypes = []; // Example: leave types where document is optional

        let isMandatory = false;
        let showDocumentField = false;

        if (mandatoryDocumentLeaveTypes.includes(selectedLeaveTypeText)) {
            isMandatory = true;
            showDocumentField = true;
        } else if (optionalDocumentLeaveTypes.includes(selectedLeaveTypeText)) {
            showDocumentField = true;
        }

        if (showDocumentField) {
            dom.medicalDocumentField.classList.remove('hidden');
            // Use Tailwind's !block to override default hidden
            dom.medicalDocumentField.classList.add('!block');
            if (isMandatory) {
                dom.medicalDocumentInput.setAttribute('required', 'required');
                dom.medicalDocumentRequiredStar.classList.remove('hidden');
                dom.medicalDocumentRequiredStar.classList.add('!inline');
            } else {
                dom.medicalDocumentInput.removeAttribute('required');
                dom.medicalDocumentRequiredStar.classList.add('hidden');
                dom.medicalDocumentRequiredStar.classList.remove('!inline');
            }
        } else {
            dom.medicalDocumentField.classList.add('hidden');
            dom.medicalDocumentField.classList.remove('!block');
            dom.medicalDocumentInput.removeAttribute('required');
            dom.medicalDocumentRequiredStar.classList.add('hidden');
            dom.medicalDocumentRequiredStar.classList.remove('!inline');
            dom.medicalDocumentInput.value = ''; // Clear file input when field is hidden
            dom.medicalFileNameDisplay.textContent = 'No file chosen';
            dom.medicalDocumentUploadLabel.classList.remove('custom-file-upload-selected');
        }
        clearFieldErrors(); // Clear errors whenever the field visibility changes
    }

    return {
        getDomElements,
        clearFieldErrors,
        showLoadingState,
        hideLoadingState,
        populateFormForUpdate,
        updateUIMode,
        validateMedicalDocument,
        handleFormErrors,
        handleFormSubmission,
        handleClearForm,
        toggleMedicalDocumentField
    };
})();
