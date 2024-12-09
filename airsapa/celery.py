from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airsapa.settings')

app = Celery('airsapa')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-weather-alerts': {
        'task': 'base.tasks.send_weather_alert',
        'schedule': crontab(minute=0, hour=8),  # Daily at 8:00 AM
    },
    'send-aqi-alerts': {
        'task': 'base.tasks.send_aqi_alert',
        'schedule': crontab(minute=0, hour=9),  # Daily at 9:00 AM
    },
    'send-health-advice': {
        'task': 'base.tasks.health_advice_mail',
        'schedule': crontab(day_of_month=1, minute=0, hour=10),  # Monthly on the 1st at 10:00 AM
    },
}