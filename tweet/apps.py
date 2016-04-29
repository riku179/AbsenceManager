from django.apps import AppConfig
from tweet.core import *

class TweetConfig(AppConfig):
    name = 'tweet'

    def ready(self):
        pass
