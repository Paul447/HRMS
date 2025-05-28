// static/ptorequest/js/modules/uiHelpers.js

/**
 * Displays a styled toast notification pop-up.
 */
export function showToast(message, type = 'success', duration = 3000) {
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'fixed bottom-5 right-5 z-[1000] flex flex-col space-y-3';
        document.body.appendChild(toastContainer);
    }

    const toast = document.createElement('div');
    let bgColor = '';
    let iconHtml = '';

    if (type === 'success') {
        bgColor = 'bg-green-600';
        iconHtml = `<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`;
    } else if (type === 'error') {
        bgColor = 'bg-red-600';
        iconHtml = `<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`;
    } else if (type === 'warning') {
        bgColor = 'bg-yellow-500';
        iconHtml = `<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.332 16c-.77 1.333.192 3 1.732 3z"></path></svg>`;
    } else { // info
        bgColor = 'bg-blue-600';
        iconHtml = `<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`;
    }

    toast.className = `p-4 rounded-lg shadow-xl ${bgColor} text-white flex items-center space-x-3 transition-all duration-300 ease-out transform translate-x-full opacity-0`;
    toast.innerHTML = `${iconHtml}<span>${message}</span>`;
    toastContainer.appendChild(toast);

    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full', 'opacity-0');
        toast.classList.add('translate-x-0', 'opacity-100');
    }, 50); // Small delay to ensure transition works

    // Animate out and remove
    setTimeout(() => {
        toast.classList.remove('translate-x-0', 'opacity-100');
        toast.classList.add('translate-x-full', 'opacity-0');
        toast.addEventListener('transitionend', () => toast.remove(), { once: true });
    }, duration);
}

/**
 * Shows/hides loading message.
 * @param {HTMLElement} loadingRow - The loading row element.
 * @param {boolean} show - True to show, false to hide.
 */
export function toggleLoading(loadingRow, show) {
    if (loadingRow) {
        loadingRow.classList.toggle('hidden', !show);
    }
}

/**
 * Shows/hides no requests message.
 * @param {HTMLElement} noRequestsMessage - The no requests message element.
 * @param {boolean} show - True to show, false to hide.
 */
export function toggleNoRequestsMessage(noRequestsMessage, show) {
    noRequestsMessage.classList.toggle('hidden', !show);
}

/**
 * Shows/hides error message.
 * @param {HTMLElement} errorMessage - The error message element.
 * @param {boolean} show - True to show, false to hide.
 */
export function toggleErrorMessage(errorMessage, show) {
    errorMessage.classList.toggle('hidden', !show);
}

/**
 * Checks URL for messages and displays them as toasts.
 */
export function checkURLForMessages() {
    const urlParams = new URLSearchParams(window.location.search);
    const message = urlParams.get('message');
    const type = urlParams.get('type'); // 'success', 'error', 'warning'

    if (message && type) {
        showToast(decodeURIComponent(message), type);
        // Clear the query parameters from the URL to prevent the message from reappearing on refresh
        const newUrl = window.location.protocol + '//' + window.location.host + window.location.pathname;
        window.history.replaceState({ path: newUrl }, '', newUrl);
    }
}