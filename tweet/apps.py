import logging
from django.apps import AppConfig
from tweet.core import *
from .core import main

log = logging.getLogger(__name__)

class TweetConfig(AppConfig):
    name = 'tweet'

