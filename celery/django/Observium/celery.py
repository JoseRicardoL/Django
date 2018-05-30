from __future__ import absolute_import, unicode_literals
from celery.schedules import crontab
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Observium.settings')

from django.conf import settings  # noqa

app = Celery('Observium')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


app.conf.beat_schedule = {
    'actualizarBDRRD': {
        'task': 'actualizarBDRRD',
        'schedule': crontab(),
    },
}
