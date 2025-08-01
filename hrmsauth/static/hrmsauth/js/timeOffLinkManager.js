/**
 * Manages the visibility of the time off link based on department data.
 */
export class TimeOffLinkManager {
    constructor() {
        this.timeOffLinkDiv = document.getElementById('timeoff');
        this.managerTimeOffManagementLink = document.getElementById('managerToolsButton');
    }

    /**
     * Fetches user data to determine if time off links should be displayed.
     * @returns {Promise<void>}
     */
    async hideTimeOffLink() {
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
                },
                credentials: 'same-origin'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            const userData = Array.isArray(data) && data[0] ? data[0] : data;

            if (!userData || typeof userData.is_time_off === 'undefined' ||
                typeof userData.is_manager === 'undefined' ||
                typeof userData.is_superuser === 'undefined') {
                throw new Error('Invalid response data structure: missing required fields');
            }

            const { is_time_off: timeoffFeatureEnabled, is_manager: isManager, is_superuser: isSuperuser } = userData;

            this.updateElementVisibility(this.timeOffLinkDiv, timeoffFeatureEnabled === true);
            this.updateElementVisibility(this.managerTimeOffManagementLink, isManager === true || isSuperuser === true);
        } catch (error) {
            console.error('Error in hideTimeOffLink:', error);
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
            console.log(`Showing element: ${element.id}`);
        } else {
            element.classList.add('hidden');
            element.setAttribute('aria-hidden', 'true');
            console.log(`Hiding element: ${element.id}`);
        }
    }
}