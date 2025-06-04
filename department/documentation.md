**User Profile and Department Management API Documentation**

**1\. Application Overview**

This application extends Django's default user functionality by introducing:

- **Departments**: Categorize users into different departments.
- **User Profiles**: One-to-one extension of the built-in User model, linking a user to a specific department.

It also provides a read-only API endpoint for retrieving a logged-in user's profile and department, and integrates with the Django admin interface for management.

**2\. Setup and Installation**

**Dependencies:**

- Django
- djangorestframework

**Steps:**

1. **Integrate the App**: Place the code in a Django app (e.g., user_management).
2. **Add to INSTALLED_APPS**:

INSTALLED_APPS = \[

'rest_framework',

'user_management',

\]

1. **Database Migrations**:

python manage.py makemigrations user_management

python manage.py migrate

1. **Include URLs**:

\# your_project/urls.py

from django.contrib import admin

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from user_management.api import register_userprofile

router = DefaultRouter()

register_userprofile(router)

urlpatterns = \[

path('admin/', admin.site.urls),

path('api/', include(router.urls)),

\]

**3\. Code Structure**

- models.py: Defines Department and UserProfile.
- serializers.py: Serializes models for API.
- views.py: Contains UserProfileViewSet.
- api.py: Registers routes.
- admin.py: Admin customization.

**4\. Detailed Components**

**4.1. models.py**

from django.db import models

class Department(models.Model):

name = models.CharField(max_length=100)

created_at = models.DateTimeField(auto_now_add=True)

updated_at = models.DateTimeField(auto_now=True)

def \__str_\_(self):

return self.name

class UserProfile(models.Model):

user = models.OneToOneField('auth.User', on_delete=models.CASCADE)

department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)

**4.2. serializers.py**

from rest_framework import serializers

from .models import Department, UserProfile

class DepartmentSerializer(serializers.ModelSerializer):

class Meta:

model = Department

fields = '\__all_\_'

class UserProfileSerializer(serializers.ModelSerializer):

department = DepartmentSerializer(read_only=True)

class Meta:

model = UserProfile

fields = \['department'\]

def to_representation(self, instance):

rep = super().to_representation(instance)

department_data = rep.pop('department', {})

rep.update(department_data)

return rep

**4.3. views.py**

from rest_framework import viewsets

from .models import UserProfile

from .serializers import UserProfileSerializer

from rest_framework.permissions import IsAuthenticated

class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):

serializer_class = UserProfileSerializer

permission_classes = \[IsAuthenticated\]

def get_queryset(self):

user = self.request.user

return UserProfile.objects.filter(user=user)

**4.4. api.py**

from .views import UserProfileViewSet

def register_userprofile(router):

router.register(r'department', UserProfileViewSet, basename='userprofile')

**4.5. admin.py**

from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from django.contrib.auth.models import User

from .models import Department, UserProfile

@admin.register(Department)

class DepartmentAdmin(admin.ModelAdmin):

list_display = ('name',)

search_fields = ('name',)

ordering = ('name',)

@admin.register(UserProfile)

class UserProfileAdmin(admin.ModelAdmin):

list_display = ('user', 'department')

search_fields = ('user_\_username', 'department_\_name')

list_filter = ('department',)

ordering = ('user_\_username',)

class UserProfileInline(admin.StackedInline):

model = UserProfile

can_delete = False

verbose_name_plural = 'Profile'

class CustomUserAdmin(BaseUserAdmin):

inlines = (UserProfileInline,)

try:

admin.site.unregister(User)

except admin.sites.NotRegistered:

pass

admin.site.register(User, CustomUserAdmin)

**5\. API Endpoints**

**Base URL: /api/department/**

- **GET /**: Retrieve the current user's UserProfile with department info.

**Example Response:**

{

"id": 1,

"name": "Human Resources",

"created_at": "2023-01-01T10:00:00Z",

"updated_at": "2023-01-01T10:00:00Z"

}

Note: This endpoint returns only the logged-in user's department profile, not a list of all departments.