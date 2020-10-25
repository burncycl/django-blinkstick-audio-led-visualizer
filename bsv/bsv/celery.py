from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
from celery.bin.purge import purge as celery_purge

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bsv.settings')
app = Celery('bsv')
#celery_purge(app).run(force=True)

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
