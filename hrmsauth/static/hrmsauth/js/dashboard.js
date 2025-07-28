// hrmsauth/static/hrmsauth/js/dashboard.js

/**
* Utility functions for common tasks.
*/
class Utils {
/**
* Gets a cookie by name.
* @param {string} name - The name of the cookie to retrieve.
* @returns {string|null} The cookie value or null if not found.
*/
static getCookie(name) {
let cookieValue = null;
if (document.cookie && document.cookie !== '') {
const cookies = document.cookie.split(';');
for (let i = 0; i < cookies.length; i++) { const cookie=cookies[i].trim(); if (cookie.substring(0, name.length +
    1)===(name + '=' )) { cookieValue=decodeURIComponent(cookie.substring(name.length + 1)); break; } } } return
    cookieValue; } /** * Formats a timestamp into a human-readable "time ago" string. * @param {string} timestamp - The
    timestamp string (e.g., ISO 8601). * @returns {string} The formatted "time ago" string. */ static
    formatTimeAgo(timestamp) { const now=new Date(); const past=new Date(timestamp); const seconds=Math.round((now -
    past) / 1000); const minutes=Math.round(seconds / 60); const hours=Math.round(minutes / 60); const
    days=Math.round(hours / 24); const months=Math.round(days / 30.44); const years=Math.round(days / 365.25); if
    (seconds < 60) return `${seconds}s ago`; if (minutes < 60) return `${minutes}m ago`; if (hours < 24) return
    `${hours}h ago`; if (days < 30) return `${days}d ago`; if (months < 12) return `${months} month${months> 1 ? 's' :
    ''} ago`;
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

    /**
    * Manages sidebar visibility and submenu toggles.
    */
    class SidebarManager {
    constructor() {
    this.sidebar = document.getElementById('sidebar');
    this.sidebarBackdrop = document.getElementById('sidebar-backdrop');
    this.sidebarOverlay = document.getElementById('sidebar-overlay'); // Assuming this exists for the full overlay
    }

    /**
    * Toggles the visibility of the sidebar and its backdrop/overlay on mobile.
    */
    toggleSidebar() {
    if (this.sidebar) {
    this.sidebar.classList.toggle('-translate-x-full');
    }
    if (this.sidebarBackdrop) {
    this.sidebarBackdrop.classList.toggle('hidden');
    }
    if (this.sidebarOverlay) { // Toggle overlay if it's separate
    this.sidebarOverlay.classList.toggle('hidden');
    }
    }

    /**
    * Toggles the visibility of a submenu and rotates its associated arrow.
    * @param {string} id - The ID of the submenu to toggle.
    */
    toggleSubmenu(id) {
    const submenu = document.getElementById(id);
    if (submenu) {
    submenu.classList.toggle('hidden');
    const arrow = document.getElementById(`${id}-arrow`);
    if (arrow) {
    arrow.classList.toggle('rotate-90');
    }
    }
    }

    /**
    * Closes the sidebar and hides its backdrop/overlay.
    */
    closeSidebar() {
    if (this.sidebar) {
    this.sidebar.classList.add('-translate-x-full');
    }
    if (this.sidebarBackdrop) {
    this.sidebarBackdrop.classList.add('hidden');
    }
    if (this.sidebarOverlay) {
    this.sidebarOverlay.classList.add('hidden');
    }
    }

    /**
    * Initializes sidebar link active states and mobile click behavior.
    */
    initSidebarLinks() {
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('#sidebar a');
    let exactMatchFound = false;
    let exactMatchLink = null;

    sidebarLinks.forEach(link => {
    const linkHref = link.getAttribute('href');
    if (linkHref && linkHref === currentPath) {
    exactMatchFound = true;
    exactMatchLink = link;
    }
    });

    sidebarLinks.forEach(link => {
    const linkHref = link.getAttribute('href');
    if (!linkHref) return;

    let isActive = false;

    if (exactMatchFound) {
    isActive = link === exactMatchLink;
    } else {
    isActive = currentPath.startsWith(linkHref) && linkHref !== '/' && currentPath !== linkHref;
    }

    if (isActive) {
    link.classList.add('bg-primary-700', 'border-l-4', 'border-primary-300', 'pl-3', 'bg-primary-900/50',
    'shadow-inner-md');
    link.classList.remove('hover:bg-primary-700', 'px-4');

    const parentSubmenu = link.closest('.space-y-0\\.5');
    if (parentSubmenu) {
    parentSubmenu.classList.remove('hidden');
    const parentButton = parentSubmenu.previousElementSibling;
    if (parentButton && parentButton.tagName === 'BUTTON') {
    const parentButtonIdMatch = parentButton.getAttribute('onclick')?.match(/'([^']*)'/);
    if (parentButtonIdMatch) {
    const parentButtonId = parentButtonIdMatch[1];
    const arrow = document.getElementById(`${parentButtonId}-arrow`);
    if (arrow) {
    arrow.classList.add('rotate-90');
    }
    parentButton.classList.add('bg-primary-700', 'bg-primary-900/50', 'shadow-inner-md');
    parentButton.setAttribute('aria-expanded', 'true');
    }
    }
    }

    if (window.innerWidth < 768) { link.addEventListener('click', this.closeSidebar.bind(this)); } } });
        window.addEventListener('resize', ()=> {
        if (window.innerWidth >= 768 && this.sidebar && !this.sidebar.classList.contains('-translate-x-full')) {
        this.closeSidebar();
        }
        });
        }
        }

