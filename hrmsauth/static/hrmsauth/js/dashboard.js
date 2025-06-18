// --- Sidebar and UI Toggles ---

/**
 * Toggles the visibility of the sidebar and its backdrop on mobile.
 */
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('-translate-x-full');
    document.getElementById('sidebar-backdrop').classList.toggle('hidden');
}

/**
 * Toggles the visibility of a submenu and rotates its associated arrow.
 * @param {string} id - The ID of the submenu to toggle.
 */
function toggleSubmenu(id) {
    document.getElementById(id).classList.toggle('hidden');
    const arrow = document.getElementById(id + '-arrow');
    if (arrow) { // Ensure arrow exists before toggling
        arrow.classList.toggle('rotate-90');
    }
}

/**
 * Closes the sidebar and hides its backdrop.
 */
function closeSidebar() {
    document.getElementById('sidebar').classList.add('-translate-x-full');
    document.getElementById('sidebar-backdrop').classList.add('hidden');
}

// --- Data Fetching and UI Updates ---

/**
 * Fetches user data and updates the UI accordingly, including
 * user name, avatar, and visibility of admin tools.
 */
async function getUserData() {
    const userNameElement = document.querySelector('.user-name');
    const userAvatarElement = document.getElementById('user-avatar');
    const onShiftReportLink = document.getElementById('onShiftReportLink');
    const timeOffManagementLink = document.getElementById('timeOffManagementLink');
    const adminToolDiv = document.getElementById('admintoolsButton');

    // Apply skeleton loading styles immediately
    userNameElement?.classList.add('skeleton-loading', 'w-24', 'h-5');
    userAvatarElement?.classList.add('skeleton-loading');
    if (userAvatarElement) userAvatarElement.textContent = '';
    if (userNameElement) userNameElement.textContent = '';

    try {
        const response = await fetch('/api/user_info/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            const data = await response.json();

            if (userNameElement) userNameElement.textContent = data.username || 'User';
            if (userAvatarElement) userAvatarElement.textContent = data.username ? data.username.charAt(0).toUpperCase() : 'U';

            const isSuperuser = data.hasOwnProperty('is_superuser') ? data.is_superuser : false;

            const adminElements = [onShiftReportLink, timeOffManagementLink, adminToolDiv];

            adminElements.forEach(el => {
                if (el) { // Check if element exists before manipulating
                    if (isSuperuser) {
                        el.classList.remove('hidden');
                        el.removeAttribute('aria-hidden');
                        if (el === adminToolDiv) el.style.display = ''; // Reset display for main admin tools div
                    } else {
                        el.classList.add('hidden');
                        el.setAttribute('aria-hidden', 'true');
                        if (el === adminToolDiv) el.style.display = 'none'; // Explicitly hide main admin tools div
                    }
                }
            });

        } else {
            console.error('Failed to fetch user data. Status:', response.status);
            if (userNameElement) userNameElement.textContent = 'Guest';
            if (userAvatarElement) userAvatarElement.textContent = '?';
            // Hide admin elements on fetch failure
            [onShiftReportLink, timeOffManagementLink, adminToolDiv].forEach(el => {
                if (el) {
                    el.classList.add('hidden');
                    el.setAttribute('aria-hidden', 'true');
                }
            });
        }
    } catch (error) {
        console.error('Error fetching user data:', error);
        if (userNameElement) userNameElement.textContent = 'Guest';
        if (userAvatarElement) userAvatarElement.textContent = '?';
        // Hide admin elements on general error
        [onShiftReportLink, timeOffManagementLink, adminToolDiv].forEach(el => {
            if (el) {
                el.classList.add('hidden');
                el.setAttribute('aria-hidden', 'true');
            }
        });
    } finally {
        // Always remove skeleton loading styles
        userNameElement?.classList.remove('skeleton-loading', 'w-24', 'h-5');
        userAvatarElement?.classList.remove('skeleton-loading');
    }
}

/**
 * Fetches department data to determine if the time off link should be hidden.
 */
