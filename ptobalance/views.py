from rest_framework import viewsets
from .models import PTOBalance
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from .serializer import PTOBalanaceSerializer
# Create your views here.

class PTOBalanceViewSet(viewsets.ModelViewSet):
    queryset = PTOBalance.objects.all()
    serializer_class = PTOBalanaceSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            # Handle the integrity error gracefully
            return Response(
                {"detail": f"Integrity Error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_update(serializer)
            return Response(serializer.data)
        except IntegrityError as e:
            # Handle the integrity error gracefully
            return Response(
                {"detail": f"Integrity Error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
