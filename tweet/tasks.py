from logging import getLogger
from celery import shared_task
from twitter import *
from allauth.socialaccount.models import SocialAccount, SocialToken
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from authentication.models import UserProfile
from table.models import Attendance, Subject, ATTENDANCE_STATUS

log = getLogger('django')


@shared_task
def followed_by_someone(user_id):
    try:
        source_user, source_user_profile = get_user_and_profile(user_id=user_id)
        source_user_profile.watch_tl = True
        source_user_profile.save()
        log.info('User:{} followed'.format(user_id))
    except ObjectDoesNotExist:
        log.info('Unknown user followed me')


@shared_task
def removed_by_someone(user_id):
    try:
        source_user, source_user_profile = get_user_and_profile(user_id=user_id)
        source_user_profile.watch_tl = False
        source_user_profile.save()
        log.info('User:{} removed'.format(user_id))
    except ObjectDoesNotExist:
        log.info('Unknown user removed me')


@shared_task
def update_attendance(user_id, attendances, today):
    log.info('started update attendance task')
    target_user, target_user_profile = get_user_and_profile(user_id=user_id)

    subjects = Subject.objects.filter(user=target_user) \
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
def reply_attendance(user_id, attendances, keys, day):
    target_user = SocialToken.objects.get(account__uid=user_id)
    auth = OAuth(token=target_user.token,
                 token_secret=target_user.token_secret,
                 consumer_key=keys[0],
                 consumer_secret=keys[1])
    rest_api = Twitter(auth=auth)
    rest_api.statuses.update(status=get_tweet_context(user_id=user_id, attendances=attendances, day=day))


def get_user_and_profile(user_id, getprofile=True):
    """

    :param user_id: Twitter User ID
    :param getprofile: then False, NOT return UserProfile Object
    :return:
    """
    try:
        user = SocialAccount.objects.get(uid=user_id).user
        if getprofile:
            user_profile = UserProfile.objects.get(user=user)
            return user, user_profile
        else:
            return user
    except ObjectDoesNotExist:
        raise


def get_tweet_context(user_id, attendances, day):
    target_user, target_user_profile = get_user_and_profile(user_id=user_id)
    subjects = Subject.objects.filter(user=target_user) \
        .filter(day=Subject.DAY_OF_WEEK[day][0]) \
        .order_by('period')

    context = ''
    for subject, attendance in zip(subjects, attendances):
        line = "{period}限 {subject_name} : {attendance}"\
            .format(period=subject.period, subject_subject_name=subject.name, attendance=attendance[1])
        context += line
    return context

