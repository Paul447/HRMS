 function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
          cookie = cookie.trim();
          if (cookie.startsWith(name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }

    const csrfToken = getCookie('csrftoken');

    const loginForm = document.getElementById("login-form");
    const refreshBtn = document.getElementById("refresh-token");
    const fetchBtn = document.getElementById("fetch-protected");
    const output = document.getElementById("output");

loginForm.addEventListener("submit", (e) => {
  e.preventDefault();

  const formData = new FormData(loginForm);

fetch("/auth/api/login/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-CSRFToken": csrfToken
  },
  credentials: "include",
  body: JSON.stringify({
    username: formData.get("username"),
    password: formData.get("password")
  })
})
.then(response => response.json())
.then(data => {
  if (data.redirect_url) {
    window.location.href = data.redirect_url;
  } else {
    alert("Login failed");
  }
})
.catch(error => {
  console.error("Login error:", error);
  alert("Login error");
});

}); async function fetchWithAutoRefresh(url, options = {}) {
  // Ensure credentials included for cookies
  const fetchOptions = {
    credentials: 'include',
    ...options,
  };

  let response = await fetch(url, fetchOptions);

  if (response.status === 401) {
    // Try refreshing token
    const refreshResponse = await fetch('/auth/api/token/refresh/', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'X-CSRFToken': csrfToken,
      },
    });

    if (refreshResponse.ok) {
      // Refresh succeeded, retry original request
      response = await fetch(url, fetchOptions);
      return response;
    } else {
      // Refresh failed - session expired or invalid, handle logout or redirect
      throw new Error('Session expired. Please log in again.');
    }
  }

  return response;
}

fetchWithAutoRefresh('/auth/api/protected/', { method: 'GET' })
  .then(async (res) => {
    if (!res.ok) {
      throw new Error('Failed to fetch protected data');
    }
    const data = await res.json();
    output.textContent = JSON.stringify(data, null, 2);
  })
  .catch((err) => {
    output.textContent = `Error: ${err.message}`;
    // Optionally redirect to login page here
}); 

    function isAccessTokenExpired(token) {
      if (!token) return true;
      const decoded = JSON.parse(atob(token.split('.')[1]));
      const exp = decoded.exp * 1000;
      return exp < Date.now();
    }

    function refreshAccessToken() {
      const refresh = localStorage.getItem('refreshToken');
      if (!refresh) return;

      return fetch('http://localhost:8000/api/token/refresh/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh }),
      })
      .then(res => res.json())
      .then(data => {
        if (data.access) {
          localStorage.setItem('accessToken', data.access);
          return data.access;
        } else {
          window.location.href = 'index.html';
        }
      });
    }

    async function loadProtectedData() {
      let accessToken = localStorage.getItem('accessToken');
      
      if (isAccessTokenExpired(accessToken)) {
        accessToken = await refreshAccessToken();
      }

      if (!accessToken) {
        alert('Session expired. Please login again.');
        window.location.href = 'index.html';
        return;
      }

      fetch('http://localhost:8000/api/protected/', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      })
      .then(res => res.json())
      .then(data => {
        document.getElementById('protectedData').textContent = JSON.stringify(data, null, 2);
      })
      .catch(err => {
        console.error('Protected fetch error:', err);
        alert('Failed to fetch protected data.');
      });
    }

    window.onload = loadProtectedData;