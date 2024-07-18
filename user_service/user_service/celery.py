import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_service.settings')
app = Celery('user_service')
app.conf.task_default_queue = 'user_service_queue'
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()