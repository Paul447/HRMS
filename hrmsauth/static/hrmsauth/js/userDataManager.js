import { Utils } from './utils.js';

/**
 * Manages user data fetching and UI updates related to user information and admin tools.
 */
export class UserDataManager {
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
        ].filter(Boolean);
    }

    /**
     * Fetches user data and updates the UI.
     */
    async getUserData() {
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
                    if (el === this.adminToolDiv) el.style.display = '';
                } else {
                    el.classList.add('hidden');
                    el.setAttribute('aria-hidden', 'true');
                    if (el === this.adminToolDiv) el.style.display = 'none';
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
        this.updateAdminToolsVisibility(false);
    }
}