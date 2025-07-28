from django.urls import path
from .views import TokenObtainPairView, LogoutView, FrontendLoginView, DashboardView

app_name = "hrmsauth"

urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("login/", FrontendLoginView.as_view(), name="frontend_login"),
    path("dashboard/", DashboardView.as_view(), name="dashboard")
]
