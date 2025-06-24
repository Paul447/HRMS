// static/ptorequest/js/modules/tableRenderer.js

/**
 * Renders PTO requests into a table body.
 * @param {Array} requests - An array of PTO request objects.
 * @param {HTMLElement} tableBodyElement - The tbody element to render into.
 * @param {HTMLElement} noResultsMessageElement - The element to show if no requests are found.
 * @param {Object} options - Rendering options.
 * @param {boolean} [options.highlightRows=false] - Whether to highlight rows based on status.
 */
export function renderPtoRequestsTable(requests, tableBodyElement, noResultsMessageElement, options = {}) {
    tableBodyElement.innerHTML = ''; // Clear existing rows
    noResultsMessageElement.classList.add('hidden'); // Hide "no results" message by default
    

    if (!requests || requests.length === 0) {
        noResultsMessageElement.classList.remove('hidden'); // Show "no results" message
        return;
    }

    requests.forEach(request => {
        const row = document.createElement('tr');

        // Determine status class for text color
        let statusTextColorClass;
        switch (request.status.toLowerCase()) {
            case 'approved':
                statusTextColorClass = 'text-green-600';
                break;
            case 'pending':
                statusTextColorClass = 'text-yellow-600';
                break;
            case 'rejected':
                statusTextColorClass = 'text-red-600';
                break;
            default:
                statusTextColorClass = 'text-gray-600';
        }

        // Determine row highlight class
        let rowHighlightClass = '';
        if (options.highlightRows) {
            switch (request.status.toLowerCase()) {
                case 'approved':
                    rowHighlightClass = 'bg-green-50/50 hover:bg-green-100'; // Light green background
                    break;
                case 'rejected':
                    rowHighlightClass = 'bg-red-50/50 hover:bg-red-100'; // Light red background
                    break;
                case 'pending':
                    rowHighlightClass = 'bg-yellow-50/50 hover:bg-yellow-100'; // Light yellow background
                    break;
                default:
                    rowHighlightClass = 'hover:bg-gray-50'; // Default hover
            }
        } else {
            rowHighlightClass = 'hover:bg-gray-50'; // Default hover if no specific highlighting
        }

        row.className = `${rowHighlightClass}`; // Apply general row styling
        const startDate = request.start_date_time ? new Date(request.start_date_time).toLocaleString('en-US', {
            year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
        }) : 'N/A';
        const endDate = request.end_date_time ? new Date(request.end_date_time).toLocaleString('en-US', {
            year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
        }) : 'N/A';

        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${request.requested_leave_type_details.display_name ? request.requested_leave_type_details.display_name : 'N/A'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${startDate}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${endDate}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${request.time_off_duration || 'N/A'}</td>
            <td class="px-6 py-4 whitespace-normal text-sm text-gray-900 max-w-xs overflow-hidden text-ellipsis">${request.employee_leave_reason}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold ${statusTextColorClass} capitalize">${request.status}</td>
        `;
        tableBodyElement.appendChild(row);
    });
}