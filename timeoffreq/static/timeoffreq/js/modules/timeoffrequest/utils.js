/**
 * utils.js
 *
 * This module provides utility functions for date and time formatting.
 */

/**
 * Formats a datetime-local input string into an ISO 8601 string with timezone offset.
 * Example: '2023-10-26T10:30' -> '2023-10-26T10:30:00-05:00' (for CDT)
 * This format is commonly expected by Django Rest Framework's DateTimeField.
 *
 * @param {string} datetimeLocalString - The string from a datetime-local input (e.g., "2023-10-26T10:30").
 * @returns {string|null} The formatted ISO 8601 string with timezone offset, or null if input is invalid.
 */
export function formatDateTimeForAPI(datetimeLocalString) {
    if (!datetimeLocalString) {
        console.warn("formatDateTimeForAPI: Input datetimeLocalString is empty or null.");
        return null;
    }

    // Create a Date object from the local datetime string.
    // This treats the string as local time, and `getTimezoneOffset` will then
    // give the offset relative to the local system's timezone at that specific time.
    const date = new Date(datetimeLocalString);

    // Validate if the date object is a valid date
    if (isNaN(date.getTime())) {
        console.error("formatDateTimeForAPI: Invalid date string provided:", datetimeLocalString);
        return null;
    }

    // Extract date and time components
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Month is 0-indexed
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = '00'; // Always set seconds to '00' as datetime-local doesn't provide them

    // Calculate timezone offset
    // getTimezoneOffset returns the difference in minutes between UTC and local time.
    // E.g., for UTC-5, it returns 300. For UTC+1, it returns -60.
    const offsetMinutes = date.getTimezoneOffset();
    const offsetSign = offsetMinutes > 0 ? '-' : '+'; // Invert sign for ISO 8601 format
    const absOffsetMinutes = Math.abs(offsetMinutes);
    const offsetHours = String(Math.floor(absOffsetMinutes / 60)).padStart(2, '0');
    const offsetRemainderMinutes = String(absOffsetMinutes % 60).padStart(2, '0');
    
    // Construct the timezone offset string (e.g., "-05:00", "+01:00")
    const timezoneOffsetString = `${offsetSign}${offsetHours}:${offsetRemainderMinutes}`;

    // Combine all parts into the desired ISO 8601 format
    return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}${timezoneOffsetString}`;
}
