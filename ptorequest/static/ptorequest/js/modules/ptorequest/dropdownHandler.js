// static/ptorequest/js/modules/ptorequest/dropdownHandler.js

import { smartFetch } from './apiService.js';
import { showNotification } from './notificationService.js';

/**
 * Fetches data from a specified API endpoint and uses it to populate
 * a given HTML <select> element.
 * @param {string} url The API URL to fetch data from.
 * @param {HTMLSelectElement} selectElement The HTML <select> element to populate.
 * @param {string} defaultOptionText The text for the default disabled/selected option.
 * @param {string} valueKey The key from the API response object to use as the option's value.
 * @param {string} labelKey The key from the API response object to use as the option's text.
 */
export async function fetchAndPopulateDropdown(url, selectElement, defaultOptionText, valueKey, labelKey) {
    console.log(`[DropdownHandler] Fetching data for dropdown: ${defaultOptionText} from ${url}`);
    try {
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const response = await smartFetch(url, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                console.error(`[DropdownHandler] Refresh token invalid for ${url}. Redirecting to login.`);
                window.location.href = '/auth/login/';
                return;
            }
            const errorData = await response.json();
            throw new Error(`Failed to load ${defaultOptionText}. Status: ${response.status}. Error: ${JSON.stringify(errorData)}`);
        }

        const data = await response.json();
        console.log(`[DropdownHandler] Data fetched for ${defaultOptionText}:`, data);

        selectElement.innerHTML = `<option value="" disabled selected>${defaultOptionText}</option>`;

        data.forEach(item => {
            const option = document.createElement('option');
            option.value = item[valueKey];
            option.textContent = item[labelKey];
            selectElement.appendChild(option);
        });
        console.log(`[DropdownHandler] Populated dropdown: ${defaultOptionText}`);
    } catch (error) {
        console.error(`[DropdownHandler] Error populating ${defaultOptionText} dropdown:`, error);
        selectElement.innerHTML = `<option value="" disabled selected>Error loading ${defaultOptionText}</option>`;
        showNotification(`Error loading ${defaultOptionText}. Please try refreshing the page.`, 'error');
    }
}