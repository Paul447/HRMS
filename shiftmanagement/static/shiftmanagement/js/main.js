// static/js/main.js

import { DOMElements } from './dom-elements.js';
// We will pass vanillaSelectBox to setupMultiSelect, so no need to import it here
import { fetchEvents, applyFilters, resetFilters } from './calendar-events.js';
import { currentYear, currentMonth } from './calendar-renderer.js';


document.addEventListener('DOMContentLoaded', function() {
    // Check if elements exist before adding listeners to avoid null errors
    if (DOMElements.applyFiltersBtn) {
        DOMElements.applyFiltersBtn.addEventListener('click', applyFilters);
    } else {
        console.error("Element with ID 'applyFilters' not found.");
    }

    if (DOMElements.resetFiltersBtn) {
        DOMElements.resetFiltersBtn.addEventListener('click', resetFilters);
    } else {
        console.error("Element with ID 'resetFilters' not found.");
    }
    
    if (DOMElements.closeModalBtn) {
        // Ensure window.hideEventModal is defined by the time this runs
        if (typeof window.hideEventModal === 'function') {
            DOMElements.closeModalBtn.addEventListener('click', window.hideEventModal); 
        } else {
            console.error("window.hideEventModal function is not defined.");
        }
    } else {
        console.error("Element with ID 'closeModal' not found.");
    }

    // Setup multi-select only if the element and vanillaSelectBox are available
    // if (DOMElements.employeeFilter) {
    //     if (typeof window.vanillaSelectBox === 'function') {
    //         setupMultiSelect(window.vanillaSelectBox); // Pass the constructor
    //     } else {
    //         console.error("vanillaSelectBox library not loaded or not a constructor. Employee multi-select not initialized.");
    //     }
    // } else {
    //     console.warn("Element with ID 'employeeFilter' not found. Multi-select not initialized.");
    // }

    fetchEvents(currentYear, currentMonth);
});