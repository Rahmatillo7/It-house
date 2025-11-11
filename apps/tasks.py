from django.utils import timezone
from apps.models import Task
from datetime import timedelta
import requests
import logging
#
# logger = logging.getLogger(__name__)
#
# TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
#
# def send_telegram_message(chat_id: str, text: str):
#     """
#     Telegram bot orqali xabar yuboradi.
#     """
#     url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
#     try:
#         response = requests.post(url, data={"chat_id": chat_id, "text": text})
#         response.raise_for_status()
#         logger.info(f"Telegram message sent to {chat_id}")
#     except requests.RequestException as e:
#         logger.error(f"Failed to send Telegram message to {chat_id}: {e}")

# @shared_task(bind=True, max_retries=3, default_retry_delay=60)
# def notify_upcoming_task(self):
#     """
#     Har daqiqada ishga tushadigan task.
#     Operatorlarga topshiriq boshlanishiga 10 va 5 daqiqa qolganda notification yuboradi.
#     """
#     now = timezone.now()
#     timeframes = [10, 5]
#
#     for minutes in timeframes:
#         target_start = now + timedelta(minutes=minutes)
#         interval_start = target_start
#         interval_end = target_start + timedelta(seconds=59)
#
#         tasks = Task.objects.filter(
#             is_completed=False,
#             deadline__range=(interval_start, interval_end)
#         ).select_related('operator')
#
#         for task in tasks:
#             operator = task.operator
#             if operator and operator.telegram_chat_id:
#                 msg = (
#                     f"Salom {operator.full_name},\n"
#                     f"Topshiriq '{task.title}' boshlanishiga {minutes} daqiqa qoldi!"
#                 )
#                 try:
#                     send_telegram_message(operator.telegram_chat_id, msg)
#                 except Exception as exc:
#                     logger.exception(f"Error sending Telegram message for task {task.id}")
#                     self.retry(exc=exc)


from celery import shared_task


from .utils import create_and_send_notification

@shared_task
def check_task_deadlines():
    now = timezone.now()
    tasks = Task.objects.filter(is_completed=False)

    for task in tasks:
        time_left = task.deadline - now

        # 10 daqiqa qolganda
        if timedelta(minutes=9) < time_left <= timedelta(minutes=10) and not task.is_notified_10min:
            message = f"'{task.title}' topshirig'ingizga 10 daqiqa qoldi!"
            create_and_send_notification(task.operator, message, data={"task_id": task.id, "rem": 10})
            task.is_notified_10min = True
            task.save(update_fields=['is_notified_10min'])

        # 5 daqiqa qolganda
        elif timedelta(minutes=4) < time_left <= timedelta(minutes=5) and not task.is_notified_5min:
            message = f"'{task.title}' topshirig'ingizga 5 daqiqa qoldi!"
            create_and_send_notification(task.operator, message, data={"task_id": task.id, "rem": 5})
            task.is_notified_5min = True
            task.save(update_fields=['is_notified_5min'])
