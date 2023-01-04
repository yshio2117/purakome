

CONSUMER_KEY = "Hbq1vcy7Sreoq56CZfij0mFsI"
CONSUMER_SECRET = "2HjVuk14J2RsCcKTSXCF1PjLG7xdLJVMbn81ufRSdSzjq70VfD"

import webbrowser
from twython import Twython

temp_client = Twython(CONSUMER_KEY, CONSUMER_SECRET)
temp_creds = temp_client.get_authentication_tokens()
url = temp_creds['auth_url']

#一時クライアントを作成し認証URLを取得

print(f"go visit {url} and get the PIN code and paste it below")
webbrowser.open(url)

PIN_CODE = input("please enter the PIN code")

#次にそのURLにアクセスしてアプリケーションを認証し、PINを読み込む

auth_client = Twython(CONSUMER_KEY,
                      CONSUMER_SECRET,
                      temp_creds['oauth_token'],
                      temp_creds['oauth_token_secret'])
final_step = auth_client.get_authorized_tokens(PIN_CODE)
ACCESS_TOKEN = final_step['oauth_token']
ACCESS_TOKEN_SECRET = final_step['oauth_token_secret']

print('ACCESS_TOKEN=',ACCESS_TOKEN)
print('ACCESS_TOKEN_SECRET=',ACCESS_TOKEN_SECRET)

#そのPIN_CODEを使用して実際のトークン取得

twitter = Twython(CONSUMER_KEY,
                  CONSUMER_SECRET,
                  ACCESS_TOKEN,
                  ACCESS_TOKEN_SECRET)

#[data scienceというフレーズを含むツイート検索]
for status in twitter.search(q='"ももクロ"')["statuses"]:
    user = status["user"]["screen_name"]
    text = status["text"]
    print(f"{user}: {text}\n")
