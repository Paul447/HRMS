from django.urls import path ,include
from rest_framework.routers import DefaultRouter
from .views import PayFrequencyViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import login_page, dashboard
# router = DefaultRouter()
# router.register(r'payfrequency', PayFrequencyViewSet)
urlpatterns = [
    path('api/protected/',PayFrequencyViewSet.as_view(), name='protected'),
    path('login/',login_page, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
]

