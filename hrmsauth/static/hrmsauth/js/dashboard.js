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
document.addEventListener('DOMContentLoaded', () => {
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('#sidebar a');

    sidebarLinks.forEach(link => {
        // Handle direct links
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('bg-primary-700', 'border-l-4', 'border-primary-300', 'pl-3');
            // Add subtle backdrop blur for active state
            link.classList.add('bg-primary-900/50', 'shadow-inner-md'); // Darker semi-transparent background
            link.classList.remove('hover:bg-primary-700', 'px-4'); // Remove general hover for active
        }

        // Handle submenu links (e.g., if /users is active, parent menu should open)
        if (link.closest('.space-y-1') && link.getAttribute('href') === currentPath) {
            let parentSubmenu = link.closest('.space-y-1.hidden');
            if (parentSubmenu) {
                parentSubmenu.classList.remove('hidden');
                let parentButton = parentSubmenu.previousElementSibling;

                if (parentButton && parentButton.tagName === 'BUTTON' && parentButton.getAttribute(
                        'onclick')) {
                    let parentButtonIdMatch = parentButton.getAttribute('onclick').match(
                        /'([^']*)'/);
                    if (parentButtonIdMatch) {
                        let parentButtonId = parentButtonIdMatch[1];
                        const arrow = document.getElementById(parentButtonId + '-arrow');
                        if (arrow) {
                            arrow.classList.add('rotate-90');
                        }
                        // Add active styles to the parent button
                        parentButton.classList.add('bg-primary-700', 'bg-primary-900/50', 'shadow-inner-md');
                    }
                }
            }
        }
    });

    // Trigger entrance animations for main content elements
    const animatedElements = document.querySelectorAll('.animate-on-load');
    animatedElements.forEach(el => {
        el.style.animationName = 'fadeInUp';
    });
});

async function getUserData() {
    const userNameElement = document.getElementsByClassName('user-name')[0];
    const userAvatarElement = document.getElementById('user-avatar');
    const onShiftReportLink = document.getElementById('onShiftReportLink');

    // Apply skeleton loading styles
    userNameElement.classList.add('skeleton-loading', 'w-24', 'h-5');
    userAvatarElement.classList.add('skeleton-loading');
    userAvatarElement.textContent = ''; // Clear content for skeleton

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
            userAvatarElement.textContent = data.username ? data.username.charAt(0)
                .toUpperCase() : 'U';

            if (data.is_superuser) {
                onShiftReportLink.classList.remove('hidden');
            } else {
                onShiftReportLink.classList.add('hidden');
            }
        } else {
            console.error('Failed to fetch user data');
            userNameElement.textContent = 'Guest';
            userAvatarElement.textContent = '?';
        }
    } catch (error) {
        console.error('Error:', error);
        userNameElement.textContent = 'Guest';
        userAvatarElement.textContent = '?';
    } finally {
        // Remove skeleton loading styles after fetch attempt
        userNameElement.classList.remove('skeleton-loading', 'w-24', 'h-5');
        userAvatarElement.classList.remove('skeleton-loading');
    }
}

// Call the function on page load
window.onload = getUserData;