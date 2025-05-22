 // This script handles the client-side logic for the PTO request form,
    // including fetching dropdown data and submitting the form data.
    // It leverages a `smartFetch` function to handle JWT token refreshes
    // in conjunction with the Django middleware, ensuring a smooth user experience.

    document.addEventListener('DOMContentLoaded', function() {
        // Get references to DOM elements
        const departmentSelect = document.getElementById('department_name');
        const payTypeSelect = document.getElementById('pay_types');
        const form = document.getElementById('ptoRequestForm');
        const successMessage = document.getElementById('successMessage');
        const errorMessage = document.getElementById('errorMessage');

        /**
         * `smartFetch` is a robust wrapper around the native Fetch API.
         * It automatically retries an API request exactly once if the initial attempt
         * returns a `401 Unauthorized` status. This is designed to work seamlessly
         * with a Django backend middleware that handles JWT token refreshing
         * via HTTP-only cookies. If the middleware successfully refreshes the access token,
         * the retry attempt will use the newly set valid cookie.
         *
         * @param {string} url The URL to send the request to.
         * @param {RequestInit} options Configuration options for the fetch request
         * (e.g., method, headers, body, credentials).
         * @param {boolean} [isRetry=false] Internal flag to prevent infinite retry loops.
         * @returns {Promise<Response>} A promise that resolves with the Fetch API Response object.
         * @throws {Error} Throws an error if a network issue occurs or if the request
         * fails after the retry attempt (and is not a 401 leading to redirect).
         */
        async function smartFetch(url, options = {}, isRetry = false) {
            try {
                // Execute the first fetch attempt
                const response = await fetch(url, options);

                // If a 401 Unauthorized status is received and it's not already a retry attempt,
                // assume the access token has expired and the Django middleware has refreshed it.
                if (response.status === 401 && !isRetry) {
                    console.warn(`[smartFetch] Received 401 for ${url}. Retrying with potentially new token.`);
                    // Recursively call smartFetch for a single retry
                    return await smartFetch(url, options, true);
                }
                
                return response; // Return the original or retried response

            } catch (error) {
                // Catch and log any network or other unexpected fetch errors
                console.error(`[smartFetch] Network or other fetch error for ${url}:`, error);
                // Re-throw the error to be handled by the calling function
                throw error;
            }
        }

        /**
         * Fetches data from a specified API endpoint and uses it to populate
         * a given HTML `<select>` element. It handles loading states and errors.
         * This function uses `smartFetch` for API calls to benefit from token retry logic.
         *
         * @param {string} url The API endpoint to fetch data from.
         * @param {HTMLSelectElement} selectElement The `<select>` DOM element to populate.
         * @param {string} defaultOptionText The text for the initial disabled option (e.g., "Select a Department").
         * @param {string} valueKey The key in the API response object representing the option's value.
         * @param {string} labelKey The key in the API response object representing the option's display text.
         */
        async function fetchAndPopulateDropdown(url, selectElement, defaultOptionText, valueKey, labelKey) {
            try {
                // Retrieve the CSRF token from the hidden input field.
                // This is needed for Django's CSRF protection on API requests.
                const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

                // Make the API call using smartFetch, including necessary headers and credentials.
                const response = await smartFetch(url, {
                    method: 'GET',
                    // `credentials: 'include'` ensures HTTP-only cookies (like JWT) are sent.
                    credentials: 'include',
                    headers: {
                        'X-CSRFToken': csrftoken, // Send the CSRF token for Django's validation
                        'Content-Type': 'application/json'
                    }
                });

                // Check if the response was successful (status 2xx)
                if (!response.ok) {
                    // If a 401 persists after smartFetch's retry, it means the refresh token is also invalid.
                    // In this case, redirect the user to the login page.
                    if (response.status === 401) {
                        console.error(`[Dropdown Fetch] Refresh token invalid for ${url}. Redirecting to login.`);
                        window.location.href = '/auth/login/';
                        return; // Stop execution
                    }
                    // For any other non-OK status, throw an error
                    throw new Error(`Failed to load ${defaultOptionText}. Status: ${response.status}`);
                }

                // Parse the JSON data from the response
                const data = await response.json();
                
                // Clear existing options and add the default placeholder option
                selectElement.innerHTML = `<option value="" disabled selected>${defaultOptionText}</option>`;

                // Populate the dropdown with data from the API response
                data.forEach(item => {
                    const option = document.createElement('option');
                    option.value = item[valueKey];       // Set the option's value
                    option.textContent = item[labelKey]; // Set the option's display text
                    selectElement.appendChild(option);   // Add the option to the select element
                });
            } catch (error) {
                // Log and display an error message if population fails
                console.error(`[Dropdown Fetch] Error populating ${defaultOptionText} dropdown:`, error);
                selectElement.innerHTML = `<option value="" disabled selected>Error loading ${defaultOptionText}</option>`;
            }
        }

        // --- Initial Data Loading ---
        // Fetch and populate the Department dropdown when the page loads
        fetchAndPopulateDropdown('/api/department/', departmentSelect, 'Select your Department', 'id', 'name');
        // Fetch and populate the Pay Type dropdown when the page loads
        fetchAndPopulateDropdown('/api/paytype/', payTypeSelect, 'Select Pay Type', 'id', 'name');

        // --- Form Submission Handling ---
        form.addEventListener('submit', async function(event) {
            event.preventDefault(); // Prevent the browser's default form submission behavior

            // Hide any previously displayed success or error messages
            successMessage.classList.add('hidden');
            errorMessage.classList.add('hidden');

            // Retrieve the CSRF token for the POST request
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // Gather all form data into a payload object
            const payload = {
                department_name: form.department_name.value,
                pay_types: form.pay_types.value,
                start_date_time: form.start_date_time.value,
                end_date_time: form.end_date_time.value,
                reason: form.reason.value
            };

            try {
                // Submit the form data to the API using smartFetch
                const response = await smartFetch('/api/pto-requests/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json', // Specify content type for JSON payload
                        'X-CSRFToken': csrftoken // Include the CSRF token for server-side validation
                    },
                    credentials: 'include', // Ensures HTTP-only cookies (like JWT) are sent with the request
                    body: JSON.stringify(payload) // Convert the payload object to a JSON string
                });

                // Check if the form submission was successful (status 2xx)
                if (!response.ok) {
                    // If a 401 persists after smartFetch's retry, redirect to login.
                    if (response.status === 401) {
                        console.error("[Form Submission] Refresh token invalid. Redirecting to login.");
                        window.location.href = '/auth/login/';
                        return; // Stop execution
                    }
                    // For any other non-OK status (e.g., 400 Bad Request, 403 Forbidden, 500 Internal Server Error)
                    // throw an error to be caught by the catch block.
                    throw new Error(`Form submission failed with status: ${response.status}`);
                }

                // If successful, display the success message and reset the form fields
                successMessage.classList.remove('hidden');
                form.reset();
                console.log("[Form Submission] PTO request submitted successfully."); // Keep this one for successful feedback

            } catch (err) {
                // If an error occurs during fetch or processing, display the error message
                errorMessage.classList.remove('hidden');
                console.error('[Form Submission] Error during submission:', err);
                // Optionally, parse and display server-side validation errors if available
                // For example: if (err.response && err.response.json) { const errorData = await err.response.json(); console.error(errorData); }
            }
        });
    });