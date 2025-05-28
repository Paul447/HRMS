// static/ptorequest/js/modules/ptorequest/notificationService.js

/**
 * Displays a styled notification pop-up.
 * This function is designed to be reusable across different parts of your application.
 *
 * @param {string} message The message to display.
 * @param {'success'|'error'|'warning'} type The type of notification.
 */
export function showNotification(message, type = 'success') {
    const existingNotification = document.getElementById('global-notification');
    if (existingNotification) {
        existingNotification.remove();
        console.log('[NotificationService] Removed existing notification with ID global-notification.');
    }

    const notification = document.createElement('div');
    notification.id = 'global-notification'; // Assign a unique ID
    notification.className = `
        fixed top-10 right-4 z-50
        px-6 py-4 rounded-lg shadow-xl
        flex items-center space-x-2 animate-slide-in
    `;

    let bgColorClass = '';
    let iconSvg = '';

    if (type === 'success') {
        bgColorClass = 'bg-green-600';
        iconSvg = `
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
            </svg>
        `;
    } else if (type === 'error') {
        bgColorClass = 'bg-red-600';
        iconSvg = `
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
        `;
    } else if (type === 'warning') {
        bgColorClass = 'bg-yellow-500';
        iconSvg = `
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.332 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
        `;
    }

    notification.classList.add(bgColorClass, 'text-white', 'font-medium');
    notification.innerHTML = `
        ${iconSvg}
        <span>${message}</span>
    `;
    document.body.appendChild(notification);
    console.log(`[NotificationService] Displayed notification: "${message}"`);

    // --- IMPORTANT DEBUGGING LOGIC ---
    // This part tries to remove the notification after a delay.
    // It first attempts an animation-based removal, then a fallback direct removal.
    setTimeout(() => {
        console.log(`[NotificationService] setTimeout triggered for: "${message}"`);
        notification.classList.remove('animate-slide-in'); // Ensure slide-in animation stops
        notification.classList.add('animate-fade-out');    // Start fade-out animation

        // Listener for the end of the fade-out animation
        notification.addEventListener('animationend', function handler() {
            console.log(`[NotificationService] animationend fired for: "${message}". Removing notification.`);
            if (document.body.contains(notification)) { // Check if it's still in the DOM
                notification.remove();
            }
            // Remove the event listener itself to prevent memory leaks if not using { once: true }
            // (though { once: true } is used, it's good to be explicit for understanding)
            notification.removeEventListener('animationend', handler);
        }, { once: true }); // Ensures listener runs only once

        // FALLBACK: If animationend never fires (e.g., CSS issue, animation-duration: 0s)
        // This ensures the notification is eventually removed regardless of animation success.
        const fallbackRemovalDelay = 1000; // Give 1 second after the 5s initial timeout for animation to complete
        setTimeout(() => {
            if (document.body.contains(notification)) {
                console.warn(`[NotificationService] Fallback removal for "${message}". animationend might not have fired or completed.`);
                notification.remove();
            }
        }, fallbackRemovalDelay);

    }, 5000); // Initial 5 seconds before fade-out animation starts
}