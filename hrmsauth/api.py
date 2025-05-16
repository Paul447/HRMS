from django.urls import path
from .views import LoginView, LogoutView, ProtectedView,  FrontendLoginView

urlpatterns = [
    path('login/', FrontendLoginView.as_view(), name='frontend-login'),  # Serve login page
    path('api/login/', LoginView.as_view(), name='login'),               # API login
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/protected/', ProtectedView.as_view(), name='protected'),
]
