from twitter import *
from allauth.socialaccount.models import SocialToken
from django.core.exceptions import ObjectDoesNotExist

from tweet.tasks import *

CONSUMER_KEY = csVH8LFOWjz4oIuhseDwnrY24
CONSUMER_SECRET = Tx81hrPOGkAx1c8pyuIzPvTc8ZNFRL5nMbXGBjoeTmcnDMKS39

def main():
    token = SocialToken.objects.get(account__user=3).token
    secret = SocialToken.objects.get(account__user=3).token_secret
    auth = OAuth(token, secret, CONSUMER_KEY, CONSUMER_SECRET)
    rest_api = Twitter(auth=auth)
    streaming_api = TwitterStream(auth=auth, domain="userstream.twitter.com")

    account_verify = rest_api.account.verify_credentials(skip_status='true')
    screen_name = account_verify['screen_name']
    user_id = account_verify['id'] #  アカウントの情報を取得する。skip_statusは最新のpostを引っ張ってくるのを無効化

    followers_list = rest_api.followers.ids(screen_name=screen_name) # followerリスト

    for msg in streaming_api.user():
        if 'friends' in msg: # 接続が確立された時最初に1度のみ受け取る
            pass

        if 'event' in msg:
            if msg['event'] == 'follow' and msg['target'] == user_id: # フォローされた
                followed_by_someone.delay(msg['source'])

            if msg['event'] == 'unfollow' and msg['target'] == user_id: # リムーブされた
                removed_by_someone.delay(msg['source'])

        if 'user' in msg:
            pass
