from rest_framework import viewsets 
from .models import  DepartmentBasedPayType
from department.models import UserProfile
from .serializer import DepartmentBasedPayTypeSerializer
from rest_framework.permissions import IsAuthenticated



# Create your views here.
class DepartmentBasedPayTypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DepartmentBasedPayTypeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        department = UserProfile.objects.filter(user=user).first()
        return DepartmentBasedPayType.objects.filter(department=department.department)
