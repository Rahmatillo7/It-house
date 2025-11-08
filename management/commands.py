from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.models import Task
from datetime import timedelta

NOTIFICATION_MINUTES = [10, 5]

class Command(BaseCommand):
    help = "Notify operators about tasks approaching deadline"

    def handle(self, *args, **options):
        now = timezone.now()
        for minutes in NOTIFICATION_MINUTES:
            notify_time = now + timedelta(minutes=minutes)
            tasks_to_notify = Task.objects.filter(
                is_completed=False,
                deadline__hour=notify_time.hour,
                deadline__minute=notify_time.minute
            )
            for task in tasks_to_notify:
                self.send_notification(task, minutes)
        self.stdout.write(self.style.SUCCESS("Notifications sent."))

    def send_notification(self, task, minutes_left):
        operator = task.operator
        if operator:
            message = f"Topshiriq '{task.title}' uchun {minutes_left} daqiqa qoldi!"
            # Bu yerda siz email, Telegram yoki SMS yuborish kodini yozasiz
            print(f"Notification to {operator.full_name}: {message}")
