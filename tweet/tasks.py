import threading
from logging import getLogger
from twitter import *
import datetime as dt
from allauth.socialaccount.models import SocialAccount, SocialToken
from django.utils.timezone import utc
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.db.utils import OperationalError
from django.db import connection

from authentication.models import UserProfile
from table.models import Attendance, Subject, ATTENDANCE_STATUS

log = getLogger('django')


#@shared_task
#def followed_by_someone(user_id):
#    try:
#        source_user, source_user_profile = get_user_and_profile(user_id=user_id)
#        source_user_profile.watch_tl = True
#        source_user_profile.save()
#        log.info('User:{} followed'.format(user_id))
#    except ObjectDoesNotExist:
#        log.info('Unknown user followed me')
#
#
#@shared_task
#def removed_by_someone(user_id):
#    try:
#        source_user, source_user_profile = get_user_and_profile(user_id=user_id)
#        source_user_profile.watch_tl = False
#        source_user_profile.save()
#        log.info('User:{} removed'.format(user_id))
#    except ObjectDoesNotExist:
#        log.info('Unknown user removed me')


def update_attendance(user_id, attendances, today):

    log.info('started update attendance task')

    try:
        target_user = get_user(user_id=user_id)
    except OperationalError:
        log.warn('OperationalError catched. Reset DB connection and retry it.')
        connection.close()
        target_user = get_user(user_id=user_id)

    # その日の
    try:
        subjects = Subject.objects.filter(user=target_user) \
            .filter(day=Subject.DAY_OF_WEEK[today][0]) \
            .order_by('period')
    except IndexError:
        log.info("Have a nice Sunday!")

    if len(attendances) != subjects.count():
        raise InvalidPatternError
    elif is_already_updated(user_id, subjects):
        log.info('Today\'s Attendance is already exits. It\'s Overrided.')
        th_update_db_attendance_no_OR = threading.Thread(target=update_db_attendance, args=(user_id, attendances, subjects, True))
        th_update_db_attendance_no_OR.start()
    else:
        th_update_db_attendance = threading.Thread(target=update_db_attendance, args=(user_id, attendances, subjects))
        th_update_db_attendance.start()


def update_db_attendance(user_id, attendances, subjects, override=False):
    """
    出席情報を上書き
    :param override: Trueが来たら最新を上書き
    :return:
    """

    if override:
        # 上書き
        for (a, subject) in zip(attendances, subjects):
            if a == ATTENDANCE_STATUS[0]:  # 出席
                attend = Attendance.objects.get(subject=subject, times=subject.sum_of_classes())
                attend.absence = ATTENDANCE_STATUS[0][0]
                attend.save()
            elif a == ATTENDANCE_STATUS[1]:  # 欠席
                attend = Attendance.objects.get(subject=subject, times=subject.sum_of_classes())
                attend.absence = ATTENDANCE_STATUS[1][0]
            elif a == ATTENDANCE_STATUS[2]:  # 遅刻
                attend = Attendance.objects.get(subject=subject, times=subject.sum_of_classes())
                attend.absence = ATTENDANCE_STATUS[2][0]
                attend.save()
            elif a == ATTENDANCE_STATUS[3]:  # 不明
                attend = Attendance.objects.get(subject=subject, times=subject.sum_of_classes())
                attend.absence = ATTENDANCE_STATUS[3][0]
                attend.save()
            elif a == ATTENDANCE_STATUS[4]:  # 休講
                attend = Attendance.objects.get(subject=subject, times=subject.sum_of_classes())
                attend.absence = ATTENDANCE_STATUS[4][0]
                attend.save()
    else:
        # 新規作成
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
                Attendance(subject=subject, times=subject.sum_of_classes() + 1, absence=ATTENDANCE_STATUS[4][0]).save()



def is_already_updated(user_id, subjects):
    # その日の最初の出席情報を取得。初回は出席情報が無いのでそのままFalseを返す
    try:
        last_attendance = Attendance.objects.get(subject=subjects[0], times=subjects[0].sum_of_classes())
    except ObjectDoesNotExist:
        log.info('This is first Attendance')
        return False

    # 最新のAttendanceのタイムスタンプは前日AM9:00よりあとのもの(今日の出席情報というあつかい)か。その場合は上書き
    if last_attendance.date > dt.datetime.combine(dt.date.today() - dt.timedelta(days=1) ,dt.time(9, 0)).replace(tzinfo=utc):
        return True
    else:
        return False


def reply_attendance(user_id, attendances, keys, day):
    target_user = SocialToken.objects.get(account__uid=user_id)
    auth = OAuth(token=target_user.token,
                 token_secret=target_user.token_secret,
                 consumer_key=keys[0],
                 consumer_secret=keys[1])
    rest_api = Twitter(auth=auth)
    rest_api.statuses.update(status=get_tweet_context(user_id=user_id, attendances=attendances, day=day))


def get_user(user_id):
    """

    :param user_id: Twitter User ID
    :param getprofile: then False, NOT return UserProfile Object
    :return:
    """
    try:
        return SocialAccount.objects.get(uid=user_id).user
    except ObjectDoesNotExist:
        log.error('User does not exist')
        raise


def get_tweet_context(user_id, attendances, day):
    target_user = get_user(user_id=user_id)
    subjects = Subject.objects.filter(user=target_user) \
        .filter(day=Subject.DAY_OF_WEEK[day][0]) \
        .order_by('period')

    context = ''
    for subject, attendance in zip(subjects, attendances):
        line = "{period+1}限 {subject_name} : {attendance}\n"\
            .format(period=subject.period+1, subject_name=subject.name, attendance=attendance[1])
        context += line
    return context

class InvalidPatternError(Exception):
    pass