        /**
        * Manages user data fetching and UI updates related to user information and admin tools.
        */
        class UserDataManager {
        constructor() {
        this.userNameElement = document.querySelector('.user-name');
        this.userAvatarElement = document.getElementById('user-avatar');
        this.onShiftReportLink = document.getElementById('onShiftReportLink');
        this.timeOffManagementLink = document.getElementById('timeOffManagementLink');
        this.adminToolDiv = document.getElementById('admintoolsButton');
        this.adminElements = [
        this.onShiftReportLink,
        this.timeOffManagementLink,
        this.adminToolDiv
        ].filter(Boolean); // Filter out any null elements
        }

        /**
        * Fetches user data and updates the UI.
        */
        async getUserData() {
        // Apply skeleton loading styles immediately
        Utils.toggleSkeletonLoading(this.userNameElement, true);
        Utils.toggleSkeletonLoading(this.userAvatarElement, true);
        if (this.userAvatarElement) this.userAvatarElement.textContent = '';
        if (this.userNameElement) this.userNameElement.textContent = '';

        try {
        const response = await fetch('/api/v1/user-info/', {
        method: 'GET',
        headers: {
        'Content-Type': 'application/json',
        }
        });

        if (response.ok) {
        const data = await response.json();
        if (this.userNameElement) this.userNameElement.textContent = data.username || 'User';
        if (this.userAvatarElement) this.userAvatarElement.textContent = data.username ?
        data.username.charAt(0).toUpperCase() : 'U';

        const isSuperuser = data.hasOwnProperty('is_superuser') ? data.is_superuser : false;
        this.updateAdminToolsVisibility(isSuperuser);
        } else {
        console.error('Failed to fetch user data. Status:', response.status);
        this.handleFetchError();
        }
        } catch (error) {
        console.error('Error fetching user data:', error);
        this.handleFetchError();
        } finally {
        // Always remove skeleton loading styles
        Utils.toggleSkeletonLoading(this.userNameElement, false);
        Utils.toggleSkeletonLoading(this.userAvatarElement, false);
        }
        }

        /**
        * Updates the visibility of admin tools based on superuser status.
        * @param {boolean} isSuperuser - True if the user is a superuser.
        */
        updateAdminToolsVisibility(isSuperuser) {
        this.adminElements.forEach(el => {
        if (el) {
        if (isSuperuser) {
        el.classList.remove('hidden');
        el.removeAttribute('aria-hidden');
        if (el === this.adminToolDiv) el.style.display = ''; // Reset display
        } else {
        el.classList.add('hidden');
        el.setAttribute('aria-hidden', 'true');
        if (el === this.adminToolDiv) el.style.display = 'none'; // Explicitly hide
        }
        }
        });
        }

