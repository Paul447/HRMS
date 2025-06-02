// static/timeclock/js/modules/timeclock/apiService.js

/**
 * smartFetch is a robust wrapper around the native Fetch API.
 * It automatically retries an API request exactly once if the initial attempt
 * returns a 401 Unauthorized status. This is designed to work seamlessly
 * with a Django backend middleware that handles JWT token refreshing
 * via HTTP-only cookies. If the middleware successfully refreshes the access token,
 * the retry attempt will use the newly set valid cookie.
 *
 * @param {string} url The URL to send the request to.
 * @param {RequestInit} options Configuration options for the fetch request
 * (e.g., method, headers, body, credentials).
 * @param {boolean} [isRetry=false] Internal flag to prevent infinite retry loops.
 * @returns {Promise<Response>} A promise that resolves with the Fetch API Response object.
 * @throws {Error} Throws an error if a network issue occurs or if the request
 * fails after the retry attempt (and is not a 401 leading to redirect).
 */
export async function smartFetch(url, options = {}, isRetry = false) {
    try {
        const response = await fetch(url, options);

        if (response.status === 401 && !isRetry) {
            console.warn(`[smartFetch] Received 401 for ${url}. Retrying with potentially new token.`);
            return await smartFetch(url, options, true);
        }

        return response;

    } catch (error) {
        console.error(`[smartFetch] Network or other fetch error for ${url}:`, error);
        throw error;
    }
}