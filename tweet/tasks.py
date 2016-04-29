from celery import shared_task
from twitter import *


@shared_task
def ready_get_messages():
    pass

@shared_task
def watch_tl():
    pass
