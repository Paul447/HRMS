// static/ptorequest/js/modules/apiService.js

/**
 * Gets a CSRF token from cookies.
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * smartFetch is a robust wrapper around the native Fetch API.
 * Handles 401 Unauthorized responses by redirecting to login.
 */
async function smartFetch(url, options = {}, isRetry = false) {
    try {
        const response = await fetch(url, options);
        if (response.status === 401 && !isRetry) {
            console.warn(`[smartFetch] Received 401 for ${url}. Redirecting to login.`);
            window.location.href = '/auth/login/';
            return; // Prevent further processing
        }
        return response;
    } catch (error) {
        console.error(`[smartFetch] Network or other fetch error for ${url}:`, error);
        throw error;
    }
}

/**
 * Fetches PTO requests from the API.
 * @param {string} [payPeriodId=null] - Optional pay period ID to filter requests.
 * @returns {Promise<Array>} A promise that resolves to an array of PTO request objects.
 */
export async function fetchPTORequests(payPeriodId = null) {
    const csrftoken = getCookie('csrftoken');
    let url = '/api/timeoffrequests/';
    if (payPeriodId) {
        url += `?pay_period_id=${payPeriodId}`;
    }

    const response = await smartFetch(url, {
        method: 'GET',
        credentials: 'include',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`Failed to load PTO requests. Status: ${response.status}. Error: ${JSON.stringify(errorData)}`);
    }

    return response.json();
}

/**
 * Fetches Pay Periods from the API.
 * @returns {Promise<Array>} A promise that resolves to an array of pay period objects.
 */
export async function fetchPAYPeriods() {
    const csrftoken = getCookie('csrftoken');
    const response = await smartFetch('/api/current-future-pay-period/', {
        method: 'GET',
        credentials: 'include',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    });
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`Failed to load pay periods. Status: ${response.status}. Error: ${JSON.stringify(errorData)}`);
    }

    return response.json();
}

/**
 * Fetches the PTO request of Approved and Rejected ones.
 * @param {string} [payPeriodId=null] - Optional pay period ID to filter requests.
 * @returns {Promise<Object>} A promise that resolves to an object containing approved and rejected PTO request arrays.
 */
export async function fetchApprovedAndRejectedRequests(payPeriodId = null) {
    const csrftoken = getCookie('csrftoken');
    let url = '/api/pto-requests/approved-and-rejected/';
    if (payPeriodId) {
        url += `?pay_period_id=${payPeriodId}`;
    }

    const response = await smartFetch(url, {
        method: 'GET',
        credentials: 'include',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`Failed to load approved/rejected PTO requests. Status: ${response.status}. Error: ${JSON.stringify(errorData)}`);
    }

    return response.json();
}

/**
 * Deletes a PTO request by ID.
 * @param {number} requestId - The ID of the request to delete.
 */
export async function deletePTORequest(requestId) {
    const csrftoken = getCookie('csrftoken');
    const response = await smartFetch(`/api/timeoffrequests/${requestId}/`, {
        method: 'DELETE',
        credentials: 'include',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`Failed to delete request. Status: ${response.status}. Error: ${JSON.stringify(errorData)}`);
    }
    // No content expected for a successful DELETE
}