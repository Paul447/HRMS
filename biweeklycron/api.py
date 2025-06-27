from .views import BiweeklyCronViewSet


def register(router):
    router.register(r"biweeklycron", BiweeklyCronViewSet, basename="biweeklycron")
