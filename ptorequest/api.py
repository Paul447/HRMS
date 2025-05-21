from .views import PTORequestsViewSet

def register(router):
    router.register(r'pto-requests', PTORequestsViewSet, basename='pto-requests')