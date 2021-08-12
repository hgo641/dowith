import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dowith.settings')

app = Celery('dowith')

# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

app.conf.beat_schedule = {
    'distribute-charge-every-midnight':{
        'task':'tasks.distribute_charge',
        'schedule' : crontab(minute=0, hour=0),
    },
}
