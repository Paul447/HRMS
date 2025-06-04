**Accrual Rate Management API Documentation**

**1\. Application Overview**

This backend API manages Accrual Rates. It allows clients to create, retrieve, update, and delete AccrualRate objects. Each AccrualRate defines how leave hours are accrued, based on:

- **Years of Experience**
- **Employee Type**
- **Pay Frequency**
- **Accrual Rate (per pay period)**
- **Annual Accrual Rate (per year)**

The API is built with Django REST Framework.

**2\. Setup and Installation**

**Dependencies:**

- Django
- djangorestframework
- employeetype app
- payfrequency app

**Steps:**

1. **Integrate the App**: Place code in a Django app named accrualrates.
2. **Add to INSTALLED_APPS**:

INSTALLED_APPS = \[

'rest_framework',

'employeetype',

'payfrequency',

'accrualrates',

\]

1. **Database Migrations**:

python manage.py makemigrations accrualrates

python manage.py migrate

1. **Include URLs**:

\# your_project/urls.py

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from accrualrates.api import register as register_accrualrates_routes

router = DefaultRouter()

register_accrualrates_routes(router)

urlpatterns = \[

path('admin/', admin.site.urls),

path('api/', include(router.urls)),

\]

**3\. Code Structure**

- **models.py**: Defines the AccrualRates model.
- **serializers.py**: Converts model instances to JSON/XML.
- **views.py**: Handles API logic via ModelViewSet.
- **api.py**: Registers routes.
- **admin.py**: Customizes admin panel.

**4\. Detailed Components**

**4.1. models.py**

from django.db import models

from employeetype.models import EmployeeType

from payfrequency.models import Pay_Frequency

class AccrualRates(models.Model):

EXPERIENCE_CHOICES = \[(i, f"{i} Year(s)") for i in range(1, 12)\]

year_of_experience = models.IntegerField(choices=EXPERIENCE_CHOICES)

accrual_rate = models.FloatField(default=0.0)

annual_accrual_rate = models.FloatField(default=0.0)

employee_type = models.ForeignKey(EmployeeType, on_delete=models.CASCADE, related_name="accrual_rates")

pay_frequency = models.ForeignKey(Pay_Frequency, on_delete=models.CASCADE, related_name="accrual_rates")

class Meta:

verbose_name = "Accrual Rate"

verbose_name_plural = "Accrual Rates"

unique_together = ('year_of_experience', 'employee_type', 'pay_frequency')

def \__str_\_(self):

return f"{self.year_of_experience} Years - {self.employee_type} - {self.pay_frequency}: {self.accrual_rate}"

**4.2. serializers.py**

from rest_framework import serializers

from .models import AccrualRates

from employeetype.models import EmployeeType

from payfrequency.models import Pay_Frequency

class EmployeeTypeSerializer(serializers.ModelSerializer):

class Meta:

model = EmployeeType

fields = \['name'\]

class PayFrequencySerializer(serializers.ModelSerializer):

class Meta:

model = Pay_Frequency

fields = \['frequency'\]

class AccuralRateSerializer(serializers.ModelSerializer):

url = serializers.HyperlinkedIdentityField(view_name='accuralrates-detail')

employee_type = EmployeeTypeSerializer(read_only=True)

pay_frequency = PayFrequencySerializer(read_only=True)

employee_type_id = serializers.PrimaryKeyRelatedField(queryset=EmployeeType.objects.all(), source='employee_type', write_only=True)

pay_frequency_id = serializers.PrimaryKeyRelatedField(queryset=Pay_Frequency.objects.all(), source='pay_frequency', write_only=True)

class Meta:

model = AccrualRates

fields = '\__all_\_'

**4.3. views.py**

from .serializer import AccuralRateSerializer

from .models import AccrualRates

from rest_framework import viewsets

class AccuralRateViewSet(viewsets.ModelViewSet):

queryset = AccrualRates.objects.all()

serializer_class = AccuralRateSerializer

**4.4. api.py**

from .views import AccuralRateViewSet

def register(router):

router.register(r'accuralrates', AccuralRateViewSet, basename='accuralrates')

**4.5. admin.py**

from django.contrib import admin

from .models import AccrualRates

@admin.register(AccrualRates)

class AccrualRatesAdmin(admin.ModelAdmin):

list_display = ('year_of_experience', 'accrual_rate', 'annual_accrual_rate', 'employee_type', 'pay_frequency')

search_fields = ('year_of_experience', 'employee_type_\_name')

list_filter = ('employee_type', 'pay_frequency')

ordering = ('year_of_experience',)

list_per_page = 10

**5\. API Endpoints**

**Base URL: /api/accuralrates/**

- **GET /**: List all accrual rates
- **POST /**: Create a new accrual rate

{

"year_of_experience": 5,

"accrual_rate": 1.75,

"annual_accrual_rate": 21.0,

"employee_type_id": 1,

"pay_frequency_id": 2

}

- **GET /{id}/**: Retrieve details of an accrual rate
- **PUT /{id}/**: Full update of an accrual rate
- **PATCH /{id}/**: Partial update
- **DELETE /{id}/**: Delete an accrual rate

End of Documentation