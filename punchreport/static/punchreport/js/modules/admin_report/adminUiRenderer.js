import { formatDate, formatOnlyTime } from '../punchreport/utils.js';

/**
 * Renders the aggregated clock data report as an HTML table.
 * @param {HTMLElement} containerElement - The DOM element where the report should be rendered.
 * @param {Object} data - The clock data report object.
 */
export function renderAdminClockDataReport(containerElement, data) {
    if (!containerElement) return;

    containerElement.innerHTML = ''; // Clear previous content

    if (!data?.pay_period || !data?.users_clock_data) {
        containerElement.innerHTML = `
            <div class="flex flex-col items-center justify-center py-16 text-gray-500 bg-white rounded-lg shadow-xl mx-auto my-8 max-w-2xl border border-gray-200">
                <svg class="w-20 h-20 mb-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <p class="text-2xl font-bold text-gray-800 mb-2">Uh oh! Report data missing.</p>
                <p class="text-lg text-gray-600 mb-4 text-center px-6">We couldn't load the clock data report. It appears to be incomplete or unavailable.</p>
                <p class="text-sm text-gray-500 mt-2">Please try selecting the pay period again or contact support if the issue persists.</p>
            </div>
        `;
        return;
    }

    const payPeriodStartDate = data.pay_period.start_date_local || 'N/A';
    const payPeriodEndDate = data.pay_period.end_date_local || 'N/A';

    let tableHtml = `
        <div class="bg-white p-6 rounded-lg shadow-xl mb-8 border border-gray-200">
            <h2 class="text-2xl sm:text-3xl font-extrabold mb-3 text-gray-900 text-center">
                Employee Clock Data Report
            </h2>
            <p class="text-lg text-gray-700 text-center mb-6">
                Pay Period: <span class="text-blue-700 font-semibold">${payPeriodStartDate} to ${payPeriodEndDate}</span>
            </p>

            <div class="p-5 bg-blue-50 rounded-lg border border-blue-200 text-sm">
                <h3 class="font-bold text-blue-800 mb-3 text-base">Color Legend:</h3>
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-y-2 gap-x-4">
                    <div class="flex items-center">
                        <span class="inline-block w-4 h-4 min-w-[1rem] rounded-full bg-gray-800 mr-2 border border-gray-300 shadow-sm"></span>
                        <span class="text-gray-700">Punch (Regular Clock In/Out)</span>
                    </div>
                    <div class="flex items-center">
                        <span class="inline-block w-4 h-4 min-w-[1rem] rounded-full bg-green-600 mr-2 border border-green-300 shadow-sm"></span>
                        <span class="text-gray-700">Holiday Pay</span>
                    </div>
                    <div class="flex items-center">
                        <span class="inline-block w-4 h-4 min-w-[1rem] rounded-full bg-purple-600 mr-2 border border-purple-300 shadow-sm"></span>
                        <span class="text-gray-700">PTO / Other Pay Types</span>
                    </div>
                    <div class="flex items-center">
                        <span class="inline-block w-4 h-4 min-w-[1rem] rounded-sm bg-green-100 mr-2 border border-green-300 shadow-sm"></span>
                        <span class="text-gray-700">Holiday Entry Row</span>
                    </div>
                    <div class="flex items-center">
                        <span class="inline-block w-4 h-4 min-w-[1rem] rounded-full bg-red-600 mr-2 border border-red-300 shadow-sm"></span>
                        <span class="text-gray-700">Overtime Hours</span>
                    </div>
                     <div class="flex items-center">
                        <span class="inline-block w-4 h-4 min-w-[1rem] rounded-full bg-yellow-400 mr-2 border border-yellow-300 shadow-sm"></span>
                        <span class="text-gray-700">Active Punch (Live)</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="overflow-x-auto relative shadow-lg rounded-lg border border-gray-200">
            <table class="w-full text-sm text-left text-gray-700" id="clockDataTable">
                <thead class="text-xxs text-gray-700 uppercase bg-gray-50 border-b border-gray-200">
                    <tr>
                        <th scope="col" class="px-5 py-3 border-r border-gray-200 font-bold tracking-wider sticky left-0 bg-gray-50 z-20" rowspan="2">
                            Employee
                        </th>
                        <th scope="col" class="px-5 py-3 border-r border-gray-200 font-bold tracking-wider text-center" rowspan="2">
                            Summary
                        </th>
                        <th scope="col" class="px-5 py-3 text-center border-b border-gray-200 font-bold tracking-wider" colspan="4">
                            Time Entry Details
                        </th>
                        <th scope="col" class="px-5 py-3 border-l border-gray-200 font-bold tracking-wider text-center" rowspan="2">
                            Regular Hrs
                        </th>
                        <th scope="col" class="px-5 py-3 border-l border-gray-200 font-bold tracking-wider text-center" rowspan="2">
                            OT Hrs
                        </th>
                        <th scope="col" class="px-5 py-3 border-l border-gray-200 font-bold tracking-wider text-center" rowspan="2">
                            Total Hrs
                        </th>
                    </tr>
                    <tr>
                        <th scope="col" class="px-5 py-2 border-r border-gray-200 font-semibold text-center">
                            IN / Start
                        </th>
                        <th scope="col" class="px-5 py-2 border-r border-gray-200 font-semibold text-center">
                            OUT / End
                        </th>
                        <th scope="col" class="px-5 py-2 border-r border-gray-200 font-semibold text-center">
                            Duration
                        </th>
                        <th scope="col" class="px-5 py-2 font-semibold text-center">
                            Type
                        </th>
                    </tr>
                </thead>
                <tbody>
    `;

    if (data.users_clock_data?.length > 0) {
        data.users_clock_data.forEach(userData => {
            const employeeName = `${userData?.first_name || ''} ${userData?.last_name || ''}`.trim() || 'Unknown Employee';
            const totalHoursCombined = Number(
                (Number(userData?.week_1_total_hours || 0) +
                 Number(userData?.week_2_total_hours || 0) +
                 Number(userData?.week_1_pto_total_hours || 0) +
                 Number(userData?.week_2_pto_total_hours || 0) +
                 Number(userData?.week_1_holiday_total_hours || 0) +
                 Number(userData?.week_2_holiday_total_hours || 0))
            ).toFixed(2);

            // Combine punches, holidays, and PTO entries for Week 1
            const week1CombinedEntries = [
                ...(userData?.week_1_entries || []).map(entry => ({ ...entry, type: 'Punch', sortTime: entry.clock_in_time })),
                ...(userData?.week_1_holiday_entries || []).map(entry => ({
                    ...entry,
                    type: 'Holiday',
                    sortTime: entry.clock_in_time,
                    isHoliday: true
                })),
                ...(userData?.week_1_pto_entries || []).map(entry => ({
                    ...entry,
                    type: entry?.leave_type_display || 'Hello',
                    sortTime: entry.start_date_time
                }))
            ].sort((a, b) => new Date(a.sortTime || 0) - new Date(b.sortTime || 0));

            // Combine punches, holidays, and PTO entries for Week 2
            const week2CombinedEntries = [
                ...(userData?.week_2_entries || []).map(entry => ({ ...entry, type: 'Punch', sortTime: entry.clock_in_time })),
                ...(userData?.week_2_holiday_entries || []).map(entry => ({
                    ...entry,
                    type: 'Holiday',
                    sortTime: entry.clock_in_time,
                    isHoliday: true
                })),
                ...(userData?.week_2_pto_entries || []).map(entry => ({
                    ...entry,
                    type: entry?.leave_type_display || 'Hello',
                    sortTime: entry.start_date_time
                }))
            ].sort((a, b) => new Date(a.sortTime || 0) - new Date(b.sortTime || 0));

            const week1MaxRows = Math.max(week1CombinedEntries.length, 1);
            const week2MaxRows = Math.max(week2CombinedEntries.length, 1);
            const totalRowsForEmployee = week1MaxRows + week2MaxRows;

            // Week 1 Block
            for (let i = 0; i < week1MaxRows; i++) {
                const entry = week1CombinedEntries[i];
                const isPunch = entry?.type === 'Punch';
                const isHoliday = entry?.type === 'Holiday';
                const isPTO = entry && !isPunch && !isHoliday;

                tableHtml += `
                    <tr class="bg-white border-b border-gray-100 hover:bg-gray-50 ${isHoliday ? 'bg-green-50/50' : ''}">
                        ${i === 0 ? `<td class="px-5 py-4 font-semibold text-gray-900 whitespace-nowrap border-r border-gray-200 text-base align-top sticky left-0 bg-white z-10" rowspan="${totalRowsForEmployee}">
                            ${employeeName}
                        </td>` : ''}

                        ${i === 0 ? `<td class="px-5 py-4 whitespace-nowrap text-gray-900 border-r border-gray-200 text-sm align-top" rowspan="${week1MaxRows}">
                            <span class="font-bold text-blue-700 text-base">Week 1</span><br>
                            <span class="text-xs text-gray-600">Punch: <span class="font-medium">${Number(userData?.week_1_total_hours || 0).toFixed(2)} hrs</span></span><br>
                            <span class="text-xs text-gray-600">Time off: <span class="font-medium">${Number(userData?.week_1_pto_total_hours || 0).toFixed(2)} hrs</span></span><br>
                            <span class="text-xs text-gray-600">Holiday: <span class="font-medium">${Number(userData?.week_1_holiday_total_hours || 0).toFixed(2)} hrs</span></span>
                        </td>` : ''}

                        <td class="px-5 py-3 whitespace-nowrap text-center">
                            ${entry ? `
                                <div class="text-gray-900 font-medium">${(isPunch || isHoliday) ? formatDate(entry.clock_in_time) : formatDate(entry.start_date_time)}</div>
                                <div class="text-gray-500 text-xxs">${(isPunch || isHoliday) ? formatOnlyTime(entry.clock_in_time) : formatOnlyTime(entry.start_date_time)}</div>
                            ` : '<span class="text-gray-400 text-xxs">N/A</span>'}
                        </td>
                        <td class="px-5 py-3 whitespace-nowrap text-center">
                            ${(isPunch || isHoliday) ? (entry.clock_out_time ? `
                                <div class="text-gray-900 font-medium">${formatDate(entry.clock_out_time)}</div>
                                <div class="text-gray-500 text-xxs">${formatOnlyTime(entry.clock_out_time)}</div>
                            ` : `<span class="inline-flex items-center text-yellow-500 font-medium animate-pulse text-xs">
                                <span class="relative flex h-2 w-2 mr-1">
                                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span>
                                    <span class="relative inline-flex rounded-full h-2 w-2 bg-yellow-500"></span>
                                </span>
                                Active
                            </span>`) : (isPTO && entry.end_date_time ? `
                                <div class="text-gray-900 font-medium">${formatDate(entry.end_date_time)}</div>
                                <div class="text-gray-500 text-xxs">${formatOnlyTime(entry.end_date_time)}</div>
                            ` : '<span class="text-gray-400 text-xxs">N/A</span>')}
                        </td>
                        <td class="px-5 py-3 whitespace-nowrap border-r border-gray-200 text-center">
                            ${entry ? `<span class="font-bold text-gray-900 text-sm">
                                ${Number((isPunch || isHoliday) ? entry.hours_worked : entry.total_hours || 0).toFixed(2)} hrs
                            </span>` : '<span class="text-gray-400 text-sm">0.00 hrs</span>'}
                        </td>
                        <td class="px-5 py-3 whitespace-nowrap text-center">
                            ${entry ? `<span class="font-bold text-xs ${isPunch ? 'text-gray-800' : (isHoliday ? 'text-green-700' : 'text-purple-700')}">${entry.type}</span>` : '<span class="text-gray-400 text-xs">N/A</span>'}
                        </td>

                        ${i === 0 ? `<td class="px-5 py-4 whitespace-nowrap text-gray-900 border-l border-gray-200 text-base font-bold align-top text-center" rowspan="${week1MaxRows}">
                            ${Number(userData?.regular_hours_week_1 || 0).toFixed(2)}
                        </td>` : ''}
                        ${i === 0 ? `<td class="px-5 py-4 whitespace-nowrap text-gray-900 border-l border-gray-200 text-base font-bold align-top text-center ${Number(userData?.overtime_hours_week_1 || 0) > 0 ? 'text-red-600' : ''}" rowspan="${week1MaxRows}">
                            ${Number(userData?.overtime_hours_week_1 || 0).toFixed(2)}
                        </td>` : ''}

                        ${i === 0 ? `<td class="px-5 py-4 whitespace-nowrap text-blue-800 font-extrabold text-xl border-l border-gray-200 align-middle text-center" rowspan="${totalRowsForEmployee}">
                            ${totalHoursCombined}
                        </td>` : ''}
                    </tr>
                `;
            }

            // Week 2 Block
            for (let i = 0; i < week2MaxRows; i++) {
                const entry = week2CombinedEntries[i];
                const isPunch = entry?.type === 'Punch';
                const isHoliday = entry?.type === 'Holiday';
                const isPTO = entry && !isPunch && !isHoliday;

                tableHtml += `
                    <tr class="bg-white border-b border-gray-100 hover:bg-gray-50 ${isHoliday ? 'bg-green-50/50' : ''}">
                        ${i === 0 ? `<td class="px-5 py-4 whitespace-nowrap text-gray-900 border-r border-gray-200 text-sm align-top" rowspan="${week2MaxRows}">
                            <span class="font-bold text-blue-700 text-base">Week 2</span><br>
                            <span class="text-xs text-gray-600">Punch: <span class="font-medium">${Number(userData?.week_2_total_hours || 0).toFixed(2)} hrs</span></span><br>
                            <span class="text-xs text-gray-600">Time off: <span class="font-medium">${Number(userData?.week_2_pto_total_hours || 0).toFixed(2)} hrs</span></span><br>
                            <span class="text-xs text-gray-600">Holiday: <span class="font-medium">${Number(userData?.week_2_holiday_total_hours || 0).toFixed(2)} hrs</span></span>
                        </td>` : ''}

                        <td class="px-5 py-3 whitespace-nowrap text-center">
                            ${entry ? `
                                <div class="text-gray-900 font-medium">${(isPunch || isHoliday) ? formatDate(entry.clock_in_time) : formatDate(entry.start_date_time)}</div>
                                <div class="text-gray-500 text-xxs">${(isPunch || isHoliday) ? formatOnlyTime(entry.clock_in_time) : formatOnlyTime(entry.start_date_time)}</div>
                            ` : '<span class="text-gray-400 text-xxs">N/A</span>'}
                        </td>
                        <td class="px-5 py-3 whitespace-nowrap text-center">
                            ${(isPunch || isHoliday) ? (entry.clock_out_time ? `
                                <div class="text-gray-900 font-medium">${formatDate(entry.clock_out_time)}</div>
                                <div class="text-gray-500 text-xxs">${formatOnlyTime(entry.clock_out_time)}</div>
                            ` : `<span class="inline-flex items-center text-yellow-500 font-medium animate-pulse text-xs">
                                <span class="relative flex h-2 w-2 mr-1">
                                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span>
                                    <span class="relative inline-flex rounded-full h-2 w-2 bg-yellow-500"></span>
                                </span>
                                Active
                            </span>`) : (isPTO && entry.end_date_time ? `
                                <div class="text-gray-900 font-medium">${formatDate(entry.end_date_time)}</div>
                                <div class="text-gray-500 text-xxs">${formatOnlyTime(entry.end_date_time)}</div>
                            ` : '<span class="text-gray-400 text-xxs">N/A</span>')}
                        </td>
                        <td class="px-5 py-3 whitespace-nowrap border-r border-gray-200 text-center">
                            ${entry ? `<span class="font-bold text-gray-900 text-sm">
                                ${Number((isPunch || isHoliday) ? entry.hours_worked : entry.total_hours || 0).toFixed(2)} hrs
                            </span>` : '<span class="text-gray-400 text-sm">0.00 hrs</span>'}
                        </td>
                        <td class="px-5 py-3 whitespace-nowrap text-center">
                            ${entry ? `<span class="font-bold text-xs ${isPunch ? 'text-gray-800' : (isHoliday ? 'text-green-700' : 'text-purple-700')}">${entry.type}</span>` : '<span class="text-gray-400 text-xs">N/A</span>'}
                        </td>

                        ${i === 0 ? `<td class="px-5 py-4 whitespace-nowrap text-gray-900 border-l border-gray-200 text-base font-bold align-top text-center" rowspan="${week2MaxRows}">
                            ${Number(userData?.regular_hours_week_2 || 0).toFixed(2)}
                        </td>` : ''}
                        ${i === 0 ? `<td class="px-5 py-4 whitespace-nowrap text-gray-900 border-l border-gray-200 text-base font-bold align-top text-center ${Number(userData?.overtime_hours_week_2 || 0) > 0 ? 'text-red-600' : ''}" rowspan="${week2MaxRows}">
                            ${Number(userData?.overtime_hours_week_2 || 0).toFixed(2)}
                        </td>` : ''}
                    </tr>
                `;
            }
            // Add separator row with a slight background for better visual separation
            tableHtml += `
                <tr class="bg-gray-50 border-t border-gray-200">
                    <td colspan="9" class="h-4"></td>
                </tr>
            `;
        });
    } else {
        tableHtml += `
            <tr>
                <td colspan="9" class="px-6 py-16 text-center text-gray-600 bg-white rounded-b-lg">
                    <svg class="mx-auto h-20 w-20 text-gray-400 mb-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                        <path vector-effect="non-scaling-stroke" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1H3z" />
                    </svg>
                    <h3 class="mt-2 text-2xl font-semibold text-gray-900">No Time Entries Found</h3>
                    <p class="mt-1 text-lg text-gray-500">
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
            exportButton.classList.remove('opacity-50', 'cursor-not-allowed', 'bg-gray-400', 'hover:bg-gray-400');
            exportButton.classList.add('bg-blue-600', 'hover:bg-blue-700', 'focus:ring-blue-500'); // Add active styles
        } else {
            exportButton.disabled = true;
            exportButton.classList.add('opacity-50', 'cursor-not-allowed', 'bg-gray-400', 'hover:bg-gray-400'); // Dim and disable
            exportButton.classList.remove('bg-blue-600', 'hover:bg-blue-700', 'focus:ring-blue-500'); // Remove active styles
        }
    }
}