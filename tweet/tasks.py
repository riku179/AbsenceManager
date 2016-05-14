import logging
from celery import shared_task
from twitter import *
from allauth.socialaccount.models import SocialAccount
from django.core.exceptions import ObjectDoesNotExist
from authentication.models import UserProfile

log = logging.getLogger(__name__)


@shared_task
def followed_by_someone(id):
    try:
        source_user = SocialAccount.objects.get(uid=id)
        source_user_profile = UserProfile.objects.get(user=source_user)
        source_user_profile.watch_tl = True
        source_user_profile.save()
    except ObjectDoesNotExist:
        log.info('unknown user followed me')


@shared_task
def removed_by_someone(id):
    try:
        source_user = SocialAccount.objects.get(uid=id)
        source_user_profile = UserProfile.objects.get(user=source_user)
        source_user_profile.watch_tl = False
        source_user_profile.save
    except ObjectDoesNotExist:
        log.info('unknown user removed me')

