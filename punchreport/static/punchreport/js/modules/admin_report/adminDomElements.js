// static/js/modules/admin_report/adminDomElements.js

/**
 * Gets references to all necessary DOM elements for the Admin Clock Data Report page.
 * @returns {Object} An object containing references to DOM elements.
 */
export function getAdminReportDomElements() {
    return {
        payPeriodSelector: document.getElementById('payPeriodSelector'),
        exportExcelButton: document.getElementById('exportExcelButton'),
        clockDataReportContainer: document.getElementById('clockDataReportContainer'),
    };
}