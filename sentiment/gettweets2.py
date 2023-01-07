# coding: UTF-8

from twython import Twython
import calendar,time,datetime
import unicodedata

import os, sys, django

CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET =os.environ.get('CONSUMER_SECRET')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')

sys.path.append('/home/yusuke/pydir/.myvenv/django_app')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')  # DJANGO_SETTINGS_MODULEにプロジェクトのsettings.pyのを指定します。
django.setup()

from sentiment.models import Tweetdata3# 利用したいモデルをインポートします。

# 日付の警告を無視
import warnings
warnings.filterwarnings('ignore')

# id重複取得エラー
from django.db.utils import IntegrityError,DataError
import re
# bert
from transformers import pipeline, AutoTokenizer,AutoModelForSequenceClassification

TEXT_SEP=[
    r'\s+', #0
    r'@[^\s]+', #1
    r'\d+', #2
    r'[!…(\.\.)(・・)]+', #3
    r'\?+', #4
    r'、、+', #5
    r'。。+', #6
]
PTN=[re.compile(d) for d in TEXT_SEP]


def cleansing_text(text):
    
    """ 
    リアルタイム用（アニメに限らず）

    """
    # http削除
    text = re.sub("https?://[^\s]+","",text)
    text = text.lower()# 小文字化   
    # reply先に実施(reply内にsao等のキャラ名やタイトルが入る可能性があるため
    text = PTN[1].sub('',text)# neologdn 英字+スペース+日本語 でスペースが無くなるためREPLYではなく@を使用
    # テキスト正規化
    text = unicodedata.normalize('NFKC',text)#表記ゆれの統一
    #text = neologdn.normalize(text)# アルファベット、数字の半角全角,'（'等の記号の全角半角統一(MeCabを通すと絵文字も統一されてしまうので注意→bert含めpredict前には使用しない)
 

    text = PTN[0].sub(' ',text)
    text = PTN[2].sub("SOMENUMBER",text)
    text = PTN[3].sub("。",text)
    text = PTN[4].sub("?",text)
    text = PTN[5].sub("、、",text)    
    text = PTN[6].sub("。。",text)
    

    text = text.strip()
        

    
    return text


class Bunrui:

    # bertで分類
    save_directory = os.environ.get('BERT_MODELS')
    #save_directory = r'static/models/hugface/bert_models/'

    BT_tokenizer = AutoTokenizer.from_pretrained(save_directory)
    BT_model = AutoModelForSequenceClassification.from_pretrained(save_directory)
    BT_classifier = pipeline(task="sentiment-analysis",model=BT_model,tokenizer=BT_tokenizer)


    def label_predict(self,contents,bert=False,lang=0):
        """
        ・contenst = 文章list
        ・事前の前処理はbert=False,True両方とも内部で行われるので不要
        ・0,1,2,3,4のリストが返る
        """

        if len(contents) == 0:
            return []

        start = 0
        l_size = len(contents)
        predictions = []

        if bert == False:
            return 'Error : ONLY BERT'

        else:
            if lang == 0: #ja
                while True:
                    end = start + 100000
                    #bert
                    ## ja,eng一旦共通(engは大小文字区別したほうがよいかも)
                    contents = [cleansing_text(content) for content in contents[start:end]]

                    for c in self.BT_classifier(contents):# 辞書のリストで返るのでlabelのみ抽出
                        if c['label'] == 'LABEL_0':
                            predictions.append(0)
                        elif c['label'] == 'LABEL_1':
                            predictions.append(1)
                        elif c['label'] == 'LABEL_2':
                            predictions.append(2)
                        elif c['label'] == 'LABEL_3':
                            predictions.append(3)
                        elif c['label'] == 'LABEL_4':
                            predictions.append(4)

                    start = end

                    if start > l_size:
                        #print("100% done.")
                        break
                    #print("{0}% done.".format(round(100*end/l_size)))

            elif lang == 1: #en
                return 'ONLY JA'

        #print(len(predictions))
        #print("done.")
        return predictions


