// This script handles fetching and displaying a list of PTO requests,
// and provides functionality to navigate to the update form.

document.addEventListener('DOMContentLoaded', function() {
    const ptoRequestsList = document.getElementById('ptoRequestsList');
    const noRequestsMessage = document.getElementById('noRequestsMessage');
    const errorMessage = document.getElementById('errorMessage');

    /**
     * smartFetch is a robust wrapper around the native Fetch API.
     * (Copied from pto.js for consistency and modularity)
     */
    async function smartFetch(url, options = {}, isRetry = false) {
        try {
            const response = await fetch(url, options);
            if (response.status === 401 && !isRetry) {
                console.warn(`[smartFetch] Received 401 for ${url}. Retrying with potentially new token.`);
                return await smartFetch(url, options, true);
            }
            return response;
        } catch (error) {
            console.error(`[smartFetch] Network or other fetch error for ${url}:`, error);
            throw error;
        }
    }

    /**
     * Displays a styled notification pop-up.
     * (Copied from pto.js for consistency and modularity)
     */
    function showNotification(message, type = 'success') {
        const existingNotification = document.getElementById('global-notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        const notification = document.createElement('div');
        notification.id = 'global-notification';
        notification.className = `
            fixed top-10 right-4 z-50
            px-6 py-4 rounded-lg shadow-xl
            flex items-center space-x-2 animate-slide-in
        `;

        let bgColorClass = '';
        let iconSvg = '';

        if (type === 'success') {
            bgColorClass = 'bg-green-600';
            iconSvg = `
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
            `;
        } else if (type === 'error') {
            bgColorClass = 'bg-red-600';
            iconSvg = `
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
            `;
        } else if (type === 'warning') {
            bgColorClass = 'bg-yellow-500';
            iconSvg = `
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.332 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
            `;
        }

        notification.classList.add(bgColorClass, 'text-white', 'font-medium');
        notification.innerHTML = `
            ${iconSvg}
            <span>${message}</span>
        `;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.remove('animate-slide-in');
            notification.classList.add('animate-fade-out');
            notification.addEventListener('animationend', () => {
                notification.remove();
            }, { once: true });
        }, 5000);
    }

    /**
     * Fetches PTO requests from the API and renders them in the table.
     */
    async function fetchPTORequests() {
        ptoRequestsList.innerHTML = `
            <tr class="bg-white border-b hover:bg-gray-50">
                <td colspan="8" class="py-4 px-6 text-center text-gray-500">Loading requests...</td>
            </tr>
        `;
        noRequestsMessage.classList.add('hidden');
        errorMessage.classList.add('hidden');

        try {
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const response = await smartFetch('/api/pto-requests/', {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/auth/login/';
                    return;
                }
                const errorData = await response.json();
                throw new Error(`Failed to load PTO requests. Status: ${response.status}. Error: ${JSON.stringify(errorData)}`);
            }

            const ptoRequests = await response.json();
            

            ptoRequestsList.innerHTML = ''; // Clear loading message

            if (ptoRequests.length === 0) {
                noRequestsMessage.classList.remove('hidden');
            } else {
                ptoRequests.forEach(request => {
                    const row = document.createElement('tr');
                    row.className = 'bg-white border-b hover:bg-gray-50';
                    
                    // Format dates for display
                    const startDate = request.start_date_time ? new Date(request.start_date_time).toLocaleString() : '';
                    const endDate = request.end_date_time ? new Date(request.end_date_time).toLocaleString() : '';

                    row.innerHTML = `
                        <td class="py-4 px-6 font-medium text-gray-900 whitespace-nowrap">${request.id}</td>
                        <td class="py-4 px-6">${request.department_name_display.name}</td> <td class="py-4 px-6">${request.pay_types_display.name}</td> <td class="py-4 px-6">${startDate}</td>
                        <td class="py-4 px-6">${endDate}</td>
                        <td class="py-4 px-6">${request.total_hours}</td>
                        <td class="py-4 px-6 truncate max-w-xs" title="${request.reason}">${request.reason}</td>
                        <td class="py-4 px-6">
                            <button data-id="${request.id}"
                                    class="update-btn font-medium text-blue-600 hover:underline inline-flex items-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                </svg>
                                Update
                            </button>
                        </td>
                    `;
                    ptoRequestsList.appendChild(row);
                });

                // Add event listeners to update buttons
                document.querySelectorAll('.update-btn').forEach(button => {
                    button.addEventListener('click', function() {
                        const id = this.dataset.id;
                        // Redirect to the form page with the ID as a query parameter
                        window.location.href = `/auth/ptorequest/?id=${id}`;
                    });
                });
            }
        } catch (error) {
            console.error('Error fetching PTO requests:', error);
            ptoRequestsList.innerHTML = ''; // Clear any loading state
            errorMessage.classList.remove('hidden');
            showNotification('Failed to load your time off requests.', 'error');
        }
    }

    // Initial fetch when the page loads
    fetchPTORequests();
});