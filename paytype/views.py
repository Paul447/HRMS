from rest_framework import viewsets 
from .models import UserBasedPayType
from .serializer import UserBasedPayTypeSerializer
from rest_framework.permissions import IsAuthenticated



class UserBasedPayTypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserBasedPayTypeSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        return UserBasedPayType.objects.filter(user=user)

# Create your views here.
