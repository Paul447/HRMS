from .views import DepartmentViewSet

def register(router):
    router.register(r'department', DepartmentViewSet, basename='department')