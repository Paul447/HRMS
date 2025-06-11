// main.js
import { smartFetch } from './modules/smartFetch.js';

document.addEventListener('DOMContentLoaded', () => {
    smartFetch('/api/ptobalance/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'  // Make sure Django template processes this
        },
        credentials: 'include'
    })
    .then(async response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        document.getElementById('employee-type').textContent = data.employee_type;
        document.getElementById('pay-frequency').textContent = data.pay_frequency;
        document.getElementById('accrual-rate').textContent = data.accrual_rate;
        document.getElementById('pto-balance').textContent = data.pto_balance;
        document.getElementById('username').textContent = data.first_name + ' ' + data.last_name;
        document.getElementById('years-of-experience').textContent = data.year_of_experience;
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
});
