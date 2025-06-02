// static/timeclock/js/admin_clock_data.js
// (This is the content from the "Frontend Implementation to Fetch and Display Pay Periods" section)

// Make sure to adapt this to your actual project structure for api_client.js and uiRenderer.js
// You might put renderClockDataReport directly in this file if it's specific to this page.
import { fetchWithAuth } from './api_client.js'; // Adjust path if needed
// Assuming renderClockDataReport is defined here or imported from uiRenderer.js
// For simplicity, let's define it here for this example:

function renderClockDataReport(containerElement, data) {
    let html = `
        <h2 class="text-xl font-bold mb-4">Clock Data for Pay Period: ${data.pay_period.start_date} to ${data.pay_period.end_date}</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    `;

    if (data.users_clock_data && data.users_clock_data.length > 0) {
        data.users_clock_data.forEach(userData => {
            html += `
                <div class="bg-white p-4 rounded-lg shadow-md">
                    <h3 class="text-lg font-semibold mb-2">${userData.first_name} ${userData.last_name} (${userData.username})</h3>
                    <p class="text-sm text-gray-600">Status: <span class="${userData.current_status === 'Clocked In' ? 'text-green-600' : 'text-gray-500'} font-medium">${userData.current_status}</span></p>
                    ${userData.active_clock_entry ? `<p class="text-xs text-gray-500">Clocked In: ${userData.active_clock_entry.clock_in_time}</p>` : ''}
                    <p class="mt-2 font-bold">Week 1 Hours: ${userData.week_1_total_hours} hours</p>
                    <p class="font-bold">Week 2 Hours: ${userData.week_2_total_hours} hours</p>
                    </div>
            `;
        });
    } else {
        html += '<p>No clock data found for this pay period.</p>';
    }

    html += `</div>`;
    containerElement.innerHTML = html;
}

async function populatePayPeriodSelector() {
    const payPeriodSelect = document.getElementById('payPeriodSelector');
    if (!payPeriodSelect) {
        console.error("Pay period selector element not found.");
        return;
    }

    try {
        const response = await fetchWithAuth('/api/clock-data/pay_periods/');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const payPeriods = await response.json();

        payPeriodSelect.innerHTML = '<option value="">Select a Pay Period</option>';

        payPeriods.forEach(payPeriod => {
            const option = document.createElement('option');
            option.value = payPeriod.id;
            option.textContent = `${payPeriod.start_date} to ${payPeriod.end_date}`;
            payPeriodSelect.appendChild(option);
        });

        payPeriodSelect.addEventListener('change', (event) => {
            const selectedPayPeriodId = event.target.value;
            if (selectedPayPeriodId) {
                fetchClockDataForPayPeriod(selectedPayPeriodId);
            } else {
                const reportContainer = document.getElementById('clockDataReportContainer');
                if (reportContainer) {
                    reportContainer.innerHTML = '<p class="text-gray-500">Select a pay period to view clock data.</p>';
                }
            }
        });

    } catch (error) {
        console.error("Error fetching pay periods:", error);
        payPeriodSelect.innerHTML = '<option value="">Error loading periods</option>';
    }
}

async function fetchClockDataForPayPeriod(payPeriodId) {
    const reportContainer = document.getElementById('clockDataReportContainer');
    if (!reportContainer) {
        console.error("Clock data report container not found.");
        return;
    }
    reportContainer.innerHTML = '<p class="text-gray-500">Loading clock data...</p>';

    try {
        const response = await fetchWithAuth(`/api/clock-data/?pay_period_id=${payPeriodId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log("Fetched Clock Data:", data);

        renderClockDataReport(reportContainer, data);

    } catch (error) {
        console.error("Error fetching clock data:", error);
        reportContainer.innerHTML = `<p class="text-red-600">Error loading clock data: ${error.message}</p>`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    populatePayPeriodSelector();
});