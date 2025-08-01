import { SidebarManager } from './sidebarManager.js';
import { UserDataManager } from './userDataManager.js';
import { TimeOffLinkManager } from './timeOffLinkManager.js';
import { NotificationManager } from './notificationManager.js';

/**
 * Main application initialization.
 */
document.addEventListener('DOMContentLoaded', () => {
    // Instantiate managers
    const sidebarManager = new SidebarManager();
    const userDataManager = new UserDataManager();
    const timeOffLinkManager = new TimeOffLinkManager();
    const notificationManager = new NotificationManager();

    // Make toggle functions globally accessible for inline onclick attributes
    window.toggleSidebar = sidebarManager.toggleSidebar.bind(sidebarManager);
    window.toggleSubmenu = sidebarManager.toggleSubmenu.bind(sidebarManager);
    window.closeSidebar = sidebarManager.closeSidebar.bind(sidebarManager);

    // Initial data fetching and UI setup
    userDataManager.getUserData();
    timeOffLinkManager.hideTimeOffLink();
    sidebarManager.initSidebarLinks();
    notificationManager.fetchNotifications();
    // notificationManager.startPeriodicRefresh(5); // Uncomment to enable periodic refresh

    // Animate elements on load
    document.querySelectorAll('.animate-on-load').forEach(el => {
        el.style.animationName = 'fadeInUp';
        el.style.animationFillMode = 'forwards';
        el.style.animationDuration = '0.5s';
        el.style.animationDelay = '0.2s';
    });

    // User menu functionality
    const userMenuButton = document.getElementById('user-menu-button');
    const userMenuDropdown = document.getElementById('user-menu-dropdown');
    const userMenuArrow = document.getElementById('user-menu-arrow');

    function toggleUserMenu() {
        const isExpanded = userMenuButton.getAttribute('aria-expanded') === 'true';
        userMenuButton.setAttribute('aria-expanded', !isExpanded);
        userMenuDropdown.classList.toggle('hidden');
        userMenuArrow.classList.toggle('rotate-180');
    }

    if (userMenuButton) {
        userMenuButton.addEventListener('click', function(event) {
            event.stopPropagation();
            toggleUserMenu();
        });
    }

    document.addEventListener('click', function(event) {
        if (!userMenuDropdown.contains(event.target) && !userMenuButton.contains(event.target)) {
            if (!userMenuDropdown.classList.contains('hidden')) {
                toggleUserMenu();
            }
        }
    });

    // Placeholder for user name
    document.getElementById('user-name').textContent = "Admin User";
    document.getElementById('dropdown-user-name').textContent = "Admin User";
});