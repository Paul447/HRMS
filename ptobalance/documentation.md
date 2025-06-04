**PTO Balance Management Application Documentation**

This documentation details a Django application designed to manage and track **Paid Time Off (PTO) balances** for employees. It provides a robust system for calculating accruals, presenting balances via an API, and integrating with a frontend view, all while linking to core HR data like employee type, pay frequency, and years of experience.

**1\. Application Overview**

This application provides the backbone for an automated PTO tracking system. Its key features include:

- **Employee-Specific PTO Balances:** Each user has a unique PTOBalance record that tracks their current PTO hours.
- **Automated Accrual:** Functions to automatically update PTO balances monthly and bi-weekly based on predefined accrual rates. These functions handle accrual caps and prevent duplicate runs for bi-weekly updates.
- **Dynamic Accrual Rate Determination:** In the Django admin, the system automatically determines the correct accrual_rate for a PTOBalance record based on the employee's employee_type, pay_frequency, and a calculated year_of_experience threshold.
- **Read-Only API:** An authenticated API endpoint allows users to securely view their own PTO balance.
- **Frontend Integration:** A secure TemplateView serves a frontend page for displaying PTO information, enforcing JWT cookie authentication.

This system aims to reduce manual PTO tracking and provide transparency to employees.

**2\. Setup and Installation**

To set up this application, you'll need an existing Django project configured with Django REST Framework and Django Simple JWT.

**Dependencies:**

- Django
- djangorestframework
- djangorestframework-simplejwt
- **Dependent Django Apps:** This application relies heavily on other custom apps for its functionality:
  - employeetype (for EmployeeType model)
  - payfrequency (for Pay_Frequency model)
  - yearofexperience (for YearOfExperience model, likely linked to User)
  - accuralrates (for AccrualRates model)
  - biweeklycron (for BiweeklyCron model, used for scheduling bi-weekly tasks)

**Steps:**

1. **Install Dependencies:**

Bash

pip install djangorestframework djangorestframework-simplejwt

1. **Integrate into your Django Project:** Place the provided files within a Django app (e.g., named ptobalance).
2. **Add to INSTALLED_APPS:** Ensure your settings.py includes this app and all its dependencies:

Python

\# settings.py

INSTALLED_APPS = \[

\# ...

'rest_framework',

'rest_framework_simplejwt',

'employeetype',

'payfrequency',

'yearofexperience',

'accuralrates',

'biweeklycron',

'ptobalance', # Your PTO Balance app

\# ...

\]

\# JWT Settings (adjust as per your project's JWT setup)

\# Ensure you have something like this for JWT to work

\# REST_FRAMEWORK = {

\# 'DEFAULT_AUTHENTICATION_CLASSES': (

\# 'rest_framework_simplejwt.authentication.JWTAuthentication',

\# ),

\# 'DEFAULT_PERMISSION_CLASSES': (

\# 'rest_framework.permissions.IsAuthenticated',

\# ),

\# }

\# SIMPLE_JWT = {

\# 'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),

\# 'REFRESH_TOKEN_LIFETIME': timedelta(days=7),

\# 'ROTATE_REFRESH_TOKENS': True,

\# 'BLACKLIST_AFTER_ROTATION': True,

\# 'UPDATE_LAST_LOGIN': False,

\# 'ALGORITHM': 'HS256',

\# 'SIGNING_KEY': settings.SECRET_KEY, # Use your Django secret key

\# 'VERIFYING_KEY': None,

\# 'AUDIENCE': None,

\# 'ISSUER': None,

\# 'JWK_URL': None,

\# 'LEEWAY': 0,

\# 'AUTH_HEADER_TYPES': ('Bearer',),

\# 'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',

\# 'USER_ID_FIELD': 'id',

\# 'USER_ID_CLAIM': 'user_id',

\# 'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

\# 'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),

\# 'TOKEN_TYPE_CLAIM': 'token_type',

\# 'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

