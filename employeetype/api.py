from .views import EmployeeTypeViewSet


def register(router):
    router.register(r"employeetype", EmployeeTypeViewSet, basename="employeetype")
