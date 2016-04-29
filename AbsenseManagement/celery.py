import os
import django
from django.conf import settings

from .celery_app import get_celery_app

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AbsenseManagement.settings')
django.setup()

app = get_celery_app()
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)