\# 'JTI_CLAIM': 'jti',

\# 'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),

\# 'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),

\# 'ACCESS_TOKEN_COOKIE_NAME': 'access_token', # Name of the cookie for access token

\# 'REFRESH_TOKEN_COOKIE_NAME': 'refresh_token', # Name of the cookie for refresh token

\# 'ACCESS_TOKEN_COOKIE_SECURE': False, # True in production (HTTPS)

\# 'REFRESH_TOKEN_COOKIE_SECURE': False, # True in production (HTTPS)

\# 'ACCESS_TOKEN_COOKIE_HTTP_ONLY': True, # Should be True

\# 'REFRESH_TOKEN_COOKIE_HTTP_ONLY': True, # Should be True

\# 'ACCESS_TOKEN_COOKIE_SAMESITE': 'Lax', # Or 'None' with secure=True

\# 'REFRESH_TOKEN_COOKIE_SAMESITE': 'Lax', # Or 'None' with secure=True

\# }

\# Define the cookie name in settings for easy access

\# ACCESS_TOKEN_COOKIE_NAME = 'access_token'

1. **Database Migrations:** Run migrations to create the necessary database tables for PTOBalance (and ensure migrations for dependent apps have been run).

Bash

python manage.py makemigrations ptobalance

python manage.py migrate

1. **Include URLs:** Register the API endpoint and the template view in your project's urls.py.

Python

\# your_project/urls.py

from django.contrib import admin

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from ptobalance.api import register as register_ptobalance_api

from ptobalance.urls import urlpatterns as ptobalance_template_urls # For the template view

router = DefaultRouter()

register_ptobalance_api(router) # Registering PTO Balance API routes

urlpatterns = \[

path('admin/', admin.site.urls),

path('api/', include(router.urls)), # Exposing API endpoints

path('ptobalance/', include(ptobalance_template_urls)), # Exposing the template view

\# Ensure you have a 'frontend_login' URL defined somewhere for redirects

\# path('login/', your_app.views.login_view, name='frontend_login'),

\# ... other paths

\]

1. **Frontend Template:** Create the ptobalance_view.html template in your app's templates directory (e.g., ptobalance/templates/ptobalance_view.html).

**3\. Code Structure and Components**

The application is structured into several key components:

- **models.py**: Defines the PTOBalance database schema and its relationships.
- **serializers.py**: Handles the conversion of PTOBalance and related models to/from JSON.
- **views.py**: Contains the API ViewSet for retrieving PTO balances and a TemplateView for rendering a frontend page with authentication enforcement.
- **urls.py**: Defines URL patterns for the TemplateView.
- **api.py**: Manages API URL routing for the PTOBalanceViewSet.
- **tasks.py (simulated/implied by update_pto_balance_monthly and update_pto_balance_biweekly functions):** Contains the core logic for automated PTO accrual.
- **forms.py**: Provides a ModelForm for PTOBalance, primarily used in the Django admin to customize user selection.
- **admin.py**: Configures the Django admin interface for PTOBalance, including sophisticated logic to automatically set accrual rates.

**4\. Detailed Component Documentation**

**4.1. ptobalance/models.py**

This file defines the PTOBalance model, which stores the core PTO information for each user.

Python

from django.db import models

from django.contrib.auth.models import User

from employeetype.models import EmployeeType

from payfrequency.models import Pay_Frequency

from yearofexperience.models import YearOfExperience # Assumed to be linked to User

from accuralrates.models import AccrualRates

class PTOBalance(models.Model):

user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="pto_balance")

employee_type = models.ForeignKey(EmployeeType, on_delete=models.CASCADE, related_name="pto_balances")

pay_frequency = models.ForeignKey(Pay_Frequency, on_delete=models.CASCADE, related_name="pto_balances")

year_of_experience = models.OneToOneField(YearOfExperience, on_delete=models.CASCADE, related_name="pto_balances", editable=False)

