// static/timeclock/js/timeclock_main.js

import { smartFetch } from './modules/timeclock/apiService.js';
import { showNotification } from './modules/timeclock/notificationService.js';
import { getDomElements } from './modules/timeclock/domElements.js';
import { renderPayPeriodCard, renderClockInOutCard, renderTimeEntries } from './modules/timeclock/uiRenderer.js';
import { handleClockAction } from './modules/timeclock/clockActions.js';

document.addEventListener('DOMContentLoaded', async function() {
    const DOMElements = getDomElements();

    // Show initial loading spinners immediately for a better UX
    const loadingSpinnerHtml = `
        <div class="flex flex-col justify-center items-center h-24 text-gray-500">
            <svg class="animate-spin h-8 w-8 text-blue-500 mb-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Loading data...</span>
        </div>
    `;

    DOMElements.payPeriodCard.innerHTML = loadingSpinnerHtml;
    DOMElements.clockInOutCard.innerHTML = loadingSpinnerHtml;
    DOMElements.timeEntriesSection.innerHTML = loadingSpinnerHtml;

    const csrftoken = DOMElements.csrftokenInput.value;

    // Initial data load when the page loads
    await fetchAndRenderClockData(DOMElements, csrftoken);
});

/**
 * Main function to fetch all clock-related data and render the UI.
 * @param {Object} DOMElements - Object containing references to all necessary DOM elements.
 * @param {string} csrftoken - The CSRF token.
 */
async function fetchAndRenderClockData(DOMElements, csrftoken) {
    try {
        const response = await smartFetch('/clock/user-clock-data/', {
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });

        if (!response.ok) {
            if (response.status === 401) {
                showNotification('Your session has expired. Redirecting to login.', 'error');
                setTimeout(() => window.location.href = '/auth/login/', 1500);
            } else {
                const errorData = await response.json();
                showNotification(`Failed to load clock data: ${errorData.detail || errorData.message || 'Unknown error.'}`, 'error');
                // Display specific error messages in cards if data loading fails
                DOMElements.payPeriodCard.innerHTML = `<div class="text-center text-red-600 p-4">Failed to load pay period data.</div>`;
                DOMElements.clockInOutCard.innerHTML = `<div class="text-center text-red-600 p-4">Failed to load clock status.</div>`;
                DOMElements.timeEntriesSection.innerHTML = `<div class="text-center text-red-600 p-4">Failed to load time entries.</div>`;
            }
            return;
        }

        const data = await response.json();
        console.log("API Response Data:", data);

        renderPayPeriodCard(DOMElements.payPeriodCard, data);
        renderClockInOutCard(DOMElements.clockInOutCard, data, () => handleClockAction(DOMElements, csrftoken, fetchAndRenderClockData));
        
        // Clear existing entries before rendering new ones to prevent duplicates on re-render
        // when fetchAndRenderClockData is called after a clock action.
        DOMElements.timeEntriesSection.innerHTML = ''; 

        renderTimeEntries(DOMElements.timeEntriesSection, data.week_1_entries, data.week_1_total_hours, 1);
        renderTimeEntries(DOMElements.timeEntriesSection, data.week_2_entries, data.week_2_total_hours, 2);

    } catch (error) {
        console.error("Network or parsing error during fetchAndRenderClockData:", error);
        showNotification('Network error while fetching data. Please check your connection.', 'error');
        // Display specific error messages in cards if network error occurs
        DOMElements.payPeriodCard.innerHTML = `<div class="text-center text-red-600 p-4">Network error loading pay period data.</div>`;
        DOMElements.clockInOutCard.innerHTML = `<div class="text-center text-red-600 p-4">Network error loading clock status.</div>`;
        DOMElements.timeEntriesSection.innerHTML = `<div class="text-center text-red-600 p-4">Network error loading time entries.</div>`;
    }
}