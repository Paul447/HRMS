from .views import UserProfileViewSet


def register_userprofile(router):
    router.register(r"department", UserProfileViewSet, basename="userprofile")
