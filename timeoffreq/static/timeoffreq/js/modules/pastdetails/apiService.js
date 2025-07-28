// static/ptorequest/js/modules/apiService.js

/**
 * Gets a CSRF token from the document cookies.
 * @returns {string | null} The CSRF token string or null if not found.
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
 * A wrapper around fetch that handles common concerns like authentication errors
 * and CSRF tokens.
 * @param {string} url - The URL to fetch.
 * @param {Object} options - Fetch options.
 * @param {boolean} [isRetry=false] - Internal flag for retry logic.
 * @returns {Promise<Response>} The fetch Response object.
 * @throws {Error} If network or fetch operation fails.
 */
export async function smartFetch(url, options = {}, isRetry = false) {
    const defaultHeaders = {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'), // Add CSRF token for POST, PUT, DELETE
    };

    options.headers = {
        ...defaultHeaders,
        ...options.headers,
    };
    options.credentials = 'include'; // Important for sending cookies/sessions

    try {
        const response = await fetch(url, options);

        // Handle 401 Unauthorized errors and retry once
        if (response.status === 401 && !isRetry) {
            console.warn(`[smartFetch] Received 401 for ${url}. Attempting to refresh token or re-authenticate.`);
            // In a real app, you'd typically have a token refresh mechanism here.
            // For now, we just retry, assuming session authentication might just need a nudge.
            return await smartFetch(url, options, true);
        }

        return response;

    } catch (error) {
        console.error(`[smartFetch] Network or other fetch error for ${url}:`, error);
        throw error;
    }
}

/**
 * Fetches all available pay periods from the /api/pay-period/ endpoint.
 * @returns {Promise<Array>} A list of pay period objects.
 * @throws {Error} If the API call fails.
 */
export async function fetchPayPeriods() {
    try {
        const response = await smartFetch('/api/v1/past-pay-period/', {
            method: 'GET',
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(
                `Failed to fetch pay periods: ${errorData.detail || response.statusText}`
            );
        }
        return await response.json();
    } catch (error) {
        console.error("Error in fetchPayPeriods:", error);
        throw error;
    }
}

/**
 * Fetches PTO requests from the /api/past-pto-requests/ endpoint.
 * @param {string | null} payPeriodId - The ID of the pay period to filter by.
 * @returns {Promise<Array>} A list of past PTO request objects.
 * @throws {Error} If the API call fails.
 */
export async function fetchPastPtoRequests(payPeriodId = null) {
    let url = '/api/v1/past-timeoff-requests/';
    if (payPeriodId) {
        url += `?pay_period_id=${payPeriodId}`;
    }

    try {
        const response = await smartFetch(url, { method: 'GET' });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(
                `Failed to fetch past PTO requests: ${errorData.detail || response.statusText}`
            );
        }
        return await response.json();
    } catch (error) {
        console.error("Error in fetchPastPtoRequests:", error);
        throw error;
    }
}