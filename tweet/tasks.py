from celery import shared_task
from twitter import *
from allauth.socialaccount.models import SocialAccount
from django.core.exceptions import ObjectDoesNotExist
from authentication.models import UserProfile


@shared_task
def followed_by_someone(id):
    try:
        source_user = SocialAccount.objects.get(uid=id)
    except ObjectDoesNotExist:
        pass
    source_user_profile = UserProfile.objects.get(user=source_user)
    source_user_profile.watch_tl = True
    source_user_profile.save()


@shared_task
def removed_by_someone(id):
    try:
        source_user = SocialAccount.objects.get(uid=id)
    except ObjectDoesNotExist:
        pass
    source_user_profile = UserProfile.objects.get(user=source_user)
    source_user_profile.watch_tl = False
    source_user_profile.save
