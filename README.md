Application Setup Guide
=======================

This guide provides step-by-step instructions to set up and run the application.

------------------------------------------------------------
1. Virtual Environment Setup
------------------------------------------------------------

Activate the existing virtual environment, or create a new one if it does not exist.

Create a virtual environment:
    python3 -m venv venv

Activate the virtual environment:

- Windows (PowerShell):
    .\venv\Scripts\activate

- Mac/Linux:
    source venv/bin/activate


------------------------------------------------------------
2. Verify Python & pip Installation
------------------------------------------------------------

Check if Python and pip are installed. If not, install them.

Mac/Linux:
    brew install python
    sudo apt install python3
    python3 -m venv venv
    pip install virtualenv


------------------------------------------------------------
3. Database Setup
------------------------------------------------------------

Ensure the database service is running and properly configured in Django.

Mac:
    brew services start mysql

Check the database configuration in your Django settings.py.


------------------------------------------------------------
4. Install Project Dependencies
------------------------------------------------------------

Install all required packages:
    pip install -r requirements.txt


------------------------------------------------------------
5. Django Setup
------------------------------------------------------------

Run the following commands to prepare and launch the application:
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver


------------------------------------------------------------
6. Asynchronous Task Setup
------------------------------------------------------------

Install Redis

Mac:
    redis-server --version
    brew install redis
    brew services start redis
    redis-server
    redis-cli ping

Windows:
    1. Download Redis from the official website.
    2. Start Redis:
        redis-server
    3. Verify Redis is running:
        redis-cli ping


------------------------------------------------------------
7. Celery Configuration
------------------------------------------------------------

Check that Celery is properly configured to use Redis as the broker.

In settings.py:
    CELERY_BROKER_URL = 'redis://localhost:6379/0'

Start the Celery worker:
    celery -A HRMS worker --loglevel=info

To enable event tracking:
    celery -A HRMS worker --loglevel=info -E


------------------------------------------------------------
Once all the above steps are completed, your HRMS application should be fully operational.
------------------------------------------------------------


### **API Endpoint Security Audit**

---

### **Endpoint: `http://127.0.0.1:8000/api/v1/pay-period/`**

| # | Category | Status | Summary / Implementation |
| :--- | :--- | :--- | :--- |
| 1 | Broken Object Level Authorization (BOLA) | ✅ OK | All users can see all pay periods; no object-level filtering is needed. |
| 2 | Broken Authentication | ✅ OK | `IsAuthenticated` ensures only logged-in users access the endpoint. |
| 3 | Broken Object Property Level Authorization | ✅ OK | The endpoint is read-only. No object-level write/update risk. |
| 4 | Unrestricted Resource Consumption | ⚠️ Review | Pagination is not used, but is safe due to limited data. |
| 5 | Broken Function Level Authorization | ✅ OK | All users have access by design. |
| 6 | Unrestricted Access to Sensitive Business Flows | ✅ OK | This view is intentionally public to all authenticated users for dropdowns. |
| 7 | Server-Side Request Forgery (SSRF) | ✅ OK | No external URL or internal fetch logic. |
| 8 | Security Misconfiguration | ⚠️ Review | Ensure `DEBUG = False`, CORS is configured, and HTTPS is enforced in production. |
| 9 | Improper Inventory Management | ✅ OK | The endpoint is versioned or documented in OpenAPI/Swagger. |
| 10 | Unsafe Consumption of APIs | ✅ OK | No third-party API usage. |

---

### **Endpoint: `http://127.0.0.1:8000/api/v1/past-pay-period/`**

| # | Category | Status | Summary / Implementation |
| :--- | :--- | :--- | :--- |
| 1 | Broken Object Level Authorization (BOLA) | ✅ OK | All users access the same dataset; no ownership logic is needed. |
| 2 | Broken Authentication | ✅ OK | Uses `IsAuthenticated` to restrict access to logged-in users. |
| 3 | Broken Object Property Level Authorization | ✅ OK | The endpoint is read-only; users cannot modify any fields. |
| 4 | Unrestricted Resource Consumption | ⚠️ Review | The endpoint returns a full list without pagination. |
| 5 | Broken Function Level Authorization | ✅ OK | All users are intended to see past pay periods. |
| 6 | Unrestricted Access to Sensitive Business Flows | ✅ OK | Access is limited to viewing past pay periods only. |
| 7 | Server-Side Request Forgery (SSRF) | ✅ OK | No external URLs are fetched. |
| 8 | Security Misconfiguration | ⚠️ Review | Ensure `DEBUG=False`, CORS is configured, and HTTPS is enforced. |
| 9 | Improper Inventory Management | ✅ OK | The endpoint is versioned (`/api/v1/...`) or documented. |
| 10 | Unsafe Consumption of APIs | ✅ OK | No third-party APIs are involved. |

---

### **Endpoint: `http://127.0.0.1:8000/api/v1/current-future-pay-period/`**

