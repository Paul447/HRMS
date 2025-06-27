# notifications_app/views.py
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet  # Used for list and retrieve operations

# Import your custom Notification model and Serializer
from .models import Notification
from .serializer import NotificationSerializer


class NotificationViewSet(ReadOnlyModelViewSet):
    """
    A ViewSet for viewing and managing notifications for the authenticated user.
    Provides endpoints for listing, retrieving, marking as read/unread, and marking all as read.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]  # Ensures only authenticated users can access these endpoints

    def get_queryset(self):
        """
        Custom queryset to ensure users can only view notifications where they are the recipient.
        This is a critical security measure.
        We use the custom manager's `for_user` method for clarity.
        """
        # Pre-fetch related data for efficiency to avoid N+1 queries
        return Notification.objects.for_user(self.request.user).select_related("actor", "content_type")
        # Note: For `content_object` (GenericForeignKey), `select_related` won't work.
        # Refer to model optimization section for more advanced prefetching of GFK.

    # GET /api/notifications/unread/
    @action(detail=False, methods=["get"])
    def unread(self, request):
        """
        Returns a list of all unread notifications for the authenticated user.
        """
        unread_notifications = self.get_queryset().unread(request.user)
        page = self.paginate_queryset(unread_notifications)  # Apply pagination
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(unread_notifications, many=True)
        return Response(serializer.data)

    # POST /api/notifications/mark_all_as_read/
    @action(detail=False, methods=["post"])
    def mark_all_as_read(self, request):
        """
        Marks all unread notifications for the authenticated user as read.
        Uses the efficient .update() method.
        """
        count = self.get_queryset().mark_all_as_read(request.user)
        return Response({"message": f"{count} notifications marked as read."}, status=status.HTTP_200_OK)

    # POST /api/notifications/{pk}/mark_as_read/
    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        """
        Marks a specific notification (by ID) as read.
        """
        try:
            # Use get_queryset() to ensure the notification belongs to the current user
            notification = self.get_queryset().get(pk=pk)
            notification.mark_as_read()  # Calls the model method
            return Response({"message": "Notification marked as read."}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({"detail": "Notification not found or you do not have permission."}, status=status.HTTP_404_NOT_FOUND)

    # POST /api/notifications/{pk}/mark_as_unread/
    @action(detail=True, methods=["post"])
    def mark_as_unread(self, request, pk=None):
        """
        Marks a specific notification (by ID) as unread.
        """
        try:
            notification = self.get_queryset().get(pk=pk)
            notification.mark_as_unread()  # Calls the model method
            return Response({"message": "Notification marked as unread."}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({"detail": "Notification not found or you do not have permission."}, status=status.HTTP_404_NOT_FOUND)

    # DELETE /api/notifications/{pk}/ (Built-in by ModelViewSet if not ReadOnlyModelViewSet)
    # If you want to allow deletion for individual notifications:
    # You'd typically use a ModelViewSet if you want standard DELETE.
    # With ReadOnlyModelViewSet, you have to add a custom action:
    @action(detail=True, methods=["delete"], url_path="delete")
    def delete_notification(self, request, pk=None):
        """
        Deletes a specific notification (by ID).
        """
        try:
            notification = self.get_queryset().get(pk=pk)
            notification.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)  # No Content status for successful deletion
        except Notification.DoesNotExist:
            return Response({"detail": "Notification not found or you do not have permission."}, status=status.HTTP_404_NOT_FOUND)
