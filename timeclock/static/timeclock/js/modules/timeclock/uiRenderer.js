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

    // Handle case where no active pay period is found
    if (!data || !data.pay_period) {
        payPeriodCardElement.innerHTML = `
            <div class="flex flex-col items-center justify-center text-red-600 p-4">
                <svg class="w-10 h-10 mb-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                </svg>
                <span class="text-base font-medium text-secondary-800">No active pay period found.</span>
                <p class="text-xs text-secondary-500 mt-1">Contact your administrator for assistance.</p>
            </div>
        `;
        return;
    }

    const pp = data.pay_period;
    const weekBoundaries = data.week_boundaries;
    
    const week1Start = weekBoundaries ? (weekBoundaries.week_1_start) : 'N/A';
    const week1End = weekBoundaries ? (weekBoundaries.week_1_end) : 'N/A';
    const week2Start = weekBoundaries ? (weekBoundaries.week_2_start) : 'N/A';
    const week2End = weekBoundaries ? (weekBoundaries.week_2_end) : 'N/A';

    const payPeriodStartDisplay = formatPayPeriodDate(pp.start_date);
    const payPeriodEndDisplay = formatPayPeriodDate(pp.end_date);

    payPeriodCardElement.innerHTML = `
        <div class="flex justify-between items-start mb-3">
            <h2 class="text-xl font-semibold text-primary-800">Current Pay Period</h2>
            <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 animate-pulse-slight">
                <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 8 8">
                    <circle cx="4" cy="4" r="3" />
                </svg>
                Active
            </span>
        </div>
        <div class="space-y-3">
            <div class="flex flex-wrap items-center gap-2">
                <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                <span class="text-base text-secondary-700 font-medium">${payPeriodStartDisplay} – ${payPeriodEndDisplay}</span>
            </div>
            <div class="flex items-center gap-2 bg-primary-100/70 border border-primary-200 rounded-full px-3 py-1.5 w-fit text-sm shadow-inner-sm">
                <svg class="w-4 h-4 text-primary-700" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span class="font-semibold text-primary-800">Week ${data.week_number || 'N/A'}: ${data.week_number === 1 ? `${week1Start} – ${week1End}` : `${week2Start} – ${week2End}`}</span>
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

    let buttonHtml = '';
    let statusHtml = '';

    // Clear any existing interval to prevent multiple running intervals
    if (window.durationInterval) {
        clearInterval(window.durationInterval);
        window.durationInterval = null;
    }

    if (data.current_status === "Clocked In" && data.active_clock_entry) {
        const clockInTime = formatOnlyTime(data.active_clock_entry.clock_in_time);

        let initialDuration = '0.00';
        if (data.active_clock_entry.clock_in_time) {
            initialDuration = formatDuration(data.active_clock_entry.clock_in_time, new Date().toISOString());
        }

        statusHtml = `
            <div class="inline-flex items-center px-4 py-1.5 rounded-full bg-green-100 text-green-800 mb-3 text-sm font-medium animate-pulse-slight shadow-sm">
                <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                </svg>
                <span>You are Clocked In</span>
            </div>
            <p class="text-secondary-700 text-base mb-1">Since: <span class="font-semibold text-primary-700">${formatDate(data.active_clock_entry.clock_in_time)} at ${clockInTime}</span></p>
            <p class="text-secondary-600 text-xl font-bold mb-5">Duration: <span id="currentDuration" class="text-primary-600 text-2xl">${initialDuration} hours</span></p>
        `;
        buttonHtml = `
            <button id="clockButton" class="w-full max-w-xs mx-auto flex items-center justify-center px-6 py-3 border border-transparent text-lg font-bold rounded-md text-white bg-danger-600 hover:bg-danger-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-danger-500 transition-all duration-300 shadow-md transform hover:-translate-y-0.5">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
                </svg>
                Clock Out
            </button>
        `;

        window.durationInterval = setInterval(() => {
            if (data.active_clock_entry && data.active_clock_entry.clock_in_time) {
                const updatedDuration = formatDuration(data.active_clock_entry.clock_in_time, new Date().toISOString());
                const durationElement = document.getElementById('currentDuration');
                if (durationElement) {
                    durationElement.textContent = `${updatedDuration} hours`;
                } else {
                    clearInterval(window.durationInterval);
                    window.durationInterval = null;
                    console.warn("[uiRenderer] currentDuration element not found, clearing duration interval.");
                }
            } else {
                clearInterval(window.durationInterval);
                window.durationInterval = null;
                console.warn("[uiRenderer] active_clock_entry missing, clearing duration interval.");
            }
        }, 1000);

    } else {
        // Clocked Out State
        if (window.durationInterval) clearInterval(window.durationInterval);
        statusHtml = `
            <div class="inline-flex items-center px-4 py-1.5 rounded-full bg-secondary-100 text-secondary-800 mb-3 text-sm font-medium shadow-sm">
                <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2A9 9 0 111 12a9 9 0 0118 0z"></path>
                </svg>
                <span>You are Clocked Out</span>
            </div>
            <p class="text-secondary-600 text-base mb-5">Ready to start your workday?</p>
        `;
        buttonHtml = `
            <button id="clockButton" class="w-full max-w-xs mx-auto flex items-center justify-center px-6 py-3 border border-transparent text-lg font-bold rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all duration-300 shadow-md transform hover:-translate-y-0.5">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Clock In
            </button>
        `;
    }

    clockInOutCardElement.innerHTML = `
        <div class="text-center">
            ${statusHtml}
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
 * @param {HTMLElement} timeEntriesSectionElement - The DOM element for the time entries section (e.g., for week 1 or week 2).
 * @param {Array} entries - Array of time entry objects for the week.
 * @param {number} totalHours - Total hours for the week.
 * @param {number} weekNum - The week number (1 or 2).
 */
