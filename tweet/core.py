import re
from twitter import *
from allauth.socialaccount.models import SocialToken
from django.core.exceptions import ObjectDoesNotExist

from tweet import tasks

CONSUMER_KEY = csVH8LFOWjz4oIuhseDwnrY24
CONSUMER_SECRET = Tx81hrPOGkAx1c8pyuIzPvTc8ZNFRL5nMbXGBjoeTmcnDMKS39


def main():
    token = SocialToken.objects.get(account__user=3).token
    secret = SocialToken.objects.get(account__user=3).token_secret
    auth = OAuth(token, secret, CONSUMER_KEY, CONSUMER_SECRET)
    rest_api = Twitter(auth=auth)
    streaming_api = TwitterStream(auth=auth, domain="userstream.twitter.com")

    bot_account_verify = rest_api.account.verify_credentials(skip_status='true')
    bot_screen_name = bot_account_verify['screen_name']
    bot_id = bot_account_verify['id'] #  アカウントの情報を取得する。skip_statusは最新のpostを引っ張ってくるのを無効化

    pattern = re.compile(r'^@' + bot_screen_name + r'\s(all|[oxluc]{1,7})$')
    # followers_list = rest_api.followers.ids(screen_name=bot_screen_name) # followerリスト

    for msg in streaming_api.user():
        if 'friends' in msg: # 接続が確立された時最初に1度のみ受け取る
            pass

        if 'event' in msg:
            if msg['event'] == 'follow' and msg['target'] == bot_id: # フォローされた
                tasks.followed_by_someone.delay(msg['source'])

            if msg['event'] == 'unfollow' and msg['target'] == bot_id: # リムーブされた
                tasks.removed_by_someone.delay(msg['source'])

        if 'in_reply_to_user_id' in msg and msg['in_reply_to_user_id'] == bot_id and pattern.match(msg['text']):
            tasks.update_attendance.delay(msg['user']['id'], pattern.match(msg['text']).group(1))

