// static/js/modules/admin_report/excelExporter.js

/**
 * Exports the provided clock data to an XLSX file using ExcelJS.
 *
 * @param {Object} data - The clock data report object.
 * @param {string} filename - The desired filename for the exported Excel file.
 */
export async function exportAdminReportToXLSX(data, filename) {
    // Check if ExcelJS is loaded globally (from CDN in your HTML)
    if (typeof ExcelJS === 'undefined') {
        console.error('ExcelJS library not loaded. Include it via CDN or npm.');
        alert('ExcelJS library is required to export the file.');
        return;
    }

    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('Clock Data Report');

    // Set column widths for the new merged structure
    worksheet.columns = [
        { width: 25 }, // A: Employee
        { width: 15 }, // B: Week
        { width: 22 }, // C: IN / Start
        { width: 22 }, // D: OUT / End
        { width: 15 }, // E: Duration
        { width: 15 }, // F: Type (Moved)
        { width: 12 }, // G: Regular Hrs
        { width: 12 }, // H: OT Hrs
        { width: 15 }  // I: Total Hrs (Combined)
    ];

    // Add headers for the simplified structure with Type moved
    worksheet.addRow([
        "Employee",
        "Week",
        "IN / Start",
        "OUT / End",
        "Duration",
        "Type", // Moved
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
            fgColor: { argb: 'FFE0E0E0' } // Light gray background
        };
        cell.border = {
            top: { style: 'thin' },
            left: { style: 'thin' },
            bottom: { style: 'thin' },
            right: { style: 'thin' }
        };
    });

    let currentRow = 2; // Start data from the second row since headers are on row 1

    if (!data || !data.users_clock_data || data.users_clock_data.length === 0) {
        worksheet.addRow(['', '', '', '', '', '', '', '', '']); // Add an empty row to show the message
        worksheet.mergeCells(`A${currentRow}:I${currentRow}`);
        worksheet.getCell(`A${currentRow}`).value = 'No time entries found for this pay period.';
        worksheet.getCell(`A${currentRow}`).alignment = { horizontal: 'center', vertical: 'middle' };
        worksheet.getCell(`A${currentRow}`).font = { italic: true, color: { argb: 'FF808080' } };
        worksheet.getRow(currentRow).height = 40; // Give it some height
        console.warn('No report data available to export.');
        return;
    }

    data.users_clock_data.forEach(userData => {
        const employeeName = `${userData.first_name} ${userData.last_name}`;
        const totalHoursCombined = (
            parseFloat(userData.week_1_total_hours || 0) +
            parseFloat(userData.week_2_total_hours || 0) +
            parseFloat(userData.week_1_pto_total_hours || 0) +
            parseFloat(userData.week_2_pto_total_hours || 0)
        ).toFixed(2);

        // --- Prepare combined entries for Week 1 ---
        const week1CombinedEntries = [
            ...(userData.week_1_entries || []).map(entry => ({
                isPunch: true,
                type: 'Punch',
                start: entry.clock_in_time,
                end: entry.clock_out_time,
                duration: parseFloat(entry.hours_worked || 0),
                sortTime: entry.clock_in_time
            })),
            ...(userData.week_1_pto_entries || []).map(entry => ({
                isPunch: false,
                type: entry.pay_types_display.name,
                start: entry.start_date_time,
                end: entry.end_date_time,
                duration: parseFloat(entry.total_hours || 0),
                sortTime: entry.start_date_time
            }))
        ].sort((a, b) => new Date(a.sortTime) - new Date(b.sortTime));

        // --- Prepare combined entries for Week 2 ---
        const week2CombinedEntries = [
            ...(userData.week_2_entries || []).map(entry => ({
                isPunch: true,
                type: 'Punch',
                start: entry.clock_in_time,
                end: entry.clock_out_time,
                duration: parseFloat(entry.hours_worked || 0),
                sortTime: entry.clock_in_time
            })),
            ...(userData.week_2_pto_entries || []).map(entry => ({
                isPunch: false,
                type: entry.pay_types_display.name,
                start: entry.start_date_time,
                end: entry.end_date_time,
                duration: parseFloat(entry.total_hours || 0),
                sortTime: entry.start_date_time
            }))
        ].sort((a, b) => new Date(a.sortTime) - new Date(b.sortTime));


        const week1RowsCount = Math.max(1, week1CombinedEntries.length);
        const week2RowsCount = Math.max(1, week2CombinedEntries.length);
        const employeeTotalRows = week1RowsCount + week2RowsCount;

        const employeeBlockStartRow = currentRow; // Row where this employee's block starts

        // --- Week 1 Data ---
        for (let i = 0; i < week1RowsCount; i++) {
            const entry = week1CombinedEntries[i];
            const isPunch = entry && entry.isPunch;
            const isPTO = entry && !entry.isPunch;

            let inOutFormatted = '';
            let outEndFormatted = '';
            let durationValue = 0;
            let typeValue = 'N/A';

            if (entry) {
                typeValue = entry.type;
                inOutFormatted = `${formatDate(entry.start)} ${formatOnlyTime(entry.start)}`;
                durationValue = entry.duration;

                if (isPunch) {
                    if (entry.end) {
                        outEndFormatted = `${formatDate(entry.end)} ${formatOnlyTime(entry.end)}`;
                    } else {
                        outEndFormatted = 'Active'; // For active punches
                    }
                } else if (isPTO) {
                    outEndFormatted = `${formatDate(entry.end)} ${formatOnlyTime(entry.end)}`;
                }
            } else {
                // Handle cases where there are no entries for a week (placeholder row)
                inOutFormatted = 'N/A';
                outEndFormatted = 'N/A';
            }

            const row = worksheet.addRow([
                i === 0 ? employeeName : "", // Employee name only on the first row of their block
                i === 0 ? `Week 1 (P: ${parseFloat(userData.week_1_total_hours || 0).toFixed(2)} / PTO: ${parseFloat(userData.week_1_pto_total_hours || 0).toFixed(2)})` : "",
                inOutFormatted,
                outEndFormatted,
                durationValue,
                typeValue, // Moved
                i === 0 ? parseFloat(userData.regular_hours_week_1 || 0) : "",
                i === 0 ? parseFloat(userData.overtime_hours_week_1 || 0) : "",
                i === 0 ? parseFloat(totalHoursCombined) : ""
            ]);

            // Apply number format to duration and hour totals
            row.getCell('E').numFmt = '0.00'; // Duration is now E
            row.getCell('G').numFmt = '0.00';
            row.getCell('H').numFmt = '0.00';
            row.getCell('I').numFmt = '0.00';

            // Style for PTO type (now column F)
            if (isPTO) {
                row.getCell('F').font = { color: { argb: 'FF0000FF' } }; // Purple color for PTO type
            }

            // Highlight OT cell (column H) if non-zero
            if (i === 0 && parseFloat(userData.overtime_hours_week_1 || 0) > 0) {
                row.getCell('H').fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFFCCCC' } }; // Light Red
            }
            currentRow++;
        }

        // --- Week 2 Data ---
        for (let i = 0; i < week2RowsCount; i++) {
            const entry = week2CombinedEntries[i];
            const isPunch = entry && entry.isPunch;
            const isPTO = entry && !entry.isPunch;

            let inOutFormatted = '';
            let outEndFormatted = '';
            let durationValue = 0;
            let typeValue = 'N/A';

            if (entry) {
                typeValue = entry.type;
                inOutFormatted = `${formatDate(entry.start)} ${formatOnlyTime(entry.start)}`;
                durationValue = entry.duration;

                if (isPunch) {
                    if (entry.end) {
                        outEndFormatted = `${formatDate(entry.end)} ${formatOnlyTime(entry.end)}`;
                    } else {
                        outEndFormatted = 'Active'; // For active punches
                    }
                } else if (isPTO) {
                    outEndFormatted = `${formatDate(entry.end)} ${formatOnlyTime(entry.end)}`;
                }
            } else {
                inOutFormatted = 'N/A';
                outEndFormatted = 'N/A';
            }

            const row = worksheet.addRow([
                "", // Employee name is merged
                i === 0 ? `Week 2 (P: ${parseFloat(userData.week_2_total_hours || 0).toFixed(2)} / PTO: ${parseFloat(userData.week_2_pto_total_hours || 0).toFixed(2)})` : "",
                inOutFormatted,
                outEndFormatted,
                durationValue,
                typeValue, // Moved
                i === 0 ? parseFloat(userData.regular_hours_week_2 || 0) : "",
                i === 0 ? parseFloat(userData.overtime_hours_week_2 || 0) : "",
                "" // Total hours already in the first row of the employee block
            ]);

            // Apply number format to duration and hour totals
            row.getCell('E').numFmt = '0.00'; // Duration is now E
            row.getCell('G').numFmt = '0.00';
            row.getCell('H').numFmt = '0.00';

            // Style for PTO type (now column F)
            if (isPTO) {
                row.getCell('F').font = { color: { argb: 'FF0000FF' } }; // Bright Blue
            }

            // Highlight OT cell (column H) if non-zero
            if (i === 0 && parseFloat(userData.overtime_hours_week_2 || 0) > 0) {
                row.getCell('H').fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFFCCCC' } }; // Light Red
            }
            currentRow++;
        }

        // --- Merge cells after all rows for the employee are added ---
        if (employeeTotalRows > 1) {
            // Merge Employee column (A)
            worksheet.mergeCells(`A${employeeBlockStartRow}:A${currentRow - 1}`);
            // Merge Total Hours column (I)
            worksheet.mergeCells(`I${employeeBlockStartRow}:I${currentRow - 1}`);
        }

        // Merge Week column (B) for Week 1
        if (week1RowsCount > 1) {
            worksheet.mergeCells(`B${employeeBlockStartRow}:B${employeeBlockStartRow + week1RowsCount - 1}`);
            worksheet.mergeCells(`G${employeeBlockStartRow}:G${employeeBlockStartRow + week1RowsCount - 1}`); // Regular Hrs Week 1
            worksheet.mergeCells(`H${employeeBlockStartRow}:H${employeeBlockStartRow + week1RowsCount - 1}`); // OT Hrs Week 1
        }

        // Merge Week column (B) for Week 2
        if (week2RowsCount > 1) {
            worksheet.mergeCells(`B${employeeBlockStartRow + week1RowsCount}:B${currentRow - 1}`);
            worksheet.mergeCells(`G${employeeBlockStartRow + week1RowsCount}:G${currentRow - 1}`); // Regular Hrs Week 2
            worksheet.mergeCells(`H${employeeBlockStartRow + week1RowsCount}:H${currentRow - 1}`); // OT Hrs Week 2
        }

        // Add blank row for separation between employees
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

// Helper functions (assuming these are available in your utils.js or defined here)
// Make sure to define these or import them if they are from another module.
function formatDate(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString);
    // Example: "Jun 03"
    return date.toLocaleDateString('en-US', {year: 'numeric', month: 'numeric', day: '2-digit', weekday: 'short' });
}

function formatOnlyTime(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString);
    // Example: "06:00 AM"
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hourCycle: 'h23'});
}