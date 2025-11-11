from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

def create_and_send_notification(user, message, data=None):
    notif = Notification.objects.create(user=user, message=message, data=data or {})
    channel_layer = get_channel_layer()
    payload = {
        "type": "send_notification",
        "message": message,
        "data": data or {},
        "created_at": timezone.localtime(notif.created_at).isoformat(),
    }
    async_to_sync(channel_layer.group_send)(f"user_{user.id}", payload)
    return notif
