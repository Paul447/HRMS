// static/js/dom-elements.js

export const DOMElements = {
    calendarEl: document.getElementById('calendar'),
    eventModal: document.getElementById('eventModal'), // Updated ID
    closeModalBtn: document.getElementById('closeModal'), // Updated ID
    modalSquad: document.getElementById('modalSquad'), // Updated ID
    modalShiftType: document.getElementById('modalShiftType'), // Updated ID
    modalStart: document.getElementById('modalStart'), // Updated ID
    modalEnd: document.getElementById('modalEnd'), // Updated ID
    modalEmployees: document.getElementById('modalEmployees'), // Updated ID
    squadFilter: document.getElementById('squadFilter'), // Updated ID
    employeeFilter: document.getElementById('employeeFilter'), // Updated ID
    applyFiltersBtn: document.getElementById('applyFilters'), // Updated ID
    resetFiltersBtn: document.getElementById('resetFilters'), // Updated ID
    loadingOverlay: document.getElementById('loadingOverlay'), // Updated ID
};

// These functions are now handled by the inline script in calendar.html
// So, you should remove them from here if you kept them.
// If you remove them, you also need to remove them from any imports.
/*
export function showLoading() {
    DOMElements.loadingOverlay.classList.remove('opacity-0', 'pointer-events-none');
    DOMElements.loadingOverlay.classList.add('opacity-100');
}

export function hideLoading() {
    DOMElements.loadingOverlay.classList.remove('opacity-100');
    DOMElements.loadingOverlay.classList.add('opacity-0', 'pointer-events-none');
}
*/