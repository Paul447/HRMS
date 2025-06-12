// static/ptorequest/js/pto_list.js

import { fetchPTORequests, deletePTORequest, fetchApprovedAndRejectedRequests } from './modules/ptoview/apiService.js';
import { showToast, toggleLoading, toggleNoRequestsMessage, toggleErrorMessage, checkURLForMessages } from './modules/ptoview/uiHelpers.js';
import { renderRequests } from './modules/ptoview/tableRenderer.js';

document.addEventListener('DOMContentLoaded', function() {
    // --- DOM Elements ---
    const tabButtons = document.querySelectorAll('.tab-button');
    const ptoRequestsTableBody = document.getElementById('ptoRequestsTableBody'); // Unified tbody
    const loadingRow = document.getElementById('loadingRow'); // Unified loading row
    const noRequestsMessage = document.getElementById('noRequestsMessage'); // Unified no data message div
    const noRequestsText = document.getElementById('noRequestsText'); // Span for specific 'no requests' text
    const errorMessage = document.getElementById('errorMessage'); // Unified error message div

    const pendingCountSpan = document.getElementById('pendingCount');
    const approvedCountSpan = document.getElementById('approvedCount');
    const rejectedCountSpan = document.getElementById('rejectedCount');

    // Modal elements
    const confirmationModal = document.getElementById('confirmationModal');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    const payPeriodDetailsElement = document.getElementById('payPeriodDetails'); // Correctly identified

    // Actions column header (to show/hide)
    const actionsHeader = document.getElementById('actionsHeader');

    // --- State Variables ---
    let allPtoRequests = { // Centralized storage for all requests
        pending: [],
        approved: [],
        rejected: []
    };
    let activeTabStatus = localStorage.getItem('activePtoTab') || 'pending'; // Default or last active tab
    let requestIdToDelete = null;

    // --- Functions ---

    /**
     * Updates the tab styling and count badges.
     */
    function updateTabDisplay() {
        tabButtons.forEach(button => {
            if (button.dataset.status === activeTabStatus) {
                button.classList.add('active'); // Apply active class
                button.setAttribute('aria-selected', 'true');
            } else {
                button.classList.remove('active'); // Remove active class
                button.setAttribute('aria-selected', 'false');
            }
        });
        // Update the 'No requests' message to be specific to the current tab
        noRequestsText.textContent = `No ${activeTabStatus} requests.`;

        // Toggle visibility of the "Actions" column header
        if (activeTabStatus === 'pending') {
            actionsHeader.classList.remove('hidden');
        } else {
            actionsHeader.classList.add('hidden');
        }
    }

    /**
     * Updates the counts on each status tab.
     */
    function updateCounts() {
        pendingCountSpan.textContent = allPtoRequests.pending.length;
        approvedCountSpan.textContent = allPtoRequests.approved.length;
        rejectedCountSpan.textContent = allPtoRequests.rejected.length;
    }

    /**
     * Updates the pay period details display.
     * Assumes pay period details are available on the first pending request,
     * or any relevant request. Adjust logic if details come from a different source.
     */
    function updatePayPeriodDisplay() {
        if (payPeriodDetailsElement) {
            // Find a request with pay period details (e.g., the most recent, or any pending)
            // For simplicity, let's try to get it from the first pending request.
            const requestWithPayPeriod = allPtoRequests.pending.length > 0 ? allPtoRequests.pending[0] : null;

            if (requestWithPayPeriod && requestWithPayPeriod.pay_period_start_date && requestWithPayPeriod.pay_period_end_date) {
                const startDate = new Date(requestWithPayPeriod.pay_period_start_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                const endDate = new Date(requestWithPayPeriod.pay_period_end_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                payPeriodDetailsElement.textContent = `Current Pay Period: ${startDate} - ${endDate}`;
                payPeriodDetailsElement.classList.remove('hidden'); // Ensure it's visible
            } else {
                // If no pay period data, hide the element or show a default message
                payPeriodDetailsElement.textContent = ''; // Clear content
                payPeriodDetailsElement.classList.add('hidden'); // Hide the element
            }
        }
    }

    /**
     * Renders requests based on the active tab status.
     */
    function renderActiveTabRequests() {
        // Hide all messages initially
        toggleNoRequestsMessage(noRequestsMessage, false);
        toggleErrorMessage(errorMessage, false);
        toggleLoading(loadingRow, true); // Keep loading state until data is rendered

        const requestsToRender = allPtoRequests[activeTabStatus];
        const allowActions = activeTabStatus === 'pending';

        renderRequests(
            requestsToRender,
            ptoRequestsTableBody,
            allowActions,
            handleUpdateClick,
            handleDeleteClick
        );

        // After rendering, check if there are no requests for the current tab
        if (!requestsToRender || requestsToRender.length === 0) {
            toggleNoRequestsMessage(noRequestsMessage, true);
        }

        toggleLoading(loadingRow, false); // Hide loading after rendering
    }

    /**
     * Fetches all PTO requests (pending, approved, rejected) and updates the UI.
     */
    async function loadAllPtoRequests() {
        toggleLoading(loadingRow, true);
        toggleNoRequestsMessage(noRequestsMessage, false);
        toggleErrorMessage(errorMessage, false);

        try {
            // Fetch pending requests
            const pending = await fetchPTORequests();
            allPtoRequests.pending = pending;

            // Fetch approved and rejected requests
            const otherRequests = await fetchApprovedAndRejectedRequests();
            allPtoRequests.approved = otherRequests.approved_requests || [];
            allPtoRequests.rejected = otherRequests.rejected_requests || [];

            updateCounts(); // Update count badges on tabs
            updatePayPeriodDisplay(); // Update the pay period details here
            renderActiveTabRequests(); // Render requests for the currently active tab

        } catch (error) {
            console.error("Error loading PTO requests:", error);
            showToast('Failed to load time off requests. Please try again.', 'error');
            toggleErrorMessage(errorMessage, true);
        } finally {
            toggleLoading(loadingRow, false);
        }
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
        confirmationModal.classList.add('flex'); // Add flex to center modal
    }

    /**
     * Handles the confirmation of deletion.
     */
    async function confirmDeletion() {
        if (!requestIdToDelete) return;

        try {
            await deletePTORequest(requestIdToDelete);
            // Remove the deleted request from the pending list
            allPtoRequests.pending = allPtoRequests.pending.filter(req => req.id !== parseInt(requestIdToDelete));
            showToast('Time off request deleted successfully!', 'success');

            updateCounts(); // Update count badges
            updatePayPeriodDisplay(); // Re-evaluate pay period display
            renderActiveTabRequests(); // Re-render the pending table (as that's where delete happens)

        } catch (error) {
            console.error('Error deleting PTO request:', error);
            showToast(error.message || 'Failed to delete time off request. Please try again.', 'error');
        } finally {
            requestIdToDelete = null; // Clear the stored ID
            closeConfirmationModal(); // Hide modal
        }
    }

    /**
     * Cancels the deletion process.
     */
    function closeConfirmationModal() {
        requestIdToDelete = null;
        confirmationModal.classList.add('hidden');
        confirmationModal.classList.remove('flex'); // Remove flex when hidden
    }

    // --- Event Listeners ---

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const newStatus = button.dataset.status;
            if (activeTabStatus !== newStatus) {
                activeTabStatus = newStatus;
                localStorage.setItem('activePtoTab', activeTabStatus); // Save active tab
                updateTabDisplay(); // Update button styling and actions header
                renderActiveTabRequests(); // Re-render table with new status
            }
        });
    });

    confirmDeleteBtn.addEventListener('click', confirmDeletion);
    cancelDeleteBtn.addEventListener('click', closeConfirmationModal);

    // Close modal if clicking outside
    confirmationModal.addEventListener('click', function(event) {
        if (event.target === confirmationModal) {
            closeConfirmationModal();
        }
    });

    // --- Initial Load ---
    updateTabDisplay(); // Set initial tab styling based on localStorage
    loadAllPtoRequests(); // Fetch all data and render based on active tab
    checkURLForMessages(); // Check for URL messages (e.g., after a successful form submission)
});