import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "drfsite.settings")

app = Celery("drfsite")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
