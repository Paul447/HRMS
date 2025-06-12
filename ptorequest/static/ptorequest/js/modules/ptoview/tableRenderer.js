// static/ptorequest/js/modules/ptoview/tableRenderer.js

/**
 * Renders the PTO requests to the table.
 * @param {Array} requests - The array of PTO request objects to render.
 * @param {HTMLElement} targetTbody - The tbody element to append rows to (e.g., ptoRequestsTableBody).
 * @param {boolean} allowActions - Whether to render the 'Actions' column and buttons.
 * @param {function} [onUpdateClick=null] - Callback for update button clicks (only used if allowActions is true).
 * @param {function} [onDeleteClick=null] - Callback for delete button clicks (only used if allowActions is true).
 */
export function renderRequests(requests, targetTbody, allowActions = false, onUpdateClick = null, onDeleteClick = null) {
    targetTbody.innerHTML = ''; // Clear existing rows

    if (!requests || requests.length === 0) {
        // No need to handle noRequestsMessageDiv here, it's handled by the main script
        return;
    }

    requests.forEach((request, index) => {
        const row = document.createElement('tr');
        row.className = 'bg-white border-b hover:bg-gray-50';

        // Format dates and times
        // Adjusting to only date, as time might make the column too wide.
        // If time is critical, consider adding a tooltip or a detail view.
        const startDate = request.start_date_time ? new Date(request.start_date_time).toLocaleDateString('en-US', {
            year: 'numeric', month: 'short', day: 'numeric'
        }) : 'N/A';
        const endDate = request.end_date_time ? new Date(request.end_date_time).toLocaleDateString('en-US', {
            year: 'numeric', month: 'short', day: 'numeric'
        }) : 'N/A';

        // Determine status badge class
        let statusText = request.status || 'Pending';
        let statusClass = 'status-pending'; // Default
        switch (statusText.toLowerCase()) {
            case 'approved':
                statusClass = 'status-approved';
                break;
            case 'rejected':
                statusClass = 'status-rejected';
                break;
            case 'pending':
                statusClass = 'status-pending';
                break;
            case 'cancelled': // If you have a 'cancelled' status
                statusClass = 'status-cancelled';
                break;
        }

        // Build the common table cells
        let rowHtml = `
            <td class="py-2.5 px-3 font-medium text-gray-900 whitespace-nowrap">${index + 1}</td>
            <td class="py-2.5 px-3">${request.department_name_display ? request.department_name_display.name : 'N/A'}</td>
            <td class="py-2.5 px-3">${request.leave_type_display ? request.leave_type_display.name : 'N/A'}</td>
            <td class="py-2.5 px-3 date-col">${startDate}</td>
            <td class="py-2.5 px-3 date-col">${endDate}</td>
            <td class="py-2.5 px-3">${request.total_hours || 'N/A'}</td>
            <td class="py-2.5 px-3 reason-col" title="${request.reason}">${request.reason || 'No reason provided'}</td>
            <td class="py-2.5 px-3">
                <span class="status-badge ${statusClass}">${statusText}</span>
            </td>
        `;

        // Conditionally add the Actions column HTML
        if (allowActions) {
            rowHtml += `
                <td class="py-2.5 px-3 text-center actions-col">
                    <div class="flex items-center justify-center space-x-2">
                        <button data-id="${request.id}"
                                class="update-btn text-blue-600 hover:text-blue-800 text-sm font-medium transition-colors duration-150"
                                title="Edit Request">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 inline-block -mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                            Edit
                        </button>
                        <button data-id="${request.id}"
                                class="delete-btn text-red-600 hover:text-red-800 text-sm font-medium transition-colors duration-150"
                                title="Delete Request">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 inline-block -mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                            Delete
                        </button>
                    </div>
                </td>
            `;
        } else {
            // If actions are not allowed, ensure the corresponding <td> is empty or contains "N/A"
            // This is crucial if your HTML table header still has an "Actions" column
            // (even if hidden via CSS, it's better to render an empty cell to maintain column count).
            // Given your HTML, the `actions-col` header is always there.
            rowHtml += `<td class="py-2.5 px-3 text-center actions-col">N/A</td>`;
        }


        row.innerHTML = rowHtml;
        targetTbody.appendChild(row);
    });

    // Add event listeners only if actions are allowed and callbacks are provided
    if (allowActions) {
        targetTbody.querySelectorAll('.update-btn').forEach(button => {
            if (onUpdateClick) {
                button.addEventListener('click', function() {
                    onUpdateClick(this.dataset.id);
                });
            }
        });

        targetTbody.querySelectorAll('.delete-btn').forEach(button => {
            if (onDeleteClick) {
                button.addEventListener('click', function() {
                    onDeleteClick(this.dataset.id);
                });
            }
        });
    }
}