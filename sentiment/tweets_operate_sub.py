# coding: UTF-8


from twython import Twython
import calendar,time,pprint,gspread,datetime
import unicodedata,neologdn

import os, sys, django

CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET =os.environ.get('CONSUMER_SECRET') 
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')

#sys.path.append('C:/Users/Yusuke/Desktop/dkango_app')
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')  # DJANGO_SETTINGS_MODULEにプロジェクトのsettings.pyのを指定します。
django.setup()

from sentiment.models import Tweetdata2,Official_names,Keywords # 利用したいモデルをインポートします。

# 日付の警告を無視
import warnings
warnings.filterwarnings('ignore')

# id重複取得エラー
from django.db.utils import IntegrityError,DataError
#import classifier
import re
import classifier_sub

# mlpでラベリング
#filename_vocab = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\myvectorizer_mlp.pkl')
#filename_model = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\mymodel_mlp.pkl')

PREF = [re.compile('北海道|札幌|hokkaido|sapporo'),re.compile('青森|aomori'),re.compile('岩手|盛岡|iwate|morioka'),re.compile('宮城|仙台|miyagi|sendai'),re.compile('秋田|akita'),re.compile('山形|yamagata'),re.compile('福島|fukushima'),re.compile('茨城|水戸|ibaraki|mito'),re.compile('栃木|宇都宮|tochigi|utunomiya'),re.compile('群馬|前橋|gunma|maebashi'),re.compile('埼玉|さいたま|saitama'),re.compile('千葉|chiba'),re.compile('東京|tokyo|新宿|渋谷|千代田区|世田谷区'),re.compile('神奈川|横浜|kanagawa|yokohama'),re.compile('新潟|niigata'),re.compile('富山|toyama'),re.compile('石川|金沢|ishikawa|kanazawa'),re.compile('福井|fukui'),re.compile('山梨|甲府|yamanashi|kofu'),re.compile('長野|nagano'),re.compile('岐阜|gihu'),re.compile('静岡|shizuoka'),re.compile('愛知|名古屋|aichi|nagoya'),re.compile('三重|mie|tsu'),re.compile('滋賀|大津|shiga|otsu'),re.compile('京都|kyoto'),re.compile('大阪|osaka'),re.compile('兵庫|神戸|hyogo'),re.compile('奈良|nara'),re.compile('和歌山|wakayama'),re.compile('鳥取|tottori'),re.compile('島根|松江|shimane|matsue'),re.compile('岡山|okayama'),re.compile('広島|hiroshima'),re.compile('山口|yamaguchi'),re.compile('徳島|tokushima'),re.compile('香川|高松|kagawa|takamatsu'),re.compile('愛媛|松山|ehime|matsuyama'),re.compile('高知|kouchi'),re.compile('福岡|fukuoka'),re.compile('佐賀|saga'),re.compile('長崎|nagasaki'),re.compile('熊本|kumamoto'),re.compile('大分|oita'),re.compile('宮崎|miyazaki'),re.compile('鹿児島|kagoshima'),re.compile('沖縄|那覇|okinawa|naha'),re.compile('関東|kanto'),re.compile('関西|kansai'),re.compile('東北|tohoku'),re.compile('四国|shokoku'),re.compile('九州|kyushu'),re.compile('日本|japan'),re.compile('世界|world'),re.compile('地球|earth'),re.compile('宇宙|universe')]


def utc_to_jtime(utcstr):
    time_utc = time.strptime(utcstr,'%a %b %d %H:%M:%S +0000 %Y')
    unix_time = calendar.timegm(time_utc)
    time_local = time.localtime(unix_time)
    return time.strftime("%Y-%m-%d %H:%M:%S",time_local)



    
