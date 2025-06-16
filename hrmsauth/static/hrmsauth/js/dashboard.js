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
