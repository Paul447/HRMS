from django.shortcuts import render
from .serializer import DepartmentLeavesSerializer
from department.models import UserProfile
from datetime import datetime
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from .pagination import DepartmentLeavesPagination
from rest_framework import filters  # Import filters
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.exceptions import NotAuthenticated
from django.shortcuts import redirect
from rest_framework.response import Response



class IsTimeOffUser(permissions.BasePermission):
    """
    Custom permission to only allow users with the 'is_time_off' profile flag
    to create PTO requests.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            user_profile = request.user.userprofile  # Assuming OneToOneField
            return user_profile.is_time_off
        except UserProfile.DoesNotExist:
            return False


class DepartmentLeavesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing all the leaves in a Department to the Department team members.
    All the leaves which have the status 'approved' and a start date greater than or equal to today will be displayed.
    Can be filtered by user's first name or last name.
    """

    def get_permissions(self):
        if self.request.user.is_superuser:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsTimeOffUser()]
    serializer_class = DepartmentLeavesSerializer
    pagination_class = DepartmentLeavesPagination
    filter_backends = [filters.SearchFilter]  # Add SearchFilter
    search_fields = ["employee__first_name", "employee__last_name"]  # Fields to search against

    def get_queryset(self):
        user = self.request.user
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return self.serializer_class.Meta.model.objects.none()

        # Filter the queryset to include only approved leaves with a start date greater than or equal to today
        return self.serializer_class.Meta.model.objects.filter(status="approved", requested_leave_type__department=user_profile.department, start_date_time__gte=datetime.now()).order_by("start_date_time")  # Order by start date for better readability


class DepartmentTemplateView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated]
    template_name = "deptleaves.html"
    login_url = "frontend_login"
    versioning_class = None  # Disable versioning for this view

    def handle_exception(self, exc):
        if isinstance(exc, NotAuthenticated):
            return redirect(self.login_url)
        return super().handle_exception(exc)

    def get(self, request, *args, **kwargs):
        return Response(template_name=self.template_name)