def utc_to_jtime(utcstr):
    time_utc = time.strptime(utcstr,'%a %b %d %H:%M:%S +0000 %Y')
    unix_time = calendar.timegm(time_utc)
    time_local = time.localtime(unix_time)
    return time.strftime("%Y-%m-%d %H:%M:%S",time_local)



def collect_tweet_realtime(query,lang):
    '''
    ツイートをリアルタイムで検索。同一ユーザーの投稿は一つのみ。スパムはdb保存しない。

    query: スペース区切り文字列。ツイッター公式クエリにできるだけ準拠。
    lang: 0:ja or 1:en

    Returns
    -------
    char:成功・失敗メッセージ

    '''


# tweet取得
    twitter = Twython(CONSUMER_KEY,
                CONSUMER_SECRET,
                ACCESS_TOKEN,
                ACCESS_TOKEN_SECRET)

    t_ids=[]
    s_names=[]
    u_ids=[]
    texts=[]
    t_dates=[]
    r_counts=[]
    f_counts=[]
    media_urls=[]
    media_urls_truncated=[]
    s_classes = []
    locations=[]
    hashtags=[]
    retweeted=[]
    u_names=[]
    p_images=[]
    verifieds=[]
    t_id_chars=[]
    entities_urls=[]
    entities_display_urls=[]

    http_mention_r=re.compile(r'https?://[^\s]+|(@[a-zA-Z_0-9]+)')

    bot_r = re.compile(r'(bot)|(BOT)')
    
    spam_r = ['質問箱','交換','譲渡','買取','在庫','完売','価格','割引','お得']
    spam_r = re.compile('|'.join(spam_r))
        
    bunruiki = Bunrui()

    #print("query:",query)
    cnt = 0 # 成功数
    next_id=''
    # text重複チェック用
    texts_record=[]
