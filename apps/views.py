from rest_framework import generics, permissions

from . import serializers
from .models import Lead
from .serializers import LeadSerializer

class LeadStatusUpdateView(generics.UpdateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Lead.objects.filter(operator=self.request.user.operator)

    def perform_update(self, serializer):
        serializer.save()


#                     task

from rest_framework import generics, permissions
from .serializers import TaskCreateSerializer


class TaskCreateView(generics.CreateAPIView):
    serializer_class = TaskCreateSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        operator = getattr(self.request.user, 'operator', None)
        if operator is None:
            raise serializers.ValidationError("Siz operator emassiz!")

        serializer.save(operator=operator)

#   lead

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Lead
from .serializers import LeadStatusUpdateSerializer

class LeadUpdateStatusView(generics.UpdateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadStatusUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Lead.objects.none()

        operator = getattr(user, 'operator', None)
        if not operator:
            return Lead.objects.none()

        return Lead.objects.filter(operator=operator)


#notification

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, pk):
    try:
        notif = Notification.objects.get(pk=pk, user=request.user)
    except Notification.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)
    notif.is_read = True
    notif.save(update_fields=['is_read'])
    return Response({"ok": True})

