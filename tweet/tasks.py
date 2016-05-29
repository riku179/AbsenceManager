import logging
from celery import shared_task
from twitter import *
from allauth.socialaccount.models import SocialAccount
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from authentication.models import UserProfile
from table.models import Attendance, Subject, ATTENDANCE_STATUS

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
        source_user_profile.save()
        log.warn('User:' + user_id + ' removed')
    except ObjectDoesNotExist:
        log.warn('Unknown user removed me')

@shared_task
def update_attendance(user_id, attendances, today):
    target_user, target_user_profile = get_user_and_profile(user_id=user_id)

    subjects = Subject.objects.filter(user=target_user.user) \
        .filter(day=Subject.DAY_OF_WEEK[today][0]) \
        .order_by('period')

    if not target_user_profile.watch_tl or len(attendances) != subjects.count():
        raise AttributeError
    else:
        for (a, subject) in zip(attendances, subjects):
            if a == ATTENDANCE_STATUS[0]:  # 出席
                Attendance(subject=subject, times=subject.sum_of_classes() + 1, absence=ATTENDANCE_STATUS[0][0]).save()
            elif a == ATTENDANCE_STATUS[1]:  # 欠席
                Attendance(subject=subject, times=subject.sum_of_classes() + 1, absence=ATTENDANCE_STATUS[1][0]).save()
            elif a == ATTENDANCE_STATUS[2]:  # 遅刻
                Attendance(subject=subject, times=subject.sum_of_classes() + 1, absence=ATTENDANCE_STATUS[2][0]).save()
            elif a == ATTENDANCE_STATUS[3]:  # 不明
                Attendance(subject=subject, times=subject.sum_of_classes() + 1, absence=ATTENDANCE_STATUS[3][0]).save()
            elif a == ATTENDANCE_STATUS[4]:  # 休講
                pass


@shared_task
def reply_attendance(user_id, attendances, api_ctrl):
    api_ctrl.statuses.update(status=get_tweet_context(user_id=user_id, attendances=attendances), attendances=attendances)


def get_user_and_profile(user_id):
    """

    :param user_id: twitter ID
    :return: User object, UserProofile object
    """
    try:
        target_user = SocialAccount.objects.get(uid=user_id)
        target_user_profile = UserProfile.objects.get(user=target_user.user)
    except ObjectDoesNotExist:
        raise
    return target_user, target_user_profile


def get_tweet_context(user_id, attendances):
    target_user, target_user_profile = get_user_and_profile(user_id=user_id)
    subjects = Subject.objects.filter(user=target_user.user) \
        .filter(day=Subject.DAY_OF_WEEK[today][0]) \
        .order_by('period')

    context = ''
    for subject in subjects:
        line = "{period}限 {subject_name} : {attendance}"\
            .format(period=subject.period, subject_subject_name=subject.name, attendance=ATTENDANCE_STATUS[period][0])
        context += line
    return context