# tweet取得(max 200twt)
    for i in range(2):
        try:
            if i == 0:
                statuses = twitter.search(q=query,tweet_mode="extended",count=100)["statuses"]
            else:
                statuses = twitter.search(q=query,tweet_mode="extended",max_id=next_id-1,count=100)["statuses"]

        except twython.exceptions.TwythonError as e:
            print(e)
            return '{0}'.format(e)

        if len(statuses)==0:
            #print("No tweets found.")
            return 'No tweets found.'


        #print("\nTweets(API):",len(statuses))

        for status in statuses:
            # 感情分析に関係しないmentionとhttp除いた文字数が140以下のみ
            if len(http_mention_r.sub("",status["full_text"]).strip())>140:
                #print("a",end="")
                continue
            if status["truncated"] == True:
                #print("b",end="")
                continue
            if len(status["entities"]["urls"]) > 1:
                #print("c",end="")
                continue
            if status['entities'].get('media')!=None:
                if len(status['entities']['media']) > 1:
                    #print("d",end="")
                    continue
                else:
                    media_urls_truncated.append(status['entities']['media'][0]['url'])
                    media_urls.append(status['entities']['media'][0]['media_url_https'])
            else:
                media_urls.append(None)
                media_urls_truncated.append(None)
            id_str = status["id_str"]
            screen_name = status["user"]["screen_name"]
            s_names.append(screen_name)
            t_ids.append("https://twitter.com/"+screen_name+"/status/"+id_str)
            u_ids.append("https://twitter.com/"+screen_name)
            texts.append(status["full_text"])
            u_names.append(status["user"]["name"])
            p_images.append(status["user"]["profile_image_url_https"])
            verifieds.append(status["user"]["verified"])
            t_dates.append(utc_to_jtime(status["created_at"]))
            r_counts.append(status["retweet_count"])
            f_counts.append(status["favorite_count"])
            t_id_chars.append(id_str)

            if len(status["entities"]["urls"])==0:
                entities_urls.append(None)
                entities_display_urls.append(None)
            else:
                entities_urls.append(status["entities"]["urls"][0]["url"])
                entities_display_urls.append(status["entities"]["urls"][0]["display_url"])

            # retweet投稿
            if status.get("retweeted_status")==None:
                retweeted.append(False)
            else:
                retweeted.append(True)
            # 位置(profile上)
            locations.append(status["user"]["location"])
            # 全ハッシュタグ取得
            hashtags_temp=[]
            for hashtag in status['entities']['hashtags']:
                hashtags_temp.append(hashtag['text'])
            hashtags.append(hashtags_temp)



    #センチメントクラス取得
        s_classes = bunruiki.label_predict(texts,bert=True) # 内部で正規処理
        #s_classes = [2 for t in range(len(texts))]

    #データベースに保存
        #print("Saving to database...")

        for t_id,u_id,t_date,text,s_name,r_count,f_count,media_url,media_url_truncated,ret,location,hashtag,u_name,p_image,verified,t_id_char,entities_url,entities_display_url,s_class \
            in zip(t_ids,u_ids,t_dates,texts,s_names,r_counts,f_counts,media_urls,media_urls_truncated,retweeted,locations,hashtags,u_names,p_images,verifieds,t_id_chars,entities_urls,entities_display_urls,s_classes):


            # 保存判定用 text前処理
            text_chk = unicodedata.normalize('NFKC',text.lower())
            #text_chk = neologdn.normalize(text_chk)# 記号の全角半角統一 (日本語の間or日本語と英字の間のスペースは消える "富岡 義勇"→"富岡義勇". 英語は消えない"abc de"→"abc de")
            text_chk = http_mention_r.sub("",text_chk).strip() # mention,urlは除去

            # 保存判定(スパムキーが本文に含まれないか
            # アカウントにbotが含まれるか。
            # クラス2ではないか)
            # 重複するツイートではないか
            ##本文にキーが含まれるかの判定はしない(DB検索時にする)
            if s_class==2 or (spam_r.search(text_chk)) or (bot_r.search(s_name + ' ' + u_name)) or (text_chk[:40] in texts_record):
                continue
            # 重複チェック用にtext保存
            texts_record.append(text_chk[:40])

            try:
                # update
                b = Tweetdata3(t_id=t_id,
                               query=query, # 検索に使った文字列をそのまま保存
                               s_class=s_class,
                               u_id=u_id,
                               t_date=t_date,
                               content=text,
                               s_name=s_name,
                               r_count=r_count,
                               f_count=f_count,
                              media_url=media_url,
                              media_url_truncated=media_url_truncated,
                              retweeted=ret,
                              location=location,
                              hashtag=hashtag,
                              u_name=u_name,
                              p_image=p_image,
                              verified=verified,
                              t_id_char=t_id_char,
                              entities_url=entities_url,
                              entities_display_url=entities_display_url,
                              lang=lang,
                              )
                b.save(force_insert=True) # force_insert指定しないとupdateされる
                #print("o",end=' ')
                cnt += 1
            except DataError as e3:
                print(e3)
                print(text)
            except ValueError as e2:
                print(e2)
                print(text)
            except IntegrityError:
                #print("x",end=' ')
                pass


        if i == 1 or status["id"] == -1:
            break
        else:
            t_ids.clear()
            s_names.clear()
            u_ids.clear()
            texts.clear()
            t_dates.clear()
            r_counts.clear()
            f_counts.clear()
            media_urls.clear()
            media_urls_truncated.clear()
            s_classes.clear()
            locations.clear()
            hashtags.clear()
            retweeted.clear()
            u_names.clear()
            p_images.clear()
            verifieds.clear()    
            t_id_chars.clear()
            entities_urls.clear()
            entities_display_urls.clear()

            next_id=status["id"]
            time.sleep(3.00) # 3秒待機 (15分以内に180(or200?)回アクセスすると大量取得エラーのため


    return 'Success!'


if __name__=='__main__':

    msg=collect_tweet_realtime('犬 猫 lang:ja -filter:retweets',0)
    print(msg)
