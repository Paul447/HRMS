/**
 * confirmationModal.js
 *
 * This module provides a reusable, promise-based confirmation modal.
 * It manages the display, animations, and user interaction (confirm/cancel).
 *
 * It no longer clones buttons, instead relying on event listener management.
 */

// Get modal elements (these are assumed to exist in the HTML and are retrieved once)
const confirmationModal = document.getElementById('confirmationModal');
const confirmModalContent = confirmationModal ? confirmationModal.querySelector('.confirm-modal-content') : null;
const confirmSubmitButton = confirmationModal ? document.getElementById('confirmSubmitButton') : null;
const confirmCancelButton = confirmationModal ? document.getElementById('confirmCancelButton') : null;

// Basic check to ensure modal elements are found
if (!confirmationModal || !confirmModalContent || !confirmSubmitButton || !confirmCancelButton) {
    console.error('ConfirmationModal: Required DOM elements not found. Please ensure #confirmationModal, .confirm-modal-content, #confirmSubmitButton, #confirmCancelButton exist in your HTML.');
    // If elements are missing, disable functionality to prevent runtime errors
    // or provide a fallback UI to the user. For now, we'll just log an error.
}

/**
 * Shows the confirmation modal with a scale-in animation.
 */
function showModal() {
    if (!confirmationModal || !confirmModalContent) return;

    confirmationModal.classList.remove('hidden');
    confirmationModal.classList.add('flex'); // Ensure flex for centering
    confirmModalContent.classList.remove('animate-fade-out-modal'); // Remove fade-out class if present
    confirmModalContent.classList.add('animate-scale-in');

    // Set focus to the first interactive element for accessibility
    confirmCancelButton.focus();
}

/**
 * Hides the confirmation modal with a fade-out animation.
 */
function hideModal() {
    if (!confirmationModal || !confirmModalContent) return;

    confirmModalContent.classList.remove('animate-scale-in');
    confirmModalContent.classList.add('animate-fade-out-modal');

    // Use a listener for the animation end to fully hide the modal
    // The { once: true } option ensures this listener runs only once.
    confirmModalContent.addEventListener('animationend', function handler() {
        confirmationModal.classList.add('hidden');
        confirmationModal.classList.remove('flex'); // Remove flex when hidden
        confirmModalContent.classList.remove('animate-fade-out-modal'); // Clean up animation class
        confirmModalContent.removeEventListener('animationend', handler); // Explicitly remove listener
    }, { once: true });
}

/**
 * Displays a confirmation modal and waits for user interaction.
 * Returns a Promise that resolves to true if confirmed, false otherwise.
 *
 * @returns {Promise<boolean>} True if the user confirms, false otherwise.
 */
export function askForConfirmation() {
    return new Promise((resolve) => {
        // Ensure buttons exist before attaching listeners
        if (!confirmSubmitButton || !confirmCancelButton) {
            console.error('ConfirmationModal: Submit or Cancel buttons not found. Cannot ask for confirmation.');
            resolve(false); // Resolve false if buttons are missing to prevent freezing
            return;
        }

        // Event handler for confirmation
        const handleConfirm = () => {
            hideModal();
            resolve(true);
            removeListeners(); // Clean up listeners after resolution
        };

        // Event handler for cancellation
        const handleCancel = () => {
            hideModal();
            resolve(false);
            removeListeners(); // Clean up listeners after resolution
        };

        // Add event listeners (using { once: true } to ensure they fire only once per modal open)
        confirmSubmitButton.addEventListener('click', handleConfirm, { once: true });
        confirmCancelButton.addEventListener('click', handleCancel, { once: true });

        // Allow closing with Escape key
        const escapeKeyHandler = (event) => {
            if (event.key === 'Escape') {
                handleCancel(); // Treat Escape as a cancellation
            }
        };
        document.addEventListener('keydown', escapeKeyHandler, { once: true }); // Listener for Escape key

        // Function to remove event listeners to prevent memory leaks and duplicate triggers
        function removeListeners() {
            // These listeners might have already fired due to { once: true }, but explicitly
            // removing them here ensures no lingering listeners if, for example, the promise
            // resolves via an external mechanism or if the modal is hidden forcefully.
            confirmSubmitButton.removeEventListener('click', handleConfirm);
            confirmCancelButton.removeEventListener('click', handleCancel);
            document.removeEventListener('keydown', escapeKeyHandler);
        }

        // Show the modal to the user
        showModal();
    });
}

// Exporting internal functions for potential external use if needed (e.g., testing)
// Though typically, only askForConfirmation is exposed.
export const ConfirmationModal = {
    showModal,
    hideModal,
    askForConfirmation
};

