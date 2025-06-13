// Toggle sidebar on mobile
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('-translate-x-full');
    document.getElementById('sidebar-backdrop').classList.toggle('hidden');
}

// Toggle submenu visibility
function toggleSubmenu(id) {
    document.getElementById(id).classList.toggle('hidden');
    const arrow = document.getElementById(id + '-arrow');
    arrow.classList.toggle('rotate-90');
}

// Close sidebar when clicking on backdrop
function closeSidebar() {
    document.getElementById('sidebar').classList.add('-translate-x-full');
    document.getElementById('sidebar-backdrop').classList.add('hidden');
}

// Highlight active sidebar link based on current URL
// Highlight active sidebar link based on current URL and close sidebar on mobile click
document.addEventListener('DOMContentLoaded', () => {
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('#sidebar a');
    let exactMatchFound = false;
    let exactMatchLink = null;

    // First pass: Find an exact match
    sidebarLinks.forEach(link => {
        const linkHref = link.getAttribute('href');
        if (linkHref === currentPath) {
            exactMatchFound = true;
            exactMatchLink = link;
        }
    });

    // Second pass: Apply styles based on exact match or parent match
    sidebarLinks.forEach(link => {
        const linkHref = link.getAttribute('href');
        let isActive = false;

        if (exactMatchFound) {
            // If an exact match exists, only highlight the exact match
            isActive = link === exactMatchLink;
        } else {
            // No exact match; check for parent match
            // A link is a parent if currentPath starts with its href, it's not the root, and it's not the currentPath itself
            isActive = currentPath.startsWith(linkHref) && linkHref !== '/' && currentPath !== linkHref + '/';
        }

        if (isActive) {
            // Apply active styles to the current active link
            link.classList.add('bg-primary-700', 'border-l-4', 'border-primary-300', 'pl-3');
            link.classList.add('bg-primary-900/50', 'shadow-inner-md');
            link.classList.remove('hover:bg-primary-700', 'px-4'); // Remove general hover for active state

            // Check if this active link is a child within a submenu
            let parentSubmenu = link.closest('.space-y-0\\.5'); // This targets the submenu container
            if (parentSubmenu) {
                parentSubmenu.classList.remove('hidden'); // Ensure the submenu is visible

                // Find the button that controls this submenu
                let parentButton = parentSubmenu.previousElementSibling;
                if (parentButton && parentButton.tagName === 'BUTTON') {
                    // Extract the submenu ID from the onclick attribute to find the arrow
                    let parentButtonIdMatch = parentButton.getAttribute('onclick').match(/'([^']*)'/);
                    if (parentButtonIdMatch) {
                        let parentButtonId = parentButtonIdMatch[1];
                        const arrow = document.getElementById(parentButtonId + '-arrow');
                        if (arrow) {
                            arrow.classList.add('rotate-90'); // Rotate arrow to indicate open state
                        }
                        // Apply active styles to the parent button
                        parentButton.classList.add('bg-primary-700', 'bg-primary-900/50', 'shadow-inner-md');
                        parentButton.setAttribute('aria-expanded', 'true'); // Set aria-expanded
                    }
                }
            }

            // For mobile click: close sidebar
            if (window.innerWidth < 768) { // Assuming md breakpoint is 768px
                link.addEventListener('click', closeSidebar);
            }
        }
    });

    // Trigger entrance animations for main content elements
    const animatedElements = document.querySelectorAll('.animate-on-load');
    animatedElements.forEach(el => {
        el.style.animationName = 'fadeInUp'; // Ensure correct animation name
        el.style.animationFillMode = 'forwards'; // Keep the end state
        el.style.animationDuration = '0.5s'; // Example duration
        el.style.animationDelay = '0.2s'; // Example delay
    });

    // Add event listener for window resize
    window.addEventListener('resize', () => {
        // Close sidebar if screen size becomes md and sidebar is open
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

// Call the function on page load
window.onload = getUserData;