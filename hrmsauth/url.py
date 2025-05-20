from django.urls import path
from .views import LoginView, RefreshTokenView, LogoutView, FrontendLoginView , DashboardView


urlpatterns = [
    path('api/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('login/', FrontendLoginView.as_view(), name='frontend_login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
