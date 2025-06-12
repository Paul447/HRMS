from django.shortcuts import render
from rest_framework import viewsets
from department.models import Department
from department.serializer import DepartmentSerializer
from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework.exceptions import ParseError
# from django.contrib.auth.mixins import LoginRequiredMixin
from payperiod.models import PayPeriod
from django.utils import timezone
from ptorequest.models import PTORequests
from timeoff_management.serializer import TimeOffManagementSerializer
from timeoff_management.filter import PTORequestFilter

# Create your views here.
class IsSuperuserCustom():
    """
    Custom permission class to check if the user is a superuser.
    This can be used to restrict access to certain views.
    """
    def has_permission(self, request, view):
        return bool(request.user.is_superuser)
    def has_object_permission(self, request, view, obj):
        return bool(request.user.is_superuser)

class DepartmentReturnView(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for returning department information.
    This is a read-only viewset that allows users to retrieve department data.
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsSuperuserCustom]

    def get_queryset(self):
        return super().get_queryset()
    

# This viewset can be used to return all the time off requests for the current pay period.
class TimeOffRequestViewCurrentPayPeriodAdmin(viewsets.ModelViewSet):
    """
    ViewSet for returning time off requests for the current pay period.
    This is a read-only viewset that allows users to retrieve time off request data.
    """
    permission_classes = [IsSuperuserCustom, IsAuthenticated]
    serializer_class = TimeOffManagementSerializer
    http_method_names = ['get', 'put', 'patch', 'head', 'options', 'trace']
    filterset_class = PTORequestFilter
    def get_queryset(self):
        # Start with the base queryset
        queryset = PTORequests.objects.filter(status='pending')
        now = timezone.now() 
        return queryset.order_by('-created_at')

    # def perform_update(self, serializer):

    #     serializer.save()