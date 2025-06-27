from .views import DepartmentBasedLeaveTypeViewSet


def register(router):
    router.register(r"departmentleavetype", DepartmentBasedLeaveTypeViewSet, basename="departmentleavetype")