async function hideTimeOffLink() {
    const timeOffLinkDiv = document.getElementById('timeoff');
    if (!timeOffLinkDiv) {
        console.warn('Time off link element not found. Skipping hideTimeOffLink.');
        return;
    }

    try {
        const response = await fetch('/api/department/', { // Added leading slash for absolute path
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            const data = await response.json();
            // Assuming data is an array and the first element contains is_time_off
            const timeoffFeatureEnabled = data[0]?.is_time_off;

            if (timeoffFeatureEnabled) {
                timeOffLinkDiv.classList.remove('hidden');
                timeOffLinkDiv.removeAttribute('aria-hidden');
            } else {
                timeOffLinkDiv.classList.add('hidden');
                timeOffLinkDiv.setAttribute('aria-hidden', 'true');
            }
        } else {
            console.error('Failed to fetch department data. Status:', response.status);
            // Default to visible or hidden if fetch fails based on your requirement.
            // For now, let's assume it should be visible if we can't determine otherwise.
            timeOffLinkDiv.classList.remove('hidden');
            timeOffLinkDiv.removeAttribute('aria-hidden');
        }
    } catch (error) {
        console.error('Error fetching department data:', error);
        // Default to visible if an error occurs
        timeOffLinkDiv.classList.remove('hidden');
        timeOffLinkDiv.removeAttribute('aria-hidden');
    }
}

// --- Initialization on DOM Content Load ---
document.addEventListener('DOMContentLoaded', () => {
    // Run all initial setup functions
    getUserData(); // Fetch and display user data
    hideTimeOffLink(); // Conditionally hide time off link

    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('#sidebar a');
    let exactMatchFound = false;
    let exactMatchLink = null;

    // First pass: Find an exact match for the current URL
    sidebarLinks.forEach(link => {
        const linkHref = link.getAttribute('href');
        if (linkHref && linkHref === currentPath) {
            exactMatchFound = true;
            exactMatchLink = link;
        }
    });

    // Second pass: Apply active styles based on exact or parent match
    sidebarLinks.forEach(link => {
        const linkHref = link.getAttribute('href');
        if (!linkHref) return; // Skip links without an href

        let isActive = false;

        if (exactMatchFound) {
            isActive = link === exactMatchLink;
        } else {
            // Check for parent match: currentPath starts with linkHref, but it's not the root and not an exact match
            isActive = currentPath.startsWith(linkHref) && linkHref !== '/' && currentPath !== linkHref; // Removed trailing slash check as it complicates things for exact match only
        }

        if (isActive) {
            // Apply active styles
            link.classList.add('bg-primary-700', 'border-l-4', 'border-primary-300', 'pl-3', 'bg-primary-900/50', 'shadow-inner-md');
            link.classList.remove('hover:bg-primary-700', 'px-4'); // Remove general hover for active state

            // If the active link is inside a submenu, ensure it's expanded
            const parentSubmenu = link.closest('.space-y-0\\.5'); // Targets the submenu container
            if (parentSubmenu) {
                parentSubmenu.classList.remove('hidden');

                const parentButton = parentSubmenu.previousElementSibling;
                if (parentButton && parentButton.tagName === 'BUTTON') {
                    const parentButtonIdMatch = parentButton.getAttribute('onclick')?.match(/'([^']*)'/);
                    if (parentButtonIdMatch) {
                        const parentButtonId = parentButtonIdMatch[1];
                        const arrow = document.getElementById(parentButtonId + '-arrow');
                        if (arrow) {
                            arrow.classList.add('rotate-90');
                        }
                        parentButton.classList.add('bg-primary-700', 'bg-primary-900/50', 'shadow-inner-md');
                        parentButton.setAttribute('aria-expanded', 'true');
                    }
                }
            }

            // For mobile, close sidebar when an active link is clicked
            if (window.innerWidth < 768) {
                link.addEventListener('click', closeSidebar);
            }
        }
    });

    // --- Animation Triggering ---
    const animatedElements = document.querySelectorAll('.animate-on-load');
    animatedElements.forEach(el => {
        // Setting animation properties directly in JS for better control
        el.style.animationName = 'fadeInUp';
        el.style.animationFillMode = 'forwards';
        el.style.animationDuration = '0.5s';
        el.style.animationDelay = '0.2s';
    });

    // --- Responsive Behavior ---
    window.addEventListener('resize', () => {
        // Close sidebar if screen size becomes tablet/desktop and sidebar is open
        if (window.innerWidth >= 768 && !document.getElementById('sidebar').classList.contains('-translate-x-full')) {
            closeSidebar();
        }
    });
});

