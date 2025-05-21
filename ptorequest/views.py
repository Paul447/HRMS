from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import PTORequests
from .serializer import PTORequestsSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import render

# Only dedicated to PTO Request Create Functionality Not for List, Update, Delete
class PTORequestsViewSet(viewsets.ModelViewSet):
    queryset = PTORequests.objects.all()
    serializer_class = PTORequestsSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        # Optionally limit to the current user's requests
        return None
    def destroy(self, request, *args, **kwargs):
        self.http_method_not_allowed(request, *args, **kwargs)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)  # allow this if you want users to see their requests
    def update(self, request, *args, **kwargs):
        self.http_method_not_allowed(request, *args, **kwargs)
    def partial_update(self, request, *args, **kwargs):
        self.http_method_not_allowed(request, *args, **kwargs)

class PTORequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return render(request, 'ptorequest.html')

