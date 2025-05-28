// static/ptorequest/js/pto_list.js

import { fetchPTORequests, deletePTORequest } from './modules/apiService.js';
import { showToast, toggleLoading, toggleNoRequestsMessage, toggleErrorMessage, checkURLForMessages } from './modules/uiHelpers.js';
import { renderRequests } from './modules/tableRenderer.js';
import { sortRequests, updateSortIndicators } from './modules/sorter.js';

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const ptoRequestsList = document.getElementById('ptoRequestsList');
    const noRequestsMessage = document.getElementById('noRequestsMessage');
    const errorMessage = document.getElementById('errorMessage');
    const loadingRow = document.getElementById('loadingRow');
    const tableHeaders = document.querySelectorAll('th[data-sort]');
    const confirmationModal = document.getElementById('confirmationModal');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');

    // State Variables
    let allRequests = [];
    let currentSortColumn = null;
    let currentSortDirection = 'asc';
    let requestIdToDelete = null;

    /**
     * Orchestrates fetching, sorting, and rendering requests.
     */
    async function loadAndRenderRequests() {
        toggleLoading(loadingRow, true);
        toggleNoRequestsMessage(noRequestsMessage, false);
        toggleErrorMessage(errorMessage, false);
        ptoRequestsList.innerHTML = ''; // Clear existing content

        try {
            allRequests = await fetchPTORequests();
            applySortingAndRender();
        } catch (error) {
            console.error('Error in loadAndRenderRequests:', error);
            toggleErrorMessage(errorMessage, true);
            showToast('Failed to load your time off requests. Please try again.', 'error');
        } finally {
            toggleLoading(loadingRow, false);
        }
    }

    /**
     * Applies the current sorting to the requests and then renders them.
     */
    function applySortingAndRender() {
        const sortedRequests = sortRequests(allRequests, currentSortColumn, currentSortDirection);
        renderRequests(
            sortedRequests,
            ptoRequestsList,
            noRequestsMessage,
            handleUpdateClick, // Pass callback for update button
            handleDeleteClick // Pass callback for delete button
        );
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
            allRequests = allRequests.filter(req => req.id !== parseInt(requestIdToDelete));
            showToast('Time off request deleted successfully!', 'success');
            applySortingAndRender(); // Re-render table with updated data
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

    // Table header sort listeners
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
            applySortingAndRender();
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
    loadAndRenderRequests();
    checkURLForMessages();
});