        /**
        * Handles UI updates on user data fetch failure.
        */
        handleFetchError() {
        if (this.userNameElement) this.userNameElement.textContent = 'Guest';
        if (this.userAvatarElement) this.userAvatarElement.textContent = '?';
        this.updateAdminToolsVisibility(false); // Hide admin elements on error
        }
        }

        /**
        * Manages the visibility of the time off link based on department data.
        */
        class TimeOffLinkManager {
        constructor() {
        this.timeOffLinkDiv = document.getElementById('timeoff');
        this.managerTimeOffManagementLink = document.getElementById('managerToolsButton');
        }

        /**
        * Fetches user data to determine if time off links should be displayed.
        * @returns {Promise<void>}
            */
            async hideTimeOffLink() {
            // Check if elements exist
            if (!this.timeOffLinkDiv || !this.managerTimeOffManagementLink) {
            console.warn('Required elements not found. Time off link:', !!this.timeOffLinkDiv,
            'Manager link:', !!this.managerTimeOffManagementLink);
            return;
            }

            try {
            const response = await fetch('/api/v1/user-info/', {
            method: 'GET',
            headers: {
            'Content-Type': 'application/json',
            // Add authentication token if required (e.g., from Django session or JWT)
            // 'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            credentials: 'same-origin' // Include cookies for Django session auth
            });

            if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            

            // Handle both array and object responses
            const userData = Array.isArray(data) && data[0] ? data[0] : data;

            // Validate required fields
            if (!userData || typeof userData.is_time_off === 'undefined' ||
            typeof userData.is_manager === 'undefined' ||
            typeof userData.is_superuser === 'undefined') {
            throw new Error('Invalid response data structure: missing required fields');
            }

            const { is_time_off: timeoffFeatureEnabled, is_manager: isManager, is_superuser: isSuperuser } = userData;

            // Update time off link visibility
            this.updateElementVisibility(
            this.timeOffLinkDiv,
            timeoffFeatureEnabled === true
            );

            // Update manager link visibility for managers or superusers
            this.updateElementVisibility(
            this.managerTimeOffManagementLink,
            isManager === true || isSuperuser === true
            );

            } catch (error) {
            console.error('Error in hideTimeOffLink:', error);
            // Default visibility: show timeOffLink, hide manager link
            this.updateElementVisibility(this.timeOffLinkDiv, true);
            this.updateElementVisibility(this.managerTimeOffManagementLink, false);
            }
            }

            /**
            * Updates element visibility and ARIA attributes
            * @param {HTMLElement} element - The element to update
            * @param {boolean} isVisible - Whether the element should be visible
            */
            updateElementVisibility(element, isVisible) {
            if (!element) return;

            if (isVisible) {
            element.classList.remove('hidden');
            element.removeAttribute('aria-hidden');
            console.log(`Showing element: ${element.id}`); // Debug: Confirm visibility
            } else {
            element.classList.add('hidden');
            element.setAttribute('aria-hidden', 'true');
            console.log(`Hiding element: ${element.id}`); // Debug: Confirm visibility
            }
            }
            }

            /**
            * Manages notification functionality (fetching, rendering, interactions).
            */
            class NotificationManager {
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

            /**
            * Initializes all event listeners for notification elements.
            */
            initEventListeners() {
            if (this.notificationBell) {
            this.notificationBell.addEventListener('click', this.toggleNotificationDropdown.bind(this));
            }
            if (this.markAllReadButton) {
            this.markAllReadButton.addEventListener('click', this.markAllNotificationsAsRead.bind(this));
            }
            document.addEventListener('click', this.closeDropdownOnClickOutside.bind(this));
            }

            /**
            * Toggles the visibility of the notification dropdown and fetches notifications if opening.
            * @param {Event} event - The click event.
            */
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

            /**
            * Fetches and renders notifications.
            * @returns {Promise<Array>} A promise that resolves with the fetched notifications.
                */
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