| # | Category | Status | Summary / Implementation |
| :--- | :--- | :--- | :--- |
| 1 | Broken Object Level Authorization (BOLA) | ✅ OK | No per-object restrictions are needed. All authenticated users can access all future/current pay periods. |
| 2 | Broken Authentication | ✅ OK | `IsAuthenticated` restricts access to logged-in users. |
| 3 | Broken Object Property Level Authorization | ✅ OK | The read-only endpoint prevents property-level updates. |
| 4 | Unrestricted Resource Consumption | ✅ OK | The query is limited to 26 results with `[:26]`. |
| 5 | Broken Function Level Authorization | ✅ OK | All authenticated users are expected to access future/current pay periods. |
| 6 | Unrestricted Access to Sensitive Business Flows | ✅ OK | No sensitive workflows are exposed; it just returns future pay period data. |
| 7 | Server-Side Request Forgery (SSRF) | ✅ OK | No user-controlled URLs or internal requests. |
| 8 | Security Misconfiguration | ⚠️ Review | Ensure deployment settings (`DEBUG`, HTTPS, CORS) are configured correctly. |
| 9 | Improper Inventory Management | ✅ OK | API versioning (`/api/v1/...`) or documentation in OpenAPI is used. |
| 10 | Unsafe Consumption of APIs | ✅ OK | No interaction with third-party APIs. |

---

### **Endpoint: `http://127.0.0.1:8000/api/v1/decisioned-timeoff/`**

| # | Category | Status | Summary / Implementation |
| :--- | :--- | :--- | :--- |
| 1 | Broken Object Level Authorization (BOLA) | ✅ OK | Managers only see requests from their department; superusers see all. |
| 2 | Broken Authentication | ✅ OK | Uses `IsAuthenticated` and role checks for access control. |
| 3 | Broken Object Property Level Authorization | ✅ OK | This is a read-only viewset; no updates are permitted. |
| 4 | Unrestricted Resource Consumption | ⚠️ Review | Pagination is enabled. |
| 5 | Broken Function Level Authorization | ✅ OK | Only superusers or managers can access; others get an empty queryset. |
| 6 | Unrestricted Access to Sensitive Business Flows | ✅ OK | Access is restricted by user role; only authorized users see requests. |
| 7 | Server-Side Request Forgery (SSRF) | ✅ OK | No user-supplied URLs or external requests are involved. |
| 8 | Security Misconfiguration | ⚠️ Review | Ensure the deployment has secure CORS, HTTPS, and `DEBUG=False`. |
| 9 | Improper Inventory Management | ✅ OK | API versioning is enabled. |
| 10 | Unsafe Consumption of APIs | ✅ OK | No third-party APIs are consumed here. |

---

### **Endpoint: `http://127.0.0.1:8000/api/department-leaves/`**

| # | Category | Status | Summary / Implementation |
| :--- | :--- | :--- | :--- |
| 1 | Broken Object Level Authorization (BOLA) | ✅ OK | Access is filtered by department using the user's profile. Superusers have full access. |
| 2 | Broken Authentication | ✅ OK | Uses `IsAuthenticated` for all access. |
| 3 | Broken Object Property Level Authorization | ✅ OK | This is a read-only viewset; no object mutation is allowed. |
| 4 | Unrestricted Resource Consumption | ⚠️ Review | Pagination is enabled using a custom class. |
| 5 | Broken Function Level Authorization | ✅ OK | `get_permissions()` checks roles dynamically for each user type. |
| 6 | Unrestricted Access to Sensitive Business Flows | ✅ OK | Only department team members can view related leaves. |
| 7 | Server-Side Request Forgery (SSRF) | ✅ OK | No SSRF risks are present. |
| 8 | Security Misconfiguration | ⚠️ Review | Ensure `DEBUG=False`, proper logging, and secure cookies/headers are enforced in production. |
| 9 | Improper Inventory Management | ⚠️ Consider | No API documentation or versioning is mentioned. |
| 10 | Unsafe Consumption of APIs | ✅ OK | No third-party or dynamic API calls are used. |

---

### **Endpoint: `http://127.0.0.1:8000/api/timeoffrequests/`**

| # | Category | Status | Summary / Implementation |
| :--- | :--- | :--- | :--- |
| 1 | Broken Object Level Authorization (BOLA) | ✅ OK | `employee` is read-only and set from `request.user`. |
| 2 | Broken Authentication | ✅ OK | Access is gated by `IsAuthenticated` and role-based permissions. |
| 3 | Broken Object Property Level Authorization | ⚠️ Review | Fields like `status` and `employee_full_name` are read-only. |
| 4 | Unrestricted Resource Consumption | ✅ OK | Throttling is configured. |
| 5 | Broken Function Level Authorization | ✅ OK | Only employees with permission can create or update leave requests. |
| 6 | Unrestricted Access to Sensitive Business Flows | ✅ OK | Data access is limited to the authenticated user and their leave requests. |
| 7 | Server-Side Request Forgery (SSRF) | ✅ OK | No external URLs or redirects are triggered from the serializer or input. |
| 8 | Security Misconfiguration | ⚠️ Review | File uploads (`document_proof`) may carry risks. |
| 9 | Improper Inventory Management | ⚠️ Consider | API docs are not shown; `"SERVE_INCLUDE_SCHEMA"` is `False`. |
| 10 | Unsafe Consumption of APIs | ✅ OK | No third-party APIs are used in this serializer logic. |

