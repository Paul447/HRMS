import { ApiService } from './modules/timeoffrequest/apiService.js';
import { NotificationService } from './modules/timeoffrequest/notificationService.js';
import { ConfirmationModal } from './modules/timeoffrequest/confirmationModal.js';
import { DropdownHandler } from './modules/timeoffrequest/dropdownHandler.js';
import { FormHandler } from './modules/timeoffrequest/formHandler.js';
import { formatDateTimeForAPI } from './modules/timeoffrequest/utils.js';

const API_ENDPOINTS = {
    LEAVE_TYPES: '/api/leave-type-dropdown/',
    SUBMIT_REQUEST: '/api/timeoffrequests/'
};

let dom = {};
let timeOffRequestId = null;

document.addEventListener('DOMContentLoaded', async function() {
    dom = FormHandler.getDomElements();

    const urlParams = new URLSearchParams(window.location.search);
    timeOffRequestId = urlParams.get('id');

    dom.medicalDocumentInput.addEventListener('change', (event) => {
        if (event.target.files.length > 0) {
            const file = event.target.files[0];
            dom.medicalFileNameDisplay.textContent = file.name;
            dom.medicalDocumentUploadLabel.classList.add('custom-file-upload-selected');
        } else {
            dom.medicalFileNameDisplay.textContent = 'No file chosen';
            dom.medicalDocumentUploadLabel.classList.remove('custom-file-upload-selected');
        }
    });

    if (timeOffRequestId) {
        await DropdownHandler.fetchAndPopulateDropdown(API_ENDPOINTS.LEAVE_TYPES, dom.leaveTypeSelect, 'Select Leave Type', 'id', 'display_name');
        await FormHandler.populateFormForUpdate(timeOffRequestId, dom, FormHandler.showLoadingState, FormHandler.hideLoadingState, NotificationService.showNotification);
        FormHandler.updateUIMode(timeOffRequestId, dom);
    } else {
        await DropdownHandler.fetchAndPopulateDropdown(API_ENDPOINTS.LEAVE_TYPES, dom.leaveTypeSelect, 'Select Leave Type', 'id', 'display_name');
        FormHandler.toggleMedicalDocumentField(dom);
    }

    dom.form.addEventListener('submit', (event) => FormHandler.handleFormSubmission(event, dom, timeOffRequestId, API_ENDPOINTS));
    dom.clearFormButton.addEventListener('click', () => FormHandler.handleClearForm(dom, timeOffRequestId));
    dom.leaveTypeSelect.addEventListener('change', () => FormHandler.toggleMedicalDocumentField(dom));
});