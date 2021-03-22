import os
from celery import Celery, platforms
from asyntasks import config

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MrRight.settings")

# create and initialize celery object
celery_app = Celery('task')
platforms.C_FORCE_ROOT = True
celery_app.config_from_object(config)
celery_app.autodiscover_tasks()
