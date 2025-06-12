// static/ptorequest/js/pto_list.js

import { fetchPTORequests, deletePTORequest, fetchApprovedAndRejectedRequests, fetchPAYPeriods } from './modules/ptoview/apiService.js';
import { showToast, toggleLoading, toggleNoRequestsMessage, toggleErrorMessage, checkURLForMessages } from './modules/ptoview/uiHelpers.js';
import { renderRequests } from './modules/ptoview/tableRenderer.js';

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements for Pending Requests
    const ptoRequestsList = document.getElementById('ptoRequestsList');
    const noRequestsMessage = document.getElementById('noRequestsMessage');
    const errorMessage = document.getElementById('errorMessage');
    const loadingRow = document.getElementById('loadingRow');

    // DOM Elements for Approved Requests
    const approvedRequestsList = document.getElementById('approvedRequestsList');
    const noApprovedRequestsMessage = document.getElementById('noApprovedRequestsMessage');
    const errorApprovedMessage = document.getElementById('errorApprovedMessage');
    const loadingApprovedRow = document.getElementById('loadingApprovedRow');

    // DOM Elements for Rejected Requests
    const rejectedRequestsList = document.getElementById('rejectedRequestsList');
    const noRejectedRequestsMessage = document.getElementById('noRejectedRequestsMessage');
    const errorRejectedMessage = document.getElementById('errorRejectedMessage');
    const loadingRejectedRow = document.getElementById('loadingRejectedRow');

    // Pay Period Selector
    const payPeriodSelector = document.getElementById('payPeriodSelector');

    // Modal Elements
    const confirmationModal = document.getElementById('confirmationModal');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');

    // State Variables
    let allPendingRequests = [];
    let requestIdToDelete = null;
    let currentSelectedPayPeriodId = null; // Stores the ID of the currently selected pay period

    /**
     * Orchestrates fetching and rendering *pending* requests.
     */
    async function loadAndRenderPendingRequests() {
        toggleLoading(loadingRow, true);
        toggleNoRequestsMessage(noRequestsMessage, false);
        toggleErrorMessage(errorMessage, false);
        ptoRequestsList.innerHTML = ''; // Clear existing content

        try {
            allPendingRequests = await fetchPTORequests(currentSelectedPayPeriodId);
            renderRequests(
                allPendingRequests,
                ptoRequestsList,
                noRequestsMessage,
                true, // allowActions = true
                handleUpdateClick,
                handleDeleteClick
            );
        } catch (error) {
            console.error('Error in loadAndRenderPendingRequests:', error);
            toggleErrorMessage(errorMessage, true);
            showToast('Failed to load your pending time off requests. Please try again.', 'error');
        } finally {
            toggleLoading(loadingRow, false);
        }
    }

    /**
     * Orchestrates fetching and rendering Pay Periods.
     * Sets the default selected pay period in the dropdown.
     */
    async function loadAndRenderPayPeriods() {
        payPeriodSelector.innerHTML = '<option value="">Loading Pay Periods...</option>'; // Reset loading state
        try {
            const payPeriods = await fetchPAYPeriods();
            const now = new Date(); // Current date for comparison

            if (payPeriods.length > 0) {
                // Sort pay periods by end_date in descending order (most recent first)
                payPeriods.sort((a, b) => new Date(b.end_date) - new Date(a.end_date));

                let optionsHtml = '<option value="">All Pay Periods</option>'; // Option to view "All Pay Periods"
                let defaultPayPeriodFound = false;

                payPeriods.forEach(period => {
                    const startDate = new Date(period.start_date);
                    const endDate = new Date(period.end_date);
                    const periodDisplay = `Pay Period: ${startDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })} - ${endDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
                    optionsHtml += `<option value="${period.id}">${periodDisplay}</option>`;

                    // Check if this is the 'current' pay period based on today's date
                    // Note: Backend uses timezone.now(), ensure consistency if strict comparison is needed
                    if (now >= startDate && now <= endDate) {
                        // Mark the ID of the current pay period
                        // This will be used as the default if no specific ID is selected
                        // and 'All Pay Periods' is not explicitly chosen.
                        if (currentSelectedPayPeriodId === null) { // Only set if not already set from URL/previous interaction
                            currentSelectedPayPeriodId = period.id;
                            defaultPayPeriodFound = true;
                        }
                    }
                });
                payPeriodSelector.innerHTML = optionsHtml;

                // Set the selected value in the dropdown
                if (currentSelectedPayPeriodId !== null) {
                    // If a specific pay period ID was previously selected (e.g., from URL or user interaction)
                    // or if a current pay period was found and set as default, select it.
                    payPeriodSelector.value = currentSelectedPayPeriodId;
                } else {
                    // If no specific pay period was selected and no current pay period found,
                    // default to "All Pay Periods"
                    payPeriodSelector.value = '';
                    currentSelectedPayPeriodId = null; // Explicitly null for "All"
                }

                // If `currentSelectedPayPeriodId` was set to a specific period because it's "current"
                // but the user's initial preference is "All", this logic ensures "All" remains.
                // This scenario can be tricky: if the backend *always* returns current for no filter,
                // then the UI needs to be smart about what it *sends* vs *shows*.
                // For simplicity, `currentSelectedPayPeriodId` now directly controls the filter.
                // When `payPeriodSelector.value` is '', `currentSelectedPayPeriodId` becomes null,
                // and the API calls will omit the pay_period_id, causing the backend to use its default (current pay period).
                // So, effectively, if the user selects "All Pay Periods", the backend's "current pay period" filter will apply.

            } else {
                payPeriodSelector.innerHTML = '<option value="">No Pay Periods Available</option>';
                payPeriodSelector.disabled = true; // Disable if no periods
                currentSelectedPayPeriodId = null;
            }
        } catch (error) {
            console.error('Error loading pay periods:', error);
            payPeriodSelector.innerHTML = '<option value="">Error loading pay periods</option>';
            payPeriodSelector.disabled = true; // Disable on error
            showToast('Failed to load pay periods. Please try again.', 'error');
            currentSelectedPayPeriodId = null; // Ensure no period is selected on error
        }
    }

    /**
     * Fetches and renders approved/rejected requests.
     */
    async function loadAndRenderApprovedRejectedRequests() {
        // Show loading spinners for both tables
        toggleLoading(loadingApprovedRow, true);
        toggleLoading(loadingRejectedRow, true);
        toggleNoRequestsMessage(noApprovedRequestsMessage, false);
        toggleNoRequestsMessage(noRejectedRequestsMessage, false);
        toggleErrorMessage(errorApprovedMessage, false);
        toggleErrorMessage(errorRejectedMessage, false);
        approvedRequestsList.innerHTML = '';
        rejectedRequestsList.innerHTML = '';

        try {
            const data = await fetchApprovedAndRejectedRequests(currentSelectedPayPeriodId);
            const approvedRequests = data.approved_requests || [];
            const rejectedRequests = data.rejected_requests || [];

            // Render approved requests (no actions)
            renderRequests(
                approvedRequests,
                approvedRequestsList,
                noApprovedRequestsMessage,
                false // allowActions = false for approved
            );

            // Render rejected requests (no actions)
            renderRequests(
                rejectedRequests,
                rejectedRequestsList,
                noRejectedRequestsMessage,
                false // allowActions = false for rejected
            );

        } catch (error) {
            console.error('Error in loadAndRenderApprovedRejectedRequests:', error);
            toggleErrorMessage(errorApprovedMessage, true);
            toggleErrorMessage(errorRejectedMessage, true);
            showToast('Failed to load approved/rejected time off requests. Please try again.', 'error');
        } finally {
            toggleLoading(loadingApprovedRow, false);
            toggleLoading(loadingRejectedRow, false);
        }
    }

    /**
     * Re-fetches and renders all request tables based on the current selected pay period.
     */
    function refreshAllRequests() {
        loadAndRenderPendingRequests();
        loadAndRenderApprovedRejectedRequests();
    }

    /**
     * Handles the click event for update buttons.
     * @param {string} id - The ID of the request to update.
     */
    function handleUpdateClick(id) {
        window.location.href = `/auth/ptorequest/?id=${id}`;
    }

    /**
     * Handles the click event for delete buttons, showing the confirmation modal.
     * @param {string} id - The ID of the request to delete.
     */
    function handleDeleteClick(id) {
        requestIdToDelete = id;
        confirmationModal.classList.remove('hidden');
    }

    /**
     * Handles the confirmation of deletion.
     */
    async function confirmDeletion() {
        if (!requestIdToDelete) return;

        try {
            await deletePTORequest(requestIdToDelete);
            allPendingRequests = allPendingRequests.filter(req => req.id !== parseInt(requestIdToDelete));
            showToast('Time off request deleted successfully!', 'success');
            // Re-render pending table with updated data (no sorting applied now)
            renderRequests(
                allPendingRequests,
                ptoRequestsList,
                noRequestsMessage,
                true, // allowActions = true
                handleUpdateClick,
                handleDeleteClick
            );
        } catch (error) {
            console.error('Error deleting PTO request:', error);
            showToast('Failed to delete time off request. Please try again.', 'error');
        } finally {
            requestIdToDelete = null; // Clear the stored ID
            confirmationModal.classList.add('hidden'); // Hide modal
        }
    }

    /**
     * Cancels the deletion process.
     */
    function cancelDeletion() {
        requestIdToDelete = null;
        confirmationModal.classList.add('hidden');
    }

    // Event listener for pay period selector change
    payPeriodSelector.addEventListener('change', function() {
        // Update currentSelectedPayPeriodId based on the dropdown selection
        // If "All Pay Periods" is selected, this.value will be an empty string,
        // which correctly translates to `null` for API calls to trigger backend default.
        currentSelectedPayPeriodId = this.value === '' ? null : this.value;
        refreshAllRequests();
    });

    // Confirmation Modal button listeners
    confirmDeleteBtn.addEventListener('click', confirmDeletion);
    cancelDeleteBtn.addEventListener('click', cancelDeletion);

    // Close modal if clicking outside
    confirmationModal.addEventListener('click', function(event) {
        if (event.target === confirmationModal) {
            cancelDeletion();
        }
    });

    // Initial load sequence
    loadAndRenderPayPeriods().then(() => {
        // After pay periods are loaded and the initial default selection is made,
        // then load requests using the determined `currentSelectedPayPeriodId`.
        refreshAllRequests();
        checkURLForMessages(); // Check for URL messages (e.g., from a redirect after a successful request)
    });
});