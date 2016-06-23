import sys, os, re, django, argparse
from logging import getLogger
sys.path.append(os.path.abspath('../../AbsenceManagement'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'AbsenseManagement.settings'
django.setup()
from datetime import date
from twitter import *
from allauth.socialaccount.models import SocialToken
from django.core.exceptions import ObjectDoesNotExist
from tweet.tasks import update_attendance, reply_attendance, followed_by_someone, removed_by_someone
from table.models import ATTENDANCE_STATUS

################ Keys ################
CONSUMER_KEY = 'csVH8LFOWjz4oIuhseDwnrY24'
CONSUMER_SECRET = 'Tx81hrPOGkAx1c8pyuIzPvTc8ZNFRL5nMbXGBjoeTmcnDMKS39'
######################################


def main(debug_day):
    log = getLogger('django')
    bot = SocialToken.objects.get(account__user=6)
    log.info('{}:{}'.format(bot.token, bot.token_secret))
    auth = OAuth(token=bot.token, token_secret=bot.token_secret, consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET)

    rest_api = Twitter(auth=auth)
    streaming_api = TwitterStream(auth=auth, domain="userstream.twitter.com")

    bot_account_verify = rest_api.account.verify_credentials(skip_status='true')
    bot_screen_name = bot_account_verify['screen_name']
    bot_id = bot_account_verify['id']  #  アカウントの情報を取得する。skip_statusは最新のpostを引っ張ってくるのを無効化
    today = date.today().weekday() if not debug_day is None else debug_day

    pattern = re.compile(r'^@' + bot_screen_name + r'\s(all|[oxluc]{1,7})$')

    for msg in streaming_api.user():
        log.info(msg)
        if 'friends' in msg:  # 接続が確立された時最初に1度のみ受け取る
            log.info('Connection established! user: ' + bot_screen_name)

        if 'event' in msg:
            if msg['event'] == 'follow' and msg['target']['id'] == bot_id:  # フォローされた
                log.info('{} followed bot!'.format(msg['source']['id']))
                try:
                    followed_by_someone.delay(user_id=msg['source']['id'])
                except Exception as err:
                    log.error('[Error]', err)

            if msg['event'] == 'unfollow' and msg['target']['id'] == bot_id:  # リムーブされた
                log.info('{} removed bot!'.format(msg['source']['id']))
                try:
                    removed_by_someone.delay(user_id=msg['source'])
                except Exception as err:
                    log.error("Unknown error occurred: {e}".format(e=err))

        if 'in_reply_to_user_id' in msg and msg['in_reply_to_user_id'] == bot_id and pattern.match(msg['text']).group(1):
            log.info('{} send attendance stats to bot!'.format(msg['user']['id']))
            attendances = pattern_translate(pattern.match(msg['text']).group(1))
            try:
                update_attendance.delay(
                    user_id=msg['user']['id'],
                    attendances=attendances,
                    today=today
                    )
            except AttributeError:
                log.error('user:{user_id} failed update attendance. Option is disabled or pattern is too long.'
                      .format(user_id=msg['user']['id']))
            except ObjectDoesNotExist:
                log.error('user:{user_id} does not exist in DB.')
            except Exception as err:
                log.error("Unknown error occurred: {e}".format(e=err))
            else:
                reply_attendance.delay(user_id=msg['user']['id'], attendances=attendances, keys=(CONSUMER_KEY, CONSUMER_SECRET), day=today)

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
    parser = argparse.ArgumentParser(description='Tweet handler for AbsenceManagement')
    parser.add_argument('--day', '-d', type=int, choices=[x for x in range(6)])
    args = parser.parse_args()

    if args.day is not None:
        main(debug_day=args.day)
else:
    pass
