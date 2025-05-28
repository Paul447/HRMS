// static/ptorequest/js/pto_list.js

import { fetchPTORequests, deletePTORequest, fetchApprovedAndRejectedRequests } from './modules/apiService.js';
import { showToast, toggleLoading, toggleNoRequestsMessage, toggleErrorMessage, checkURLForMessages } from './modules/uiHelpers.js';
import { renderRequests } from './modules/tableRenderer.js';
import { sortRequests, updateSortIndicators } from './modules/sorter.js';

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements for Pending Requests
    const ptoRequestsList = document.getElementById('ptoRequestsList');
    const noRequestsMessage = document.getElementById('noRequestsMessage');
    const errorMessage = document.getElementById('errorMessage');
    const loadingRow = document.getElementById('loadingRow');
    const tableHeaders = document.querySelectorAll('th[data-sort]'); // Only for pending table

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

    // Modal Elements
    const confirmationModal = document.getElementById('confirmationModal');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');

    // State Variables
    let allPendingRequests = [];
    let currentSortColumn = null;
    let currentSortDirection = 'asc';
    let requestIdToDelete = null;

    /**
     * Orchestrates fetching, sorting, and rendering *pending* requests.
     */
    async function loadAndRenderPendingRequests() {
        toggleLoading(loadingRow, true);
        toggleNoRequestsMessage(noRequestsMessage, false);
        toggleErrorMessage(errorMessage, false);
        ptoRequestsList.innerHTML = ''; // Clear existing content

        try {
            allPendingRequests = await fetchPTORequests();
            applySortingAndRenderPending();
        } catch (error) {
            console.error('Error in loadAndRenderPendingRequests:', error);
            toggleErrorMessage(errorMessage, true);
            showToast('Failed to load your pending time off requests. Please try again.', 'error');
        } finally {
            toggleLoading(loadingRow, false);
        }
    }

    /**
     * Applies the current sorting to the pending requests and then renders them.
     */
    function applySortingAndRenderPending() {
        const sortedRequests = sortRequests(allPendingRequests, currentSortColumn, currentSortDirection);
        // Pass true for `allowActions` for pending requests
        renderRequests(
            sortedRequests,
            ptoRequestsList,
            noRequestsMessage,
            true, // allowActions = true
            handleUpdateClick,
            handleDeleteClick
        );
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
            const data = await fetchApprovedAndRejectedRequests();
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
            applySortingAndRenderPending(); // Re-render pending table with updated data
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

    // --- Event Listeners ---

    // Table header sort listeners (only for pending requests table)
    tableHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const sortColumn = this.dataset.sort;
            if (currentSortColumn === sortColumn) {
                currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                currentSortColumn = sortColumn;
                currentSortDirection = 'asc'; // Default to ascending when changing column
            }
            updateSortIndicators(tableHeaders, currentSortColumn, currentSortDirection);
            applySortingAndRenderPending();
        });
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

    // Initial load and URL message check
    loadAndRenderPendingRequests();
    loadAndRenderApprovedRejectedRequests(); // Call new function to load approved/rejected data
    checkURLForMessages();
});