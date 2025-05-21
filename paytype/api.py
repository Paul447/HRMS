from  .views import PayTypeViewSet

def register(router):
    router.register(r'paytype', PayTypeViewSet, basename='paytype')
    