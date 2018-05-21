from celery.schedules import crontab
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Observium.settings')

from django.conf import settings  # noqa

app = Celery('Observium')

app.config_from_object('django.conf:settings')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


app.conf.update(
    BROKER_URL='redis://redis:6379/0',
    CELERY_RESULT_BACKEND='redis://redis:6379/0',
    CELERY_TIMEZONE='America/Mexico_City',
    CELERY_BEAT_SCHEDULE={
        'actualizarBDRRD': {
            'task': 'Administrador.tasks.actualizarBDRRD',
            'schedule': crontab(minute=1),
        }
    },
)
# 2 diapositivas, 2 tareas
