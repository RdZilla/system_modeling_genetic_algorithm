import logging
import os

from celery import Celery


common_logger = logging.getLogger("common")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modeling_system_backend.settings')

app = Celery('modeling_system_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    common_logger.debug(f"Request: {self.request!r}")
