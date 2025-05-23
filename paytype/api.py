from  .views import UserBasedPayTypeViewSet

def register(router):   
    router.register(r'paytype', UserBasedPayTypeViewSet, basename='paytype')


    