// smartFetch.js
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
