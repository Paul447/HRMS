document.addEventListener('DOMContentLoaded', () => {
        // --- Constants and DOM Elements ---
        const ptoRequestsList = document.getElementById('ptoRequestsList');
        // Filter inputs are removed from the HTML and thus from DOM elements
        const prevPageButton = document.getElementById('prevPage');
        const nextPageButton = document.getElementById('nextPage');
        const paginationInfo = document.getElementById('paginationInfo');
        const confirmationModal = document.getElementById('confirmationModal');
        const modalIcon = document.getElementById('modalIcon');
        const modalTitle = document.getElementById('modalTitle');
        const modalMessage = document.getElementById('modalMessage');
        const rejectionReasonGroup = document.getElementById('rejectionReasonGroup');
        const rejectionReasonInput = document.getElementById('rejectionReason');
        const confirmActionBtn = document.getElementById('confirmActionBtn');
        const cancelActionBtn = document.getElementById('cancelActionBtn');
        const toastContainer = document.getElementById('toast-container');

        // Base API endpoint for fetching requests
        const API_BASE_ENDPOINT = '/api/manager-timeoff-approval/';
        const ITEMS_PER_PAGE = 10; // Assuming the backend pagination uses 10 items per page

        let currentPage = 1;
        let selectedRequestId = null;
        let currentActionType = null; // 'approve' or 'reject'

        // --- Utility Functions ---

        /**
         * Retrieves the CSRF token from cookies.
         * @param {string} name - The name of the cookie (e.g., 'csrftoken').
         * @returns {string|null} The cookie value or null if not found.
         */
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        /**
         * Displays a temporary toast notification.
         * @param {string} message - The message to display.
         * @param {'success'|'error'|'info'} type - The type of toast (determines color).
         */
        function showToast(message, type = 'info') {
            const toast = document.createElement('div');
            let bgColor, textColor;

            switch (type) {
                case 'success':
                    bgColor = 'bg-green-100';
                    textColor = 'text-green-800';
                    break;
                case 'error':
                    bgColor = 'bg-red-100';
                    textColor = 'text-red-800';
                    break;
                case 'info':
                default:
                    bgColor = 'bg-blue-100';
                    textColor = 'text-blue-800';
                    break;
            }

            toast.className = `px-5 py-3 rounded-lg shadow-lg ${bgColor} ${textColor} text-sm font-medium animate-slide-in`;
            toast.textContent = message;
            toastContainer.appendChild(toast);

            setTimeout(() => {
                toast.classList.add('animate-fade-out'); // Add fade out class if needed
                toast.remove();
            }, 3500); // Toast disappears after 3.5 seconds
        }

        // --- Data Fetching Logic ---

        /**
         * Fetches time off requests from the API based on current page.
         * Filters are no longer applicable.
         * @param {number} page - The current page number.
         */
        async function fetchData(page = 1) {
            // Show loading state
            ptoRequestsList.innerHTML = '<tr><td colspan="10" class="py-5 px-4 text-center text-gray-500">Loading requests...</td></tr>';
            
            let url = `${API_BASE_ENDPOINT}?page=${page}`;

            try {
                const response = await fetch(url);
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                displayData(data.results, data.count, page, data.previous, data.next);
            } catch (error) {
                console.error('Error fetching data:', error);
                showToast(`Error loading data: ${error.message}`, 'error');
                ptoRequestsList.innerHTML = '<tr><td colspan="10" class="py-5 px-4 text-center text-red-500">Failed to load requests. Please try again.</td></tr>';
            }
        }

        // --- DOM Manipulation / Rendering ---

        /**
         * Generates HTML for the document cell (view/download icons).
         * Uses 'document_proof' from the new data structure.
         * @param {object} request - The time off request object.
         * @returns {string} HTML string for the document cell.
         */
        function createDocumentCellHtml(request) {
            if (!request.document_proof) {
                return '<span class="text-gray-400 text-center block">- N/A -</span>';
            }
            const docUrl = request.document_proof;
            return `
                <div class="flex items-center justify-center space-x-2">
                    <a href="${docUrl}" target="_blank" class="text-blue-600 hover:text-blue-800 transition-colors duration-200" title="View Document">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                    </a>
                    <a href="${docUrl}" download class="text-gray-600 hover:text-gray-800 transition-colors duration-200" title="Download Document">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                    </a>
                </div>
            `;
        }

        /**
         * Generates a status badge HTML based on the request status.
         * @param {string} status - The status of the request ('pending', 'approved', 'rejected').
         * @returns {string} HTML string for the status badge.
         */
        function getStatusBadge(status) {
            let colorClass = '';
            let text = '';
            switch (status) {
                case 'pending':
                    colorClass = 'bg-yellow-100 text-yellow-800';
                    text = 'Pending';
                    break;
                case 'approved':
                    colorClass = 'bg-green-100';
                    text = 'Approved';
                    break;
                case 'rejected':
                    colorClass = 'bg-red-100';
                    text = 'Rejected';
                    break;
                default:
                    colorClass = 'bg-gray-100';
                    text = 'Unknown';
            }
            return `<span class="px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}">${text}</span>`;
        }

        /**
         * Displays the fetched time off requests in the table.
         * Adjusted to match the new data structure.
         * @param {Array<object>} requests - Array of request objects.
         * @param {number} totalCount - Total number of requests (for pagination info).
         * @param {number} page - Current page number.
         * @param {string|null} prevUrl - URL for previous page.
         * @param {string|null} nextUrl - URL for next page.
         */
        function displayData(requests, totalCount, page, prevUrl, nextUrl) {
            ptoRequestsList.innerHTML = ''; // Clear previous data
            
            if (requests.length === 0) {
                ptoRequestsList.innerHTML = '<tr><td colspan="10" class="py-5 px-4 text-center text-gray-500">No requests found.</td></tr>';
            } else {
                requests.forEach((request, index) => {
                    const serialNumber = (page - 1) * ITEMS_PER_PAGE + index + 1;
                    const row = document.createElement('tr');
                    row.dataset.requestId = request.id;

                    const documentCellHtml = createDocumentCellHtml(request);
                    const statusBadgeHtml = getStatusBadge(request.status);
                    const isPending = request.status === 'pending';
                    const buttonClasses = `text-xs font-semibold py-2 px-3 rounded-lg transition-colors duration-200 shadow-sm`;

                    row.innerHTML = `
                        <td class="py-3 px-4">${serialNumber}</td>
                        <td class="py-3 px-4">${request.employee_full_name}</td>
                        <td class="py-3 px-4">${request.requested_leave_type_details.display_name}</td>
                        <td class="py-3 px-4">${(new Date(request.start_date_time)).toLocaleDateString()} ${new Date(request.start_date_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</td>
                        <td class="py-3 px-4">${(new Date(request.end_date_time)).toLocaleDateString()} ${new Date(request.end_date_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</td>
                        <td class="py-3 px-4">${request.time_off_duration}</td>
                        <td class="py-3 px-4">
                            <div class="h-12 overflow-y-auto border border-gray-200 rounded p-2 text-sm bg-gray-50">
                                ${request.employee_leave_reason || '<span class="text-gray-400">No reason provided</span>'}
                            </div>
                        </td>
                        <td class="py-3 px-4">${statusBadgeHtml}</td>
                        <td class="py-3 px-4 text-center">${documentCellHtml}</td>
                        <td class="py-3 px-4 text-center">
                            <div class="flex flex-col sm:flex-row items-center justify-center space-y-2 sm:space-y-0 sm:space-x-2">
                                <button class="action-btn approve-btn ${buttonClasses} ${isPending ? 'bg-green-500 hover:bg-green-600 text-white' : 'bg-gray-200 text-gray-500 cursor-not-allowed'}" data-action="approve" ${isPending ? '' : 'disabled'}>
                                    Approve
                                </button>
                                <button class="action-btn reject-btn ${buttonClasses} ${isPending ? 'bg-red-500 hover:bg-red-600 text-white' : 'bg-gray-200 text-gray-500 cursor-not-allowed'}" data-action="reject" ${isPending ? '' : 'disabled'}>
                                    Reject
                                </button>
                            </div>
                        </td>
                    `;
                    ptoRequestsList.appendChild(row);
                });
            }

            updatePaginationControls(totalCount, page, prevUrl, nextUrl);
        }

        /**
         * Updates the pagination buttons' enabled state and info text.
         * @param {number} totalCount - Total number of requests.
         * @param {number} page - Current page number.
         * @param {string|null} prevUrl - URL for previous page.
         * @param {string|null} nextUrl - URL for next page.
         */
        function updatePaginationControls(totalCount, page, prevUrl, nextUrl) {
            prevPageButton.disabled = !prevUrl;
            nextPageButton.disabled = !nextUrl;
            const totalPages = Math.ceil(totalCount / ITEMS_PER_PAGE);
            paginationInfo.textContent = `Showing ${Math.min((page - 1) * ITEMS_PER_PAGE + 1, totalCount)} - ${Math.min(page * ITEMS_PER_PAGE, totalCount)} of ${totalCount} requests`;
            if (totalCount === 0) {
                 paginationInfo.textContent = `No requests to display.`;
            }
        }

        // --- Confirmation Modal Logic ---

        /**
         * Shows the confirmation modal with dynamic content based on the action.
         * @param {string} requestId - The ID of the request being acted upon.
         * @param {'approve'|'reject'} actionType - The type of action.
         */
        function showConfirmationModal(requestId, actionType) {
            selectedRequestId = requestId;
            currentActionType = actionType;
            rejectionReasonInput.value = ''; // Clear previous reason

            // Set modal content based on action type
            if (actionType === 'approve') {
                modalIcon.innerHTML = `<svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`;
                modalIcon.className = 'mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 text-green-600 mb-4';
                modalTitle.textContent = 'Approve Request';
                modalMessage.textContent = 'Are you sure you want to approve this time off request? This action cannot be undone.';
                rejectionReasonGroup.classList.add('hidden'); // Hide reason for approval
                confirmActionBtn.className = 'flex-1 px-5 py-2.5 rounded-lg text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200 shadow-md';
            } else if (actionType === 'reject') {
                modalIcon.innerHTML = `<svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`;
                modalIcon.className = 'mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 text-red-600 mb-4';
                modalTitle.textContent = 'Reject Request';
                modalMessage.textContent = 'Are you sure you want to reject this time off request? You can optionally provide a reason.';
                rejectionReasonGroup.classList.remove('hidden'); // Show reason for rejection
                confirmActionBtn.className = 'flex-1 px-5 py-2.5 rounded-lg text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-200 shadow-md';
            }

            confirmationModal.classList.remove('hidden');
            // Add animation classes
            confirmationModal.classList.add('modal-enter-active');
            confirmationModal.querySelector('.relative').classList.add('modal-enter-active');
        }

        /**
         * Hides the confirmation modal.
         */
        function hideConfirmationModal() {
            // Trigger exit animation
            confirmationModal.classList.remove('modal-enter-active');
            confirmationModal.querySelector('.relative').classList.remove('modal-enter-active');
            confirmationModal.classList.add('modal-exit-active');
            confirmationModal.querySelector('.relative').classList.add('modal-exit-active');

            // Hide after animation completes
            setTimeout(() => {
                confirmationModal.classList.add('hidden');
                confirmationModal.classList.remove('modal-exit-active');
                confirmationModal.querySelector('.relative').classList.remove('modal-exit-active');
                selectedRequestId = null;
                currentActionType = null;
            }, 300); // Match animation duration
        }

        // --- API Action Handlers ---

        /**
         * Handles the approve/reject action after confirmation.
         */
        async function handleConfirmAction() {
            if (!selectedRequestId || !currentActionType) return;

            const actionUrl = `${API_BASE_ENDPOINT}${selectedRequestId}/${currentActionType}/`;
            const csrftoken = getCookie('csrftoken');
            const headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            };
            const body = {};

            if (currentActionType === 'reject') {
                body.reason = rejectionReasonInput.value.trim();
            }

            try {
                const response = await fetch(actionUrl, {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify(body) // Send empty object for approve, or reason for reject
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `Failed to ${currentActionType} request. Status: ${response.status}`);
                }

                showToast(`Request ${currentActionType === 'approve' ? 'approved' : 'rejected'} successfully!`, 'success');
                hideConfirmationModal();
                fetchData(currentPage); // Refresh data after action, no filters to pass
            } catch (error) {
                console.error(`Error ${currentActionType}ing request:`, error);
                showToast(`Error: ${error.message}`, 'error');
                hideConfirmationModal();
            }
        }

        // --- Event Listeners Initialization ---

        // Delegation for Approve/Reject button clicks
        ptoRequestsList.addEventListener('click', (event) => {
            const target = event.target;
            if (target.classList.contains('action-btn')) {
                const row = target.closest('tr');
                const requestId = row.dataset.requestId;
                const actionType = target.dataset.action; // 'approve' or 'reject'
                showConfirmationModal(requestId, actionType);
            }
        });

        // Confirmation modal buttons
        confirmActionBtn.addEventListener('click', handleConfirmAction);
        cancelActionBtn.addEventListener('click', hideConfirmationModal);

        // Pagination controls
        prevPageButton.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                fetchData(currentPage); // No filters to pass
            }
        });

        nextPageButton.addEventListener('click', () => {
            currentPage++;
            fetchData(currentPage); // No filters to pass
        });

        // Initial data load on page load
        fetchData(currentPage);
    });