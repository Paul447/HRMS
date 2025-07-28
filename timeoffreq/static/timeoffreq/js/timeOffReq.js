/**
 * timeOffReq.js
 *
 * This is the main entry point for the Time Off Request frontend application.
 * It initializes DOM elements, sets up event listeners, and coordinates
 * interactions between various modules (API, Notifications, Confirmation, Dropdowns, Form Handling).
 */


import { NotificationService } from './modules/timeoffrequest/notificationService.js'; // Ensure this path is correct
// ConfirmationModal.js now exports askForConfirmation directly, not an object
// import { ConfirmationModal } from './confirmationModal.js';
import { DropdownHandler } from './modules/timeoffrequest/dropdownHandler.js'; // Ensure this path is correct
import { FormHandler } from './modules/timeoffrequest/formHandler.js'; // Ensure this path is correct


// Define API Endpoints used by various modules
const API_ENDPOINTS = {
    LEAVE_TYPES: '/api/v1/leave-type-dropdown/', // Endpoint for fetching leave types for dropdown
    SUBMIT_REQUEST: '/api/v1/timeoffrequests/' // Endpoint for submitting/updating time off requests
};

let dom = {}; // Global object to store DOM element references
let timeOffRequestId = null; // Stores the ID of the request if in update mode

document.addEventListener('DOMContentLoaded', async function() {
    // Get all necessary DOM elements and store them in the 'dom' object
    dom = FormHandler.getDomElements();

    // Check URL parameters for an 'id' to determine if it's an update operation
    const urlParams = new URLSearchParams(window.location.search);
    timeOffRequestId = urlParams.get('id');

    // Event listener for the medical document file input
    // This provides immediate visual feedback to the user about selected file.
    dom.medicalDocumentInput.addEventListener('change', (event) => {
        if (event.target.files.length > 0) {
            const file = event.target.files[0];
            dom.medicalFileNameDisplay.textContent = file.name;
            // Add a class for visual feedback (e.g., border color change)
            dom.medicalDocumentUploadLabel.classList.add('custom-file-upload-selected');
        } else {
            dom.medicalFileNameDisplay.textContent = 'No file chosen';
            dom.medicalDocumentUploadLabel.classList.remove('custom-file-upload-selected');
        }
    });

    // Initialize the form based on whether it's a new request or an update
    if (timeOffRequestId) {
        // In update mode:
        // 1. Fetch and populate the leave type dropdown
        await DropdownHandler.fetchAndPopulateDropdown(
            API_ENDPOINTS.LEAVE_TYPES,
            dom.leaveTypeSelect,
            'Select Leave Type',
            'id',
            'display_name'
        );
        // 2. Populate the form fields with existing data for the given ID
        await FormHandler.populateFormForUpdate(
            timeOffRequestId,
            dom,
            FormHandler.showLoadingState,
            FormHandler.hideLoadingState,
            NotificationService.showNotification
        );
        // 3. Update the UI mode (e.g., change button text to "Update")
        FormHandler.updateUIMode(timeOffRequestId, dom);
    } else {
        // In create new request mode:
        // 1. Fetch and populate the leave type dropdown
        await DropdownHandler.fetchAndPopulateDropdown(
            API_ENDPOINTS.LEAVE_TYPES,
            dom.leaveTypeSelect,
            'Select Leave Type',
            'id',
            'display_name'
        );
        // 2. Initialize the medical document field visibility based on default/selected leave type
        FormHandler.toggleMedicalDocumentField(dom);
    }

    // Set up main event listeners for the form
    // The FormHandler now takes care of validation, confirmation, and API submission.
    dom.form.addEventListener('submit', (event) => FormHandler.handleFormSubmission(event, dom, timeOffRequestId, API_ENDPOINTS));
    
    // Listener for the "Clear Form" button
    dom.clearFormButton.addEventListener('click', () => FormHandler.handleClearForm(dom, timeOffRequestId));
    
    // Listener for changes in the "Leave Type" select box
    // This dynamically shows/hides the medical document field.
    dom.leaveTypeSelect.addEventListener('change', () => FormHandler.toggleMedicalDocumentField(dom));

    // Initialize date/time inputs to current time when the page loads, but allow them to be cleared.
    const now = new Date();
    // Adjust to local time zone offset for correct display in datetime-local input
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    const currentTime = now.toISOString().slice(0, 16);

    // Set default value only if inputs are empty (e.g., not populated by update mode)
    if (!dom.startDateInput.value) {
        dom.startDateInput.value = currentTime;
    }
    if (!dom.endDateInput.value) {
        dom.endDateInput.value = currentTime;
    }

    // Set min date for date inputs to prevent selecting past dates (only date part)
    const today = new Date();
    today.setMinutes(today.getMinutes() - today.getTimezoneOffset());
    const todayString = today.toISOString().split('T')[0];

    // Set min attribute for both date-time inputs to prevent past dates
    dom.startDateInput.min = todayString + 'T00:00';
    dom.endDateInput.min = todayString + 'T00:00';

    // Update end date min based on start date selection
    dom.startDateInput.addEventListener('change', () => {
        if (dom.startDateInput.value) {
            // Ensure end date minimum is not before the selected start date
            dom.endDateInput.min = dom.startDateInput.value;
            // If end date is currently before the new start date, update it
            if (new Date(dom.endDateInput.value) < new Date(dom.startDateInput.value)) {
                dom.endDateInput.value = dom.startDateInput.value;
            }
        } else {
            // If start date is cleared, reset end date min to today
            dom.endDateInput.min = todayString + 'T00:00';
        }
    });
});
