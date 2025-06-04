// static/js/modules/admin_report/adminUiRenderer.js

import { formatDate, formatOnlyTime } from '../timeclock/utils.js';

/**
 * Renders the aggregated clock data report as an HTML table.
 * @param {HTMLElement} containerElement - The DOM element where the report should be rendered.
 * @param {Object} data - The clock data report object.
 */
export function renderAdminClockDataReport(containerElement, data) {
    containerElement.innerHTML = ''; // Clear previous content

    if (!data || !data.pay_period || !data.users_clock_data) {
        containerElement.innerHTML = `
            <div class="flex flex-col items-center justify-center py-12 text-gray-500">
                <svg class="w-16 h-16 mb-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <p class="text-xl font-semibold">Oops! Something went wrong.</p>
                <p class="text-md">Failed to load report data or the data is incomplete.</p>
                <p class="text-sm mt-2 text-gray-400">Please try selecting the pay period again or contact support if the issue persists.</p>
            </div>
        `;
        return;
    }

    const payPeriodStartDate = data.pay_period.start_date_local;
    const payPeriodEndDate = data.pay_period.end_date_local;

    let tableHtml = `
        <h2 class="text-xl font-bold mb-6 text-gray-800 text-center">
            Clock Data for Pay Period: <span class="text-blue-600">${payPeriodStartDate} to ${payPeriodEndDate}</span>
        </h2>

        <div class="overflow-x-auto relative shadow-md sm:rounded-lg border border-gray-200">
            <table class="w-full text-sm text-left text-gray-700" id="clockDataTable">
                <thead class="text-xs text-gray-700 uppercase bg-gray-100">
                    <tr>
                        <th scope="col" class="px-6 py-3 border-r border-gray-200" rowspan="2">
                            Employee
                        </th>
                        <th scope="col" class="px-6 py-3 border-r border-gray-200" rowspan="2">
                            Week
                        </th>
                        <th scope="col" class="px-6 py-3 text-center border-b border-gray-200" colspan="4">
                            Time Entries
                        </th>
                        <th scope="col" class="px-6 py-3 border-l border-gray-200" rowspan="2">
                            Regular Hrs
                        </th>
                        <th scope="col" class="px-6 py-3 border-l border-gray-200" rowspan="2">
                            OT Hrs
                        </th>
                        <th scope="col" class="px-6 py-3 border-l border-gray-200" rowspan="2">
                            Total Hrs
                        </th>
                    </tr>
                    <tr>
                        <th scope="col" class="px-6 py-2 border-r border-gray-200">
                            IN / Start
                        </th>
                        <th scope="col" class="px-6 py-2 border-r border-gray-200">
                            OUT / End
                        </th>
                        <th scope="col" class="px-6 py-2 border-r border-gray-200">
                            Duration
                        </th>
                        <th scope="col" class="px-6 py-2">
                            Type
                        </th>
                    </tr>
                </thead>
                <tbody>
    `;

    if (data.users_clock_data.length > 0) {
        data.users_clock_data.forEach(userData => {
            const employeeName = `${userData.first_name} ${userData.last_name}`;
            const totalHoursCombined = (parseFloat(userData.week_1_total_hours || 0) + parseFloat(userData.week_2_total_hours || 0) + parseFloat(userData.week_1_pto_total_hours || 0) + parseFloat(userData.week_2_pto_total_hours || 0)).toFixed(2);

            // Combine punches and PTO entries for Week 1
            const week1CombinedEntries = [
                ...(userData.week_1_entries || []).map(entry => ({ ...entry, type: 'Punch', sortTime: entry.clock_in_time })),
                ...(userData.week_1_pto_entries || []).map(entry => ({ ...entry, type: entry.pay_types_display.name, sortTime: entry.start_date_time }))
            ].sort((a, b) => new Date(a.sortTime) - new Date(b.sortTime)); // Sort by start time

            // Combine punches and PTO entries for Week 2
            const week2CombinedEntries = [
                ...(userData.week_2_entries || []).map(entry => ({ ...entry, type: 'Punch', sortTime: entry.clock_in_time })),
                ...(userData.week_2_pto_entries || []).map(entry => ({ ...entry, type: entry.pay_types_display.name, sortTime: entry.start_date_time }))
            ].sort((a, b) => new Date(a.sortTime) - new Date(b.sortTime)); // Sort by start time

            const week1MaxRows = Math.max(week1CombinedEntries.length, 1);
            const week2MaxRows = Math.max(week2CombinedEntries.length, 1);

            const totalRowsForEmployee = week1MaxRows + week2MaxRows;

            // --- Week 1 Block ---
            for (let i = 0; i < week1MaxRows; i++) {
                const entry = week1CombinedEntries[i];
                const isPunch = entry && entry.type === 'Punch';
                const isPTO = entry && entry.type !== 'Punch';

                tableHtml += `
                    <tr class="bg-white border-b hover:bg-gray-50">
                        ${i === 0 ? `<td class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap border-r border-gray-200" rowspan="${totalRowsForEmployee}">
                            ${employeeName}
                        </td>` : ''}

                        ${i === 0 ? `<td class="px-6 py-4 whitespace-nowrap text-gray-900 border-r border-gray-200" rowspan="${week1MaxRows}">
                            <span class="font-semibold text-blue-700">Week 1</span><br>
                            <span class="text-xs text-gray-500">Punch: ${parseFloat(userData.week_1_total_hours || 0).toFixed(2)} hrs</span><br>
                            <span class="text-xs text-gray-500">PTO: ${parseFloat(userData.week_1_pto_total_hours || 0).toFixed(2)} hrs</span>
                        </td>` : ''}

                        <td class="px-6 py-4 whitespace-nowrap">
                            ${entry ? `
                                <div class="text-gray-900">${formatDate(isPunch ? entry.clock_in_time : entry.start_date_time)}</div>
                                <div class="text-gray-500 text-xs">${formatOnlyTime(isPunch ? entry.clock_in_time : entry.start_date_time)}</div>
                            ` : '<span class="text-gray-400">N/A</span>'}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            ${isPunch && entry.clock_out_time ? `
                                <div class="text-gray-900">${formatDate(entry.clock_out_time)}</div>
                                <div class="text-gray-500 text-xs">${formatOnlyTime(entry.clock_out_time)}</div>
                            ` : (isPunch && !entry.clock_out_time ? `<span class="inline-flex items-center text-green-600 font-medium animate-pulse">
                                <span class="relative flex h-2 w-2 mr-1">
                                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                    <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                                </span>
                                Active
                            </span>` : (isPTO && entry.end_date_time ? `
                                <div class="text-gray-900">${formatDate(entry.end_date_time)}</div>
                                <div class="text-gray-500 text-xs">${formatOnlyTime(entry.end_date_time)}</div>
                            ` : '<span class="text-gray-400">N/A</span>'))}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap border-r border-gray-200">
                            ${entry ? `<span class="font-medium text-gray-900">${parseFloat(isPunch ? entry.hours_worked : entry.total_hours || 0).toFixed(2)} hrs</span>` : '<span class="text-gray-400">0.00 hrs</span>'}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            ${entry ? `<span class="font-medium ${isPunch ? 'text-gray-900' : 'text-purple-700'}">${entry.type}</span>` : '<span class="text-gray-400">N/A</span>'}
                        </td>

                        ${i === 0 ? `<td class="px-6 py-4 whitespace-nowrap text-gray-900 border-l border-gray-200" rowspan="${week1MaxRows}">
                            <span class="font-semibold">${parseFloat(userData.regular_hours_week_1 || 0).toFixed(2)}</span>
                        </td>` : ''}
                        ${i === 0 ? `<td class="px-6 py-4 whitespace-nowrap text-gray-900 border-l border-gray-200 ${parseFloat(userData.overtime_hours_week_1 || 0) > 0 ? 'text-red-600 font-bold' : ''}" rowspan="${week1MaxRows}">
                            <span class="font-semibold">${parseFloat(userData.overtime_hours_week_1 || 0).toFixed(2)}</span>
                        </td>` : ''}

                        ${i === 0 ? `<td class="px-6 py-4 whitespace-nowrap text-blue-800 font-bold text-lg border-l border-gray-200" rowspan="${totalRowsForEmployee}">
                            ${totalHoursCombined}
                        </td>` : ''}
                    </tr>
                `;
            }

            // --- Week 2 Block ---
            for (let i = 0; i < week2MaxRows; i++) {
                const entry = week2CombinedEntries[i];
                const isPunch = entry && entry.type === 'Punch';
                const isPTO = entry && entry.type !== 'Punch';

                tableHtml += `
                    <tr class="bg-white border-b hover:bg-gray-50">
                        ${i === 0 ? `<td class="px-6 py-4 whitespace-nowrap text-gray-900 border-r border-gray-200" rowspan="${week2MaxRows}">
                            <span class="font-semibold text-blue-700">Week 2</span><br>
                            <span class="text-xs text-gray-500">Punch: ${parseFloat(userData.week_2_total_hours || 0).toFixed(2)} hrs</span><br>
                            <span class="text-xs text-gray-500">PTO: ${parseFloat(userData.week_2_pto_total_hours || 0).toFixed(2)} hrs</span>
                        </td>` : ''}

                        <td class="px-6 py-4 whitespace-nowrap">
                            ${entry ? `
                                <div class="text-gray-900">${formatDate(isPunch ? entry.clock_in_time : entry.start_date_time)}</div>
                                <div class="text-gray-500 text-xs">${formatOnlyTime(isPunch ? entry.clock_in_time : entry.start_date_time)}</div>
                            ` : '<span class="text-gray-400">N/A</span>'}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            ${isPunch && entry.clock_out_time ? `
                                <div class="text-gray-900">${formatDate(entry.clock_out_time)}</div>
                                <div class="text-gray-500 text-xs">${formatOnlyTime(entry.clock_out_time)}</div>
                            ` : (isPunch && !entry.clock_out_time ? `<span class="inline-flex items-center text-green-600 font-medium animate-pulse">
                                <span class="relative flex h-2 w-2 mr-1">
                                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                    <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                                </span>
                                Active
                            </span>` : (isPTO && entry.end_date_time ? `
                                <div class="text-gray-900">${formatDate(entry.end_date_time)}</div>
                                <div class="text-gray-500 text-xs">${formatOnlyTime(entry.end_date_time)}</div>
                            ` : '<span class="text-gray-400">N/A</span>'))}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap border-r border-gray-200">
                            ${entry ? `<span class="font-medium text-gray-900">${parseFloat(isPunch ? entry.hours_worked : entry.total_hours || 0).toFixed(2)} hrs</span>` : '<span class="text-gray-400">0.00 hrs</span>'}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            ${entry ? `<span class="font-medium ${isPunch ? 'text-gray-900' : 'text-purple-700'}">${entry.type}</span>` : '<span class="text-gray-400">N/A</span>'}
                        </td>

                        ${i === 0 ? `<td class="px-6 py-4 whitespace-nowrap text-gray-900 border-l border-gray-200" rowspan="${week2MaxRows}">
                            <span class="font-semibold">${parseFloat(userData.regular_hours_week_2 || 0).toFixed(2)}</span>
                        </td>` : ''}
                        ${i === 0 ? `<td class="px-6 py-4 whitespace-nowrap text-gray-900 border-l border-gray-200 ${parseFloat(userData.overtime_hours_week_2 || 0) > 0 ? 'text-red-600 font-bold' : ''}" rowspan="${week2MaxRows}">
                            <span class="font-semibold">${parseFloat(userData.overtime_hours_week_2 || 0).toFixed(2)}</span>
                        </td>` : ''}
                    </tr>
                `;
            }
            // Add a separator row between employees for better readability
            tableHtml += `
                <tr class="bg-gray-50">
                    <td colspan="9" class="h-4"></td>
                </tr>
            `;
        });
    } else {
        tableHtml += `
                <tr>
                    <td colspan="9" class="px-6 py-12 text-center text-gray-600">
                        <svg class="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                            <path vector-effect="non-scaling-stroke" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1H3z" />
                        </svg>
                        <h3 class="mt-2 text-xl font-medium text-gray-900">No time entries found</h3>
                        <p class="mt-1 text-md text-gray-500">
                            There are no clock data entries for any user in this selected pay period.
                        </p>
                    </td>
                </tr>
            `;
    }

    tableHtml += `
                </tbody>
            </table>
        </div>
    `;

    containerElement.innerHTML = tableHtml;
}

/**
 * Updates the state of the export Excel button based on data availability.
 * @param {HTMLElement} exportButton - The export button DOM element.
 * @param {Object} data - The clock data report object.
 */
export function updateExportButtonState(exportButton, data) {
    if (exportButton) {
        if (data && data.users_clock_data && data.users_clock_data.length > 0) {
            exportButton.disabled = false;
            exportButton.classList.remove('opacity-50', 'cursor-not-allowed');
        } else {
            exportButton.disabled = true;
            exportButton.classList.add('opacity-50', 'cursor-not-allowed');
        }
    }
}