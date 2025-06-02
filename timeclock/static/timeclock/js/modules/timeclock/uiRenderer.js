// static/timeclock/js/modules/timeclock/uiRenderer.js

import { formatDate, formatOnlyTime, formatDuration, formatPayPeriodDate } from './utils.js';

/**
 * Renders the Pay Period Card.
 * @param {HTMLElement} payPeriodCardElement - The DOM element for the pay period card.
 * @param {Object} data - The clock data containing pay period and week boundaries.
 */
export function renderPayPeriodCard(payPeriodCardElement, data) {
    if (!payPeriodCardElement) {
        console.error("Element for pay period card not found.");
        return;
    }

    console.log("[uiRenderer] Rendering Pay Period Card with data:", data);

    // Handle case where no active pay period is found
    if (!data || !data.pay_period) {
        payPeriodCardElement.innerHTML = `
            <div class="flex flex-col items-center justify-center text-red-600 p-4">
                <svg class="w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                </svg>
                <span class="text-lg font-medium">No active pay period found.</span>
                <p class="text-sm text-gray-500">Please contact your administrator for assistance.</p>
            </div>
        `;
        return;
    }

    const pp = data.pay_period;
    const weekBoundaries = data.week_boundaries;

    // Ensure week_boundaries exist and are valid before formatting
    const week1Start = weekBoundaries ? formatDate(weekBoundaries.week_1_start) : 'N/A';
    const week1End = weekBoundaries ? formatDate(weekBoundaries.week_1_end) : 'N/A';
    const week2Start = weekBoundaries ? formatDate(weekBoundaries.week_2_start) : 'N/A';
    const week2End = weekBoundaries ? formatDate(weekBoundaries.week_2_end) : 'N/A';

    const payPeriodStartDisplay = formatPayPeriodDate(pp.start_date);
    const payPeriodEndDisplay = formatPayPeriodDate(pp.end_date);

    payPeriodCardElement.innerHTML = `
        <div class="flex justify-between items-start mb-2">
            <h2 class="text-xl font-semibold text-blue-800">Current Pay Period</h2>
            <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 animate-pulse-slight">
                <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 8 8">
                    <circle cx="4" cy="4" r="3" />
                </svg>
                Active
            </span>
        </div>
        <div class="space-y-3">
            <div class="flex flex-wrap items-center gap-2">
                <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                <span class="text-gray-700 font-medium">${payPeriodStartDisplay} - ${payPeriodEndDisplay}</span>
            </div>
            <div class="flex items-center gap-2 bg-blue-100/50 border border-blue-200 rounded-full px-3 py-1.5 w-fit">
                <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span class="text-sm font-medium text-blue-800">Week ${data.week_number || 'N/A'}: ${data.week_number === 1 ? `${week1Start} - ${week1End}` : `${week2Start} - ${week2End}`}</span>
            </div>
        </div>
    `;
}

/**
 * Renders the Clock In/Out Card.
 * @param {HTMLElement} clockInOutCardElement - The DOM element for the clock in/out card.
 * @param {Object} data - The clock data containing current status and active entry.
 * @param {Function} clockActionHandler - Callback function for the clock button click.
 */
export function renderClockInOutCard(clockInOutCardElement, data, clockActionHandler) {
    if (!clockInOutCardElement) {
        console.error("Element for clock in/out card not found.");
        return;
    }

    console.log("[uiRenderer] Rendering Clock In/Out Card with data:", data);

    let buttonHtml = '';
    let statusHtml = '';

    // Clear any existing interval to prevent multiple running intervals
    if (window.durationInterval) {
        clearInterval(window.durationInterval);
        window.durationInterval = null;
    }

    if (data.current_status === "Clocked In" && data.active_clock_entry) {
        const clockInTime = formatOnlyTime(data.active_clock_entry.clock_in_time);
        let initialDuration = '0:00';
        if (data.active_clock_entry.clock_in_time) {
            initialDuration = formatDuration(data.active_clock_entry.clock_in_time, new Date().toISOString());
        }

        statusHtml = `
            <div class="inline-flex items-center px-4 py-2 rounded-full bg-green-100 text-green-800 mb-3 animate-pulse-slight">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span class="font-medium">Clocked In</span>
            </div>
            <p class="text-gray-600 mb-1">Since: <span class="font-medium text-gray-800">${formatDate(data.active_clock_entry.clock_in_time)} ${clockInTime}</span></p>
            <p class="text-sm text-gray-500">Duration: <span id="currentDuration" class="font-semibold text-gray-800">${initialDuration}</span></p>
        `;
        buttonHtml = `
            <button id="clockButton" class="w-full max-w-xs mx-auto flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-200 shadow-md">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Clock Out
            </button>
        `;

        // Start interval for duration updates
        window.durationInterval = setInterval(() => {
            if (data.active_clock_entry && data.active_clock_entry.clock_in_time) {
                const updatedDuration = formatDuration(data.active_clock_entry.clock_in_time, new Date().toISOString());
                const durationElement = document.getElementById('currentDuration');
                if (durationElement) {
                    durationElement.textContent = updatedDuration;
                } else {
                    // If element is not found, stop interval to prevent errors
                    clearInterval(window.durationInterval);
                    window.durationInterval = null;
                    console.warn("[uiRenderer] currentDuration element not found, clearing duration interval.");
                }
            } else {
                 // If active_clock_entry becomes null/undefined, stop interval
                clearInterval(window.durationInterval);
                window.durationInterval = null;
                console.warn("[uiRenderer] active_clock_entry missing, clearing duration interval.");
            }
        }, 1000);

    } else {
        // Clocked Out State
        if (window.durationInterval) clearInterval(window.durationInterval); // Ensure interval is cleared if not clocked in
        statusHtml = `
            <div class="inline-flex items-center px-4 py-2 rounded-full bg-gray-100 text-gray-800 mb-3">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span class="font-medium">Clocked Out</span>
            </div>
            <p class="text-gray-600">Ready to start your workday?</p>
        `;
        buttonHtml = `
            <button id="clockButton" class="w-full max-w-xs mx-auto flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200 shadow-md">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Clock In
            </button>
        `;
    }

    clockInOutCardElement.innerHTML = `
        <div class="text-center">
            <div class="mb-5">
                ${statusHtml}
            </div>
            ${buttonHtml}
        </div>
    `;

    const clockButton = clockInOutCardElement.querySelector('#clockButton');
    if (clockButton) {
        clockButton.addEventListener('click', clockActionHandler);
    } else {
        console.error("[uiRenderer] Clock button element not found after rendering clockInOutCard.");
    }
}

