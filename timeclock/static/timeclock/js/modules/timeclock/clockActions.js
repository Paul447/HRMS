// static/timeclock/js/modules/timeclock/clockActions.js

import { smartFetch } from './apiService.js';
import { showNotification } from './notificationService.js';

/**
 * Shows the loading spinner and disables the clock button.
 * @param {HTMLElement} clockButton The clock button element.
 * @param {string} buttonText The text to display next to the spinner.
 */
function showClockButtonLoadingState(clockButton, buttonText = 'Processing...') {
    clockButton.disabled = true;
    clockButton.innerHTML = `
        <svg class="animate-spin h-5 w-5 mr-3 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        ${buttonText}
    `;
    clockButton.classList.add('pointer-events-none'); // Prevent further clicks
}

/**
 * Hides the loading spinner and enables the clock button.
 * Note: In this specific implementation, renderClockInOutCard re-renders the button,
 * so explicitly calling this might not always be necessary right before re-render,
 * but it's good for immediate feedback or if re-rendering is skipped.
 * @param {HTMLElement} clockButton The clock button element.
 * @param {string} originalHtml The original HTML content of the button.
 */
function hideClockButtonLoadingState(clockButton, originalHtml) {
    clockButton.disabled = false;
    clockButton.innerHTML = originalHtml;
    clockButton.classList.remove('pointer-events-none');
}

/**
 * Handles the clock in/out action.
 * @param {Object} DOMElements - Object containing references to all necessary DOM elements.
 * @param {string} csrftoken - The CSRF token.
 * @param {Function} fetchAndRenderClockData - Callback to re-fetch and re-render all data after action.
 */
export async function handleClockAction(DOMElements, csrftoken, fetchAndRenderClockData) {
    console.log("[clockActions] Clock button clicked. Attempting clock action...");

    const clockButton = DOMElements.clockInOutCard.querySelector('#clockButton');
    if (!clockButton) {
        console.error("[clockActions] Clock button not found for action handling.");
        showNotification('An internal error occurred. Please refresh the page.', 'error');
        return;
    }

    const originalButtonHtml = clockButton.innerHTML; // Store original content to restore
    const currentAction = clockButton.textContent.includes('Clock In') ? 'Clock In' : 'Clock Out';

    showClockButtonLoadingState(clockButton, `${currentAction}ing...`);

    try {
        const response = await smartFetch('/clock/clock-in-out/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({})
        });

        const data = await response.json();
        console.log("[clockActions] Clock action API Response:", data);

        if (response.ok) {
            showNotification(data.message, 'success');
            await fetchAndRenderClockData(DOMElements, csrftoken); // Re-fetch and re-render UI
        } else {
            if (response.status === 401) {
                showNotification('Your session has expired. Redirecting to login.', 'error');
                setTimeout(() => window.location.href = '/auth/login/', 1500);
            } else {
                showNotification(`Failed to ${currentAction.toLowerCase()}: ${data.detail || data.message || 'Unknown error.'}`, 'error');
            }
        }
    } catch (error) {
        console.error("[clockActions] Network or parsing error on clock action:", error);
        showNotification('Network error during clock action. Please try again.', 'error');
    } finally {
        // This 'finally' block ensures the button state is reset even if an error occurs.
        // However, since `fetchAndRenderClockData` re-renders the entire card,
        // this `hideClockButtonLoadingState` primarily offers immediate visual
        // feedback for very quick responses. The subsequent full re-render will set
        // the final state.
        hideClockButtonLoadingState(clockButton, originalButtonHtml);
    }
}