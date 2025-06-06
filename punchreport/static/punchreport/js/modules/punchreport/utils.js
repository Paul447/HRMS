// static/timeclock/js/modules/shared/utils.js

/**
 * Formats an ISO string to a displayable date (e.g., "Fri 05/30/25")
 * @param {string|null|undefined} isoString - The ISO 8601 date string.
 * @returns {string} Formatted date string or an error message.
 */
export function formatDate(isoString) {
    if (!isoString) {
        console.warn("formatDate called with null or undefined isoString:", isoString);
        return 'N/A';
    }
    try {
        const date = new Date(isoString);
        if (isNaN(date.getTime())) {
            console.error("Invalid date string passed to formatDate:", isoString);
            return 'Invalid Date';
        }
        const options = {
            weekday: 'short',
            month: '2-digit',
            day: '2-digit',
            year: '2-digit'
        };
        return date.toLocaleString(navigator.language, options);
    } catch (e) {
        console.error("Error formatting date:", isoString, e);
        return 'Error Formatting';
    }
}

/**
 * Formats an ISO string to a displayable date (e.g., "Fri, May 30") suitable for main period.
 * @param {string|null|undefined} isoString - The ISO 8601 date string.
 * @returns {string} Formatted date string or "N/A".
 */
export function formatPayPeriodDate(isoString) {
    if (!isoString) return 'N/A';
    try {
        const date = new Date(isoString);
        if (isNaN(date.getTime())) {
            console.error("Invalid date string passed to formatPayPeriodDate:", isoString);
            return 'Invalid Date';
        }
        const options = {
            weekday: 'short',
            month: 'short',
            day: 'numeric'
        };
        return date.toLocaleString(navigator.language, options);
    } catch (e) {
        console.error("Error formatting pay period date:", isoString, e);
        return 'Error Formatting';
    }
}

/**
 * Formats an ISO string to a displayable time (e.g., "11:24 AM")
 * @param {string|null|undefined} isoString - The ISO 8601 date string.
 * @returns {string} Formatted time string or an empty string if null/undefined.
 */
export function formatOnlyTime(isoString) {
    if (!isoString) {
        return '';
    }
    try {
        const date = new Date(isoString);
        if (isNaN(date.getTime())) {
            console.error("Invalid date string passed to formatOnlyTime:", isoString);
            return 'Invalid Time';
        }
        const options = {
            hour: '2-digit',
            minute: '2-digit',
            // hour24:true, 
            hourCycle: 'h23' // Use 24-hour format
        };
        return date.toLocaleString(navigator.language, options);
    } catch (e) {
        console.error("Error formatting time:", isoString, e);
        return 'Error Time';
    }
}

/**
 * Calculates duration between two ISO strings and formats it (e.g., "X:YY")
 * @param {string} clockInIso - ISO 8601 string for clock-in time.
 * @param {string} clockOutIso - ISO 8601 string for clock-out time.
 * @returns {string} Formatted duration or an error message.
 */
// static/timeclock/js/modules/shared/utils.js


// static/timeclock/js/modules/shared/utils.js

export function formatDuration(clockInIso, clockOutIso) {
    // Basic validation for missing inputs
    if (!clockInIso || !clockOutIso) {
        console.warn("formatDuration called with missing clockInIso or clockOutIso for calculation:", clockInIso,
            clockOutIso);
        return '0.00'; // Default for incomplete data, now as decimal hours
    }

    try {
        const inTime = new Date(clockInIso);
        const outTime = new Date(clockOutIso);

        // Debugging logs: uncomment if you need to see the Date objects themselves
        // console.log("--- DEBUG: formatDuration START ---");
        // console.log("Input clockInIso:", clockInIso);
        // console.log("Input clockOutIso:", clockOutIso);
        // console.log("inTime (Date object):", inTime.toISOString());
        // console.log("outTime (Date object):", outTime.toISOString());

        // Validate if Date objects are valid
        if (isNaN(inTime.getTime()) || isNaN(outTime.getTime())) {
            console.error("Invalid date(s) in formatDuration:", clockInIso, clockOutIso);
            return 'Invalid'; // Changed from 'Invalid Duration' for decimal output
        }

        // Calculate the difference in milliseconds
        const diffMs = outTime - inTime;
        // Debugging log
        

        // Handle negative durations (clock out before clock in)
        if (diffMs < 0) {
            console.warn("Clock out time is before clock in time for duration calculation.");
            return 'Invalid'; // Changed from 'Invalid Duration' for decimal output
        }

        // Convert milliseconds to total seconds
        const totalSeconds = Math.floor(diffMs / 1000);
        // Debugging log
        

        // Calculate total hours as a decimal
        const totalHours = totalSeconds / 3600;
        

        // Return total hours rounded to two decimal places
        // Note: JavaScript's toFixed() rounds "half up" (e.g., 0.045 becomes 0.05).
        // Python's round() uses "round half to even" (e.g., round(0.045, 2) is 0.04).
        // This might lead to slight differences for specific half-way values,
        // but for general use, toFixed(2) is standard.
        return totalHours.toFixed(2);

    } catch (e) {
        // Catch any unexpected errors during calculation
        console.error("Error calculating duration:", clockInIso, clockOutIso, e);
        return 'Error'; // Changed from 'Error Calc.' for decimal output
    }
}

// Ensure other utility functions like formatDate, formatOnlyTime, etc., are also in this file
// if they are imported elsewhere.

// Global variable for interval management (to clear old intervals on re-render)
// This is typically managed by the module that creates it, but for simplicity
// and matching your original pattern, we keep it here.
window.durationInterval = null;