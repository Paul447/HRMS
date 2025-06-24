export const NotificationService = (function() {
    function showNotification(message, type = 'success') {
        let notification = document.getElementById('global-notification');

        if (notification) {
            notification.remove();
        }

        notification = document.createElement('div');
        notification.id = 'global-notification';
        notification.className = `
            fixed top-10 right-4 z-50
            px-6 py-4 rounded-lg shadow-xl
            flex items-center space-x-2
            text-white font-medium
        `;

        let bgColorClass = '';
        let iconSvg = '';

        if (type === 'success') {
            bgColorClass = 'bg-green-600';
            iconSvg = `<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" /></svg>`;
        } else if (type === 'error') {
            bgColorClass = 'bg-red-600';
            iconSvg = `<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>`;
        } else if (type === 'warning') {
            bgColorClass = 'bg-yellow-500';
            iconSvg = `<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.332 16c-.77 1.333.192 3 1.732 3z" /></svg>`;
        }

        notification.classList.add(bgColorClass);
        notification.innerHTML = `${iconSvg}<span>${message}</span>`;
        document.body.appendChild(notification);
        
        requestAnimationFrame(() => {
            notification.classList.add('animate-slide-in');
        });

        setTimeout(() => {
            notification.classList.remove('animate-slide-in');
            notification.classList.add('animate-fade-out');

            notification.addEventListener('animationend', function handler() {
                if (document.body.contains(notification)) {
                    notification.remove();
                }
                notification.removeEventListener('animationend', handler);
            }, { once: true });

            setTimeout(() => {
                if (document.body.contains(notification)) {
                    console.warn(`[NotificationService] Fallback removal for notification. Animation might not have completed.`);
                    notification.remove();
                }
            }, 1000);
        }, 5000);
    }
    return { showNotification };
})();