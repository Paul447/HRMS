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


document.addEventListener('DOMContentLoaded', async function() {
    const {
        departmentSelect,
        payTypeSelect,
        form,
        submitButton,
        submitButtonText,
        loadingSpinner,
        clearFormButton,
        confirmationModal,
        confirmSubmitButton,
        confirmCancelButton,
        pageTitle,
        formHeading,
        formParagraph
    } = getDomElements();

    let ptoRequestId = null; // Variable to store PTO request ID if in update mode

    // --- Confirmation Modal Event Listeners ---
    // Note: The click handlers inside askForConfirmation are already using { once: true },
    // so explicit listeners here might be redundant if askForConfirmation is always used.
    // However, it's good practice to ensure modal can be closed by its buttons.
    // The hideConfirmationModal function needs the modal element itself.
    confirmSubmitButton.addEventListener('click', () => {
        // No direct action here, askForConfirmation's promise resolution handles this.
        // But call hideModal directly if askForConfirmation isn't managing it.
        hideConfirmationModal(confirmationModal);
    });

    confirmCancelButton.addEventListener('click', () => {
        // No direct action here, askForConfirmation's promise resolution handles this.
        hideConfirmationModal(confirmationModal);
    });

    // Close modal if clicking outside
    confirmationModal.addEventListener('click', function(event) {
        if (event.target === confirmationModal) {
            hideConfirmationModal(confirmationModal);
            // Optionally, if askForConfirmation promise is active, resolve it to false here too
            // This is more complex and usually handled by the explicit cancel button.
            // For simplicity, clicking outside just closes the modal visually.
        }
    });

    // --- Initial Data Loading & Mode Check ---
    const urlParams = new URLSearchParams(window.location.search);
    ptoRequestId = urlParams.get('id');

    if (ptoRequestId) {
        
        // In update mode, populate dropdowns and then form data
        await fetchAndPopulateDropdown('/api/department/', departmentSelect, 'Select your Department', 'id', 'name');
        await fetchAndPopulateDropdown('/api/departmentpaytype/', payTypeSelect, 'Select Pay Type', 'id', 'name');
        await populateFormForUpdate(ptoRequestId, form, pageTitle, formHeading, formParagraph, submitButtonText, clearFormButton, showLoadingState, hideLoadingState, showNotification);
        updateUIMode(ptoRequestId, pageTitle, formHeading, formParagraph, submitButtonText, clearFormButton);
    } else {
        
        // In create mode, just populate dropdowns
        fetchAndPopulateDropdown('/api/department/', departmentSelect, 'Select your Department', 'id', 'name');
        fetchAndPopulateDropdown('/api/departmentpaytype/', payTypeSelect, 'Select Pay Type', 'id', 'name');
    }

    // --- Form Submission Handling ---
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        

        // Ask for confirmation using the reusable modal
        const confirmed = await askForConfirmation(confirmationModal, confirmSubmitButton, confirmCancelButton);
        if (!confirmed) {
            showNotification('PTO request submission cancelled.', 'warning');
            
            return;
        }
        

        clearFieldErrors();
        showLoadingState(submitButton, submitButtonText, loadingSpinner, ptoRequestId ? 'Updating...' : 'Submitting...');

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
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                credentials: 'include',
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                const data = await response.json();
                
                // Pass the success message via URL query parameter for details page
                window.location.href = `/auth/ptorequest/details/?message=${encodeURIComponent(successMessage)}&type=success`;
            } else if (response.status === 400) {
                const errorData = await response.json();
                

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
                
                window.location.href = '/auth/login/';
            } else {
                const errorText = await response.text();
                
                showNotification(`An unexpected error occurred (${response.status}). Please try again.`, 'error');
            }
        } catch (err) {
            
            showNotification('Network error, please check your internet connection and try again.', 'error');
        } finally {
            hideLoadingState(submitButton, submitButtonText, loadingSpinner, ptoRequestId ? 'Update Request' : 'Submit Request');
        }
    });

    // --- Clear/Reset Form Button Handling ---
    clearFormButton.addEventListener('click', function() {
        form.reset();
        clearFieldErrors();
        if (ptoRequestId) {
            showNotification('Form cleared. To revert, refresh the page.', 'warning');
        } else {
            showNotification('Form cleared!', 'warning');
        }
        
    });
});