import { ApiService } from './apiService.js';
import { NotificationService } from './notificationService.js';
import { ConfirmationModal } from './confirmationModal.js';
import { formatDateTimeForAPI } from './utils.js';

export const FormHandler = (function() {
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
            confirmationModal: document.getElementById('confirmationModal'),
            confirmSubmitButton: document.getElementById('confirmSubmitButton'),
            confirmCancelButton: document.getElementById('confirmCancelButton'),
            leaveTypeErrors: document.getElementById('leaveTypeErrors'),
            startDateErrors: document.getElementById('startDateErrors'),
            endDateErrors: document.getElementById('endDateErrors'),
            reasonErrors: document.getElementById('reasonErrors'),
            documentProofErrors: document.getElementById('documentProofErrors'),
            pageTitle: document.getElementById('page_title'),
            formHeading: document.getElementById('form_heading'),
            formParagraph: document.getElementById('form_paragraph')
        };
    }

    function clearFieldErrors() {
        document.querySelectorAll('.field-errors').forEach(errorDiv => {
            errorDiv.textContent = '';
        });
    }

    function showLoadingState(submitButton, submitButtonText, loadingSpinner, buttonText = 'Processing...') {
        submitButton.disabled = true;
        submitButton.classList.add('opacity-50', 'cursor-not-allowed');
        submitButtonText.classList.add('hidden');
        loadingSpinner.classList.remove('hidden');
    }

    function hideLoadingState(submitButton, submitButtonText, loadingSpinner, originalText = 'Submit Request') {
        submitButton.disabled = false;
        submitButton.classList.remove('opacity-50', 'cursor-not-allowed');
        submitButtonText.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2 inline-block align-text-bottom" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" /></svg>${originalText}`;
        submitButtonText.classList.remove('hidden');
        loadingSpinner.classList.add('hidden');
    }

    async function populateFormForUpdate(id, domElements, showLoadingStateFn, hideLoadingStateFn, showNotificationFn) {
        showLoadingStateFn(domElements.submitButton, domElements.submitButtonText, domElements.loadingSpinner, 'Loading Data...');
        
        try {
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const response = await ApiService.smartFetch(`/api/timeoffrequests/${id}/`, {
                method: 'GET',
                credentials: 'include',
                headers: { 'X-CSRFToken': csrftoken, 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    showNotificationFn('Your session has expired. Please log in again.', 'error');
                    return;
                }
                const errorData = await response.json();
                throw new Error(`Failed to load Time Off request for update. Status: ${response.status}. Error: ${JSON.stringify(errorData)}`);
            }

            const timeOffRequest = await response.json();
            
            await DropdownHandler.fetchAndPopulateDropdown(API_ENDPOINTS.LEAVE_TYPES, domElements.leaveTypeSelect, 'Select Leave Type', 'id', 'display_name');

            domElements.leaveTypeSelect.value = timeOffRequest.requested_leave_type_details.id;
            domElements.startDateInput.value = timeOffRequest.start_date_time ? timeOffRequest.start_date_time.slice(0, 16) : '';
            domElements.endDateInput.value = timeOffRequest.end_date_time ? timeOffRequest.end_date_time.slice(0, 16) : '';
            domElements.reasonTextarea.value = timeOffRequest.employee_leave_reason || '';

            if (timeOffRequest.document_proof) {
                domElements.medicalFileNameDisplay.textContent = 'Existing file: ' + timeOffRequest.document_proof.split('/').pop();
                domElements.medicalDocumentUploadLabel.classList.add('custom-file-upload-selected');
            } else {
                domElements.medicalFileNameDisplay.textContent = 'No file chosen';
                domElements.medicalDocumentUploadLabel.classList.remove('custom-file-upload-selected');
            }
            
            const changeEvent = new Event('change');
            domElements.leaveTypeSelect.dispatchEvent(changeEvent);

            showNotificationFn('Form loaded for update.', 'success');
        } catch (error) {
            showNotificationFn('Failed to load request details. Please try again.', 'error');
            console.error('[FormHandler] Error populating form for update:', error);
        } finally {
            hideLoadingStateFn(domElements.submitButton, domElements.submitButtonText, domElements.loadingSpinner, 'Update Request');
        }
    }

    function updateUIMode(timeOffRequestId, domElements) {
        if (timeOffRequestId) {
            domElements.submitButtonText.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2 inline-block align-text-bottom" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" /></svg>Update Request`;
            if (domElements.pageTitle) domElements.pageTitle.textContent = 'Edit Time Off Request';
            if (domElements.formHeading) domElements.formHeading.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>Edit Your Time Off Request`;
            if (domElements.formParagraph) domElements.formParagraph.textContent = 'Modify the details of your time off request and submit the updates.';
            domElements.clearFormButton.textContent = 'Reset Form';
        } else {
            domElements.submitButtonText.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2 inline-block align-text-bottom" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" /></svg>Submit Request`;
            if (domElements.pageTitle) domElements.pageTitle.textContent = 'Submit New Time Off Request';
            if (domElements.formHeading) domElements.formHeading.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>Request Time Off`;
            if (domElements.formParagraph) domElements.formParagraph.textContent = 'Fill out the form below to submit a new time off request.';
            domElements.clearFormButton.textContent = 'Clear';
        }
    }

    function validateMedicalDocument(leaveTypeSelectElement, medicalDocumentInput, medicalDocumentFieldErrors) {
        const selectedOption = leaveTypeSelectElement.options[leaveTypeSelectElement.selectedIndex];
        const selectedLeaveTypeName = selectedOption ? selectedOption.textContent : null;
        const mandatoryDocumentLeaveTypes = ['FVSL', 'VSL'];

        if (mandatoryDocumentLeaveTypes.includes(selectedLeaveTypeName) && (!medicalDocumentInput || medicalDocumentInput.files.length === 0)) {
            NotificationService.showNotification('Document proof is required for this leave type (FVSL/VSL).', 'error');
            if (medicalDocumentFieldErrors) {
                medicalDocumentFieldErrors.textContent = 'This field is required.';
            }
            return false;
        }
        return true;
    }

    function handleFormErrors(errorData, domElements) {
        clearFieldErrors();

        let generalErrorMessages = [];

        if (errorData.detail) { generalErrorMessages.push(errorData.detail); }
        if (errorData.non_field_errors) { generalErrorMessages.push(errorData.non_field_errors.join(' ')); }

        for (const fieldName in errorData) {
            if (errorData.hasOwnProperty(fieldName)) {
                const errorMessages = Array.isArray(errorData[fieldName]) ? errorData[fieldName].join(', ') : errorData[fieldName];
                let targetErrorDiv = null;

                switch (fieldName) {
                    case 'requested_leave_type': targetErrorDiv = domElements.leaveTypeErrors; break;
                    case 'start_date_time': targetErrorDiv = domElements.startDateErrors; break;
                    case 'end_date_time': targetErrorDiv = domElements.endDateErrors; break;
                    case 'employee_leave_reason': targetErrorDiv = domElements.reasonErrors; break;
                    case 'document_proof': targetErrorDiv = domElements.documentProofErrors; break;
                    default:
                        if (fieldName !== 'detail' && fieldName !== 'non_field_errors') {
                            generalErrorMessages.push(`${fieldName}: ${errorMessages}`);
                        }
                        break;
                }

                if (targetErrorDiv) {
                    targetErrorDiv.textContent = errorMessages;
                }
            }
        }

        if (generalErrorMessages.length > 0) {
            NotificationService.showNotification(generalErrorMessages.join('\n'), 'error');
        } else {
            NotificationService.showNotification('Please correct the errors in the form.', 'error');
        }
    }

    async function handleFormSubmission(event, dom, timeOffRequestId, apiEndpoints) {
        event.preventDefault();

        if (!validateMedicalDocument(dom.leaveTypeSelect, dom.medicalDocumentInput, dom.documentProofErrors)) {
            return;
        }

        const confirmed = await ConfirmationModal.askForConfirmation(dom.confirmationModal, dom.confirmSubmitButton, dom.confirmCancelButton);
        if (!confirmed) {
            NotificationService.showNotification('Time off request submission cancelled.', 'warning');
            return;
        }

        clearFieldErrors();
        showLoadingState(dom.submitButton, dom.submitButtonText, dom.loadingSpinner, timeOffRequestId ? 'Updating...' : 'Submitting...');

        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const formData = new FormData();
        
        formData.append('requested_leave_type', dom.leaveTypeSelect.value);
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

        if (dom.medicalDocumentInput.files.length > 0) {
            formData.append('document_proof', dom.medicalDocumentInput.files[0]);
        }

        let method = 'POST';
        let url = apiEndpoints.SUBMIT_REQUEST;
        let successMessage = 'Your time off request was successfully submitted!';

        if (timeOffRequestId) {
            method = 'PUT';
            url = `${apiEndpoints.SUBMIT_REQUEST}${timeOffRequestId}/`;
            successMessage = 'Your time off request was successfully updated!';
            NotificationService.showNotification('Attempting to update request...', 'warning');
        } else {
            NotificationService.showNotification('Attempting to submit new request...', 'warning');
        }

        try {
            const response = await ApiService.smartFetch(url, {
                method: method,
                headers: { 'X-CSRFToken': csrftoken },
                credentials: 'include',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                console.log('Request successful:', result);
                NotificationService.showNotification(successMessage, 'success');
                dom.form.reset();
                dom.medicalFileNameDisplay.textContent = 'No file chosen';
                dom.medicalDocumentUploadLabel.classList.remove('custom-file-upload-selected');
                dom.medicalDocumentField.classList.add('hidden');
                dom.medicalDocumentRequiredStar.classList.add('hidden');
                dom.medicalDocumentInput.required = false;
                dom.leaveTypeSelect.value = '';
            } else if (response.status === 400) {
                const errorData = await response.json();
                console.error('Validation errors:', errorData);
                handleFormErrors(errorData, dom);
            } else if (response.status === 401) {
                NotificationService.showNotification('Your session has expired. Please log in again.', 'error');
            } else {
                const errorText = await response.text();
                console.error('Server error:', response.status, errorText);
                NotificationService.showNotification(`An unexpected error occurred (${response.status}). Please try again.`, 'error');
            }
        } catch (err) {
            console.error('Fetch error:', err);
            NotificationService.showNotification('Network error, please check your internet connection and try again.', 'error');
        } finally {
            hideLoadingState(dom.submitButton, dom.submitButtonText, dom.loadingSpinner, timeOffRequestId ? 'Update Request' : 'Submit Request');
        }
    }

    function handleClearForm(dom, timeOffRequestId) {
        dom.form.reset();
        clearFieldErrors();
        dom.medicalDocumentInput.value = '';
        dom.medicalFileNameDisplay.textContent = 'No file chosen';
        dom.medicalDocumentUploadLabel.classList.remove('custom-file-upload-selected');
        
        dom.medicalDocumentField.classList.add('hidden');
        dom.medicalDocumentRequiredStar.classList.add('hidden');
        dom.medicalDocumentInput.required = false;

        dom.leaveTypeSelect.value = '';

        NotificationService.showNotification('Form cleared!', 'warning');
        updateUIMode(timeOffRequestId, dom);
    }

    function toggleMedicalDocumentField(dom) {
        const selectedOption = dom.leaveTypeSelect.options[dom.leaveTypeSelect.selectedIndex];
        const selectedLeaveTypeName = selectedOption ? selectedOption.textContent : null;

        const mandatoryDocumentLeaveTypes = ['FVSL', 'VSL'];
        const optionalDocumentLeaveTypes = [];

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
            dom.medicalFileNameDisplay.textContent = 'No file chosen';
            dom.medicalDocumentUploadLabel.classList.remove('custom-file-upload-selected');
        }
        clearFieldErrors();
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