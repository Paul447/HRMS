from .views import YearOfExperienceViewSet


def register(router):
    router.register(r"experience", YearOfExperienceViewSet)