async function getUserData() {
    const userNameElement = document.getElementsByClassName('user-name')[0];
    const userAvatarElement = document.getElementById('user-avatar');
    const onShiftReportLink = document.getElementById('onShiftReportLink');
    const timeOffManagementLink = document.getElementById('timeOffManagementLink');
    const adminToolDiv = document.getElementById('admintoolsButton');
    

    // Apply skeleton loading styles
    userNameElement.classList.add('skeleton-loading', 'w-24', 'h-5');
    userAvatarElement.classList.add('skeleton-loading');
    userAvatarElement.textContent = ''; // Clear content for skeleton
    userNameElement.textContent = ''; // Clear text during loading

    try {
        const response = await fetch('/api/user_info/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            const data = await response.json();

            userNameElement.textContent = data.username || 'User';
            userAvatarElement.textContent = data.username ? data.username.charAt(0).toUpperCase() : 'U';

            const isSuperuser = data.hasOwnProperty('is_superuser') ? data.is_superuser : false;

            // Define all admin-related links/divs
            const adminElements = [onShiftReportLink, timeOffManagementLink, adminToolDiv];

            if (isSuperuser) {
                // If it's a superuser, show all admin elements
                adminElements.forEach(el => {
                    if (el) { // Check if element exists
                        el.classList.remove('hidden');
                        el.removeAttribute('aria-hidden'); // Make it accessible
                    }
                });
                // Ensure the top-level adminToolsButton display is not overridden by previous inline style
                if(adminToolDiv) adminToolDiv.style.display = ''; // Reset to default (block from CSS)

            } else {
                // If not a superuser, ensure all admin elements remain hidden (or are hidden)
                // This block is actually less critical if they are already hidden by default in HTML
                // but it's good for robustness if initial state might vary or if data changes
                adminElements.forEach(el => {
                    if (el) { // Check if element exists
                        el.classList.add('hidden');
                        el.setAttribute('aria-hidden', 'true'); // Hide from screen readers
                    }
                });
                 // Explicitly set display:none for the main admin tools div if it was manually set to block previously
                if(adminToolDiv) adminToolDiv.style.display = 'none';
            }
        } else {
            console.error('Failed to fetch user data');
            userNameElement.textContent = 'Guest';
            userAvatarElement.textContent = '?';
            // Also ensure admin elements are hidden on fetch failure
            [onShiftReportLink, timeOffManagementLink, adminToolDiv].forEach(el => {
                if (el) {
                    el.classList.add('hidden');
                    el.setAttribute('aria-hidden', 'true');
                }
            });
        }
    } catch (error) {
        console.error('Error:', error);
        userNameElement.textContent = 'Guest';
        userAvatarElement.textContent = '?';
        // Also ensure admin elements are hidden on general error
        [onShiftReportLink, timeOffManagementLink, adminToolDiv].forEach(el => {
            if (el) {
                el.classList.add('hidden');
                el.setAttribute('aria-hidden', 'true');
            }
        });
    } finally {
        // Remove skeleton loading styles after fetch attempt
        userNameElement.classList.remove('skeleton-loading', 'w-24', 'h-5');
        userAvatarElement.classList.remove('skeleton-loading');
    }
}


