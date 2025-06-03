// static/js/timeclock_punch.js

import { getAdminReportDomElements } from './modules/admin_report/adminDomElements.js';
import { getPayPeriodsAdmin, getClockDataAdmin } from './modules/admin_report/adminApi.js';
import { renderAdminClockDataReport, updateExportButtonState } from './modules/admin_report/adminUiRenderer.js';
import { exportAdminReportToXLSX } from './modules/admin_report/excelExporter.js';
import { showNotification } from './modules/timeclock/notificationService.js'; // Reusing your existing notification service

// Global variable to store the current report data for export
let currentReportData = null;

document.addEventListener('DOMContentLoaded', async function() {
    const DOMElements = getAdminReportDomElements();

    // Initial loading state
    const loadingHtml = `
        <div class="flex flex-col justify-center items-center h-24 text-gray-500">
            <svg class="animate-spin h-8 w-8 text-blue-500 mb-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Loading data...</span>
        </div>
    `;
    DOMElements.clockDataReportContainer.innerHTML = loadingHtml;
    DOMElements.exportExcelButton.disabled = true;
    DOMElements.exportExcelButton.classList.add('opacity-50', 'cursor-not-allowed');

    // Populate the pay period selector and trigger initial data load
    await populatePayPeriodSelector(DOMElements);

    // Attach event listener to the export button
    DOMElements.exportExcelButton.addEventListener('click', () => {
        if (currentReportData) {
            const selectedOption = DOMElements.payPeriodSelector.options[DOMElements.payPeriodSelector.selectedIndex];
            const payPeriodText = selectedOption.textContent.trim();
            const filename = `Employee_Clock_Report_${payPeriodText.replace(/[^a-zA-Z0-9_ -]/g, '')}.xlsx`;
            exportAdminReportToXLSX(currentReportData, filename);
        } else {
            showNotification('No data available to export. Please select a pay period first.', 'warning');
        }
    });
});

/**
 * Fetches and populates the pay period selector dropdown.
 * @param {Object} DOMElements - Object containing references to all necessary DOM elements.
 */
async function populatePayPeriodSelector(DOMElements) {
    const { payPeriodSelector, clockDataReportContainer, exportExcelButton } = DOMElements;

    payPeriodSelector.innerHTML = '<option value="">Loading Pay Periods...</option>';

    try {
        const payPeriods = await getPayPeriodsAdmin();

        payPeriodSelector.innerHTML = '<option value="">Select a Pay Period</option>';

        if (payPeriods.length > 0) {
            payPeriods.forEach(payPeriod => {
                const option = document.createElement('option');
                option.value = payPeriod.id;
                option.textContent = `${payPeriod.start_date_local} to ${payPeriod.end_date_local}`;
                payPeriodSelector.appendChild(option);
            });
            // Pre-select the most recent pay period and trigger initial data fetch
            if (payPeriods[0] && payPeriods[0].id) {
                payPeriodSelector.value = payPeriods[0].id;
                await fetchAndRenderAdminClockData(payPeriods[0].id, DOMElements);
            }

        } else {
            payPeriodSelector.innerHTML = '<option value="">No Pay Periods Found</option>';
            payPeriodSelector.disabled = true;
            clockDataReportContainer.innerHTML = '<p class="text-gray-500 text-center py-4">No pay periods found.</p>';
            updateExportButtonState(exportExcelButton, null);
        }

        // Add change listener after initial population
        payPeriodSelector.addEventListener('change', async (event) => {
            const selectedPayPeriodId = event.target.value;
            if (selectedPayPeriodId) {
                await fetchAndRenderAdminClockData(selectedPayPeriodId, DOMElements);
            } else {
                clockDataReportContainer.innerHTML = '<p class="text-gray-500">Select a pay period to view clock data.</p>';
                currentReportData = null;
                updateExportButtonState(exportExcelButton, null);
            }
        });

    } catch (error) {
        console.error("Error populating pay period selector:", error);
        payPeriodSelector.innerHTML = '<option value="">Error loading periods</option>';
        payPeriodSelector.disabled = true;
        clockDataReportContainer.innerHTML = `<p class="text-red-600 text-center py-4">Error loading pay periods: ${error.message}</p>`;
        showNotification(`Error loading pay periods: ${error.message}`, 'error');
        updateExportButtonState(exportExcelButton, null);
    }
}

/**
 * Fetches clock data for a specific pay period and renders it.
 * Manages loading states and updates the export button.
 * @param {string} payPeriodId - The ID of the pay period.
 * @param {Object} DOMElements - Object containing references to all necessary DOM elements.
 */
async function fetchAndRenderAdminClockData(payPeriodId, DOMElements) {
    const { clockDataReportContainer, exportExcelButton } = DOMElements;

    clockDataReportContainer.innerHTML = '<p class="text-gray-500 text-center py-4">Loading clock data for the selected pay period...</p>';
    updateExportButtonState(exportExcelButton, null); // Disable button while loading
    currentReportData = null; // Clear previous data

    try {
        const data = await getClockDataAdmin(payPeriodId);
        currentReportData = data; // Store the fetched data globally

        renderAdminClockDataReport(clockDataReportContainer, data); // Render the fetched data
        updateExportButtonState(exportExcelButton, data); // Update button based on new data

    } catch (error) {
        console.error("Error fetching clock data for pay period:", error);
        clockDataReportContainer.innerHTML = `<p class="text-red-600 text-center py-4">Error loading clock data: ${error.message}</p>`;
        showNotification(`Error loading clock data: ${error.message}`, 'error');
        updateExportButtonState(exportExcelButton, null); // Ensure disabled on error
    }
}