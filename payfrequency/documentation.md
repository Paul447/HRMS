Pay Frequency Management API Documentation  
This documentation outlines the core components of an API designed to manage Pay Frequencies. It provides a standardized way to define and categorize how often employees are paid within a system.

1. Application Overview  
    This application serves as a backend API for managing Pay_Frequency records. It exposes endpoints to create, retrieve, update, and delete various payment frequencies (e.g., "Monthly", "Bi-Weekly", "Weekly"). Each Pay_Frequency is uniquely identified by its frequency name.

A key aspect of this API is that its management operations are restricted to administrators, ensuring that only authorized users can modify the defined pay frequencies. The API is built using Django REST Framework, offering standard CRUD operations with an emphasis on security.

1. Setup and Installation  
    To set up this application, you'll need a Django project configured with Django REST Framework.

Dependencies:

- Django
- djangorestframework

Steps:

1. Integrate into your Django Project: Place the provided files within a Django app (e.g., named payfrequency).
2. Add to INSTALLED_APPS: Ensure your settings.py includes this app:

\# settings.py

INSTALLED_APPS = \[

\# ...

'rest_framework',

'payfrequency', # Your pay frequency app

\# ...

\]

1. Database Migrations: Run migrations to create the necessary database tables for Pay_Frequency:

python manage.py makemigrations payfrequency

python manage.py migrate

1. Include URLs: Register the API endpoints in your project's urls.py. This example uses DefaultRouter from Django REST Framework:

\# your_project/urls.py

from django.contrib import admin

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from payfrequency.api import register as register_payfrequency_routes

router = DefaultRouter()

register_payfrequency_routes(router) # Registering pay frequency routes

urlpatterns = \[

path('admin/', admin.site.urls),

path('api/', include(router.urls)), # Exposing API endpoints

\# ... other paths

\]

1. Code Structure and Components  
    The application is structured into several key components:

- models.py: Defines the database schema for Pay_Frequency.
- serializers.py: Handles the conversion of Pay_Frequency model instances to and from JSON/XML.
- views.py: Contains the logic for handling API requests using Django REST Framework's ModelViewSet, with admin-only permissions.
- api.py: Manages API URL routing using DefaultRouter.
- admin.py: Configures the Django admin interface for Pay_Frequency.

1. Detailed Component Documentation

4.1. payfrequency/models.py

from django.db import models

from django.contrib.auth.models import User # This import is not directly used in the model

class Pay_Frequency(models.Model):

frequency = models.CharField(max_length=100, unique=True)

class Meta:

verbose_name = "Pay Frequency"

verbose_name_plural = "Pay Frequencies"

def \__str_\_(self):

return self.frequency

- frequency: A CharField representing the name of the pay frequency (e.g., "Monthly", "Bi-Weekly").
- unique=True: Prevents duplicate entries.
- Meta class adds human-readable names for the admin interface.

4.2. payfrequency/serializers.py

from rest_framework import serializers

from .models import Pay_Frequency

from django.contrib.auth.models import User , Permission, Group

class PayFrequencySerializer(serializers.ModelSerializer):

url = serializers.HyperlinkedIdentityField(view_name = 'pay-detail')

class Meta:

model = Pay_Frequency

fields = '\__all_\_'

- HyperlinkedIdentityField generates the detail view URL.
- Meta links the serializer to the model and includes all fields.

4.3. payfrequency/views.py

from .serializer import PayFrequencySerializer

from rest_framework import viewsets

from .models import Pay_Frequency

from rest_framework.permissions import IsAdminUser

class PayFrequencyViewSet(viewsets.ModelViewSet):

permission_classes = \[IsAdminUser\]

queryset = Pay_Frequency.objects.all()

serializer_class = PayFrequencySerializer

- Only admin users can access the endpoints.
- Provides full CRUD functionality via ModelViewSet.

4.4. payfrequency/api.py

from .views import PayFrequencyViewSet

def register(router):

router.register(r'pay', PayFrequencyViewSet, basename = "pay")

- Registers the viewset with the router at endpoint /api/pay/.

4.5. payfrequency/admin.py

from django.contrib import admin

from .models import Pay_Frequency

@admin.register(Pay_Frequency)

class PayFrequencyAdmin(admin.ModelAdmin):

list_display = ('frequency',)

search_fields = ('frequency',)

list_filter = ('frequency',)

ordering = ('frequency',)

list_per_page = 10

- Customizes the admin interface: display, filtering, search, pagination.

1. API Endpoints  
    Once integrated and running, the API will expose the following endpoints (assuming your base API URL is /api/). All endpoints require admin permissions.

- GET /api/pay/: Retrieve a list of all pay frequencies.
- POST /api/pay/: Create a new pay frequency.
  - Request Body Example:
  - {
  - "frequency": "Monthly"
  - }
- GET /api/pay/{id}/: Retrieve details of a specific pay frequency by ID.
- PUT /api/pay/{id}/: Full update of a pay frequency.
- PATCH /api/pay/{id}/: Partial update of a pay frequency.
- DELETE /api/pay/{id}/: Delete a pay frequency by ID.