accrual_rate = models.ForeignKey(AccrualRates, on_delete=models.CASCADE, related_name="pto_balances", editable=False)

pto_balance = models.FloatField(default=0.0)

def calculate_initial_balance(self):

"""Calculate initial PTO balance based on accrual rate and experience."""

return self.accrual_rate.accrual_rate # Placeholder logic

def \__str_\_(self):

return f"{self.user.username} - PTO: {self.pto_balance}"

class Meta:

verbose_name = "PTO Balance"

verbose_name_plural = "PTO Balance"

- **PTOBalance Model:**
  - **user**: A OneToOneField linking to Django's built-in User model. This ensures each user has exactly one PTO balance record. related_name="pto_balance" allows accessing the balance directly from a User instance (e.g., user.pto_balance).
  - **employee_type**: A ForeignKey to the EmployeeType model (from employeetype app), specifying the employee's classification.
  - **pay_frequency**: A ForeignKey to the Pay_Frequency model (from payfrequency app), indicating how often the employee is paid.
  - **year_of_experience**: A OneToOneField to YearOfExperience (from yearofexperience app). This suggests that each user's experience is tracked uniquely. editable=False indicates this field's value is set programmatically (e.g., in admin save_model).
  - **accrual_rate**: A ForeignKey to AccrualRates (from accuralrates app). This links to the specific rate at which PTO accrues. editable=False implies this is also set automatically.
  - **pto_balance**: A FloatField storing the current PTO balance, defaulting to 0.0.
  - **calculate_initial_balance()**: A placeholder method, suggesting that initial balance calculation can be customized.
  - **\__str_\_(self)**: Provides a user-friendly string displaying the username and their current PTO balance.

**4.2. ptobalance/serializers.py**

This file defines the serializers for PTOBalance and its related models, controlling how this complex data structure is exposed via the API.

Python

from rest_framework import serializers

from .models import PTOBalance

from employeetype.models import EmployeeType

from payfrequency.models import Pay_Frequency

from yearofexperience.models import YearOfExperience

from django.contrib.auth.models import User

from accuralrates.models import AccrualRates

class EmployeeTypeSerializer(serializers.ModelSerializer):

class Meta:

model = EmployeeType

fields = \['name'\] # Only expose the name of the employee type

class PayFrequencySerializer(serializers.ModelSerializer):

class Meta:

model = Pay_Frequency

fields = \['frequency'\] # Only expose the frequency name

class AccuralRateSerializer(serializers.ModelSerializer):

class Meta:

model = AccrualRates

fields = \['accrual_rate'\] # Only expose the accrual rate value

class UserSerializer(serializers.ModelSerializer):

class Meta:

model = User

fields = \['username'\] # Only expose the username

class YearOfExperienceSerializer(serializers.ModelSerializer):

class Meta:

model = YearOfExperience

fields = \['years_of_experience'\] # Only expose the years of experience value

class PTOBalanaceSerializer(serializers.ModelSerializer):

\# Nested serializers for read-only display of related data

employee_type = EmployeeTypeSerializer(read_only=True)

pay_frequency = PayFrequencySerializer(read_only=True)

accrual_rate = AccuralRateSerializer(read_only=True)

user = UserSerializer(read_only=True)

year_of_experience = YearOfExperienceSerializer(read_only=True)

class Meta:

model = PTOBalance

fields = \['employee_type', 'pay_frequency', 'accrual_rate', 'user', 'year_of_experience', 'pto_balance'\]

- **Nested Serializers:** Separate serializers are defined for EmployeeType, Pay_Frequency, AccrualRates, User, and YearOfExperience. These are used to display only specific fields (e.g., name, frequency, accrual_rate, username, years_of_experience) of the related objects within the main PTOBalanaceSerializer.
- **PTOBalanaceSerializer:**
  - **Nested Fields**: It includes instances of the other serializers (employee_type, pay_frequency, accrual_rate, user, year_of_experience) as read_only=True fields. This means when a PTOBalance is serialized, these related objects' data will be embedded directly in the response.
  - **Meta Class:**
    - model: Specifies PTOBalance as the target model.
    - fields: Explicitly lists all the fields to be included in the API representation, including the nested fields.

