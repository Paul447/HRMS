from django.shortcuts import render
from .serializer import DecisionedTimeOffSerializer
from rest_framework import viewsets
from timeoffreq.models import TimeoffRequest
from rest_framework import permissions
from .permissions import IsManagerOfDepartment

# Create your views here.


class DecisionedTimeOffViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing decisioned time off requests.
    """

    serializer_class = DecisionedTimeOffSerializer
    queryset = TimeoffRequest.objects.filter(status__in=["approved", "rejected"]).select_related("employee", "requested_leave_type__leave_type")

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        Superusers will only require IsAuthenticated.
        """
        if self.request.user.is_superuser:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsManagerOfDepartment()]

    def get_queryset(self):
        # Optionally filter by user or other criteria
        user = self.request.user
        if user.is_superuser:
            return self.queryset.filter(employee=self.request.user) if self.request.user.is_authenticated else self.queryset.none()
