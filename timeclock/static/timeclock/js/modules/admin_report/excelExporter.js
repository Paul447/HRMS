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

    // Set column widths
    worksheet.columns = [
        { width: 25 }, // A: Employee
        { width: 15 }, // B: Week Total
        { width: 20 }, // C: Week Punches - IN
        { width: 20 }, // D: Week Punches - OUT
        { width: 15 }, // E: Punches Duration
        { width: 10 }, // F: Regular
        { width: 10 }, // G: OT
        { width: 15 }  // H: Total Hours
    ];

    // Add headers
    worksheet.addRow(["Employee", "Week Total", "Week Punches", "", "Punches Duration", "Regular", "OT", "Total Hours"]);
    worksheet.addRow(["", "", "IN", "OUT", "", "", "", ""]);

    // Merge header cells
    worksheet.mergeCells('A1:A2');
    worksheet.mergeCells('B1:B2');
    worksheet.mergeCells('C1:D1');
    worksheet.mergeCells('E1:E2');
    worksheet.mergeCells('F1:F2');
    worksheet.mergeCells('G1:G2');
    worksheet.mergeCells('H1:H2');

    // Style headers
    worksheet.getRow(1).eachCell(cell => {
        cell.font = { bold: true };
        cell.alignment = { vertical: 'middle', horizontal: 'center' };
    });
    worksheet.getRow(2).eachCell(cell => {
        cell.font = { bold: true };
        cell.alignment = { vertical: 'middle', horizontal: 'center' };
    });

    let currentRow = 3;

    if (!data || !data.users_clock_data) {
        console.error('No report data available to export:', data);
        alert('No report data available to export.');
        return;
    }

    data.users_clock_data.forEach(userData => {
        const employeeName = `${userData.first_name} ${userData.last_name}`;
        // Change this line:
const totalHoursCombined = parseFloat((parseFloat(userData.week_1_total_hours || 0) + parseFloat(userData.week_2_total_hours || 0)).toFixed(2));

        const week1Total = parseFloat(userData.week_1_total_hours || 0).toFixed(2);
        const week2Total = parseFloat(userData.week_2_total_hours || 0).toFixed(2);
        const week1Regular = parseFloat(userData.regular_hours_week_1 || 0);
        const week1OT = parseFloat(userData.overtime_hours_week_1 || 0);
        const week2Regular = parseFloat(userData.regular_hours_week_2 || 0);
        const week2OT = parseFloat(userData.overtime_hours_week_2 || 0);

        const week1Punches = userData.week_1_entries || [];
        const week2Punches = userData.week_2_entries || [];

        const week1RowsCount = Math.max(1, week1Punches.length);
        const week2RowsCount = Math.max(1, week2Punches.length);

        const employeeBlockStartRow = currentRow;

        // Week 1 block
        for (let i = 0; i < week1RowsCount; i++) {
            const punch1 = week1Punches[i];
            const row = worksheet.addRow([
                i === 0 ? employeeName : "",
                i === 0 ? `Week 1 = ${week1Total}` : "",
                punch1 ? `${new Date(punch1.clock_in_time).toLocaleDateString()} ${new Date(punch1.clock_in_time).toLocaleTimeString()}` : (i === 0 && week1Punches.length === 0 ? "No Punches" : ""),
                punch1 && punch1.clock_out_time ? `${new Date(punch1.clock_out_time).toLocaleDateString()} ${new Date(punch1.clock_out_time).toLocaleTimeString()}` : (punch1 ? 'Active' : ''),
                punch1 ? parseFloat(punch1.hours_worked || 0) : (i === 0 && week1Punches.length === 0 ? 0 : ""),
                i === 0 ? week1Regular : "",
                i === 0 ? week1OT : "",
                i === 0 ? totalHoursCombined : ""
            ]);

            // Format relevant cells as numbers with two decimals
            row.getCell('E').numFmt = '0.00';
            row.getCell('F').numFmt = '0.00';
            row.getCell('G').numFmt = '0.00';
            row.getCell('H').numFmt = '0.00';

            // Highlight OT cell (column G) if non-zero
            if (i === 0 && week1OT > 0) {
                row.getCell('G').fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFF0000' } }; // Red
            }
            currentRow++;
        }

        if (week1RowsCount > 1) {
            worksheet.mergeCells(`B${employeeBlockStartRow}:B${employeeBlockStartRow + week1RowsCount - 1}`);
            worksheet.mergeCells(`F${employeeBlockStartRow}:F${employeeBlockStartRow + week1RowsCount - 1}`);
            worksheet.mergeCells(`G${employeeBlockStartRow}:G${employeeBlockStartRow + week1RowsCount - 1}`);
        }

        const week2BlockStartRow = currentRow;

        // Week 2 block
        for (let i = 0; i < week2RowsCount; i++) {
            const punch2 = week2Punches[i];
            const row = worksheet.addRow([
                "",
                i === 0 ? `Week 2 = ${week2Total}` : "",
                punch2 ? `${new Date(punch2.clock_in_time).toLocaleDateString()} ${new Date(punch2.clock_in_time).toLocaleTimeString()}` : (i === 0 && week2Punches.length === 0 ? "No Punches" : ""),
                punch2 && punch2.clock_out_time ? `${new Date(punch2.clock_out_time).toLocaleDateString()} ${new Date(punch2.clock_out_time).toLocaleTimeString()}` : (punch2 ? 'Active' : ''),
                punch2 ? parseFloat(punch2.hours_worked || 0) : (i === 0 && week2Punches.length === 0 ? 0 : ""),
                i === 0 ? week2Regular : "",
                i === 0 ? week2OT : "",
                "" // Total hours already in the first row of the employee block
            ]);

            // Format relevant cells as numbers with two decimals
            row.getCell('E').numFmt = '0.00';
            row.getCell('F').numFmt = '0.00';
            row.getCell('G').numFmt = '0.00';


            // Highlight OT cell (column G) if non-zero
            if (i === 0 && week2OT > 0) {
                row.getCell('G').fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFF0000' } }; // Red
            }
            currentRow++;
        }

        if (week2RowsCount > 1) {
            worksheet.mergeCells(`B${week2BlockStartRow}:B${week2BlockStartRow + week2RowsCount - 1}`);
            worksheet.mergeCells(`F${week2BlockStartRow}:F${week2BlockStartRow + week2RowsCount - 1}`);
            worksheet.mergeCells(`G${week2BlockStartRow}:G${week2BlockStartRow + week2RowsCount - 1}`);
        }

        // Merge Employee and Total Hours
        if (currentRow - employeeBlockStartRow > 1) {
            worksheet.mergeCells(`A${employeeBlockStartRow}:A${currentRow - 1}`);
            worksheet.mergeCells(`H${employeeBlockStartRow}:H${currentRow - 1}`);
        }

        // Add blank row for separation
        worksheet.addRow(["", "", "", "", "", "", "", ""]);
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