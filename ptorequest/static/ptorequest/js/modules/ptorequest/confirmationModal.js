// static/ptorequest/js/modules/ptorequest/confirmationModal.js

let confirmPromiseResolve;

/**
 * Shows the confirmation modal.
 * @param {HTMLElement} confirmationModal The modal overlay element.
 */
export function showConfirmationModal(confirmationModal) {
    confirmationModal.classList.remove('hidden');
    confirmationModal.classList.remove('animate-fade-out-modal');
    const modalContent = confirmationModal.querySelector('.confirm-modal-content');
    modalContent.classList.remove('animate-fade-out-modal');
    modalContent.classList.add('animate-scale-in');
    console.log('[ConfirmationModal] Modal shown.');
}

/**
 * Hides the confirmation modal.
 * @param {HTMLElement} confirmationModal The modal overlay element.
 * @param {boolean} [animate=true] Whether to animate the hide transition.
 */
export function hideConfirmationModal(confirmationModal, animate = true) {
    const modalContent = confirmationModal.querySelector('.confirm-modal-content');
    if (animate) {
        confirmationModal.classList.add('animate-fade-out-modal');
        modalContent.classList.remove('animate-scale-in');
        modalContent.classList.add('animate-fade-out-modal');
        confirmationModal.addEventListener('animationend', function handler() {
            confirmationModal.classList.add('hidden');
            confirmationModal.classList.remove('animate-fade-out-modal');
            modalContent.classList.remove('animate-fade-out-modal');
            console.log('[ConfirmationModal] Modal hidden after animation.');
            confirmationModal.removeEventListener('animationend', handler); // Remove listener after use
        }, { once: true });
    } else {
        confirmationModal.classList.add('hidden');
        console.log('[ConfirmationModal] Modal hidden instantly.');
    }
}

/**
 * Shows the confirmation modal and returns a Promise that resolves with
 * `true` if confirmed, `false` if cancelled.
 * @param {HTMLElement} confirmationModal The modal overlay element.
 * @param {HTMLElement} confirmButton The button that confirms the action.
 * @param {HTMLElement} cancelButton The button that cancels the action.
 * @returns {Promise<boolean>} A promise resolving to true for confirm, false for cancel.
 */
export function askForConfirmation(confirmationModal, confirmButton, cancelButton) {
    return new Promise(resolve => {
        confirmPromiseResolve = resolve;

        // Clone and replace buttons to remove all existing event listeners safely
        const clonedConfirmButton = confirmButton.cloneNode(true);
        confirmButton.parentNode.replaceChild(clonedConfirmButton, confirmButton);

        const clonedCancelButton = cancelButton.cloneNode(true);
        cancelButton.parentNode.replaceChild(clonedCancelButton, cancelButton);

        clonedConfirmButton.addEventListener('click', () => {
            hideConfirmationModal(confirmationModal);
            confirmPromiseResolve(true);
            console.log('[ConfirmationModal] User confirmed.');
        }, { once: true });

        clonedCancelButton.addEventListener('click', () => {
            hideConfirmationModal(confirmationModal);
            confirmPromiseResolve(false);
            console.log('[ConfirmationModal] User cancelled.');
        }, { once: true });

        showConfirmationModal(confirmationModal);
    });
}