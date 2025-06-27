from .views import PayFrequencyViewSet


def register(router):
    router.register(r"pay", PayFrequencyViewSet, basename="pay")
