import sys, os, re, django, logging
sys.path.append('/home/user/PycharmProjects/AbsenceManagement')
os.environ['DJANGO_SETTINGS_MODULE'] = 'AbsenseManagement.settings'
django.setup()
from datetime import date
from twitter import *
from allauth.socialaccount.models import SocialToken
from django.core.exceptions import ObjectDoesNotExist
from tweet import tasks

log = logging.getLogger(__name__)

CONSUMER_KEY = 'csVH8LFOWjz4oIuhseDwnrY24'
CONSUMER_SECRET = 'Tx81hrPOGkAx1c8pyuIzPvTc8ZNFRL5nMbXGBjoeTmcnDMKS39'


def main():
    bot = SocialToken.objects.get(account__user=6)
    token, secret = bot.token, bot.token_secret
    auth = OAuth(token, secret, CONSUMER_KEY, CONSUMER_SECRET)
    rest_api = Twitter(auth=auth)
    streaming_api = TwitterStream(auth=auth, domain="userstream.twitter.com")

    bot_account_verify = rest_api.account.verify_credentials(skip_status='true')
    bot_screen_name = bot_account_verify['screen_name']
    bot_id = bot_account_verify['id'] #  アカウントの情報を取得する。skip_statusは最新のpostを引っ張ってくるのを無効化

    pattern = re.compile(r'^@' + bot_screen_name + r'\s(all|[oxluc]{1,7})$')

    for msg in streaming_api.user():
        print(msg)
        if 'friends' in msg: # 接続が確立された時最初に1度のみ受け取る
            log.warn('Connection established! user: ' + bot_screen_name)

        if 'event' in msg:
            if msg['event'] == 'follow' and msg['target'] == bot_id: # フォローされた
                try:
                    tasks.followed_by_someone.delay(user_id=msg['source'])
                except Exception as err:
                    log.error('[Error]', err)

            if msg['event'] == 'unfollow' and msg['target'] == bot_id: # リムーブされた
                try:
                    tasks.removed_by_someone.delay(user_id=msg['source'])
                except Exception as err:
                    log.error('[Error]', err)

        if 'in_reply_to_user_id' in msg and msg['in_reply_to_user_id'] == bot_id and pattern.match(msg['text']):
            try:
                tasks.update_attendance.delay(user_id=msg['user']['id'], attendance_pattern=pattern.match(msg['text']).group(1), today=date.today().weekday())
            except tasks.UnexpectedRequestError:
                pass
            except Exception as err:
                log.error('[Error]', err)
            else:
                rest_api.statuses.update(status=tasks.create_reply_text(user_id=msg['user']['id']))

if __name__ == '__main__':
    main()
