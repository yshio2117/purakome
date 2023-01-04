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
sys.path.append('C:/Users/yusuk/dkango_app/sentiment')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dkango_app.settings')  # DJANGO_SETTINGS_MODULEにプロジェクトのsettings.pyのを指定します。
django.setup()

from sum.models import Tweetdata2,Keywords,Official_names # 利用したいモデルをインポートします。

# 日付の警告を無視
import warnings
warnings.filterwarnings('ignore')

# id重複取得エラー
from django.db.utils import IntegrityError
#import classifier
import re
import classifier_forsite

# mlpでラベリング
filename_vocab = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\myvectorizer_mlp.pkl')
filename_model = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\mymodel_mlp.pkl')


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



    
    #bunruiki = classifier_forsite.Myclassifier()
    #識別器と辞書読み込み
    #vocab,vocab2,model = bunruiki.load_mlp()  
    
#記録用spreadsheetオープン
## DBではなくspreadsheetからキーワード取得する

    print("accessing the spreadsheet..")
    gc = gspread.service_account()
    
    # 全キャラ名取得
    print("character names taking..")
    sh = gc.open_by_key('1b-89Ynrpek39vny4sPfkaYqNp-WYLZJ6txAjaEAld9I') # anime_keywords
    worksheet = sh.worksheet('all_charas')
    title_list = worksheet.row_values(1)
    title_list.pop(0)
    title_list.pop(0)
    character_list = worksheet.row_values(2)
    character_list.pop(0)
    character_list.pop(0)
    allchara_key = [neologdn.normalize(unicodedata.normalize('NFKC',i)) for i in (worksheet.acell('a2').value).split(',')] # salormoon
    print('allchara_key:',allchara_key)
    print("done.")
    

    print("character dic taking..")
    worksheet = sh.worksheet('char_dic')

    key_dic = [neologdn.normalize(unicodedata.normalize('NFKC',i)) for i in worksheet.col_values(1)]
    key_dic.pop(0)

    tmp = worksheet.col_values(2)
    tmp.pop(0)
    title_dic = [int(i) for i in tmp]

    tmp = worksheet.col_values(3)
    tmp.pop(0)    
    title_no_dic = [int(i) for i in tmp]

    tmp = worksheet.col_values(4)
    tmp.pop(0)
    char_no_dic = [int(i) for i in tmp]  

    official_dic = [neologdn.normalize(unicodedata.normalize('NFKC',i)) for i in worksheet.col_values(5)]
    official_dic.pop(0)
    
    print('key_dic:',key_dic)
    print('title_dic:',title_dic)
    print('title_no_dic:',title_no_dic)
    print('char_no_dic:',char_no_dic)
    print('official_dic:',official_dic)
    if len(key_dic) != len(title_dic) or\
       len(title_dic) != len(title_no_dic) or\
       len(title_no_dic) != len(char_no_dic) or\
       len(char_no_dic) != len(official_dic): 
        return "dic error!!"
 
    print('done.')
    

    
    ptn1 = re.compile(r'https://[^\s]+')
    ptn2 = re.compile(r'[@＠][a-zA-Z_0-9]+')
    ptn3 = re.compile(r'bot')
    

  
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
    
    for keyword in keywords:

        query = keyword+" lang:ja -filter:retweets" #retweet除外 含める場合は先頭の-を除く.
                                           ## 空白でキーワードを区切るとAND検索らしい
                                           ### 9/12 14:00実施で9/4 05:00まで（9日分）
        print("Keyword:{0}".format(keyword))
              
        while next_id != -1:
            if i==0:# 初回のみ
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
                
                allkey = []
                # text前処理,labeling(2022/01/04以降)
                text_chk = unicodedata.normalize('NFKC',text)
                text_chk = neologdn.normalize(text_chk)# 記号の全角半角統一 (日本語の間のスペースは消える "富岡 義勇"→"富岡義勇". 英語は消えない"abc de"→"abc de")              
                text_chk = (ptn1.sub("",text_chk)).strip() # predict,key判定用にテキスト内http除去(データベースには元のツイートを保存する)
                # メンション除くテキスト内の全キーワードの検索
                for key in keywords:
                    if key in ptn2.sub("",text_chk): # mention内は除外
                        allkey.append(key)   
                if len(allkey) == 0 or ptn3.search(s_name) != None or ptn3.search(u_name) != None: # キーワードがない場合、 botは無視
                    continue
             
                # title,char番号取得
                title_nos = []
                character_nos = []

                for key in allkey:
                    try:
                        index = key_dic.index(key)
                    except ValueError as e:
                        print(e)
                    else:
                        if title_dic[index] == 1: # titleの場合
                            title_nos.append(title_no_dic[index]) # title_no取得

                        elif title_dic[index] == 0:
                            title_nos.append(title_no_dic[index]) # title_no取得
                            character_nos.append(char_no_dic[index]) # char_no取得
    
                title_nos = sorted(list(set(title_nos)),reverse=False)
                character_nos = sorted(list(set(character_nos)),reverse=False)
                # title3,chara5に満たない場合は0で初期化
                rest = 3 - len(title_nos)
                for r in range(rest):
                    title_nos.append(None)
                rest = 5 - len(character_nos)
                for r in range(rest):
                    character_nos.append(None)                
                    
                            
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
                                  character1=character_nos[0],character2=character_nos[1],character3=character_nos[2],character4=character_nos[3],character5=character_nos[4])
                    b.save() 
                    print("o",end=' ')
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

            
            worksheet.update_cell(row, col, str(next_id)+" "+str(next_date))       
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
        col=col+1
        i=0    
        next_id=''
        next_date=''
        
    return 'Success!'


