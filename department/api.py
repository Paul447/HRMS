from .views import DepartmentViewSet , UserProfileViewSet

def register(router):
    router.register(r'department', DepartmentViewSet, basename='department')
def register_userprofile(router):
    router.register(r'userprofile', UserProfileViewSet, basename='userprofile')