                /**
                * Updates the notification UI with the given notifications.
                * @param {Array} notifications - An array of notification objects.
                */
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

                /**
                * Creates a single notification HTML element.
                * @param {object} notification - The notification data.
                * @returns {HTMLElement} The created notification div element.
                */
                createNotificationItem(notification) {
                const notificationItem = document.createElement('div');
                notificationItem.classList.add('flex', 'items-start', 'px-4', 'py-3', 'hover:bg-secondary-50',
                'transition-colors', 'duration-150', 'border-b', 'border-secondary-100', 'last:border-b-0', 'group',
                notification.read ? 'text-secondary-500' : 'text-secondary-800', notification.read ? '' :
                'font-medium');
                notificationItem.setAttribute('data-notification-id', notification.id);

                let iconSvg = `<svg
                    class="h-5 w-5 flex-shrink-0 mt-1 mr-3 ${notification.read ? 'text-secondary-400' : 'text-primary-500'}"
                    fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>`;
                if (notification.verb && notification.verb.includes("Time Off")) {
                iconSvg = `<svg
                    class="h-5 w-5 flex-shrink-0 mt-1 mr-3 ${notification.read ? 'text-secondary-400' : 'text-green-500'}"
                    fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>`;
                }

                notificationItem.innerHTML = `
                ${iconSvg}
                <div class="flex-grow">
                    <p class="text-sm leading-snug">${notification.description}</p>
                    <p class="text-xs text-secondary-500 mt-1">${Utils.formatTimeAgo(notification.timestamp)}</p>
                    ${notification.content_object_display ? `<p class="text-xs text-secondary-600 mt-1 italic">
                        ${notification.content_object_display}</p>` : ''}
                    ${notification.action_url ? `<a href="${notification.action_url}"
                        class="text-xs text-primary-500 hover:underline mt-1 block">View Details</a>` : ''}
                </div>
                <div class="flex flex-col ml-2 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
                    <button class="mark-toggle-btn text-xs px-2 py-1 rounded hover:bg-primary-100 text-primary-600 mb-1"
                        data-id="${notification.id}" data-read="${notification.read}">
                        ${notification.read ? 'Mark as Unread' : 'Mark as Read'}
                    </button>
                    <button class="delete-notification-btn text-xs px-2 py-1 rounded hover:bg-red-100 text-danger-500"
                        data-id="${notification.id}">
                        Delete
                    </button>
                </div>
                `;
                return notificationItem;
                }

                /**
                * Attaches event listeners to the mark/delete buttons within notifications.
                */
                attachNotificationEventListeners() {
                document.querySelectorAll('.mark-toggle-btn').forEach(button => {
                button.onclick = this.handleMarkToggleClick.bind(this);
                });

                document.querySelectorAll('.delete-notification-btn').forEach(button => {
                button.onclick = this.handleDeleteNotificationClick.bind(this);
                });
                }

                /**
                * Handles click event for marking notifications as read/unread.
                * @param {Event} event - The click event.
                */
                async handleMarkToggleClick(event) {
                event.stopPropagation();
                const id = event.currentTarget.dataset.id;
                const isCurrentlyRead = event.currentTarget.dataset.read === 'true';
                const endpoint = isCurrentlyRead ? `/api/v1/notifications/${id}/mark_as_unread/` :
                `/api/v1/notifications/${id}/mark_as_read/`;
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

                /**
                * Handles click event for deleting notifications.
                * @param {Event} event - The click event.
                */
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
                if (response.status === 204) {
                console.log(`Notification ${id} deleted.`);
                await this.fetchNotifications();
                } else {
                throw new Error(`Failed to delete notification, status: ${response.status}`);
                }
                } catch (error) {
                console.error('Error deleting notification:', error);
                }
                }

                /**
                * Marks all notifications as read.
                */
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

