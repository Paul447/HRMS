from django.urls import path
from .views import LoginView, RefreshTokenView, LogoutView, ProtectedView, FrontendLoginView , UserViewSet, DashboardView, RegisterUserView, GroupViewSet, UserRegisterPermissionViewSet, UserRegisterGroupViewSet

def register_user(router):
    router.register(r'users', UserViewSet, basename='user')

def register_group(router):
    router.register(r'groups', GroupViewSet, basename='group')

def register_user_permission(router):
    router.register(r'permissions', UserRegisterPermissionViewSet, basename='permission')


def register_user_group(router):
    router.register(r'user_groups', UserRegisterGroupViewSet, basename='user_group')


urlpatterns = [
    path('api/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/protected/', ProtectedView.as_view(), name='protected'),
    path('login/', FrontendLoginView.as_view(), name='frontend_login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('register/', RegisterUserView.as_view(), name='register_user'),
]
