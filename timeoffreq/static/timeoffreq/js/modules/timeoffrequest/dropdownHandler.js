import { ApiService } from './apiService.js';
import { NotificationService } from './notificationService.js';

export const DropdownHandler = (function() {
    async function fetchAndPopulateDropdown(url, selectElement, defaultOptionText, valueKey, labelKey) {
        try {
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const response = await ApiService.smartFetch(url, {
                method: 'GET',
                credentials: 'include',
                headers: { 'X-CSRFToken': csrftoken, 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    NotificationService.showNotification('Your session has expired. Please log in again.', 'error');
                    return;
                }
                const errorData = await response.json();
                throw new Error(`Failed to load ${defaultOptionText}. Status: ${response.status}. Error: ${JSON.stringify(errorData)}`);
            }

            const data = await response.json();
            selectElement.innerHTML = `<option value="" disabled selected>${defaultOptionText}</option>`;
            data.forEach(item => {
                const option = document.createElement('option');
                option.value = item[valueKey];
                option.textContent = item[labelKey];
                selectElement.appendChild(option);
            });
            
        } catch (error) {
            selectElement.innerHTML = `<option value="" disabled selected>Error loading ${defaultOptionText}</option>`;
            NotificationService.showNotification(`Error loading ${defaultOptionText}. Please try refreshing the page.`, 'error');
            console.error('[DropdownHandler] Error:', error);
        }
    }
    return { fetchAndPopulateDropdown };
})();