from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auth_service.settings")
app = Celery("auth_service", include=["authentication.tasks"])
app.conf.task_default_queue = "auth_service_queue"
app.config_from_object("django.conf.settings", namespace="CELERY")
app.autodiscover_tasks()