async function hideTimeOffLink() {
    const timeOffLinkDiv = document.getElementById('timeoff');
    try{
        const response = await fetch('/api/department/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        // console.log('Response:', response);
        if (response.ok){
            const data = await response.json();
            // console.log('Data:', data);
            const timeoff = data[0].is_time_off;

            if (!timeoff) {
                timeOffLinkDiv.classList.add('hidden');
                timeOffLinkDiv.setAttribute('aria-hidden', 'true'); // Hide from screen readers
            } else {
                timeOffLinkDiv.classList.remove('hidden');
                timeOffLinkDiv.removeAttribute('aria-hidden'); // Make it accessible
            }


        }

    }catch (error) {
        console.error('Error:', error);
    }
}

// hrmsauth/static/hrmsauth/js/dashboard.js

document.addEventListener('DOMContentLoaded', function() {
    // --- Sidebar Toggle (existing) ---
    window.toggleSidebar = function() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebar-overlay');
        sidebar.classList.toggle('-translate-x-full');
        overlay.classList.toggle('hidden');
    };




    // --- Notification Functionality ---
    const notificationBell = document.getElementById('notification-bell');
    const notificationCount = document.getElementById('notification-count');
    const notificationDropdown = document.getElementById('notification-dropdown');
    const notificationList = document.getElementById('notification-list');
    const noNotificationsMessage = document.getElementById('no-notifications');
    const markAllReadButton = document.getElementById('mark-all-read');

    // Function to get CSRF token (adjust if your setup is different)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const CSRF_TOKEN = getCookie('csrftoken'); // Assumes CSRF token is in a cookie

    // Helper to format timestamp
    function formatTimeAgo(timestamp) {
        const now = new Date();
        const past = new Date(timestamp);
        const seconds = Math.round((now - past) / 1000);
        const minutes = Math.round(seconds / 60);
        const hours = Math.round(minutes / 60);
        const days = Math.round(hours / 24);
        const months = Math.round(days / 30.44); // Average days in a month
        const years = Math.round(days / 365.25); // Average days in a year

        if (seconds < 60) return `${seconds}s ago`;
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        if (days < 30) return `${days}d ago`;
        if (months < 12) return `${months} month${months > 1 ? 's' : ''} ago`;
        return `${years} year${years > 1 ? 's' : ''} ago`;
    }


    // Function to fetch and render notifications
    async function fetchNotifications() {
        try {
            const response = await fetch('/api/notifications/unread/'); // Your unread endpoint
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const notifications = await response.json();
            updateNotificationUI(notifications);
            return notifications; // Return for further processing if needed
        } catch (error) {
            console.error('Error fetching notifications:', error);
            notificationCount.textContent = '0';
            notificationList.innerHTML = '';
            noNotificationsMessage.classList.remove('hidden');
            markAllReadButton.disabled = true;
        }
    }

    // Function to update the notification UI
    function updateNotificationUI(notifications) {
        notificationCount.textContent = notifications.length;
        notificationList.innerHTML = ''; // Clear existing notifications

        if (notifications.length === 0) {
            noNotificationsMessage.classList.remove('hidden');
            markAllReadButton.disabled = true;
        } else {
            noNotificationsMessage.classList.add('hidden');
            markAllReadButton.disabled = false;
            notifications.forEach(notification => {
                const notificationItem = document.createElement('div');
                notificationItem.classList.add('flex', 'items-start', 'px-4', 'py-3', 'hover:bg-secondary-50', 'transition-colors', 'duration-150', 'border-b', 'border-secondary-100', 'last:border-b-0', 'group', notification.read ? 'text-secondary-500' : 'text-secondary-800', notification.read ? '' : 'font-medium');
                notificationItem.setAttribute('data-notification-id', notification.id);

                let iconSvg = `<svg class="h-5 w-5 flex-shrink-0 mt-1 mr-3 ${notification.read ? 'text-secondary-400' : 'text-primary-500'}" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`;
                if (notification.verb.includes("Time Off")) {
                    iconSvg = `<svg class="h-5 w-5 flex-shrink-0 mt-1 mr-3 ${notification.read ? 'text-secondary-400' : 'text-green-500'}" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>`;
                }
                // Add more icon conditions based on 'verb' or 'content_type_model'

                notificationItem.innerHTML = `
                    ${iconSvg}
                    <div class="flex-grow">
                        <p class="text-sm leading-snug">${notification.description}</p>
                        <p class="text-xs text-secondary-500 mt-1">${formatTimeAgo(notification.timestamp)}</p>
                        ${notification.content_object_display ? `<p class="text-xs text-secondary-600 mt-1 italic">${notification.content_object_display}</p>` : ''}
                        ${notification.action_url ? `<a href="${notification.action_url}" class="text-xs text-primary-500 hover:underline mt-1 block">View Details</a>` : ''}
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
                notificationList.appendChild(notificationItem);
            });
            attachNotificationEventListeners(); // Re-attach event listeners for newly added elements
        }
    }

    // Attach event listeners for mark/delete buttons
    function attachNotificationEventListeners() {
        document.querySelectorAll('.mark-toggle-btn').forEach(button => {
            button.onclick = async (event) => {
                event.stopPropagation(); // Prevent dropdown from closing if it's open
                const id = button.dataset.id;
                const isCurrentlyRead = button.dataset.read === 'true';
                const endpoint = isCurrentlyRead ? `/api/notifications/${id}/mark_as_unread/` : `/api/notifications/${id}/mark_as_read/`;
                try {
                    const response = await fetch(endpoint, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': CSRF_TOKEN,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({})
                    });
                    if (!response.ok) throw new Error('Failed to toggle read status');
                    console.log(`Notification ${id} status toggled.`);
                    fetchNotifications(); // Refresh notifications
                } catch (error) {
                    console.error('Error toggling notification status:', error);
                }
            };
        });

        document.querySelectorAll('.delete-notification-btn').forEach(button => {
            button.onclick = async (event) => {
                event.stopPropagation(); // Prevent dropdown from closing
                if (!confirm('Are you sure you want to delete this notification?')) {
                    return;
                }
                const id = button.dataset.id;
                try {
                    const response = await fetch(`/api/notifications/${id}/delete/`, { // Note: Your URL is /api/notifications/{pk}/delete/
                        method: 'DELETE',
                        headers: {
                            'X-CSRFToken': CSRF_TOKEN,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({})
                    });
                    if (response.status === 204) { // 204 No Content for successful deletion
                        console.log(`Notification ${id} deleted.`);
                        fetchNotifications(); // Refresh notifications
                    } else {
                        throw new Error(`Failed to delete notification, status: ${response.status}`);
                    }
                } catch (error) {
                    console.error('Error deleting notification:', error);
                }
            };
        });
    }


    // Toggle notification dropdown
    notificationBell.addEventListener('click', async (event) => {
        event.stopPropagation(); // Prevent click from bubbling to document and closing immediately
        const isHidden = notificationDropdown.classList.contains('hidden');
        if (isHidden) {
            notificationDropdown.classList.remove('hidden');
            await fetchNotifications(); // Fetch and display notifications when opening
        } else {
            notificationDropdown.classList.add('hidden');
        }
    });

    // Mark all as read functionality
    markAllReadButton.addEventListener('click', async () => {
        if (markAllReadButton.disabled) return;
        try {
            const response = await fetch('/api/notifications/mark_all_as_read/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': CSRF_TOKEN,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });
            if (!response.ok) throw new Error('Failed to mark all as read');
            const data = await response.json();
            console.log(data.message);
            fetchNotifications(); // Refresh notifications after marking all as read
        } catch (error) {
            console.error('Error marking all notifications as read:', error);
        }
    });

    // Close dropdown if clicked outside
    document.addEventListener('click', (event) => {
        if (!notificationDropdown.contains(event.target) && !notificationBell.contains(event.target)) {
            notificationDropdown.classList.add('hidden');
        }
    });

    // Initial fetch of unread count when the page loads
    fetchNotifications();

    // Optional: Periodically refresh notifications (e.g., every 5 minutes)
    // setInterval(fetchNotifications, 5 * 60 * 1000);
});
