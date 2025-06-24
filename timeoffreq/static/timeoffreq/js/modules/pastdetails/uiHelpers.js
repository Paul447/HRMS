// static/ptorequest/js/modules/uiHelpers.js

/**
 * Displays a toast notification.
 * @param {string} message - The message to display.
 * @param {'success' | 'error' | 'info'} type - Type of toast (influences styling).
 */
export function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        console.warn('Toast container not found. Cannot display toast.');
        return;
    }

    const toast = document.createElement('div');
    toast.className = `p-3 mb-2 rounded-md shadow-lg text-white text-sm animate-fade-in-down`;

    switch (type) {
        case 'success':
            toast.classList.add('bg-green-500');
            break;
        case 'error':
            toast.classList.add('bg-red-500');
            break;
        case 'info':
        default:
            toast.classList.add('bg-blue-500');
            break;
    }

    toast.textContent = message;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('animate-fade-out-up');
        toast.addEventListener('animationend', () => toast.remove());
    }, 3000); // Remove after 3 seconds
}

/**
 * Toggles the visibility of a loading message row in a table.
 * @param {HTMLElement} loadingRowElement - The table row element for the loading message.
 * @param {boolean} show - True to show, false to hide.
 */
export function toggleLoading(loadingRowElement, show) {
    if (loadingRowElement) {
        loadingRowElement.style.display = show ? 'table-row' : 'none';
    }
}

/**
 * Toggles the visibility of a "no items found" message row in a table.
 * @param {HTMLElement} noResultsRowElement - The table row element for the no results message.
 * @param {boolean} show - True to show, false to hide.
 */
export function toggleNoResultsMessage(noResultsRowElement, show) {
    if (noResultsRowElement) {
        noResultsRowElement.classList.toggle('hidden', !show);
    }
}

/**
 * Toggles the visibility of an error message row in a table.
 * @param {HTMLElement} errorRowElement - The table row element for the error message.
 * @param {boolean} show - True to show, false to hide.
 */
export function toggleErrorMessage(errorRowElement, show) {
    if (errorRowElement) {
        errorRowElement.classList.toggle('hidden', !show);
    }
}