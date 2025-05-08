from django.urls import path ,include
from rest_framework.routers import DefaultRouter
from .views import PayFrequencyViewSet

router = DefaultRouter()
router.register(r'payfrequency', PayFrequencyViewSet, basename='payfrequency')
urlpatterns = [
    path('', include(router.urls)),
]
