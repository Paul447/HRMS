from django.urls import path ,include
from .views import PayFrequencyViewSet,UserViewSet,  GroupViewSet


def register(router):
    router.register(r'pay', PayFrequencyViewSet, basename = "pay")
def register_group(router):
    router.register(r'group', GroupViewSet  , basename = "group")
def register_register(router):
    router.register(r'register', UserViewSet , basename = "user")