def collect_tweet(tweet_days,anime_filter,character_filter,id_filter,start_from):
    '''
    
    Parameters
    ----------
    tweet_days : int
        取得する日付(例:1→昨日～今日, 2→一昨日～今日)    
    anime_filter : char
        空欄ではない場合全キャラで取得
    character_filter : char
        空欄ではない場合そのキャラのみ
    id_filter : int
        特定キャラの続きから取得
    character_from : int
        アニメ&特定キャラの続きから取得

    Returns 
    -------
    char:成功・失敗メッセージ

    '''



    
    #bunruiki = classifier_sub.Myclassifier()
    #識別器と辞書読み込み
    #vocab,vocab2,model = bunruiki.load_mlp()  
    
    print("accessing the spreadsheet..")
    gc = gspread.service_account()
        
    
    print("character names taking..")
    sh = gc.open_by_key('1b-89Ynrpek39vny4sPfkaYqNp-WYLZJ6txAjaEAld9I') # anime_keywords
    worksheet = sh.worksheet('all_charas')
    title_list = worksheet.row_values(1)
    title_list.pop(0)
    title_list.pop(0)
    character_list = worksheet.row_values(2)
    character_list.pop(0)
    character_list.pop(0)
    keysfortweet= [i for i in (worksheet.acell('b2').value).split(',')] # salormoon
    print('keysfortweet:',keysfortweet)
    print("done.")

    
    if character_filter == '' and anime_filter =='':
        print("No anime and character are chosen.")
        return "FAILED:No anime and character are chosen."


    elif character_filter != '':
        print("Get tweet by character.")
        print(character_list)
        
        for i,c in enumerate(character_list):
            if character_filter in c.split(','):
                worksheet = sh.worksheet(title_list[i])
                break
            if i+1 == len(character_list):
                print("failed finding anime sheet:{0}".format(character_filter))
                return 'FAILED:Character_filter!'

        
    # 個別アニメ取得
    elif anime_filter != '':
        print("Get tweet by anime.")
        print(title_list)
        for i,t in enumerate(title_list): # アニメ管理シート検索
            if anime_filter == t:
                worksheet = sh.worksheet(t)
                break
            if i+1 == len(title_list):
                print("failed finding anime sheet:{0}".format(anime_filter))
                return 'FAILED:anime_filter!'

    row = worksheet.acell('A1').value #?列目

    
    character_list = worksheet.row_values(2)
    if start_from!='': # 途中から始める場合,前列までのキャラリストを削除
        for i in range(start_from):
            character_list.pop(0)
    else:
        character_list.pop(0) # 1列目は除外
    character_list=[i for i in character_list if i != '']# 空欄も除外
    

    keywords=[]
    if character_filter != '': # キャラ指定の場合
        try:
            col = character_list.index(character_filter)+2 #?列目のキャラのみを取得
            keywords.append(character_filter)
        except ValueError:
            return "FAILED:Keyword no exist!"
        
    else: # anime_filterの場合
        if start_from!='':
            col = start_from+1
        else:
            col = 2 # 2列目から全列取得
        keywords=character_list

    
    print("Keyword_list:{0}".format(keywords))
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
    if id_filter != "": # 途中から始める場合
        next_id=id_filter
        print("continue from ID:",next_id)
        i=1 # 各キーワードで何回目の実行か(1回目と2回目以降で処理が違うため)
    else:
        next_id=''
        i=0
        
    next_date='' # spreadsheet 経過表記用

    ptn1 = re.compile(r'https://[^\s]+')
    ptn2 = re.compile(r'[@＠][a-zA-Z_0-9]+')
    ptn3 = re.compile(r'bot')
    
    for keyword in keywords:

        query = keyword+" lang:ja -filter:retweets" #retweet除外 含める場合は先頭の-を除く.
                                           ## 空白でキーワードを区切るとAND検索らしい
                                           ### 9/12 14:00実施で9/4 05:00まで（9日分）
        print("Keyword:{0}".format(keyword))
              
        while next_id != -1:
            if i==0:# 初回のみ
                try:
                    statuses = twitter.search(q=query,tweet_mode="extended",count=100)["statuses"]
                except Twython.exceptions.TwythonError as e:
                    print(e)
                    time.sleep(30.00)             
                    print("once more try..")
                    statuses = twitter.search(q=query,tweet_mode="extended",count=100)["statuses"]
                
                if len(statuses)==0:
                    print("No tweets found.")
                    next_id=-1
                    next_date='2021-01-01'
            
                else:
                    print("Tweets:",len(statuses))
                    for status in statuses:
            
                        if len(status["full_text"])>140:
                            continue
                        if status["truncated"] == True:
                            continue                        
                        if len(status["entities"]["urls"]) > 1:
                            continue                     
                        if status['entities'].get('media')!=None:
                            if len(status['entities']['media']) > 1:
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
            
        
    
                    next_id=status["id"]
                    next_date=utc_to_jtime(status["created_at"])
        
    
            else:# 2回目以降
                try:
                    statuses = twitter.search(q=query,tweet_mode="extended",max_id=next_id-1,count=100)["statuses"]
                except Twython.exceptions.TwythonError as e:
                    print(e)
                    time.sleep(30.00)             
                    print("once more try..")
                    statuses = twitter.search(q=query,tweet_mode="extended",max_id=next_id-1,count=100)["statuses"]

                    
                if len(statuses)==0:
                    print("No tweets found.")
                    next_id=-1
                    next_date='2021-01-01'
                else:
                    print("Tweets:",len(statuses))        
                    for status in statuses:
                        
                        if len(status["full_text"])>140:
                            continue
                        if status["truncated"] == True:
                            continue                           
                        if len(status["entities"]["urls"]) > 1:
                            continue                     
                        if status['entities'].get('media')!=None:
                            if len(status['entities']['media']) > 1:
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
                        u_names.append(status["user"]["name"]) #20220129追加
                        p_images.append(status["user"]["profile_image_url_https"])
                        verifieds.append(status["user"]["verified"])
                        texts.append(status["full_text"])
            
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
                        # ハッシュタグ取得
                        hashtags_temp=[]
                        for hashtag in status['entities']['hashtags']:
                            hashtags_temp.append(hashtag['text'])
                        hashtags.append(hashtags_temp)

    
                    next_id=status["id"]
                    next_date=utc_to_jtime(status["created_at"])
            
      
            #センチメントクラス取得
            '''
            print("Classifying labels...")
            for text in texts:
                s_classes.append(1)
            print("Done.",end=' ')
            '''
        # 最初のスペースまでをキーワードとする
        #keyword=keyword.split()[0]
        
        #データベースに保存
            print("Classifying label and Saving to database...")
            #duplicates=0
            for t_id,u_id,t_date,text,s_name,r_count,f_count,media_url,media_url_truncated,ret,location,hashtag,u_name,p_image,verified,t_id_char,entities_url,entities_display_url \
                in zip(t_ids,u_ids,t_dates,texts,s_names,r_counts,f_counts,media_urls,media_urls_truncated,retweeted,locations,hashtags,u_names,p_images,verifieds,t_id_chars,entities_urls,entities_display_urls):        
                
                keyword_intext = []
                # text前処理,labeling(2022/01/04以降)
                text_chk = unicodedata.normalize('NFKC',text)
                text_chk = neologdn.normalize(text_chk)# 記号の全角半角統一 (日本語の間のスペースは消える "富岡 義勇"→"富岡義勇". 英語は消えない"abc de"→"abc de")              
                text_chk = (ptn1.sub("",text_chk)).strip() # predict,key判定用にテキスト内http除去(データベースには元のツイートを保存する)
                # メンション除くテキスト内の全キーワードの検索
                for key in keysfortweet:
                    if key in ptn2.sub("",text_chk): # mention内は除外
                        keyword_intext.append(key)   
                if len(keyword_intext) == 0 or ptn3.search(s_name) != None or ptn3.search(u_name) != None: # キーワードがない場合、 botは無視
                    continue
             
            # title,char番号取得-----------
                title_nos = []
                character_nos = []

                for key in keyword_intext:
                    try:
                        record = Official_names.objects.get(index = Keywords.objects.get(keyword=key).official_name_id)
                    except:
                        print('{0} could not be found in DB.'.format(key))
                        continue
                    else:
                        if record.title == True:
                            title_nos.append(record.index)
                        else:
                            character_nos.append(record.index)
                            # キャラが属するアニメ名
                            title_nos.append(Official_names.objects.get(title_name=record.title_name,
                                                                        title=True).index)
                        
                title_nos = list(set(title_nos))
                character_nos = list(set(character_nos))
          
                # title3,chara5に満たない場合はNoneで初期化
                rest = 3 - len(title_nos)
                for r in range(rest):
                    title_nos.append(None)
                rest = 5 - len(character_nos)
                for r in range(rest):
                    character_nos.append(None)   
                    
                if set(title_nos) == {None} and set(character_nos) == {None}:
                    continue
              #-----------------------------

                # pref取得
                pref_id = ""
                if location in ["", None]:
                    pref_id = None
                else:
                    # locationからprefecture検索
                    for k,p in enumerate(PREF):
                        if p.search(location.lower()):
                            pref_id = k+1
                            break
                    if pref_id == "":
                        pref_id = None
              
                            
                # classifying 20220110以降取得データ
                #s_class = bunruiki.predict_mlp([text_chk],vocab,vocab2,model)[0]
                s_class = 2
                try:
                    #s_class = -1
                    # update
                    b = Tweetdata2(s_class=s_class,t_id=t_id,u_id=u_id,t_date=t_date,
                                   content=text,s_name=s_name,
                                   r_count=r_count,f_count=f_count,
                                  media_url=media_url,media_url_truncated=media_url_truncated,retweeted=ret,location=location,
                                  hashtag=hashtag,u_name=u_name,p_image=p_image,
                                  verified=verified,t_id_char=t_id_char,
                                  entities_url=entities_url,
                                  entities_display_url=entities_display_url,
                                  title1=title_nos[0],title2=title_nos[1],title3=title_nos[2],
                                  character1=character_nos[0],character2=character_nos[1],character3=character_nos[2],character4=character_nos[3],character5=character_nos[4],
                                  prefecture=pref_id)
                    b.save() 
                    print("o",end=' ')
                except DataError as e3:
                    print(e3)
                    print(text)
                except ValueError as e2:
                    print(e2)
                    print(text)
                except IntegrityError as e:
                    print("x",end=' ')
                    '''
                    # 重複判定用
                    duplicates=duplicates+1
                    if duplicates==len(s_classes):
                        duplicates=-1
                    '''
                   # print('type:'+str(type(e)))
        
            # 途中で止めれるようにnext_id セルに保存
            print("\nlast_saved_date:",next_date)
            print("last_saved_id:",next_id)

            
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
            i=i+1

            try:
                worksheet.update_cell(row, col, str(next_id)+" "+str(next_date))       
            except gspread.exceptions.APIError:
                time.sleep(30.00)
                try: # tmporary error 30秒後に再度繰り返す
                    worksheet.update_cell(row, col, str(next_id)+" "+str(next_date))  
                except:
                    return 'Gspread API Failure!'
                
            time.sleep(5.00) # 5秒待機 (15分以内に180(or200?)回アクセスすると大量取得エラーのため

                        
            # 今日~昨日のみ取得.(daysを変えればx日分に変更可能.正しく動く)
            if (datetime.date.today()-datetime.timedelta(days=tweet_days)) > datetime.datetime.strptime(str(next_date)[:10],'%Y-%m-%d').date():# 最終取得日付(str)をdatetimeへ変換して日付のみ比較
                worksheet.update_cell(row, col, str(datetime.date.today()))
                print("{0}:successfully got all tweets:[{1}-{2}]".format(keyword,str(datetime.date.today()-datetime.timedelta(days=tweet_days)),str(datetime.date.today())))
                if len(keywords)==1: #1キーワードの場合終了
                    return '{0}:successfully got all tweets:[{1}-{2}]'.format(keyword,str(datetime.date.today()-datetime.timedelta(days=tweet_days)),str(datetime.date.today()))
                else:# 複数キーワードの場合次のキーワード(行)へ
                    break 
            '''
            # 重複するまで取得
            if duplicates==-1: # 取得全投稿が既に登録済みの場合
                worksheet.update_cell(row, col, str(datetime.date.today()))
                print("{0}:tweets are all duplicates.".format(keyword))
                if len(keywords)==1: #1キーワードの場合終了
                    return 'Success!(tweets are all duplicates)'
                else:# 複数キーワードの場合次のキーワード(行)へ
                    break
            '''
            
    #完了したら(取得日付)を貼り付ける
        worksheet.update_cell(row, col, str(datetime.date.today()))
        print("{0}:successfully got all tweets.".format(keyword))
        time.sleep(5.00)
        col=col+1
        i=0    
        next_id=''
        next_date=''
        
    return 'Success!'


if __name__=='__main__':
    
    titles = ['salormoon','鬼滅','現実','異世界食堂','転スラ','プラチナエンド','進化の実','吸血鬼すぐ死ぬ','見える子ちゃん','古見さん','半妖の夜叉姫','海賊王女','最果てのパラディン','ありふれた職業で世界最強','着せ恋','錆喰いビスコ','ヴァニタスの手記','リーマンズクラブ','東京24区']    

    tweet_days = int(input("tweet_days:"))
    pprint.pprint([(i,t) for i,t in enumerate(titles)])
    anime_from = int(input("anime_from(default:0):"))
    character_from = int(input("character_from(default:1):"))
    
    print(tweet_days,anime_from,character_from)    

    '''
    tweet_days = 1
    anime_from = 0 # 途中のアニメから始める場合(初期値0)
    character_from = 1# 途中キャラから始める場合は列入力(初期値1)    
    '''
    titles = titles[anime_from:]
    
    for i,title in enumerate(titles):     
        if i==0:
            msg = collect_tweet(tweet_days,title,'','',character_from)
        else:
            msg = collect_tweet(tweet_days,title,'','','') # セーラームーンから全アニメ取得   
        print(msg)
