import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('it-house')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'notify-upcoming-task-every-5-minutes': {
        'task': 'apps.tasks.notify_upcoming_task',
        'schedule': crontab(minute='*/5'),
    },
    'daily-report-task': {
        'task': 'apps.tasks.daily_report_task',
        'schedule': crontab(hour=9, minute=0),
    },
}

app.conf.timezone = 'Asia/Tashkent'