**4.3. ptobalance/views.py**

This file contains two main views: an API ViewSet for retrieving PTO balances and a TemplateView for rendering a frontend page.

Python

from rest_framework import viewsets

from .models import PTOBalance

from .serializer import PTOBalanaceSerializer

from rest_framework.permissions import IsAuthenticated

from django.views.generic import TemplateView

from django.conf import settings

from django.urls import reverse

from rest_framework_simplejwt.tokens import AccessToken, TokenError

from django.shortcuts import redirect

class PTOBalanceViewSet(viewsets.ReadOnlyModelViewSet):

serializer_class = PTOBalanaceSerializer

permission_classes = \[IsAuthenticated\] # Requires user to be authenticated

def get_queryset(self):

user = self.request.user # Get the currently authenticated user

return PTOBalance.objects.filter(user=user) # Return only that user's PTO balance

class PTOBalanceView(TemplateView):

template_name = 'ptobalance_view.html' # Template to render

def dispatch(self, request, \*args, \*\*kwargs):

\# Retrieve the access token from cookies

access_token = request.COOKIES.get(settings.ACCESS_TOKEN_COOKIE_NAME)

\# If no token, redirect to login

if not access_token:

return redirect(reverse('frontend_login'))

try:

\# Verify the access token's validity

AccessToken(access_token).verify()

except TokenError:

\# If token is invalid or expired, redirect to login

return redirect(reverse('frontend_login'))

\# If token is valid, proceed with the view (render the template)

return super().dispatch(request, \*args, \*\*kwargs)

- **PTOBalanceViewSet:**
  - Inherits from viewsets.ReadOnlyModelViewSet, meaning it only provides read operations (list and retrieve) for PTO balances.
  - permission_classes = \[IsAuthenticated\]: Restricts access to authenticated users only.
  - **get_queryset(self)**: **Crucially**, this method filters the queryset to return _only the PTOBalance object associated with the currently authenticated user (self.request.user)_. This ensures users can only view their own PTO information.
- **PTOBalanceView:**
  - A TemplateView that renders a specific HTML template (ptobalance_view.html).
  - **dispatch(self, request, \*args, \*\*kwargs)**: This method intercepts incoming requests _before_ the view logic runs.
    - It tries to retrieve the JWT access_token from the request's cookies (using a name defined in settings.ACCESS_TOKEN_COOKIE_NAME).
    - If the token is missing or if AccessToken(access_token).verify() raises a TokenError (e.g., token is invalid, expired, or tampered with), the user is **redirected to a frontend login URL** (frontend_login defined in urls.py).
    - If the token is present and valid, the original dispatch method (which renders the template) is called, allowing the view to proceed. This effectively acts as a server-side authentication gate for the frontend view.

**4.4. ptobalance/urls.py**

This file specifically defines the URL patterns for the PTOBalanceView (the template view).

Python

from django.urls import path

from .views import PTOBalanceView

urlpatterns = \[

path('', PTOBalanceView.as_view(), name='ptobalance'), # Maps root of app to PTOBalanceView

\]

- This defines a URL pattern that, when included in a project's urls.py (e.g., path('ptobalance/', include(ptobalance_template_urls))), would map /ptobalance/ to the PTOBalanceView. The name='ptobalance' allows for easy referencing via reverse('ptobalance').

**4.5. ptobalance/api.py**

This file is responsible for registering the PTOBalanceViewSet with the Django REST Framework router.

Python

from .views import PTOBalanceViewSet

def register(router):

router.register(r'ptobalance', PTOBalanceViewSet, basename='ptobalance')

