from .views import PTOBalanceViewSet

def register(router):
    router.register(r'ptobalance',PTOBalanceViewSet, basename = 'ptobalance')