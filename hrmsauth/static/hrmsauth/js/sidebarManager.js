/**
 * Manages sidebar visibility and submenu toggles.
 */
export class SidebarManager {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        this.sidebarBackdrop = document.getElementById('sidebar-backdrop');
        this.sidebarOverlay = document.getElementById('sidebar-overlay');
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
        if (this.sidebarOverlay) {
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
            const isExpanded = !submenu.classList.contains('hidden');
            document.querySelector(`[aria-controls="${id}"]`)?.setAttribute('aria-expanded', isExpanded);
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
                link.classList.add('bg-primary-700', 'border-l-4', 'border-primary-300', 'pl-3', 'bg-primary-900/50', 'shadow-inner-md');
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
            }

            if (window.innerWidth < 768) {
                link.addEventListener('click', this.closeSidebar.bind(this));
            }
        });

        window.addEventListener('resize', () => {
            if (window.innerWidth >= 768 && this.sidebar && !this.sidebar.classList.contains('-translate-x-full')) {
                this.closeSidebar();
            }
        });
    }
}