/**
 * notificationService.js
 *
 * This module provides a service for displaying global notifications (toasts).
 * It manages the content, type (success, error, warning, info), and animations.
 * It reuses a single #global-notification element in the HTML for efficiency.
 */

// Get notification elements (these are assumed to exist in the HTML and are retrieved once)
const globalNotification = document.getElementById('global-notification');
const notificationIcon = globalNotification ? globalNotification.querySelector('#notification-icon') : null;
const notificationMessage = globalNotification ? globalNotification.querySelector('#notification-message') : null;

// Basic check to ensure notification elements are found
if (!globalNotification || !notificationIcon || !notificationMessage) {
    console.error('NotificationService: Required DOM elements for global notification not found. Please ensure #global-notification, #notification-icon, #notification-message exist in your HTML.');
    // If elements are missing, consider a fallback or disable notification functionality.
    // For now, we'll just log an error and try to proceed, which might lead to further errors.
}

/**
 * Shows a global notification message.
 * The base styling for the notification element should be defined in CSS.
 *
 * @param {string} message The text message to display in the notification.
 * @param {'success'|'error'|'warning'|'info'} [type='info'] The type of notification, affecting its color and icon.
 */
export function showNotification(message, type = 'info') {
    if (!globalNotification || !notificationIcon || !notificationMessage) {
        console.error('NotificationService: Cannot show notification, elements are missing.');
        return; // Exit if essential elements are not found
    }

    // Reset all type-specific background classes and animation classes
    globalNotification.className = 'global-notification-base opacity-0 transition-all duration-300 ease-out transform translate-x-full';
    globalNotification.classList.add('flex'); // Ensure flex display for content alignment
    notificationIcon.innerHTML = ''; // Clear previous icon

    // Set message content
    notificationMessage.textContent = message;

    // Set type-specific classes and icons
    let bgColorClass = '';
    let svgIcon = '';

    switch (type) {
        case 'success':
            bgColorClass = 'bg-green-600';
            svgIcon = `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                       </svg>`;
            break;
        case 'error':
            bgColorClass = 'bg-red-600';
            svgIcon = `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                       </svg>`;
            break;
        case 'warning':
            bgColorClass = 'bg-yellow-500'; // Adjusted to a common warning color
            svgIcon = `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                       </svg>`;
            break;
        case 'info': // Default type for general information
        default:
            bgColorClass = 'bg-blue-600';
            svgIcon = `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                       </svg>`;
            break;
    }

    globalNotification.classList.add(bgColorClass);
    notificationIcon.innerHTML = svgIcon; // Set the icon SVG

    // Make notification visible and animate in
    globalNotification.style.visibility = 'visible';
    globalNotification.classList.add('animate-slide-in');

    // Set timeout to start fade-out animation and then hide
    setTimeout(() => {
        globalNotification.classList.remove('animate-slide-in');
        globalNotification.classList.add('animate-fade-out');

        // Listen for animation end to fully hide and reset state
        globalNotification.addEventListener('animationend', function handler() {
            globalNotification.classList.remove('animate-fade-out');
            globalNotification.style.visibility = 'hidden';
            globalNotification.classList.remove('flex'); // Remove flex display when fully hidden
            globalNotification.style.opacity = '0'; // Ensure opacity is reset for future animations
            globalNotification.style.transform = 'translateX(100%)'; // Reset transform
            globalNotification.removeEventListener('animationend', handler); // Clean up listener
        }, { once: true }); // Ensure this listener runs only once
    }, 5000); // Notification stays for 5 seconds
}

// Export the service
export const NotificationService = {
    showNotification
};