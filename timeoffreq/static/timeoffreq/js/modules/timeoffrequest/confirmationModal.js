export const ConfirmationModal = (function() {
    let confirmPromiseResolve;

    function showConfirmationModal(confirmationModal) {
        confirmationModal.classList.remove('hidden');
        confirmationModal.classList.remove('animate-fade-out-modal');
        const modalContent = confirmationModal.querySelector('.confirm-modal-content');
        modalContent.classList.remove('animate-fade-out-modal');
        modalContent.classList.add('animate-scale-in');
    }

    function hideConfirmationModal(confirmationModal, animate = true) {
        const modalContent = confirmationModal.querySelector('.confirm-modal-content');
        if (animate) {
            confirmationModal.classList.add('animate-fade-out-modal');
            modalContent.classList.remove('animate-scale-in');
            modalContent.classList.add('animate-fade-out-modal');
            confirmationModal.addEventListener('animationend', function handler() {
                confirmationModal.classList.add('hidden');
                confirmationModal.classList.remove('animate-fade-out-modal');
                modalContent.classList.remove('animate-fade-out-modal');
                confirmationModal.removeEventListener('animationend', handler);
            }, { once: true });
        } else {
            confirmationModal.classList.add('hidden');
        }
    }

    function askForConfirmation(confirmationModal, confirmButton, cancelButton) {
        return new Promise(resolve => {
            confirmPromiseResolve = resolve;

            const clonedConfirmButton = confirmButton.cloneNode(true);
            confirmButton.parentNode.replaceChild(clonedConfirmButton, confirmButton);

            const clonedCancelButton = cancelButton.cloneNode(true);
            cancelButton.parentNode.replaceChild(clonedCancelButton, cancelButton);

            clonedConfirmButton.addEventListener('click', () => {
                hideConfirmationModal(confirmationModal);
                confirmPromiseResolve(true);
            }, { once: true });

            clonedCancelButton.addEventListener('click', () => {
                hideConfirmationModal(confirmationModal);
                confirmPromiseResolve(false);
            }, { once: true });

            showConfirmationModal(confirmationModal);
        });
    }
    return { showConfirmationModal, hideConfirmationModal, askForConfirmation };
})();