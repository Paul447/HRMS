// static/ptorequest/js/past_pto_list.js

import {
    fetchPayPeriods,
    fetchPastPtoRequests
} from './modules/pastdetails/apiService.js';
import {
    showToast,
    toggleLoading,
    toggleNoResultsMessage,
    toggleErrorMessage
} from './modules/pastdetails/uiHelpers.js';
import {
    renderPtoRequestsTable
} from './modules/pastdetails/tableRender.js';

document.addEventListener('DOMContentLoaded', function() {
    // --- DOM Elements ---
    const payPeriodSelect = document.getElementById('payPeriodSelect');
    const filterButton = document.getElementById('filterButton');
    const ptoRequestsTableBody = document.getElementById('ptoRequestsTableBody');
    const noRequestsMessageRow = document.getElementById('noRequestsMessage'); // The hidden tr
    const loadingMessageRow = document.createElement('tr'); // Create a dynamic loading row
    loadingMessageRow.innerHTML = `<td colspan="7" class="px-6 py-4 text-center text-gray-500">Loading past PTO requests...</td>`;
    loadingMessageRow.id = 'loadingMessageRow';
    loadingMessageRow.classList.add('hidden'); // Hidden by default

    // Add loading row to table body initially
    ptoRequestsTableBody.appendChild(loadingMessageRow);

    // --- State Management ---
    let selectedPayPeriodId = localStorage.getItem('lastSelectedPayPeriodId') || null;

    // --- Functions ---

    /**
     * Populates the pay period dropdown with past pay periods.
     * Sets the default selected value based on localStorage or the most recent past period.
     */
    async function populatePayPeriods() {
        payPeriodSelect.innerHTML = ''; // Clear existing options

        // Add a "Loading" option
        const loadingOption = document.createElement('option');
        loadingOption.value = "";
        loadingOption.textContent = "Loading Pay Periods...";
        loadingOption.disabled = true;
        payPeriodSelect.appendChild(loadingOption);

        try {
            const payPeriods = await fetchPayPeriods();
            const now = new Date();
            now.setHours(0, 0, 0, 0); // Normalize today for comparison

            // Filter for past pay periods (end_date strictly before today)
            const pastPayPeriods = payPeriods.filter(period => {
                const endDate = new Date(period.end_date);
                endDate.setHours(0, 0, 0, 0);
                return endDate < now;
            });

            // Sort past pay periods by end_date in descending order (most recent first)
            pastPayPeriods.sort((a, b) => new Date(b.end_date) - new Date(a.end_date));

            payPeriodSelect.innerHTML = ''; // Clear loading option

            // Add "All Past Pay Periods" option
            const allOption = document.createElement('option');
            allOption.value = "";
            allOption.textContent = "Current Pay Period";
            payPeriodSelect.appendChild(allOption);


            if (pastPayPeriods.length > 0) {
                pastPayPeriods.forEach(period => {
                    const option = document.createElement('option');
                    option.value = period.id;
                    const startDate = new Date(period.start_date);
                    const endDate = new Date(period.end_date);
                    option.textContent = `Pay Period: ${startDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })} - ${endDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
                    payPeriodSelect.appendChild(option);
                });

                // Set initial selection
                if (selectedPayPeriodId && pastPayPeriods.some(p => String(p.id) === selectedPayPeriodId)) {
                    // If a valid ID was saved, use it
                    payPeriodSelect.value = selectedPayPeriodId;
                } else if (pastPayPeriods.length > 0) {
                    // Otherwise, default to the most recent past pay period
                    payPeriodSelect.value = pastPayPeriods[0].id;
                    selectedPayPeriodId = String(pastPayPeriods[0].id); // Update state
                    localStorage.setItem('lastSelectedPayPeriodId', selectedPayPeriodId);
                } else {
                    // No past periods available, default to "All" (which should show no data)
                    payPeriodSelect.value = "";
                    selectedPayPeriodId = null;
                    localStorage.removeItem('lastSelectedPayPeriodId');
                }
            } else {
                const noPeriodsOption = document.createElement('option');
                noPeriodsOption.value = "";
                noPeriodsOption.textContent = "No past pay periods available";
                noPeriodsOption.disabled = true;
                payPeriodSelect.appendChild(noPeriodsOption);
                selectedPayPeriodId = null;
                localStorage.removeItem('lastSelectedPayPeriodId');
            }
        } catch (error) {
            console.error("Error populating pay periods:", error);
            payPeriodSelect.innerHTML = '<option value="">Failed to load pay periods</option>';
            payPeriodSelect.disabled = true;
            showToast('Failed to load pay periods. Please refresh the page.', 'error');
            selectedPayPeriodId = null;
            localStorage.removeItem('lastSelectedPayPeriodId');
        }
    }

    /**
     * Fetches and renders past PTO requests based on the selected pay period.
     */
    async function loadAndRenderPastPtoRequests() {
        toggleLoading(loadingMessageRow, true);
        toggleNoResultsMessage(noRequestsMessageRow, false);
        // Ensure no prior error message is visible (from uiHelpers)
        // (You might need a specific error row for this table if uiHelpers doesn't provide it)
        // For now, we'll clear the tbody for errors directly.
        ptoRequestsTableBody.innerHTML = '';
        ptoRequestsTableBody.appendChild(loadingMessageRow); // Re-add loading row for visibility

        try {
            const requests = await fetchPastPtoRequests(selectedPayPeriodId);
            renderPtoRequestsTable(requests, ptoRequestsTableBody, noRequestsMessageRow, {
                highlightRows: true
            });
            // If data was loaded successfully, remove the loading row
            loadingMessageRow.classList.add('hidden');

        } catch (error) {
            console.error('Error fetching past PTO requests:', error);
            showToast('Failed to load past PTO requests. Please try again.', 'error');
            ptoRequestsTableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="px-6 py-4 text-center text-red-500">
                        Failed to load past PTO requests. ${error.message || 'Please try again later.'}
                    </td>
                </tr>
            `;
            toggleNoResultsMessage(noRequestsMessageRow, false); // Hide "no results" if error
        } finally {
            toggleLoading(loadingMessageRow, false); // Always hide loading indicator
        }
    }

    // --- Event Listeners ---

    // When the filter button is clicked
    filterButton.addEventListener('click', () => {
        selectedPayPeriodId = payPeriodSelect.value === "" ? null : payPeriodSelect.value;
        localStorage.setItem('lastSelectedPayPeriodId', selectedPayPeriodId || ''); // Save to localStorage
        loadAndRenderPastPtoRequests();
    });

    // --- Initial Load ---
    // Populate dropdown first, then fetch requests based on the initial selection
    populatePayPeriods().then(() => {
        // After pay periods are populated, the `selectedPayPeriodId` state variable
        // will be correctly set by `populatePayPeriods` based on localStorage or default.
        loadAndRenderPastPtoRequests();
    });
});