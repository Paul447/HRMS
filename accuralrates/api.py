from .views import AccuralRateViewSet


def register(router):
    router.register(r"accuralrates", AccuralRateViewSet, basename="accuralrates")
