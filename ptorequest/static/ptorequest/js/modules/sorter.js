// static/ptorequest/js/modules/sorter.js

/**
 * Sorts an array of objects based on a specified column and direction.
 * @param {Array} requests - The array of request objects to sort.
 * @param {string} column - The column (property name) to sort by.
 * @param {string} direction - 'asc' for ascending, 'desc' for descending.
 * @returns {Array} The sorted array.
 */
export function sortRequests(requests, column, direction) {
    const sortedRequests = [...requests]; // Create a shallow copy to avoid modifying the original array

    if (!column) {
        return sortedRequests; // No sorting applied
    }

    sortedRequests.sort((a, b) => {
        let valA = a[column];
        let valB = b[column];

        // Handle nested objects for sorting (e.g., department_name_display.name)
        if (column === 'department_name_display') {
            valA = a.department_name_display ? a.department_name_display.name : '';
            valB = b.department_name_display ? b.department_name_display.name : '';
        } else if (column === 'pay_types_display') {
            valA = a.pay_types_display ? a.pay_types_display.name : '';
            valB = b.pay_types_display ? b.pay_types_display.name : '';
        }

        // Convert to proper types for comparison
        if (column === 'start_date_time' || column === 'end_date_time') {
            valA = new Date(valA);
            valB = new Date(valB);
        } else if (column === 'total_hours' || column === 'id') {
            valA = parseFloat(valA) || 0;
            valB = parseFloat(valB) || 0;
        } else if (typeof valA === 'string') {
            valA = valA.toLowerCase();
            valB = valB.toLowerCase();
        }

        if (valA < valB) return direction === 'asc' ? -1 : 1;
        if (valA > valB) return direction === 'asc' ? 1 : -1;
        return 0;
    });

    return sortedRequests;
}

/**
 * Updates the visual sort indicators on table headers.
 * @param {NodeList} tableHeaders - All table header elements with data-sort attribute.
 * @param {string} currentSortColumn - The column currently being sorted.
 * @param {string} currentSortDirection - The current sort direction ('asc' or 'desc').
 */
export function updateSortIndicators(tableHeaders, currentSortColumn, currentSortDirection) {
    tableHeaders.forEach(th => {
        th.classList.remove('sorted-asc', 'sorted-desc');
        if (th.dataset.sort === currentSortColumn) {
            th.classList.add(`sorted-${currentSortDirection}`);
        }
    });
}