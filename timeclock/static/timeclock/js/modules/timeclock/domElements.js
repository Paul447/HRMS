// static/timeclock/js/modules/timeclock/domElements.js

/**
 * Gets references to all necessary DOM elements for the Timeclock application.
 * @returns {Object} An object containing references to DOM elements.
 */
export function getDomElements() {
    // Helper function to get CSRF token from a hidden input field
    // It's crucial for Django's security.
    function getCsrfToken() {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput && csrfInput.value) {
            return csrfInput.value;
        }
        // Fallback for getting from cookies if no input is present
        // (Less common with modern Django setup where it's in a hidden input)
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken' + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                    break;
                }
            }
        }
        console.warn("[domElements] CSRF token not found in hidden input. Falling back to cookie. Ensure {% csrf_token %} is in your HTML.");
        return cookieValue;
    }

    return {
        payPeriodCard: document.getElementById('payPeriodCard'),
        clockInOutCard: document.getElementById('clockInOutCard'),
        timeEntriesSection: document.getElementById('timeEntriesSection'),
        // Store the CSRF token value directly for easier access
        csrftokenInput: { value: getCsrfToken() }
    };
}