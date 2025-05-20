from django.contrib import admin
from django.urls import path, include   
from .models import YearOfExperience

@admin.register(YearOfExperience)
class YearOfExperienceAdmin(admin.ModelAdmin):
    list_display = ('user', 'years_of_experience',)
    search_fields = ('user__username',)
    list_filter = ('years_of_experience',)
    ordering = ('-years_of_experience',)
    list_per_page = 10