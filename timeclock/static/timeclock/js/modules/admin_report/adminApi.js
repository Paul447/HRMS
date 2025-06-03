// static/js/modules/admin_report/adminApi.js

import { smartFetch } from '../timeclock/apiService.js'; // Assuming apiService is one level up

/**
 * Fetches a list of available pay periods from the API.
 * @returns {Promise<Array>} - A promise that resolves to an array of pay period objects.
 * @throws {Error} - Throws if the API call fails.
 */
export async function getPayPeriodsAdmin() {
    try {
        const response = await smartFetch('/api/clock/pay_periods/', {
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include'
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Failed to fetch pay periods: ${errorData.detail || errorData.message || response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Error in getPayPeriodsAdmin:", error);
        throw error;
    }
}

/**
 * Fetches aggregated clock data for a specific pay period from the API.
 * @param {string} payPeriodId - The ID of the pay period.
 * @returns {Promise<Object>} - A promise that resolves to the clock data object.
 * @throws {Error} - Throws if the API call fails.
 */
export async function getClockDataAdmin(payPeriodId) {
    try {
        const response = await smartFetch(`/api/clock/?pay_period_id=${payPeriodId}`, {
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include'
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Failed to fetch clock data: ${errorData.detail || errorData.message || response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Error in getClockDataAdmin:", error);
        throw error;
    }
}