- **register(router) Function:**
  - Takes a router object (e.g., DefaultRouter) as an argument.
  - router.register(r'ptobalance',PTOBalanceViewSet, basename = 'ptobalance'): This sets up the API endpoints for PTOBalanceViewSet under the /api/ptobalance/ path.

**4.6. ptobalance/tasks.py (Implied from the provided functions)**

These functions contain the core logic for automatically updating PTO balances, typically run as scheduled tasks (e.g., via Django-RQ, Celery, or a simple cron job).

Python

from datetime import datetime

from .models import PTOBalance # Model for PTO balance

from biweeklycron.models import BiweeklyCron # Control model for biweekly tasks

from django.utils.timezone import localdate # For current local date

from django.core.exceptions import ObjectDoesNotExist # For error handling

def update_pto_balance_monthly():

"""

Updates the PTO balance for eligible full-time employees on a monthly basis.

"""

print(f"Running monthly PTO update at {datetime.now()}")

\# Query eligible full-time employees with monthly pay frequency and PTO less than cap

for obj in PTOBalance.objects.filter(

employee_type_\_name="Full Time",

pay_frequency_\_frequency="Monthly",

pto_balance_\_lt=340 # Only update if below the cap

):

\# Increase PTO balance, ensuring it doesn't exceed 340 hours

obj.pto_balance = min(obj.pto_balance + obj.accrual_rate.accrual_rate, 340)

obj.save() # Save the updated balance

return "Monthly PTO updated"

def update_pto_balance_biweekly():

"""

Updates the PTO balance for eligible full-time employees with a biweekly pay frequency.

Uses \`BiweeklyCron\` to ensure it runs only once per scheduled date.

"""

today = localdate() # Get today's date in local timezone

try:

\# Attempt to get an active biweekly cron job record for today

record = BiweeklyCron.objects.get(run_date=today, is_active=True)

\# Filter eligible full-time, biweekly employees with PTO < 340

for obj in PTOBalance.objects.filter(

employee_type_\_name="Full Time",

pay_frequency_\_frequency="Biweekly",

pto_balance_\_lt=340

):

\# Update and cap the PTO balance

obj.pto_balance = min(obj.pto_balance + obj.accrual_rate.accrual_rate, 340)

obj.save()

\# Mark this cron record as inactive to prevent it from running again today

record.is_active = False

record.save()

return "✅ Biweekly PTO updated"

except ObjectDoesNotExist:

\# If no active cron record for today, log and return a message

print(f"❌ No active biweekly record for {today}")

return f"No active record for {today}"

- **update_pto_balance_monthly():**
  - This function iterates through PTOBalance records.
  - It **filters** for "Full Time" employees with "Monthly" pay frequency whose pto_balance is currently less than 340 hours (the defined cap).
  - For each qualifying employee, it **adds their accrual_rate** to their pto_balance, using min() to ensure the balance **never exceeds 340**.
  - The updated PTOBalance object is then saved.
- **update_pto_balance_biweekly():**
  - This function handles bi-weekly accruals and includes a **control mechanism** using BiweeklyCron model.
  - It first tries to retrieve an active BiweeklyCron record for the current localdate(). This is crucial to ensure the bi-weekly update runs _only once_ on a given schedule date, even if the script is triggered multiple times.
  - If an active record exists, it proceeds to filter and update PTOBalance records for "Full Time" employees with "Biweekly" pay frequency, similar to the monthly update logic.
  - **After successful updates**, it marks the BiweeklyCron record as is_active = False to prevent subsequent runs for that day.
  - If no active BiweeklyCron record is found for today, it gracefully exits, indicating that the scheduled condition for the update has not been met.

**4.7. ptobalance/forms.py**

This file provides a Django ModelForm used primarily within the admin to manage user selection.

Python

from django import forms

from django.contrib.auth.models import User

from .models import PTOBalance

class PTOBalanceForm(forms.ModelForm):

class Meta:

model = PTOBalance

