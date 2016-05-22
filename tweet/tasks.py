import logging
from celery import shared_task
from twitter import *
from allauth.socialaccount.models import SocialAccount
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from authentication.models import UserProfile
from table.models import Attendance, Subject

log = logging.getLogger(__name__)


@shared_task
def followed_by_someone(user_id):
    try:
        source_user = SocialAccount.objects.get(uid=user_id)
        source_user_profile = UserProfile.objects.get(user=source_user)
        source_user_profile.watch_tl = True
        source_user_profile.save()
        log.warn('User: ' + user_id + ' followd')
    except ObjectDoesNotExist:
        log.warn('Unknown user followed me')


@shared_task
def removed_by_someone(user_id):
    try:
        source_user = SocialAccount.objects.get(uid=user_id)
        source_user_profile = UserProfile.objects.get(user=source_user)
        source_user_profile.watch_tl = False
        source_user_profile.save
        log.warn('User:' + user_id + ' removed')
    except ObjectDoesNotExist:
        log.warn('Unknown user removed me')

@shared_task
def update_attendance(user_id, attendance_pattern, today):
    target_user, target_user_profile = _get_user_and_profile(user_id=user_id)

    subjects = Subject.objects.filter(user=target_user.user) \
        .filter(day=Subject.DAY_OF_WEEK[today][0]) \
        .order_by('period')

    if target_user_profile.watch_tl == False or len(attendance_pattern) != subjects.count():
        log.error('"watch_tl" is False or length of pattern is incorrect.')
        raise UnexpectedRequestError
    else:
        for (a, subject) in zip(attendance_pattern, subjects):
            if a == 'o': # 出席
                Attendance(subject=subject, times=subject.sum_of_classes() + 1, absence=Attendance.ATTENDANCE_STATUS[0][0]).save()
            elif a == 'x': # 欠席
                Attendance(subject=subject, times=subject.sum_of_classes() + 1, absence=Attendance.ATTENDANCE_STATUS[1][0]).save()
            elif a == 'l': # 遅刻
                Attendance(subject=subject, times=subject.sum_of_classes() + 1, absence=Attendance.ATTENDANCE_STATUS[2][0]).save()
            elif a == 'u': # 不明
                Attendance(subject=subject, times=subject.sum_of_classes() + 1, absence=Attendance.ATTENDANCE_STATUS[3][0]).save()
            elif a == 'c': # 休講
                pass


def _get_user_and_profile(user_id):
    try:
        target_user = SocialAccount.objects.get(uid=user_id)
        target_user_profile = UserProfile.objects.get(user=target_user.user)
    except ObjectDoesNotExist:
        raise
    return target_user, target_user_profile


def get_attendance_text(user_id):
    target_user, target_user_profile = _get_user_and_profile(user_id=user_id)
    subjects = Subject.objects.filter(user=target_user.user) \
        .filter(day=Subject.DAY_OF_WEEK[today][0]) \
        .order_by('period')

    for subject in subjects:


class UnexpectedRequestError(Exception):
    pass
