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
            <div class="flex flex-col items-center justify-center py-20 text-gray-500 bg-white rounded-2xl shadow-xl mx-auto my-8 max-w-3xl border border-gray-200">
                <svg class="w-24 h-24 mb-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <p class="text-3xl font-extrabold text-gray-800 mb-3">No Report Data Available</p>
                <p class="text-xl text-gray-600 mb-6 text-center px-8 leading-relaxed">It seems there's no clock data for the selected pay period. Please try a different period or check back later.</p>
                <p class="text-base text-gray-500 mt-2">If the issue persists, please contact support.</p>
            </div>
        `;
        return;
    }

    const payPeriodStartDate = data.pay_period.start_date_local || 'N/A';
    const payPeriodEndDate = data.pay_period.end_date_local || 'N/A';

    let tableHtml = `
        <div class="bg-white p-8 rounded-2xl shadow-2xl mb-10 border border-gray-100">
            <h2 class="text-3xl sm:text-4xl font-extrabold mb-4 text-gray-900 text-center">
                Employee Clock Data Report
            </h2>
            <p class="text-xl text-gray-700 text-center mb-8">
                Pay Period: <span class="text-blue-700 font-extrabold">${payPeriodStartDate} to ${payPeriodEndDate}</span>
            </p>

            <div class="p-5 bg-blue-50 rounded-xl border border-blue-200 text-sm shadow-inner">
                <h3 class="font-bold text-blue-800 mb-4 text-lg">Color Legend:</h3>
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-y-3 gap-x-6">
                    <div class="flex items-center">
                        <span class="inline-block w-4 h-4 min-w-[1rem] rounded-full bg-gray-800 mr-2.5 border border-gray-300 shadow-sm"></span>
                        <span class="text-gray-700 font-medium">Punch (Regular Clock In/Out)</span>
                    </div>
                    <div class="flex items-center">
                        <span class="inline-block w-4 h-4 min-w-[1rem] rounded-full bg-green-600 mr-2.5 border border-green-300 shadow-sm"></span>
                        <span class="text-gray-700 font-medium">Holiday Pay</span>
                    </div>
                    <div class="flex items-center">
                        <span class="inline-block w-4 h-4 min-w-[1rem] rounded-full bg-purple-600 mr-2.5 border border-purple-300 shadow-sm"></span>
                        <span class="text-gray-700 font-medium">PTO / Other Pay Types</span>
                    </div>
                    <div class="flex items-center">
                        <span class="inline-block w-4 h-4 min-w-[1rem] rounded-sm bg-green-100 mr-2.5 border border-green-300 shadow-sm"></span>
                        <span class="text-gray-700 font-medium">Holiday Entry Row</span>
                    </div>
                    <div class="flex items-center">
                        <span class="inline-block w-4 h-4 min-w-[1rem] rounded-full bg-red-600 mr-2.5 border border-red-300 shadow-sm"></span>
                        <span class="text-gray-700 font-medium">Overtime Hours (Highlighted)</span>
                    </div>
                     <div class="flex items-center">
                        <span class="inline-block w-4 h-4 min-w-[1rem] rounded-full bg-yellow-400 mr-2.5 border border-yellow-300 shadow-sm"></span>
                        <span class="text-gray-700 font-medium">Active Punch (Currently Clocked In)</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="overflow-x-auto relative shadow-2xl rounded-2xl border border-gray-100">
            <table class="w-full text-base text-left text-gray-700" id="clockDataTable">
                <thead class="text-xs text-gray-700 uppercase bg-gray-100 border-b-2 border-gray-200">
                    <tr>
                        <th scope="col" class="px-4 py-3 border-r border-gray-200 font-bold tracking-wider sticky left-0 bg-gray-100 z-10 whitespace-nowrap" rowspan="2">
                            Employee
                        </th>
                        <th scope="col" class="px-4 py-3 border-r border-gray-200 font-bold tracking-wider text-center whitespace-nowrap" rowspan="2">
                            Summary
                        </th>
                        <th scope="col" class="px-4 py-3 text-center border-b border-gray-200 font-bold tracking-wider whitespace-nowrap" colspan="4">
                            Time Entry Details
                        </th>
                        <th scope="col" class="px-4 py-3 border-l border-gray-200 font-bold tracking-wider text-center whitespace-nowrap" rowspan="2">
                            Regular Hrs
                        </th>
                        <th scope="col" class="px-4 py-3 border-l border-gray-200 font-bold tracking-wider text-center whitespace-nowrap" rowspan="2">
                            OT Hrs
                        </th>
                        <th scope="col" class="px-4 py-3 border-l border-gray-200 font-bold tracking-wider text-center whitespace-nowrap" rowspan="2">
                            Total Hrs
                        </th>
                    </tr>
                    <tr>
                        <th scope="col" class="px-4 py-3 border-r border-gray-200 font-semibold text-center whitespace-nowrap">
                            IN / Start
                        </th>
                        <th scope="col" class="px-4 py-3 border-r border-gray-200 font-semibold text-center whitespace-nowrap">
                            OUT / End
                        </th>
                        <th scope="col" class="px-4 py-3 border-r border-gray-200 font-semibold text-center whitespace-nowrap">
                            Duration
                        </th>
                        <th scope="col" class="px-4 py-3 font-semibold text-center whitespace-nowrap">
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
                    type: entry?.leave_type || 'Time Off', // Default to 'Time Off' if leave_type is missing
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
                    type: entry?.leave_type|| 'Time Off', // Default to 'Time Off' if leave_type is missing
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
                // Check if it's a known PTO/Leave type (e.g., if type is not "Punch" or "Holiday")
                const isPTO = entry && !isPunch && !isHoliday;


                tableHtml += `
                    <tr class="bg-white border-b border-gray-100 hover:bg-gray-50 ${isHoliday ? 'bg-green-50' : ''}">
                        ${i === 0 ? `<td class="px-4 py-3 font-semibold text-gray-900 whitespace-nowrap border-r border-gray-200 text-base align-top sticky left-0 bg-white z-10 shadow-sm" rowspan="${totalRowsForEmployee}">
                            ${employeeName}
                        </td>` : ''}

                        ${i === 0 ? `<td class="px-4 py-3 whitespace-nowrap text-gray-900 border-r border-gray-200 text-xs align-middle bg-blue-50/50" rowspan="${week1MaxRows}">
                            <span class="font-bold text-blue-800 text-sm">Week 1 Summary</span><br>
                            <span class="text-xxs text-gray-700">Punch: <span class="font-semibold">${Number(userData?.week_1_total_hours || 0).toFixed(2)} hrs</span></span><br>
                            <span class="text-xxs text-gray-700">Time off: <span class="font-semibold">${Number(userData?.week_1_pto_total_hours || 0).toFixed(2)} hrs</span></span><br>
                            <span class="text-xxs text-gray-700">Holiday: <span class="font-semibold">${Number(userData?.week_1_holiday_total_hours || 0).toFixed(2)} hrs</span></span>
                        </td>` : ''}

                        <td class="px-4 py-2 whitespace-nowrap text-center">
                            ${entry ? `
                                <div class="text-gray-900 font-medium text-sm">${(isPunch || isHoliday) ? formatDate(entry.clock_in_time) : formatDate(entry.start_date_time)}</div>
                                <div class="text-gray-500 text-xs">${(isPunch || isHoliday) ? formatOnlyTime(entry.clock_in_time) : formatOnlyTime(entry.start_date_time)}</div>
                            ` : '<span class="text-gray-400 text-xs">N/A</span>'}
                        </td>
                        <td class="px-4 py-2 whitespace-nowrap text-center">
                            ${(isPunch || isHoliday) ? (entry.clock_out_time ? `
                                <div class="text-gray-900 font-medium text-sm">${formatDate(entry.clock_out_time)}</div>
                                <div class="text-gray-500 text-xs">${formatOnlyTime(entry.clock_out_time)}</div>
                            ` : `<span class="inline-flex items-center text-yellow-600 font-semibold animate-pulse text-xs py-1 px-2 bg-yellow-100 rounded-md">
                                <span class="relative flex h-2.5 w-2.5 mr-1">
                                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span>
                                    <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-yellow-500"></span>
                                </span>
                                Active
                            </span>`) : (isPTO && entry.end_date_time ? `
                                <div class="text-gray-900 font-medium text-sm">${formatDate(entry.end_date_time)}</div>
                                <div class="text-gray-500 text-xs">${formatOnlyTime(entry.end_date_time)}</div>
                            ` : '<span class="text-gray-400 text-xs">N/A</span>')}
                        </td>
                        <td class="px-4 py-2 whitespace-nowrap border-r border-gray-200 text-center">
                            ${entry ? `<span class="font-bold text-gray-900 text-base">
                                ${Number((isPunch || isHoliday) ? entry.hours_worked : entry.total_hours || 0).toFixed(2)} <span class="font-normal text-sm text-gray-600">hrs</span>
                            </span>` : '<span class="text-gray-400 text-sm">0.00 <span class="font-normal text-xs">hrs</span></span>'}
                        </td>
                        <td class="px-4 py-2 whitespace-nowrap text-center">
                            ${entry ? `<span class="font-semibold text-xs py-1 px-2 rounded-md ${isPunch ? 'bg-gray-100 text-gray-800' : (isHoliday ? 'bg-green-100 text-green-700' : 'bg-purple-100 text-purple-700')}">${entry.type}</span>` : '<span class="text-gray-400 text-xs">N/A</span>'}
                        </td>

                        ${i === 0 ? `<td class="px-4 py-3 whitespace-nowrap text-gray-900 border-l border-gray-200 text-base font-bold align-middle text-center bg-gray-50/50" rowspan="${week1MaxRows}">
                            ${Number(userData?.regular_hours_week_1 || 0).toFixed(2)}
                        </td>` : ''}
                        ${i === 0 ? `<td class="px-4 py-3 whitespace-nowrap text-gray-900 border-l border-gray-200 text-base font-bold align-middle text-center bg-gray-50/50 ${Number(userData?.overtime_hours_week_1 || 0) > 0 ? 'text-red-600' : ''}" rowspan="${week1MaxRows}">
                            ${Number(userData?.overtime_hours_week_1 || 0).toFixed(2)}
                        </td>` : ''}

                        ${i === 0 ? `<td class="px-4 py-3 whitespace-nowrap text-blue-800 font-extrabold text-xl border-l border-gray-200 align-middle text-center bg-blue-100/50" rowspan="${totalRowsForEmployee}">
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
                    <tr class="bg-white border-b border-gray-100 hover:bg-gray-50 ${isHoliday ? 'bg-green-50' : ''}">
                        ${i === 0 ? `<td class="px-4 py-3 whitespace-nowrap text-gray-900 border-r border-gray-200 text-xs align-middle bg-blue-50/50" rowspan="${week2MaxRows}">
                            <span class="font-bold text-blue-800 text-sm">Week 2 Summary</span><br>
                            <span class="text-xxs text-gray-700">Punch: <span class="font-semibold">${Number(userData?.week_2_total_hours || 0).toFixed(2)} hrs</span></span><br>
                            <span class="text-xxs text-gray-700">Time off: <span class="font-semibold">${Number(userData?.week_2_pto_total_hours || 0).toFixed(2)} hrs</span></span><br>
                            <span class="text-xxs text-gray-700">Holiday: <span class="font-semibold">${Number(userData?.week_2_holiday_total_hours || 0).toFixed(2)} hrs</span></span>
                        </td>` : ''}

                        <td class="px-4 py-2 whitespace-nowrap text-center">
                            ${entry ? `
                                <div class="text-gray-900 font-medium text-sm">${(isPunch || isHoliday) ? formatDate(entry.clock_in_time) : formatDate(entry.start_date_time)}</div>
                                <div class="text-gray-500 text-xs">${(isPunch || isHoliday) ? formatOnlyTime(entry.clock_in_time) : formatOnlyTime(entry.start_date_time)}</div>
                            ` : '<span class="text-gray-400 text-xs">N/A</span>'}
                        </td>
                        <td class="px-4 py-2 whitespace-nowrap text-center">
                            ${(isPunch || isHoliday) ? (entry.clock_out_time ? `
                                <div class="text-gray-900 font-medium text-sm">${formatDate(entry.clock_out_time)}</div>
                                <div class="text-gray-500 text-xs">${formatOnlyTime(entry.clock_out_time)}</div>
                            ` : `<span class="inline-flex items-center text-yellow-600 font-semibold animate-pulse text-xs py-1 px-2 bg-yellow-100 rounded-md">
                                <span class="relative flex h-2.5 w-2.5 mr-1">
                                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span>
                                    <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-yellow-500"></span>
                                </span>
                                Active
                            </span>`) : (isPTO && entry.end_date_time ? `
                                <div class="text-gray-900 font-medium text-sm">${formatDate(entry.end_date_time)}</div>
                                <div class="text-gray-500 text-xs">${formatOnlyTime(entry.end_date_time)}</div>
                            ` : '<span class="text-gray-400 text-xs">N/A</span>')}
                        </td>
                        <td class="px-4 py-2 whitespace-nowrap border-r border-gray-200 text-center">
                            ${entry ? `<span class="font-bold text-gray-900 text-base">
                                ${Number((isPunch || isHoliday) ? entry.hours_worked : entry.time_off_duration || 0).toFixed(2)} <span class="font-normal text-sm text-gray-600">hrs</span>
                            </span>` : '<span class="text-gray-400 text-sm">0.00 <span class="font-normal text-xs">hrs</span></span>'}
                        </td>
                        <td class="px-4 py-2 whitespace-nowrap text-center">
                            ${entry ? `<span class="font-semibold text-xs py-1 px-2 rounded-md ${isPunch ? 'bg-gray-100 text-gray-800' : (isHoliday ? 'bg-green-100 text-green-700' : 'bg-purple-100 text-purple-700')}">${entry.type}</span>` : '<span class="text-gray-400 text-xs">N/A</span>'}
                        </td>

                        ${i === 0 ? `<td class="px-4 py-3 whitespace-nowrap text-gray-900 border-l border-gray-200 text-base font-bold align-middle text-center bg-gray-50/50" rowspan="${week2MaxRows}">
                            ${Number(userData?.regular_hours_week_2 || 0).toFixed(2)}
                        </td>` : ''}
                        ${i === 0 ? `<td class="px-4 py-3 whitespace-nowrap text-gray-900 border-l border-gray-200 text-base font-bold align-middle text-center bg-gray-50/50 ${Number(userData?.overtime_hours_week_2 || 0) > 0 ? 'text-red-600' : ''}" rowspan="${week2MaxRows}">
                            ${Number(userData?.overtime_hours_week_2 || 0).toFixed(2)}
                        </td>` : ''}
                    </tr>
                `;
            }
            // Add separator row with a slight background for better visual separation
            tableHtml += `
                <tr class="bg-gray-100 border-t-2 border-gray-200">
                    <td colspan="9" class="h-6"></td>
                </tr>
            `;
        });
    } else {
        tableHtml += `
            <tr>
                <td colspan="9" class="px-8 py-20 text-center text-gray-600 bg-white rounded-b-2xl">
                    <svg class="mx-auto h-24 w-24 text-gray-400 mb-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                        <path vector-effect="non-scaling-stroke" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1H3z" />
                    </svg>
                    <h3 class="mt-2 text-3xl font-bold text-gray-900 mb-3">No Time Entries Found</h3>
                    <p class="mt-1 text-xl text-gray-600 leading-relaxed">
                        There are no clock data entries for any employee in this selected pay period.
                    </p>
                    <p class="mt-3 text-base text-gray-500">Try selecting a different pay period above.</p>
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
            exportButton.classList.add('bg-green-600', 'hover:bg-green-700', 'focus:ring-green-500'); // Add active styles
        } else {
            exportButton.disabled = true;
            exportButton.classList.add('opacity-50', 'cursor-not-allowed', 'bg-gray-400', 'hover:bg-gray-400'); // Dim and disable
            exportButton.classList.remove('bg-green-600', 'hover:bg-green-700', 'focus:ring-green-500'); // Remove active styles
        }
    }
}