fields = '\__all_\_'

def \__init_\_(self, \*args, \*\*kwargs):

super().\__init_\_(\*args, \*\*kwargs)

\# Customize the user queryset to prevent duplicate PTOBalance records

if self.instance and self.instance.pk: # Editing an existing record

\# Allow selecting the current user OR users without an existing PTOBalance

self.fields\['user'\].queryset = User.objects.filter(pto_balance_\_isnull=True) | User.objects.filter(pk=self.instance.user.pk)

else: # Creating a new record

\# Only allow selecting users who do NOT yet have a PTOBalance record

self.fields\['user'\].queryset = User.objects.filter(pto_balance_\_isnull=True)

- **PTOBalanceForm:**
  - A ModelForm for the PTOBalance model.
  - **\__init_\_(self, \*args, \*\*kwargs)**: This method customizes the queryset for the user field in the form.
    - When **creating a new** PTOBalance record, it limits the user dropdown to only display users who _do not already_ have an associated PTOBalance (pto_balance_\_isnull=True). This prevents accidentally creating duplicate PTO records for a single user.
    - When **editing an existing** PTOBalance record, it ensures that the currently selected user remains available in the dropdown, along with any other users who don't yet have a PTO balance.

**4.8. ptobalance/admin.py**

This file extensively customizes the Django admin interface for the PTOBalance model, including crucial logic for setting accrual_rate and year_of_experience automatically.

Python

from django.contrib import admin

from django.db import models # Not directly used in the final version of the snippet, but good for context

from .models import PTOBalance, AccrualRates, YearOfExperience # Ensure these are imported

@admin.register(PTOBalance)

class PTOBalanceAdmin(admin.ModelAdmin):

list_display = ('user', 'employee_type', 'pay_frequency', 'pto_balance', 'accrual_rate', 'display_year_of_experience')

search_fields = ('user_\_username', 'employee_type_\_name', 'pay_frequency_\_frequency')

\# form = PTOBalanceForm # (Not in provided code, but recommended to use custom form)

def display_year_of_experience(self, obj):

"""Custom display method to show user's years of experience."""

try:

\# Accesses the YearOfExperience object through the User's related_name 'experience'

return obj.user.experience.years_of_experience

except YearOfExperience.DoesNotExist:

return "N/A"

display_year_of_experience.short_description = 'Years of Experience'

\# Allows sorting the admin list by years of experience

display_year_of_experience.admin_order_field = 'user_\_experience_\_years_of_experience'

def save_model(self, request, obj, form, change):

"""

Overrides save_model to automatically determine and assign

'accrual_rate' and 'year_of_experience' before saving.

"""

employeetype = obj.employee_type

payfrequency = obj.pay_frequency

\# 1. Determine the user's Years of Experience

try:

\# Assumes User has a related_name 'experience' pointing to YearOfExperience

user_experience_obj = obj.user.experience

year_of_experience_value = user_experience_obj.years_of_experience

except YearOfExperience.DoesNotExist:

year_of_experience_value = 0.0 # Default if no experience record

user_experience_obj = None

print(f"Warning: YearOfExperience record missing for user {obj.user.username}")

\# 2. Map Years of Experience to a defined threshold (1-10, or 11+)

\# This logic determines which 'x' value (representing YOE threshold) to use for lookup

thresholds = \[1, 2, 3, 4, 5, 6, 7, 8, 9, 10\]

x = 1

for threshold in thresholds:

if year_of_experience_value < threshold:

x = threshold # Use the first threshold the YOE is \*less than\*

break

else: # If YOE is 10 or more, assign x=11

x = 11

\# 3. Look up the appropriate AccrualRate

accrualrate = AccrualRates.objects.filter(

employee_type=employeetype,

pay_frequency=payfrequency,

year_of_experience=x # Use the calculated 'x' (threshold value)

).first()

\# 4. Assign the found AccrualRate to the PTOBalance object

if accrualrate:

