from  .views import  DepartmentBasedPayTypeViewSet


def register_department(router):
    router.register(r'departmentpaytype', DepartmentBasedPayTypeViewSet, basename='departmentpaytype')


    