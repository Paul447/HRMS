from rest_framework import viewsets 
from .models import  DepartmentBasedLeaveType
from department.models import UserProfile
from .serializer import DepartmentBasedLeaveTypeSerializer
from rest_framework.permissions import IsAuthenticated



# Create your views here.
class DepartmentBasedLeaveTypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DepartmentBasedLeaveTypeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        department = UserProfile.objects.filter(user=user).first()
        return DepartmentBasedLeaveType.objects.filter(department=department.department)
