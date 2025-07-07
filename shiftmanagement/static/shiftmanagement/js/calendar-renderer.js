// static/js/calendar-renderer.js

import { DOMElements } from './dom-elements.js'; // Keep DOMElements import
import { formatModalDate, getEmployeeDisplayNames } from './utils.js';
import { fetchEvents } from './calendar-events.js';

let calendarInstance;
export let currentYear = new Date().getFullYear();
export let currentMonth = new Date().getMonth() + 1;
let currentlyRenderedEvents = [];

/**
 * Renders or updates the FullCalendar instance with provided events.
 * @param {Array<Object>} eventsToDisplay - Array of event objects for FullCalendar.
 */
export function renderCalendar(eventsToDisplay) {
    currentlyRenderedEvents = eventsToDisplay;

    if (calendarInstance) {
        const currentViewDate = calendarInstance.getDate();
        calendarInstance.destroy();
        currentYear = currentViewDate.getFullYear();
        currentMonth = currentViewDate.getMonth() + 1;
    }

    calendarInstance = new FullCalendar.Calendar(DOMElements.calendarEl, {
        initialView: 'dayGridMonth',
        initialDate: new Date(currentYear, currentMonth - 1, 1),
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        views: {
            timeGridWeek: {
                slotMinTime: '06:00:00',
                slotMaxTime: '30:00:00',
                slotDuration: '00:30:00',
                slotLabelFormat: {
                    hour: 'numeric',
                    minute: '2-digit',
                    meridiem: 'short'
                }
            },
            timeGridDay: {
                slotMinTime: '06:00:00',
                slotMaxTime: '30:00:00',
                slotDuration: '00:30:00',
                slotLabelFormat: {
                    hour: 'numeric',
                    minute: '2-digit',
                    meridiem: 'short'
                }
            }
        },
        height: 'auto',
        navLinks: true,
        editable: false,
        dayMaxEvents: 4,
        eventTimeFormat: {
            hour: 'numeric',
            minute: '2-digit',
            meridiem: 'short'
        },
        events: eventsToDisplay,
        eventContent: function(arg) {
            const employeeNames = arg.event.extendedProps.employee_names || [];
            const employeeNamesText = employeeNames.length > 0
                ? employeeNames.slice(0, 2).join(', ') + (employeeNames.length > 2 ? '...' : '')
                : 'No Employees';
            const shiftType = arg.event.extendedProps.shift_type || 'N/A';
            const isNightSplit = (arg.event.extendedProps.original_start_hour === 18 && arg.event.extendedProps.original_end_hour === 6);

            const timeText = isNightSplit
                ? ` (${new Date(arg.event.start).getHours() >= 18 || (new Date(arg.event.start).getHours() < new Date(arg.event.end).getHours() && new Date(arg.event.end).getHours() === 6) ? 'Dusk' : 'Dawn'})`
                : '';
            return { html: `
                <div class="fc-event-main-content">
                    <strong>Squad ${arg.event.extendedProps.squad_name || 'N/A'} - ${shiftType} ${timeText}</strong>
                    <div class="text-xs">${employeeNamesText}</div>
                </div>
            ` };
        },
        eventDidMount: function(info) {
            if (info.event.extendedProps?.squad_name) {
                info.el.classList.add(`squad-${info.event.extendedProps.squad_name}-event`);
            }
            tippy(info.el, {
                content: `
                    <strong>Squad:</strong> ${info.event.extendedProps.squad_name || 'N/A'}<br>
                    <strong>Shift Type:</strong> ${info.event.extendedProps.shift_type || 'N/A'}<br>
                    <strong>Start:</strong> ${formatModalDate(info.event.start)}<br>
                    <strong>End:</strong> ${formatModalDate(info.event.end)}<br>
                    <strong>Employees:</strong> ${getEmployeeDisplayNames(info.event.extendedProps.employee_names)}
                `,
                allowHTML: true,
                animation: 'fade',
                placement: 'top',
                theme: 'light-border',
                maxWidth: 300
            });
        },
        eventClick: function(info) {
            // Call the global showEventModalDetails, which in turn uses window.showEventModal()
            window.showEventModalDetails(info.event.extendedProps, info.event.start, info.event.end);
        },
        loading: function(isLoading) {
            // Call the global showLoading/hideLoading functions
            isLoading ? window.showLoading() : window.hideLoading();
        },
        datesSet: function(dateInfo) {
            const newYear = dateInfo.view.calendar.getDate().getFullYear();
            const newMonth = dateInfo.view.calendar.getDate().getMonth() + 1;
            if (newYear !== currentYear || newMonth !== currentMonth) {
                currentYear = newYear;
                currentMonth = newMonth;
                fetchEvents(currentYear, currentMonth);
            }
        }
    });
    calendarInstance.render();
}

// showEventModalDetails remains as an export for calendar-events.js to call it
// It in turn calls the global window.showEventModal()
export function showEventModalDetails(extendedProps, start, end) {
    DOMElements.modalSquad.textContent = extendedProps.squad_name || 'N/A';
    DOMElements.modalShiftType.textContent = extendedProps.shift_type || 'N/A';
    DOMElements.modalStart.textContent = formatModalDate(start);
    DOMElements.modalEnd.textContent = formatModalDate(end);
    DOMElements.modalEmployees.textContent = getEmployeeDisplayNames(extendedProps.employee_names);
    window.showEventModal(); // This calls the global function defined in calendar.html
}
window.showEventModalDetails = function(extendedProps, start, end) {
    DOMElements.modalSquad.textContent = extendedProps.squad_name || 'N/A';
    DOMElements.modalShiftType.textContent = extendedProps.shift_type || 'N/A';
    DOMElements.modalStart.textContent = formatModalDate(start);
    DOMElements.modalEnd.textContent = formatModalDate(end);
    DOMElements.modalEmployees.textContent = getEmployeeDisplayNames(extendedProps.employee_names);
    window.showEventModal();
};