import sys, os, re, django, logging
sys.path.append('/home/user/PycharmProjects/AbsenceManagement')
os.environ['DJANGO_SETTINGS_MODULE'] = 'AbsenseManagement.settings'
django.setup()
from datetime import date
from twitter import *
from allauth.socialaccount.models import SocialToken
from django.core.exceptions import ObjectDoesNotExist
from tweet.tasks import update_attendance, reply_attendance
from table.models import ATTENDANCE_STATUS

log = logging.getLogger(__name__)

CONSUMER_KEY = 'csVH8LFOWjz4oIuhseDwnrY24'
CONSUMER_SECRET = 'Tx81hrPOGkAx1c8pyuIzPvTc8ZNFRL5nMbXGBjoeTmcnDMKS39'


def main():
    bot = SocialToken.objects.get(account__user=6)
    auth = OAuth(token=bot.token, token_secret=bot.token_secret, consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET)
    rest_api = Twitter(auth=auth)
    streaming_api = TwitterStream(auth=auth, domain="userstream.twitter.com")

    bot_account_verify = rest_api.account.verify_credentials(skip_status='true')
    bot_screen_name = bot_account_verify['screen_name']
    bot_id = bot_account_verify['id']  #  アカウントの情報を取得する。skip_statusは最新のpostを引っ張ってくるのを無効化

    pattern = re.compile(r'^@' + bot_screen_name + r'\s(all|[oxluc]{1,7})$')

    for msg in streaming_api.user():
        print(msg)
        if 'friends' in msg:  # 接続が確立された時最初に1度のみ受け取る
            log.warn('Connection established! user: ' + bot_screen_name)

        if 'event' in msg:
            if msg['event'] == 'follow' and msg['target'] == bot_id:  # フォローされた
                try:
                    tasks.followed_by_someone.delay(user_id=msg['source'])
                except Exception as err:
                    log.error('[Error]', err)

            if msg['event'] == 'unfollow' and msg['target'] == bot_id:  # リムーブされた
                try:
                    tasks.removed_by_someone.delay(user_id=msg['source'])
                except Exception as err:
                    log.error("Unknown error occurred: {e}".format(e=err))

        matched_pattern = pattern.match(msg['text']).group(1)
        if 'in_reply_to_user_id' in msg and msg['in_reply_to_user_id'] == bot_id and matched_pattern:
            attendances = pattern_translate(matched_pattern)
            try:
                update_attendance.delay(
                    user_id=msg['user']['id'],
                    attendances=attendances,
                    today=date.today().weekday(),
                    )
            except AttributeError:
                log.error('user:{user_id} failed update attendance. Option is disabled or pattern is too long.'
                      .format(user_id=msg['user']['id']))
            except ObjectDoesNotExist:
                log.error('user:{user_id} does not exist in DB.')
            except Exception as err:
                log.error("Unknown error occurred: {e}".format(e=err))
            else:
                reply_attendance.delay(user_id=msg['user']['id'], attendances=attendances, keys=(CONSUMER_KEY, CONSUMER_SECRET))

def pattern_translate(pattern):
    """

    :param pattern: pattern strings ex) loxoou
    :return: list of attendances
    """
    attendances = []
    for c in pattern:
        if c == 'o':
            attendances.append(ATTENDANCE_STATUS[0])
        elif c == 'x':
            attendances.append(ATTENDANCE_STATUS[1])
        elif c == 'l':
            attendances.append(ATTENDANCE_STATUS[2])
        elif c == 'u':
            attendances.append(ATTENDANCE_STATUS[3])
        elif c == 'c':
            attendances.append(ATTENDANCE_STATUS[4])

    return attendances


if __name__ == '__main__':
    main()
