import { formatDate, formatOnlyTime } from '../timeclock/utils.js';

/**
 * Exports the provided clock data to an XLSX file using ExcelJS.
 *
 * @param {Object} data - The clock data report object.
 * @param {string} filename - The desired filename for the exported Excel file.
 */
export async function exportAdminReportToXLSX(data, filename) {
    if (typeof ExcelJS === 'undefined') {
        console.error('ExcelJS library not loaded. Include it via CDN or npm.');
        alert('ExcelJS library is required to export the file.');
        return;
    }

    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('Clock Data Report');

    // Set column widths
    worksheet.columns = [
        { width: 25 }, // A: Employee
        { width: 15 }, // B: Week
        { width: 22 }, // C: IN / Start
        { width: 22 }, // D: OUT / End
        { width: 15 }, // E: Duration
        { width: 15 }, // F: Type
        { width: 12 }, // G: Regular Hrs
        { width: 12 }, // H: OT Hrs
        { width: 15 }  // I: Total Hrs
    ];

    // Add headers
    worksheet.addRow([
        "Employee",
        "Week",
        "IN / Start",
        "OUT / End",
        "Duration",
        "Type",
        "Regular Hrs",
        "OT Hrs",
        "Total Hrs"
    ]);

    // Style headers
    worksheet.getRow(1).eachCell(cell => {
        cell.font = { bold: true };
        cell.alignment = { vertical: 'middle', horizontal: 'center' };
        cell.fill = {
            type: 'pattern',
            pattern: 'solid',
            fgColor: { argb: 'FFE0E0E0' } // Light gray
        };
        cell.border = {
            top: { style: 'thin' },
            left: { style: 'thin' },
            bottom: { style: 'thin' },
            right: { style: 'thin' }
        };
    });

    let currentRow = 2;

    if (!data?.users_clock_data?.length) {
        worksheet.addRow(['', '', '', '', '', '', '', '', '']);
        worksheet.mergeCells(`A${currentRow}:I${currentRow}`);
        worksheet.getCell(`A${currentRow}`).value = 'No time entries found for this pay period.';
        worksheet.getCell(`A${currentRow}`).alignment = { horizontal: 'center', vertical: 'middle' };
        worksheet.getCell(`A${currentRow}`).font = { italic: true, color: { argb: 'FF808080' } };
        worksheet.getRow(currentRow).height = 40;
        console.warn('No report data available to export.');
        try {
            const buffer = await workbook.xlsx.writeBuffer();
            const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = filename;
            link.click();
            URL.revokeObjectURL(link.href);
        } catch (error) {
            console.error('Error generating XLSX file:', error);
            alert('Failed to generate XLSX file. Check console for details.');
        }
        return;
    }

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
            ...(userData?.week_1_entries || []).map(entry => ({
                isPunch: true,
                isHoliday: false,
                type: 'Punch',
                start: entry.clock_in_time,
                end: entry.clock_out_time,
                duration: Number(entry.hours_worked || 0),
                sortTime: entry.clock_in_time
            })),
            ...(userData?.week_1_holiday_entries || []).map(entry => ({
                isPunch: false,
                isHoliday: true,
                type: 'Holiday',
                start: entry.clock_in_time,
                end: entry.clock_out_time,
                duration: Number(entry.hours_worked || 0),
                sortTime: entry.clock_in_time
            })),
            ...(userData?.week_1_pto_entries || []).map(entry => ({
                isPunch: false,
                isHoliday: false,
                type: entry?.pay_types_display?.name || 'PTO',
                start: entry.start_date_time,
                end: entry.end_date_time,
                duration: Number(entry.total_hours || 0),
                sortTime: entry.start_date_time
            }))
        ].sort((a, b) => new Date(a.sortTime || 0) - new Date(b.sortTime || 0));

        // Combine punches, holidays, and PTO entries for Week 2
        const week2CombinedEntries = [
            ...(userData?.week_2_entries || []).map(entry => ({
                isPunch: true,
                isHoliday: false,
                type: 'Punch',
                start: entry.clock_in_time,
                end: entry.clock_out_time,
                duration: Number(entry.hours_worked || 0),
                sortTime: entry.clock_in_time
            })),
            ...(userData?.week_2_holiday_entries || []).map(entry => ({
                isPunch: false,
                isHoliday: true,
                type: 'Holiday',
                start: entry.clock_in_time,
                end: entry.clock_out_time,
                duration: Number(entry.hours_worked || 0),
                sortTime: entry.clock_in_time
            })),
            ...(userData?.week_2_pto_entries || []).map(entry => ({
                isPunch: false,
                isHoliday: false,
                type: entry?.pay_types_display?.name || 'PTO',
                start: entry.start_date_time,
                end: entry.end_date_time,
                duration: Number(entry.total_hours || 0),
                sortTime: entry.start_date_time
            }))
        ].sort((a, b) => new Date(a.sortTime || 0) - new Date(b.sortTime || 0));

        const week1RowsCount = Math.max(1, week1CombinedEntries.length);
        const week2RowsCount = Math.max(1, week2CombinedEntries.length);
        const employeeTotalRows = week1RowsCount + week2RowsCount;
        const employeeBlockStartRow = currentRow;

        // Week 1 Data
        for (let i = 0; i < week1RowsCount; i++) {
            const entry = week1CombinedEntries[i];
            const isPunch = entry?.isPunch;
            const isHoliday = entry?.isHoliday;
            const isPTO = entry && !isPunch && !isHoliday;

            let inOutFormatted = 'N/A';
            let outEndFormatted = 'N/A';
            let durationValue = 0;
            let typeValue = 'N/A';

            if (entry) {
                typeValue = entry.type;
                inOutFormatted = entry.start ? `${formatDate(entry.start)} ${formatOnlyTime(entry.start)}` : 'N/A';
                durationValue = entry.duration;
                if (isPunch || isHoliday) {
                    outEndFormatted = entry.end ? `${formatDate(entry.end)} ${formatOnlyTime(entry.end)}` : 'Active';
                } else if (isPTO) {
                    outEndFormatted = entry.end ? `${formatDate(entry.end)} ${formatOnlyTime(entry.end)}` : 'N/A';
                }
            }

            const row = worksheet.addRow([
                i === 0 ? employeeName : "",
                i === 0 ? `Week 1 (P: ${Number(userData?.week_1_total_hours || 0).toFixed(2)} / PTO: ${Number(userData?.week_1_pto_total_hours || 0).toFixed(2)} / H: ${Number(userData?.week_1_holiday_total_hours || 0).toFixed(2)})` : "",
                inOutFormatted,
                outEndFormatted,
                durationValue,
                typeValue,
                i === 0 ? Number(userData?.regular_hours_week_1 || 0) : "",
                i === 0 ? Number(userData?.overtime_hours_week_1 || 0) : "",
                i === 0 ? totalHoursCombined : ""
            ]);

            // Apply number format
            row.getCell('E').numFmt = '0.00';
            row.getCell('G').numFmt = '0.00';
            row.getCell('H').numFmt = '0.00';
            row.getCell('I').numFmt = '0.00';

            // Style for Type column (F)
            if (isPTO) {
                row.getCell('F').font = { color: { argb: 'FF800080' } }; // Purple for PTO
            } else if (isHoliday) {
                row.getCell('F').font = { color: { argb: 'FF008000' } }; // Green for Holiday
                row.getCell('A').fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFE6F3E6' } }; // Light green row
            }

            // Highlight OT cell (H) if non-zero
            if (i === 0 && Number(userData?.overtime_hours_week_1 || 0) > 0) {
                row.getCell('H').fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFFCCCC' } }; // Light red
            }

            currentRow++;
        }

        // Week 2 Data
        for (let i = 0; i < week2RowsCount; i++) {
            const entry = week2CombinedEntries[i];
            const isPunch = entry?.isPunch;
            const isHoliday = entry?.isHoliday;
            const isPTO = entry && !isPunch && !isHoliday;

            let inOutFormatted = 'N/A';
            let outEndFormatted = 'N/A';
            let durationValue = 0;
            let typeValue = 'N/A';

            if (entry) {
                typeValue = entry.type;
                inOutFormatted = entry.start ? `${formatDate(entry.start)} ${formatOnlyTime(entry.start)}` : 'N/A';
                durationValue = entry.duration;
                if (isPunch || isHoliday) {
                    outEndFormatted = entry.end ? `${formatDate(entry.end)} ${formatOnlyTime(entry.end)}` : 'Active';
                } else if (isPTO) {
                    outEndFormatted = entry.end ? `${formatDate(entry.end)} ${formatOnlyTime(entry.end)}` : 'N/A';
                }
            }

            const row = worksheet.addRow([
                "",
                i === 0 ? `Week 2 (P: ${Number(userData?.week_2_total_hours || 0).toFixed(2)} / PTO: ${Number(userData?.week_2_pto_total_hours || 0).toFixed(2)} / H: ${Number(userData?.week_2_holiday_total_hours || 0).toFixed(2)})` : "",
                inOutFormatted,
                outEndFormatted,
                durationValue,
                typeValue,
                i === 0 ? Number(userData?.regular_hours_week_2 || 0) : "",
                i === 0 ? Number(userData?.overtime_hours_week_2 || 0) : "",
                ""
            ]);

            // Apply number format
            row.getCell('E').numFmt = '0.00';
            row.getCell('G').numFmt = '0.00';
            row.getCell('H').numFmt = '0.00';

            // Style for Type column (F)
            if (isPTO) {
                row.getCell('F').font = { color: { argb: 'FF800080' } }; // Purple for PTO
            } else if (isHoliday) {
                row.getCell('F').font = { color: { argb: 'FF008000' } }; // Green for Holiday
                row.getCell('A').fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFE6F3E6' } }; // Light green row
            }

            // Highlight OT cell (H) if non-zero
            if (i === 0 && Number(userData?.overtime_hours_week_2 || 0) > 0) {
                row.getCell('H').fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFFCCCC' } }; // Light red
            }

            currentRow++;
        }

        // Merge cells
        if (employeeTotalRows > 1) {
            worksheet.mergeCells(`A${employeeBlockStartRow}:A${currentRow - 1}`);
            worksheet.mergeCells(`I${employeeBlockStartRow}:I${currentRow - 1}`);
        }
        if (week1RowsCount > 1) {
            worksheet.mergeCells(`B${employeeBlockStartRow}:B${employeeBlockStartRow + week1RowsCount - 1}`);
            worksheet.mergeCells(`G${employeeBlockStartRow}:G${employeeBlockStartRow + week1RowsCount - 1}`);
            worksheet.mergeCells(`H${employeeBlockStartRow}:H${employeeBlockStartRow + week1RowsCount - 1}`);
        }
        if (week2RowsCount > 1) {
            worksheet.mergeCells(`B${employeeBlockStartRow + week1RowsCount}:B${currentRow - 1}`);
            worksheet.mergeCells(`G${employeeBlockStartRow + week1RowsCount}:G${currentRow - 1}`);
            worksheet.mergeCells(`H${employeeBlockStartRow + week1RowsCount}:H${currentRow - 1}`);
        }

        // Add separator row
        worksheet.addRow([]);
        currentRow++;
    });

    // Save file
    try {
        const buffer = await workbook.xlsx.writeBuffer();
        const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        link.click();
        URL.revokeObjectURL(link.href);
        console.log('File generated successfully:', filename);
    } catch (error) {
        console.error('Error generating XLSX file:', error);
        alert('Failed to generate XLSX file. Check console for details.');
    }
}