// static/ptorequest/js/modules/ptoview/apiService.js

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
 * Fetches PTO requests from the API (specifically pending ones based on your current endpoint usage).
 * @returns {Promise<Array>} A promise that resolves to an array of PTO request objects.
 */
export async function fetchPTORequests() {
    const csrftoken = getCookie('csrftoken');
    const response = await smartFetch('/api/pto-requests/', {
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
 * Fetches approved and rejected PTO requests.
 * @returns {Promise<Object>} A promise that resolves to an object containing approved_requests and rejected_requests arrays.
 */
export async function fetchApprovedAndRejectedRequests() {
    const csrftoken = getCookie('csrftoken');
    const response = await smartFetch('/api/pto-requests/approved-and-rejected/', {
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
    const response = await smartFetch(`/api/pto-requests/${requestId}/`, {
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
    // No content expected for a successful DELETE, so no need to return JSON
}