---

### **Endpoint: `http://127.0.0.1:8000/api/past-timeoff-requests/`**

| # | Category | Status | Summary / Implementation |
| :--- | :--- | :--- | :--- |
| 1 | Broken Object Level Authorization (BOLA) | ✅ OK | Only shows requests belonging to `request.user`. |
| 2 | Broken Authentication | ✅ OK | `IsAuthenticated` permission ensures only logged-in users can access the endpoint. |
| 3 | Broken Object Property Level Authorization | ✅ OK | The queryset filters by `employee=user` and restricts pending status. |
| 4 | Unrestricted Resource Consumption | ⚠️ Review | No pagination is enforced in the shown snippet. |
| 5 | Broken Function Level Authorization | ✅ OK | This is a read-only `ViewSet`. |
| 6 | Unrestricted Access to Sensitive Business Flows | ✅ OK | A user can only see their own past requests. |
| 7 | Server-Side Request Forgery (SSRF) | ✅ OK | No external requests or URLs are used. |
| 8 | Security Misconfiguration | ⚠️ Review | No mention of rate-limiting, caching, or error handling customization. |
| 9 | Improper Inventory Management | ⚠️ Consider | No documented schema is shown. |
| 10 | Unsafe Consumption of APIs | ✅ OK | No third-party APIs are used. |

---

### **Endpoint: `http://127.0.0.1:8000/api/v1/manager-timeoff-approval/`**

| # | Category | Status | Summary / Implementation |
| :--- | :--- | :--- | :--- |
| 1 | Broken Object Level Authorization (BOLA) | ✅ OK | Managers can only act on requests from their department; superusers see all. |
| 2 | Broken Authentication | ✅ OK | Only `IsAuthenticated` users with manager or superuser roles can access the view. |
| 3 | Broken Object Property Level Authorization | ✅ OK | `status` is updated via controlled logic in `approve` and `reject` actions only. |
| 4 | Unrestricted Resource Consumption | ⚠️ Review | Pagination exists, but bulk approval/rejection logic could involve heavy notifications. |
| 5 | Broken Function Level Authorization | ✅ OK | Custom `@action` methods explicitly check permissions against the manager’s department. |
| 6 | Unrestricted Access to Sensitive Business Flows | ✅ OK | Only managers/superusers can approve/reject. |
| 7 | Server-Side Request Forgery (SSRF) | ✅ OK | No user-supplied URLs or external requests are present. |
| 8 | Security Misconfiguration | ⚠️ Review | No throttling for `POST` actions like `approve`/`reject`. |
| 9 | Improper Inventory Management | ✅ OK | The endpoint is dynamic but lacks schema generation comments. |
| 10 | Unsafe Consumption of APIs | ⚠️ Review | Calls `send_pto_notification_and_email_task`. |

---

### **Endpoint: `http://127.0.0.1:8000/auth/api/token/`**

| # | Category | Status | Summary / Implementation |
| :--- | :--- | :--- | :--- |
| 1 | Broken Object Level Authorization (BOLA) | ✅ OK | Not applicable here; the login endpoint does not expose object-level data. |
| 2 | Broken Authentication | ✅ OK | Uses SimpleJWT with cookie storage. |
| 3 | Broken Object Property Level Authorization | ✅ OK | No exposure of sensitive fields like `is_staff` or `is_superuser` in the response. |
| 4 | Unrestricted Resource Consumption | ✅ OK | `LoginRateThrottle` is applied. |
| 5 | Broken Function Level Authorization | ✅ OK | `IsUnauthenticated` permission ensures only unauthenticated users can access the login. |
| 6 | Unrestricted Access to Sensitive Business Flows | ✅ OK | The login endpoint is isolated and restricted. |
| 7 | Server-Side Request Forgery (SSRF) | ✅ OK | No internal URL access or user-provided URLs. |
| 8 | Security Misconfiguration | ⚠️ Review | Cookies are secure only if `settings.DEBUG` is `False`. |
| 9 | Improper Inventory Management | ✅ OK | No schema/doc exposure. |
| 10 | Unsafe Consumption of APIs | ✅ OK | Uses the built-in `TokenObtainPairSerializer` from SimpleJWT. |

---

### **Endpoint: `http://127.0.0.1:8000/api/v1/punch-report/`**

| # | Category | Status | Summary / Implementation |
| :--- | :--- | :--- | :--- |
| 1 | Broken Object Level Authorization (BOLA) | ✅ OK | Implemented `IsSelfOrSuperuser` and `check_object_permissions` to ensure users access only their own data. |
| 2 | Broken User Authentication | ✅ OK | The endpoint is protected by `IsAuthenticated` permission. |
| 3 | Broken Object Property Level Authorization | ✅ OK | Sensitive user properties are reviewed; serializers and data exposure are controlled. |
|
