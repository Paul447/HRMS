/**
 * Formats a date string for display in the modal.
 * @param {string} dateString - The date string (e.g., ISO 8601).
 * @returns {string} Formatted date and time.
 */
export const formatModalDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'Invalid Date';
    return date.toLocaleString('en-US', { dateStyle: 'medium', timeStyle: 'short' });
};

/**
 * Returns a comma-separated string of employee names.
 * @param {string[]} employeeNames - An array of employee names.
 * @returns {string} Formatted employee names or 'N/A'.
 */
export const getEmployeeDisplayNames = (employeeNames) => {
    return Array.isArray(employeeNames) && employeeNames.length > 0
        ? employeeNames.join(', ')
        : 'N/A';
};