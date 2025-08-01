import { Utils } from './utils.js';

/**
 * Manages notification functionality (fetching, rendering, interactions).
 */
export class NotificationManager {
    constructor() {
        this.CSRF_TOKEN = Utils.getCookie('csrftoken');
        this.notificationBell = document.getElementById('notification-bell');
        this.notificationCount = document.getElementById('notification-count');
        this.notificationDropdown = document.getElementById('notification-dropdown');
        this.notificationList = document.getElementById('notification-list');
        this.noNotificationsMessage = document.getElementById('no-notifications');
        this.markAllReadButton = document.getElementById('mark-all-read');

        this.initEventListeners();
    }

    initEventListeners() {
        if (this.notificationBell) {
            this.notificationBell.addEventListener('click', this.toggleNotificationDropdown.bind(this));
        }
        if (this.markAllReadButton) {
            this.markAllReadButton.addEventListener('click', this.markAllNotificationsAsRead.bind(this));
        }
        document.addEventListener('click', this.closeDropdownOnClickOutside.bind(this));
    }

    async toggleNotificationDropdown(event) {
        event.stopPropagation();
        const isHidden = this.notificationDropdown.classList.contains('hidden');
        if (isHidden) {
            this.notificationDropdown.classList.remove('hidden');
            await this.fetchNotifications();
        } else {
            this.notificationDropdown.classList.add('hidden');
        }
    }

    async fetchNotifications() {
        try {
            const response = await fetch('/api/v1/notifications/unread/');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const notifications = await response.json();
            this.updateNotificationUI(notifications);
            return notifications;
        } catch (error) {
            console.error('Error fetching notifications:', error);
            if (this.notificationCount) this.notificationCount.textContent = '0';
            if (this.notificationList) this.notificationList.innerHTML = '';
            if (this.noNotificationsMessage) this.noNotificationsMessage.classList.remove('hidden');
            if (this.markAllReadButton) this.markAllReadButton.disabled = true;
            return [];
        }
    }

    updateNotificationUI(notifications) {
        if (this.notificationCount) this.notificationCount.textContent = notifications.length;
        if (this.notificationList) this.notificationList.innerHTML = '';

        if (notifications.length === 0) {
            if (this.noNotificationsMessage) this.noNotificationsMessage.classList.remove('hidden');
            if (this.markAllReadButton) this.markAllReadButton.disabled = true;
        } else {
            if (this.noNotificationsMessage) this.noNotificationsMessage.classList.add('hidden');
            if (this.markAllReadButton) this.markAllReadButton.disabled = false;

            notifications.forEach(notification => {
                const notificationItem = this.createNotificationItem(notification);
                this.notificationList.appendChild(notificationItem);
            });
            this.attachNotificationEventListeners();
        }
    }

    createNotificationItem(notification) {
        const notificationItem = document.createElement('div');
        notificationItem.classList.add('flex', 'items-start', 'px-4', 'py-3', 'hover:bg-secondary-50',
            'transition-colors', 'duration-150', 'border-b', 'border-secondary-100', 'last:border-b-0', 'group',
            notification.read ? 'text-secondary-500' : 'text-secondary-800', notification.read ? '' : 'font-medium');
        notificationItem.setAttribute('data-notification-id', notification.id);

        let iconSvg = `<svg class="h-5 w-5 flex-shrink-0 mt-1 mr-3 ${notification.read ? 'text-secondary-400' : 'text-primary-500'}" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`;
        if (notification.verb && notification.verb.includes("Time Off")) {
            iconSvg = `<svg class="h-5 w-5 flex-shrink-0 mt-1 mr-3 ${notification.read ? 'text-secondary-400' : 'text-green-500'}" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 0 00-2 2v12a2 2 0 002 2z"></path></svg>`;
        }

        notificationItem.innerHTML = `
            ${iconSvg}
            <div class="flex-grow">
                <p class="text-sm leading-snug">${notification.description}</p>
                <p class="text-xs text-secondary-500 mt-1">${Utils.formatTimeAgo(notification.timestamp)}</p>
                ${notification.content_object_display ? `<p class="text-xs text-secondary-600 mt-1 italic">${notification.content_object_display}</p>` : ''}
                ${notification.action_url ? `<a href="${notification.action_url}" class="text-xs text-primary-500 hover:underline mt-1 block">View Details</a>` : ''}
            </div>
            <div class="flex flex-col ml-2 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
                <button class="mark-toggle-btn text-xs px-2 py-1 rounded hover:bg-primary-100 text-primary-600 mb-1" data-id="${notification.id}" data-read="${notification.read}">
                    ${notification.read ? 'Mark as Unread' : 'Mark as Read'}
                </button>
                <button class="delete-notification-btn text-xs px-2 py-1 rounded hover:bg-red-100 text-danger-500" data-id="${notification.id}">
                    Delete
                </button>
            </div>
        `;
        return notificationItem;
    }

    attachNotificationEventListeners() {
        document.querySelectorAll('.mark-toggle-btn').forEach(button => {
            button.onclick = this.handleMarkToggleClick.bind(this);
        });

        document.querySelectorAll('.delete-notification-btn').forEach(button => {
            button.onclick = this.handleDeleteNotificationClick.bind(this);
        });
    }

    async handleMarkToggleClick(event) {
        event.stopPropagation();
        const id = event.currentTarget.dataset.id;
        const isCurrentlyRead = event.currentTarget.dataset.read === 'true';
        const endpoint = isCurrentlyRead ? `/api/v1/notifications/${id}/mark_as_unread/` : `/api/v1/notifications/${id}/mark_as_read/`;
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.CSRF_TOKEN,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });
            if (!response.ok) throw new Error('Failed to toggle read status');
            console.log(`Notification ${id} status toggled.`);
            await this.fetchNotifications();
        } catch (error) {
            console.error('Error toggling notification status:', error);
        }
    }

    async handleDeleteNotificationClick(event) {
        event.stopPropagation();
        if (!confirm('Are you sure you want to delete this notification?')) {
            return;
        }
        const id = event.currentTarget.dataset.id;
        try {
            const response = await fetch(`/api/v1/notifications/${id}/delete/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.CSRF_TOKEN,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });
            if (!response.ok) throw new Error(`Failed to delete notification, status: ${response.status}`);
            console.log(`Notification ${id} deleted.`);
            await this.fetchNotifications();
        } catch (error) {
            console.error('Error deleting notification:', error);
        }
    }

    async markAllNotificationsAsRead() {
        if (this.markAllReadButton && this.markAllReadButton.disabled) return;
        try {
            const response = await fetch('/api/v1/notifications/mark_all_as_read/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.CSRF_TOKEN,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });
            if (!response.ok) throw new Error('Failed to mark all as read');
            const data = await response.json();
            console.log(data.message);
            await this.fetchNotifications();
        } catch (error) {
            console.error('Error marking all notifications as read:', error);
        }
    }

    closeDropdownOnClickOutside(event) {
        if (this.notificationDropdown && this.notificationBell &&
            !this.notificationDropdown.contains(event.target) &&
            !this.notificationBell.contains(event.target)) {
            this.notificationDropdown.classList.add('hidden');
        }
    }

    startPeriodicRefresh(intervalMinutes = 5) {
        setInterval(() => this.fetchNotifications(), intervalMinutes * 60 * 1000);
    }
}