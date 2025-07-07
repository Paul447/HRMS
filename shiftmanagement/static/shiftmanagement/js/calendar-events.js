// static/js/calendar-events.js

// Removed showLoading, hideLoading from import list
import { DOMElements } from './dom-elements.js';
import { getSelectedEmployees, setSelectedEmployees } from './multi-select.js';
import { renderCalendar } from './calendar-renderer.js';

export let allEvents = [];
export let paginationData = {};

/**
 * Fetches events for a given year and month from the API.
 * @param {number} year
 * @param {number} month
 */
export async function fetchEvents(year, month) {
    // window.showLoading(); // Call the global function
    try {
        const response = await fetch(`/api/calendar-events/?year=${year}&month=${month}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        

        allEvents = data.calendar_events.map(event => ({
            ...event,
            extendedProps: {
                ...event.extendedProps,
                employee_names: Array.isArray(event.extendedProps.employee_names)
                    ? event.extendedProps.employee_names
                    : (event.extendedProps.employee_names ? [event.extendedProps.employee_names] : []),
                employee_ids: Array.isArray(event.extendedProps.employee_ids)
                    ? event.extendedProps.employee_ids.map(String)
                    : (event.extendedProps.employee_ids ? [String(event.extendedProps.employee_ids)] : [])
            }
        }));
        paginationData = data.pagination;
        applyFilters(); // Apply filters after new events are fetched
    } catch (error) {
        console.error('Error fetching events:', error);
        alert('Failed to load calendar events. Please try again.');
    } finally {
        window.hideLoading(); // Call the global function
    }
}

/**
 * Applies filters to the fetched events and renders the calendar.
 */
export function applyFilters() {
    const selectedSquadId = DOMElements.squadFilter.value;
    const selectedEmployees = getSelectedEmployees();

    const filteredEvents = allEvents.filter(event => {
        const matchesSquad = !selectedSquadId || String(event.extendedProps.squad_id) === selectedSquadId;
        const matchesEmployee = selectedEmployees.length === 0 ||
            event.extendedProps.employee_ids?.some(id => selectedEmployees.includes(id));
        return matchesSquad && matchesEmployee;
    });
    renderCalendar(filteredEvents);
}

/**
 * Resets all filters to their default state.
 */
export function resetFilters() {
    DOMElements.squadFilter.value = '';
    setSelectedEmployees([]);
    applyFilters();
}