// static/timeclock/js/timeclock_main.js

import { smartFetch } from './modules/timeclock/apiService.js';
import { showNotification } from './modules/timeclock/notificationService.js';
import { getDomElements } from './modules/timeclock/domElements.js';
import { renderPayPeriodCard, renderClockInOutCard, renderTimeEntries } from './modules/timeclock/uiRenderer.js';
import { handleClockAction } from './modules/timeclock/clockActions.js';

document.addEventListener('DOMContentLoaded', async function() {
    const DOMElements = getDomElements();

    // Add robust checks for critical elements
    if (!DOMElements.payPeriodCard) { console.error("DOM Error: 'payPeriodCard' not found."); showNotification('UI Error: Pay Period section missing.', 'error'); return; }
    if (!DOMElements.clockInOutCard) { console.error("DOM Error: 'clockInOutCard' not found."); showNotification('UI Error: Clock In/Out section missing.', 'error'); return; }
    if (!DOMElements.timeEntriesSectionWeek1) { console.error("DOM Error: 'timeEntriesSectionWeek1' not found."); showNotification('UI Error: Week 1 entries section missing.', 'error'); return; }
    if (!DOMElements.timeEntriesSectionWeek2) { console.error("DOM Error: 'timeEntriesSectionWeek2' not found."); showNotification('UI Error: Week 2 entries section missing.', 'error'); return; }
    if (!DOMElements.csrftokenInput || !DOMElements.csrftokenInput.value) { console.error("DOM Error: CSRF token input not found or empty."); showNotification('Security Error: CSRF token missing.', 'error'); return; }


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
        const response = await smartFetch('/api/clock/user-clock-data/', {
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
                DOMElements.payPeriodCard.innerHTML = `<div class="flex flex-col items-center justify-center h-24 text-red-600 p-4"><svg class="w-10 h-10 mb-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2A9 9 0 111 12a9 9 0 0118 0z"></path></svg><span class="text-base font-medium">Failed to load pay period data.</span><p class="text-xs text-gray-500">Try refreshing.</p></div>`;
                DOMElements.clockInOutCard.innerHTML = `<div class="flex flex-col items-center justify-center h-40 text-red-600 p-4"><svg class="w-10 h-10 mb-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2A9 9 0 111 12a9 9 0 0118 0z"></path></svg><span class="text-base font-medium">Failed to load clock status.</span><p class="text-xs text-gray-500">Try refreshing.</p></div>`;
                // Clear and display error for both week sections
                DOMElements.timeEntriesSectionWeek1.innerHTML = `<div class="bg-white rounded-lg shadow-md overflow-hidden border border-secondary-200"><div class="flex flex-col items-center justify-center py-8 text-red-600 p-4"><svg class="w-10 h-10 mb-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2A9 9 0 111 12a9 9 0 0118 0z"></path></svg><span class="text-base font-medium">Failed to load Week 1 entries.</span><p class="text-xs text-gray-500">Try refreshing.</p></div></div>`;
                DOMElements.timeEntriesSectionWeek2.innerHTML = `<div class="bg-white rounded-lg shadow-md overflow-hidden border border-secondary-200"><div class="flex flex-col items-center justify-center py-8 text-red-600 p-4"><svg class="w-10 h-10 mb-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2A9 9 0 111 12a9 9 0 0118 0z"></path></svg><span class="text-base font-medium">Failed to load Week 2 entries.</span><p class="text-xs text-gray-500">Try refreshing.</p></div></div>`;
            }
            return;
        }

        const data = await response.json();
        
        renderPayPeriodCard(DOMElements.payPeriodCard, data);
        renderClockInOutCard(DOMElements.clockInOutCard, data, () => handleClockAction(DOMElements, csrftoken, fetchAndRenderClockData));
        
        // Clear existing entries for both weeks before rendering new ones
        DOMElements.timeEntriesSectionWeek1.innerHTML = ''; 
        DOMElements.timeEntriesSectionWeek2.innerHTML = ''; 

        renderTimeEntries(DOMElements.timeEntriesSectionWeek1, data.week_1_entries, data.week_1_total_hours, 1);
        renderTimeEntries(DOMElements.timeEntriesSectionWeek2, data.week_2_entries, data.week_2_total_hours, 2);

    } catch (error) {
        console.error("Network or parsing error during fetchAndRenderClockData:", error);
        showNotification('Network error while fetching data. Please check your connection.', 'error');
        // Display specific error messages in cards if network error occurs
        DOMElements.payPeriodCard.innerHTML = `<div class="flex flex-col items-center justify-center h-24 text-red-600 p-4"><svg class="w-10 h-10 mb-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2A9 9 0 111 12a9 9 0 0118 0z"></path></svg><span class="text-base font-medium">Network error loading pay period data.</span><p class="text-xs text-gray-500">Check connection and try again.</p></div>`;
        DOMElements.clockInOutCard.innerHTML = `<div class="flex flex-col items-center justify-center h-40 text-red-600 p-4"><svg class="w-10 h-10 mb-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2A9 9 0 111 12a9 9 0 0118 0z"></path></svg><span class="text-base font-medium">Network error loading clock status.</span><p class="text-xs text-gray-500">Check connection and try again.</p></div>`;
        DOMElements.timeEntriesSectionWeek1.innerHTML = `<div class="bg-white rounded-lg shadow-md overflow-hidden border border-secondary-200"><div class="flex flex-col items-center justify-center py-8 text-red-600 p-4"><svg class="w-10 h-10 mb-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2A9 9 0 111 12a9 9 0 0118 0z"></path></svg><span class="text-base font-medium">Network error loading Week 1 entries.</span><p class="text-xs text-gray-500">Check connection and try again.</p></div></div>`;
        DOMElements.timeEntriesSectionWeek2.innerHTML = `<div class="bg-white rounded-lg shadow-md overflow-hidden border border-secondary-200"><div class="flex flex-col items-center justify-center py-8 text-red-600 p-4"><svg class="w-10 h-10 mb-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2A9 9 0 111 12a9 9 0 0118 0z"></path></svg><span class="text-base font-medium">Network error loading Week 2 entries.</span><p class="text-xs text-gray-500">Check connection and try again.</p></div></div>`;
    }
}