obj.accrual_rate = accrualrate

else:

obj.accrual_rate = None # Or handle error appropriately

print(f"Warning: No AccrualRate found for EType:{employeetype.name}, PFreq:{payfrequency.frequency}, YOE:{x}")

\# 5. Assign the YearOfExperience object (found or None)

obj.year_of_experience = user_experience_obj

\# 6. Call the original save_model to save the object with updated fields

super().save_model(request, obj, form, change)

- **PTOBalanceAdmin:**
  - **list_display**: Configures the columns displayed in the admin list view, including a custom display_year_of_experience method.
  - **search_fields**: Enables searching by username, employee type name, and pay frequency.
  - **display_year_of_experience(self, obj)**: A custom method to show the years_of_experience directly from the user's related YearOfExperience object. It includes error handling if the YearOfExperience object doesn't exist for a user.
  - **save_model(self, request, obj, form, change)**: This is a crucial override for automated logic. It executes **before** a PTOBalance object is saved (or updated) in the admin.
        1. **Retrieve Dependencies**: It fetches the employee_type and pay_frequency from the PTOBalance object being saved.
        2. **Determine Years of Experience**: It attempts to get the years_of_experience from the related User object (assuming User has a related_name='experience' pointing to YearOfExperience). It provides a default of 0.0 if not found.
        3. **Map YOE to Threshold**: It then maps the actual years_of_experience_value to a defined set of thresholds (1 through 10, or 11+). This x value is used for looking up the AccrualRates. This is a common pattern for defining tier-based benefits.
        4. **Look Up Accrual Rate**: It queries the AccrualRates model, searching for a record that matches the employee_type, pay_frequency, and the calculated x (years of experience threshold).
        5. **Assign Accrual Rate**: If a matching accrualrate is found, it's assigned to obj.accrual_rate. If not, it's set to None (or an appropriate error/warning is logged).
        6. **Assign YearOfExperience Object**: The actual YearOfExperience object (or None) is assigned to obj.year_of_experience.
        7. **Save Model**: Finally, super().save_model() is called to save the PTOBalance object with these automatically determined foreign key assignments.

**5\. API Endpoints and Frontend Views**

- **API Endpoint:**
  - **GET /api/ptobalance/**: Allows an authenticated user to retrieve their own PTO balance details.
    - **Authentication Required:** Requires a valid JWT access token in cookies or Authorization header.
    - **Example Response:**

JSON

\[

{

"employee_type": { "name": "Full Time" },

"pay_frequency": { "frequency": "Biweekly" },

"accrual_rate": { "accrual_rate": 8.67 },

"user": { "username": "john.doe" },

"year_of_experience": { "years_of_experience": 5.0 },

"pto_balance": 125.5

}

\]

(Note: Response is a list, as ReadOnlyModelViewSet by default provides a list view. If there's only one balance per user, it will be a list containing one object.)

- **Frontend Template View:**
  - **GET /ptobalance/**: Renders the ptobalance_view.html template.
    - **Authentication Enforced:** This view performs server-side validation of the JWT access token from cookies. If the token is missing or invalid, the user is redirected to a login page (assuming a URL named frontend_login exists).
    - This view acts as a secure gateway for displaying PTO information to the user in a rich web interface.

**6\. Scheduled Tasks (PTO Accrual)**

The update_pto_balance_monthly() and update_pto_balance_biweekly() functions are designed to be run periodically outside of the web request cycle.

- **Monthly Accrual:** Should be scheduled to run once a month (e.g., first day of the month) to add PTO to monthly-paid full-time employees.
- **Bi-weekly Accrual:** Should be scheduled to run every two weeks. The BiweeklyCron model acts as a safeguard, ensuring that the update only happens once per designated bi-weekly run_date, preventing accidental multiple accruals on the same day.

These scheduled tasks are critical for automating the PTO accrual process, ensuring balances are kept up-to-date without manual intervention.