/**
 * Renders time entries for a given week.
 * @param {HTMLElement} timeEntriesSectionElement - The DOM element for the time entries section.
 * @param {Array} entries - Array of time entry objects for the week.
 * @param {number} totalHours - Total hours for the week.
 * @param {number} weekNum - The week number (1 or 2).
 */
export function renderTimeEntries(timeEntriesSectionElement, entries, totalHours, weekNum) {
    if (!timeEntriesSectionElement) {
        console.error("Element for time entries section not found!");
        return;
    }

    console.log(`[uiRenderer] Rendering Week ${weekNum} entries:`, entries, `Total: ${totalHours}`);

    // No need to clear existing sections here, as timeclock_main.js now clears the whole section
    // before calling renderTimeEntries for both weeks.
    // If you were rendering individual week sections without clearing the parent, then you'd need this.
    // const existingWeekSection = timeEntriesSectionElement.querySelector(`#week${weekNum}Section`);
    // if (existingWeekSection) {
    //     existingWeekSection.remove();
    // }

    if (!entries || entries.length === 0) {
        const noEntriesHtml = `
            <div id="week${weekNum}Section" class="bg-white rounded-lg shadow overflow-hidden mb-4">
                <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
                    <h3 class="text-lg font-medium text-gray-900 flex items-center">
                        <span class="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center mr-2">${weekNum}</span>
                        Week ${weekNum} Summary
                    </h3>
                </div>
                <div class="p-6 text-center text-gray-500">
                    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                        <path vector-effect="non-scaling-stroke" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1H3z" />
                    </svg>
                    <h3 class="mt-2 text-sm font-medium text-gray-900">No time entries</h3>
                    <p class="mt-1 text-sm text-gray-500">
                        Looks like you haven't clocked any hours for Week ${weekNum} yet.
                    </p>
                </div>
            </div>
        `;
        timeEntriesSectionElement.insertAdjacentHTML('beforeend', noEntriesHtml);
        return;
    }

    const entriesHtml = entries.map(entry => {
        let displayClockOutTime;
        if (entry.clock_out_time) {
            displayClockOutTime = formatOnlyTime(entry.clock_out_time);
        } else {
            // Enhanced "Still In" display for active entry with a blinking dot
            displayClockOutTime = `
                <span class="inline-flex items-center">
                    <span class="relative flex h-2 w-2">
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                    </span>
                    <span class="ml-2">Still In</span>
                </span>
            `;
        }

        const displayHoursWorked = entry.hours_worked !== null ? parseFloat(entry.hours_worked).toFixed(2) :
            '0.00';

        return `
            <div class="px-6 py-4 hover:bg-gray-50 transition-colors duration-150 border-b border-gray-100 last:border-b-0">
                <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                    <div class="flex items-center mb-2 sm:mb-0">
                        <span class="text-sm font-medium text-gray-500 mr-3">${formatDate(entry.clock_in_time)}</span>
                        <span class="text-sm bg-blue-100 text-blue-800 px-2 py-0.5 rounded">${displayHoursWorked} hours</span>
                    </div>
                    <div class="text-sm text-gray-500">
                        <span class="font-medium">${formatOnlyTime(entry.clock_in_time)}</span> -
                        <span class="font-medium">${displayClockOutTime}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    const weekSectionHtml = `
        <div id="week${weekNum}Section" class="bg-white rounded-lg shadow overflow-hidden mb-8">
            <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
                <h3 class="text-lg font-medium text-gray-900 flex items-center">
                    <span class="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center mr-2">${weekNum}</span>
                    Week ${weekNum} Summary
                </h3>
            </div>
            <div class="divide-y divide-gray-200">
                ${entriesHtml}
            </div>
            <div class="px-6 py-3 bg-gray-50 text-right">
                <p class="text-sm font-medium text-gray-700">
                    Total: <span class="text-blue-600 font-bold">${parseFloat(totalHours).toFixed(2) || '0.00'} hours</span>
                </p>
            </div>
        </div>
    `;
    timeEntriesSectionElement.insertAdjacentHTML('beforeend', weekSectionHtml);
}