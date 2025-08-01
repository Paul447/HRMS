/**
 * Utility functions for common tasks.
 */
export class Utils {
    /**
     * Gets a cookie by name.
     * @param {string} name - The name of the cookie to retrieve.
     * @returns {string|null} The cookie value or null if not found.
     */
    static getCookie(name) {
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
     * Formats a timestamp into a human-readable "time ago" string.
     * @param {string} timestamp - The timestamp string (e.g., ISO 8601).
     * @returns {string} The formatted "time ago" string.
     */
    static formatTimeAgo(timestamp) {
        const now = new Date();
        const past = new Date(timestamp);
        const seconds = Math.round((now - past) / 1000);
        const minutes = Math.round(seconds / 60);
        const hours = Math.round(minutes / 60);
        const days = Math.round(hours / 24);
        const months = Math.round(days / 30.44);
        const years = Math.round(days / 365.25);

        if (seconds < 60) return `${seconds}s ago`;
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        if (days < 30) return `${days}d ago`;
        if (months < 12) return `${months} month${months > 1 ? 's' : ''} ago`;
        return `${years} year${years > 1 ? 's' : ''} ago`;
    }

    /**
     * Applies or removes skeleton loading styles to an element.
     * @param {HTMLElement} element - The HTML element to modify.
     * @param {boolean} isLoading - True to apply loading styles, false to remove.
     */
    static toggleSkeletonLoading(element, isLoading) {
        if (!element) return;
        if (isLoading) {
            element.classList.add('skeleton-loading');
            if (element.classList.contains('user-name')) {
                element.classList.add('w-24', 'h-5');
            }
            element.textContent = ''; // Clear content for skeleton
        } else {
            element.classList.remove('skeleton-loading', 'w-24', 'h-5');
        }
    }
}