export function renderTimeEntries(timeEntriesSectionElement, entries, totalHours, weekNum) {
    if (!timeEntriesSectionElement) {
        console.error(`Element for Week ${weekNum} time entries section not found!`);
        return;
    }
    
    if (!entries || entries.length === 0) {
        const noEntriesHtml = `
            <div id="week${weekNum}Section" class="bg-white rounded-lg shadow-md overflow-hidden mb-6 border border-secondary-200 animate-fade-in-up animate-delay-${400 + (weekNum * 100)}">
                <div class="px-5 py-4 border-b border-secondary-200 bg-secondary-50">
                    <h3 class="text-lg font-medium text-secondary-800 flex items-center">
                        <span class="bg-primary-600 text-white rounded-full w-7 h-7 flex items-center justify-center mr-2 text-base font-bold">${weekNum}</span>
                        Week ${weekNum} Summary
                    </h3>
                </div>
                <div class="p-6 text-center text-secondary-500">
                    <svg class="mx-auto h-14 w-14 text-secondary-400 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                        <path vector-effect="non-scaling-stroke" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1H3z" />
                    </svg>
                    <h3 class="mt-2 text-base font-medium text-secondary-900">No entries yet</h3>
                    <p class="mt-1 text-sm text-secondary-600">
                        No hours clocked for Week ${weekNum}.
                    </p>
                </div>
            </div>
        `;
        timeEntriesSectionElement.insertAdjacentHTML('beforeend', noEntriesHtml);
        return;
    }

    const entriesHtml = entries.map(entry => {
        let displayClockOutTime;
        let clockOutClass = "text-secondary-700";
        if (entry.clock_out_time) {
            displayClockOutTime = formatOnlyTime(entry.clock_out_time);
        } else {
            displayClockOutTime = `
                <span class="inline-flex items-center text-green-600 font-semibold text-sm">
                    <span class="relative flex h-2.5 w-2.5 mr-1.5">
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
                    </span>
                    Still In
                </span>
            `;
            clockOutClass = ""; // Clear class for "Still In" for custom styling
        }

        const displayHoursWorked = entry.hours_worked !== null ? parseFloat(entry.hours_worked).toFixed(2) :
            '0.00';

        return `
            <div class="px-5 py-4 hover:bg-secondary-50 transition-colors duration-200 border-b border-secondary-100 last:border-b-0">
                <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1.5">
                    <div class="flex items-center text-secondary-700 text-sm">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5 text-secondary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <span class="font-medium mr-2">${formatDate(entry.clock_in_time)}</span>
                        <span class="bg-primary-100 text-primary-800 px-2 py-0.5 rounded-full text-xs font-semibold shadow-sm">${displayHoursWorked} hrs</span>
                    </div>
                    <div class="text-sm text-secondary-700">
                        <span class="font-semibold">${formatOnlyTime(entry.clock_in_time)}</span> 
                        <span class="text-secondary-400 mx-0.5">—</span> 
                        <span class="font-semibold ${clockOutClass}">${displayClockOutTime}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    const weekSectionHtml = `
        <div id="week${weekNum}Section" class="bg-white rounded-lg shadow-md overflow-hidden mb-6 border border-secondary-200 animate-fade-in-up animate-delay-${400 + (weekNum * 100)}">
            <div class="px-5 py-4 border-b border-secondary-200 bg-secondary-50">
                <h3 class="text-lg font-medium text-secondary-800 flex items-center">
                    <span class="bg-primary-600 text-white rounded-full w-7 h-7 flex items-center justify-center mr-2 text-base font-bold">${weekNum}</span>
                    Week ${weekNum} Summary
                </h3>
            </div>
            <div class="divide-y divide-secondary-200">
                ${entriesHtml}
            </div>
            <div class="px-5 py-3 bg-secondary-100 text-right">
                <p class="text-base font-bold text-primary-700">
                    Week Total: <span class="text-primary-800">${parseFloat(totalHours).toFixed(2) || '0.00'} hrs</span>
                </p>
            </div>
        </div>
    `;
    timeEntriesSectionElement.insertAdjacentHTML('beforeend', weekSectionHtml);
}