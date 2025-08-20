// main.js
import { smartFetch } from './modules/smartFetch.js';
import { showNotification } from './modules/notificationService.js';


function getCsrfToken() {
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput && csrfInput.value) {
        return csrfInput.value;
    }
    // Fallback for getting from cookies if no input is present
    // (Less common with modern Django setup where it's in a hidden input)
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken' + '=')) {
                cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                break;
            }
        }
    }
    console.warn("[domElements] CSRF token not found in hidden input. Falling back to cookie. Ensure {% csrf_token %} is in your HTML.");
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    fetchAndRenderPTOBalance();
});

async function fetchAndRenderPTOBalance() {
    try {
        const response = await smartFetch('/api/v1/pto-balance/', {
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });

        if (!response.ok) {
            if (response.status === 401) {
                showNotification('Your session has expired. Redirecting to login.', 'error');
                setTimeout(() => window.location.href = '/auth/login/', 1500);
            } else {
                const errorData = await response.json();
                showNotification(`Failed to load PTO balance data: ${errorData.detail || errorData.message || 'Unknown error.'}`, 'error');
            }
            return;
        }

        const data = await response.json();
        // Render the PTO balance data in the UI
        renderPTOBalance(data);

    } catch (error) {
        console.error('Error fetching PTO balance:', error);
        showNotification('An unexpected error occurred while fetching PTO balance.', 'error');
    }
}

export function renderPTOBalance(data) {
    document.getElementById('employee-type').textContent = data.employee_type || 'N/A';
    document.getElementById('pay-frequency').textContent = data.pay_frequency || 'N/A';
    document.getElementById('accrual-rate').textContent = data.accrual_rate || 'N/A';
    document.getElementById('username').textContent = (data.first_name || '') + ' ' + (data.last_name || '') || 'N/A';
    document.getElementById('years-of-experience').textContent = data.year_of_experience || 'N/A';
    document.getElementById('pto-balance').textContent = data.pto_balance || 'N/A';
    // New fields
    document.getElementById('verified-sick-balance').textContent = data.verified_sick_balance || '0.00';
    document.getElementById('unverified-sick-balance').textContent = data.unverified_sick_balance || '0.00';
    document.getElementById('used-fvsl').textContent = data.used_FVSL || '0.00';
}