                /**
                * Closes the notification dropdown if a click occurs outside of it.
                * @param {Event} event - The click event.
                */
                closeDropdownOnClickOutside(event) {
                if (this.notificationDropdown && this.notificationBell &&
                !this.notificationDropdown.contains(event.target) &&
                !this.notificationBell.contains(event.target)) {
                this.notificationDropdown.classList.add('hidden');
                }
                }

                /**
                * Initiates periodic fetching of notifications.
                * @param {number} intervalMinutes - The interval in minutes to refresh notifications.
                */
                startPeriodicRefresh(intervalMinutes = 5) {
                setInterval(() => this.fetchNotifications(), intervalMinutes * 60 * 1000);
                }
                }

                /**
                * Main application initialization.
                */
                document.addEventListener('DOMContentLoaded', () => {
                // Instantiate managers
                const sidebarManager = new SidebarManager();
                const userDataManager = new UserDataManager();
                const timeOffLinkManager = new TimeOffLinkManager();
                const notificationManager = new NotificationManager();

                // Make toggleSidebar globally accessible if needed for inline onclick attributes
                window.toggleSidebar = sidebarManager.toggleSidebar.bind(sidebarManager);
                window.toggleSubmenu = sidebarManager.toggleSubmenu.bind(sidebarManager);

                // Initial data fetching and UI setup
                userDataManager.getUserData();
                timeOffLinkManager.hideTimeOffLink();
                sidebarManager.initSidebarLinks();
                notificationManager.fetchNotifications(); // Initial fetch
                // notificationManager.startPeriodicRefresh(5); // Uncomment to enable periodic refresh

                // Animate elements on load
                document.querySelectorAll('.animate-on-load').forEach(el => {
                el.style.animationName = 'fadeInUp';
                el.style.animationFillMode = 'forwards';
                el.style.animationDuration = '0.5s';
                el.style.animationDelay = '0.2s';
                });
                }); document.addEventListener('DOMContentLoaded', function() {
                const userMenuButton = document.getElementById('user-menu-button');
                const userMenuDropdown = document.getElementById('user-menu-dropdown');
                const userMenuArrow = document.getElementById('user-menu-arrow');

                function toggleUserMenu() {
                const isExpanded = userMenuButton.getAttribute('aria-expanded') === 'true';
                userMenuButton.setAttribute('aria-expanded', !isExpanded);
                userMenuDropdown.classList.toggle('hidden');
                userMenuArrow.classList.toggle('rotate-180'); // Rotate arrow for visual feedback
                }

                userMenuButton.addEventListener('click', function(event) {
                event.stopPropagation(); // Prevent click from bubbling up to document
                toggleUserMenu();
                });

                // Close dropdown if clicked outside
                document.addEventListener('click', function(event) {
                if (!userMenuDropdown.contains(event.target) && !userMenuButton.contains(event.target)) {
                if (!userMenuDropdown.classList.contains('hidden')) {
                toggleUserMenu();
                }
                }
                });

                // Existing sidebar toggle functions (ensure these are present or re-add them)
                window.toggleSidebar = function() {
                document.getElementById('sidebar').classList.toggle('-translate-x-full');
                document.getElementById('sidebar-backdrop').classList.toggle('hidden');
                }

                window.closeSidebar = function() {
                document.getElementById('sidebar').classList.add('-translate-x-full');
                document.getElementById('sidebar-backdrop').classList.add('hidden');
                }

                // Existing submenu toggle function (ensure this is present or re-add it)
                window.toggleSubmenu = function(submenuId) {
                const submenu = document.getElementById(submenuId);
                const arrow = document.getElementById(submenuId + '-arrow');
                const isExpanded = submenu.classList.contains('hidden');

                submenu.classList.toggle('hidden');
                arrow.classList.toggle('rotate-90');
                // Update aria-expanded for accessibility
                document.querySelector(`[aria-controls="${submenuId}"]`).setAttribute('aria-expanded', isExpanded);
                }

                // Placeholder for user name. You'd typically populate this dynamically.
                document.getElementById('user-name').textContent = "Admin User"; // Replace with actual user name
                document.getElementById('dropdown-user-name').textContent = "Admin User"; // Replace with actual user
                name
                });
