// static/js/multi-select.js

import { DOMElements } from './dom-elements.js';

let selectedEmployees = [];
let multiSelectInstance;

export function setupMultiSelect() {
    // Ensure the select element exists before attempting to initialize vanillaSelectBox
    if (DOMElements.employeeFilter) {
        // Explicitly use window.vanillaSelectBox
        multiSelectInstance = new window.vanillaSelectBox(DOMElements.employeeFilter, {
            "minWidth": 200,
            "maxHeight": 200,
            "search": true,
            "stayOpen": false,
            "disableNative": false,
            "placeholder": "Select Employees",
            "maxItems": 50,
        });

        DOMElements.employeeFilter.addEventListener("change", function() {
            selectedEmployees = Array.from(this.selectedOptions).map(option => option.value);
        });
    } else {
        console.error("Employee filter element not found for multi-select initialization.");
    }
}

export function getSelectedEmployees() {
    return selectedEmployees;
}

export function setSelectedEmployees(employeeIds) {
    if (multiSelectInstance && DOMElements.employeeFilter) {
        selectedEmployees = employeeIds;
        multiSelectInstance.setValue(employeeIds);
    } else {
        selectedEmployees = employeeIds;
        console.warn("Attempted to set selected employees before multi-select instance was ready.");
    }
}