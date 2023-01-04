# coding: UTF-8

#from models import Tweetdata
import classifier_sub
import numpy as np
import csv
import os, sys, django
#sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dkango_app'))
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')  # DJANGO_SETTINGS_MODULEにプロジェクトのsettings.pyのを指定します。
django.setup()
from sentiment.models import Tweetdata2,Summarys,Statistics1week,Official_names,Keywords,Prefectures # 利用したいモデルをインポートします。
from django.utils import timezone

# 日付の警告を無視
import warnings
warnings.filterwarnings('ignore')
from django.db.models import Q
# id重複取得エラー
from django.db.utils import IntegrityError
import re
import tokenizer
import datetime
import MeCab
import itertools
import neologdn,unicodedata
import math
import pprint
import random

#wordcloud
from wordcloud import WordCloud
from PIL import Image

from takesummary_forsite import take_summary
from twython import Twython
import gspread
CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET =os.environ.get('CONSUMER_SECRET') 
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')


def keywords_update():
    
    print("accessing the spreadsheet..",end='')
    gc = gspread.service_account()
    #ファイルオープン
    sh = gc.open_by_key('1b-89Ynrpek39vny4sPfkaYqNp-WYLZJ6txAjaEAld9I') # anime_keywords
    worksheet = sh.worksheet('index_summary')
 
    tmp = worksheet.col_values(1)
    tmp.pop(0)
    indexes = [int(i) for i in tmp]

    
    # keywordはカンマ区切りで複数あり
    keywords = [i.split(',') for i in worksheet.col_values(5)]
    keywords.pop(0)
    

    if len(indexes) != len(keywords):
        return 'number of indexes is different.'
    
    pairs = [(i,k) for i,k in zip(indexes,keywords) if k != ['']] # キーワード空欄(欠番)は除外

    print("deleting DB..")
    
    Keywords.objects.all().delete()

        
    print("done.")
    
    print('bulk update..')                                              
    update_list = []
    for pair in pairs:
        for key in pair[1]:
            update_list.append(Keywords(official_name_id = pair[0],
                                              keyword = key
                                              ))

        
    Keywords.objects.bulk_create(update_list)


    print("done.")
    print("done.")

    return 'success.'
    
    
def official_names_update():
    
    print("accessing the spreadsheet..",end='')
    gc = gspread.service_account()
    #ファイルオープン
    sh = gc.open_by_key('1b-89Ynrpek39vny4sPfkaYqNp-WYLZJ6txAjaEAld9I') # anime_keywords
    worksheet = sh.worksheet('index_summary')

    tmp = worksheet.col_values(1)
    tmp.pop(0)
    indexes = [int(i) for i in tmp]


    tmp = worksheet.col_values(2)
    tmp.pop(0)
    titles = [i for i in tmp]


    official_names = [i for i in worksheet.col_values(3)]
    official_names.pop(0)


    title_names = [i for i in worksheet.col_values(4)]
    title_names.pop(0)    

    
    if (len(indexes) != len(titles) or len(titles) != len(official_names) or len(titles) != len(title_names)):
        return 'number of indexes is different.'


        
        
    print("updating Official_names..")
    
    #Official_names.objects.all().delete()
    for index,title,official_name,title_name in zip(indexes,titles,official_names,title_names):
        obj, created = Official_names.objects.update_or_create(
            index = index,

            defaults={
                'title' : True if title == 'TRUE' else False,
                'official_name' : official_name,
                'title_name' : title_name
            }
        )


    print("done.")

    return 'success.'
            


def dataupdate(days=1):
    
    
    dt_now = datetime.datetime.now()
    e_date = datetime.datetime(dt_now.year,
                              dt_now.month, 
                              dt_now.day, 0, 0, 0, 0,tzinfo=datetime.timezone.utc) - datetime.timedelta(hours=9)
    s_date = e_date - datetime.timedelta(days=days) 
    print('date:{0}-{1}'.format(s_date,e_date))

    # 全キャラ名取得
    keywords = list(Keywords.objects.all().values())
    print('keywords:',keywords)
    print("done.")

    print("accesing DB..")
    #DBから本文取得
    ## 最大14日程度目安
    data = Tweetdata2.objects.filter(t_date__range=[s_date,
                                                    e_date]
                                       ).only('id',
                                            'content',
                                            's_class',
                                            'wakachi',
                                            'spam',
                                            'title1',
                                            'title2',
                                            'title3',
                                            'character1',
                                            'character2',
                                            'character3',
                                            'character4',
                                            'character5').order_by('id') # 何らかのキーで並び替えないとbulk updateが正しい順序でupdateできないらしい
    
    
    print("done.")
    
    contents = list(data.values_list("content", flat=True))
    print('total:',len(contents))

    # char_dic判定用 contents作成(キャラ名を正規化しない&neolognd.normalizeを追加でする)
    ptn1 = re.compile(r'https://[^\s]+')
    contents_chk = [(ptn1.sub("",neologdn.normalize(unicodedata.normalize('NFKC',i)))).strip() for i in contents]
    if len(contents) != len(contents_chk):
        return "len(contents_chk) error!"
        
    print("done.")
    
    print("形態素解析 SPAM判定 Keyword整理..")
    # wakachi
    tagger = MeCab.Tagger(r'-u C:\Users\yusuk\wikidump_20220429.dic')
    wakachis = [] # wordcloud
    spams = [] # spam判定
    spam_l = ['在庫','定価','価格','完売','実施中','配信中','開催中','株式会社','受注','売れ筋','所持','好評','楽天市場','お買い得','質問箱','譲渡','求','譲','譲り','売','買','交換','提供','検討','販売','予約販売','発売','新発売','入荷','再入荷','買取','DM','送料'] # 20220116 譲り,交換　追加
    title1 = []
    title2 = []
    title3 = []
    character1 = []
    character2 = []
    character3 = []
    character4 = []
    character5 = []
    
    p1 = re.compile(r'[@＠][a-zA-Z_0-9]+') # \wがうまくいかない?
    p2 = re.compile(r'熟女|マッサージ|数量限定|景品情報|プライズ情報|キャラ診断|店頭|特典|ココからどうぞ|是非|お声がけ|お声掛け|rakuten|激安|お譲り|商品情報|商品紹介|漫画紹介|お得な|しくお願い致します|しくお願いいたします|shindanmaker')
    p3 = re.compile(r'\n')
    for content,content_chk in zip(contents,contents_chk):

# title,character no 取得        

        title_nos = []
        character_nos = []
        
        for keyword in keywords:
            if keyword['keyword'] in p1.sub('',content_chk): # mention内は除外
                record = Official_names.objects.get(index=keyword['official_name_id'])
                if record.title == True:
                    title_nos.append(record.index)
                else:
                    character_nos.append(record.index)
                    # キャラが属するアニメ名
                    try:
                        title_nos.append(Official_names.objects.get(title_name=record.title_name,
                                                                title=True).index)
                    except:
                        print('record',record)
                        print('record.title_name',record.title_name)
                        return 'error'

        title_nos = list(set(title_nos))
        character_nos = list(set(character_nos))
  
        # title3,chara5に満たない場合はNoneで初期化
        rest = 3 - len(title_nos)
        for r in range(rest):
            title_nos.append(None)
        rest = 5 - len(character_nos)
        for r in range(rest):
            character_nos.append(None)   

        title1.append(title_nos[0])
        title2.append(title_nos[1])
        title3.append(title_nos[2])
        character1.append(character_nos[0])
        character2.append(character_nos[1])
        character3.append(character_nos[2])
        character4.append(character_nos[3])
        character5.append(character_nos[4])        
# ------------------        
            
        #node = tagger.parseToNode(tokenizer.cleansing_text(content))
        node = tagger.parseToNode(content_chk) # キャラ名をwordcloudに入れたいのでtokenizer.cleaningは使わない
        flag = False # spamフラグ
        if title1[-1] == None: # アニメではない投稿の場合
            flag = True
        if p2.search(content_chk.lower()) != None: #spam単語が原文に含まれる場合
            flag = True
        if len(p3.findall(content_chk))>=8: # 改行が多すぎる場合もspam
            flag = True
        wakachi = []
        while node:
            features = node.feature.split(',')
            if features[0] != 'BOS/EOS':
                if flag == False and features[0] == '名詞' and features[6].lower() in spam_l:
                    flag = True # 文内に一つでも該当ワードが含まれればspam扱い
                
                if (features[0] == '形容詞' and features[1] == '自立') or (features[0] == '名詞' and features[1] == '一般') or features[1] == '形容動詞語幹':
                    token = features[6] if features[6] != '*' else node.surface
                    wakachi.append(token)
                
            node = node.next
        spams.append(flag)
    
        wakachis.append(' '.join(list(set(wakachi))))
        
    
    print("done.")
    print("contents:",len(contents))
    print('wakachi:',len(wakachis))
    print('spam:',len(spams))
    print('t1:',len(title1))
    print('t2:',len(title2))
    print('t3:',len(title3))
    print('c1:',len(character1))
    print('c2:',len(character2))
    print('c3:',len(character3))
    print('c4:',len(character4))
    print('c5:',len(character5))
    
    #識別器と辞書読み込み
    bunruiki = classifier_sub.Myclassifier()
    vocab,vocab2,model = bunruiki.load_mlp()  
            

    print("data predicting by mlp bm25..")
    predictions = []
    start = 0
    l_size = len(contents)
    while True:
        end = start + 100000
        predictions.append(bunruiki.predict_mlp(contents[start:end],vocab,vocab2,model)) # np.str_
        start = end
    
        if start > l_size:
            print("100% done.")
            break
        print("{0}% done.".format(round(100*end/l_size)))
    predictions = list(itertools.chain.from_iterable(predictions))
    
    print(len(predictions))
    print("done.")


    
    print("DB update..")
    # DB update
    # salormoon 通常更新は240000投稿で2時間かかる
    # batch処理　同salormoon 5分程度で終了
    update_list = []
    print("making update_list..")

    for prediction,wakachi,spam,t1,t2,t3,c1,c2,c3,c4,c5,obj in zip(predictions,wakachis,spams,title1,title2,title3,character1,character2,character3,character4,character5,data):
        
        obj.s_class = prediction
        obj.wakachi = wakachi
        if prediction == 2: # eはスパム扱い
            obj.spam = True
        else:
            obj.spam = spam
        
        obj.title1 = t1
        obj.title2 = t2
        obj.title3 = t3
        obj.character1 = c1
        obj.character2 = c2
        obj.character3 = c3
        obj.character4 = c4
        obj.character5 = c5
        update_list.append(obj)
    print('done.')
    print('bulk update..')
    # コピーを取得した時と同じ順序でないと正しい順番でbulk updateできない
    data.bulk_update(update_list, fields=['s_class',
                                            'wakachi',
                                            'spam',
                                            'title1',
                                            'title2',
                                            'title3',
                                            'character1',
                                            'character2',
                                            'character3',
                                            'character4',
                                            'character5'],batch_size=1000)
    
    return "done."


    # http削除
HTTP = re.compile(r'http[^\s]+')
HASHTAG = re.compile(r'[#＃][^\s]+')
MENTION = re.compile(r'[@＠][a-zA-Z_0-9]+') # \wがうまくいかない?
ETC = re.compile(r'…+|。+|、+|\!+|\?+')
GREETING = re.compile(r'おはようございます|ありがとうございます|ありがとうございました|こんにちは|こんにちわ|こんばんは|こんばんわ|お疲れ様です')
EMOJI = re.compile(r'[😉😁😂😃😄😅😆😇😈😉😊😋😌😍😎😏😐😑😒😓😔😕😖😗😘😙😚😛😜😝😞😟😠😡😢😣😤😥😦😧😨😩😪😫😬😭😮😯😰😱😲😳😴😵😶😷😸😹😺😻😼😽😾😿🙀🙁🙂🙃🙄🤐🤑🤒🤓🤣🤔🥺🙇‍🙏☔️🙋‍💦💕]')
def cleaning(document, tagger):
    
    
    text = document[0] # (content, id)
    text = HTTP.sub('',text)
    text = HASHTAG.sub('',text)
    text = MENTION.sub('',text)
    text = GREETING.sub('',text)
    text = ETC.sub('。',text)
    text = EMOJI.sub('。',text)
    text = neologdn.normalize(text)
    text = text.strip()
    text = text.lower()

    node = tagger.parseToNode(text)

    w_classes = []
    while node:
        features = node.feature.split(',')
        if features[0] != 'BOS/EOS':
            w_classes.append((features[0], features[1]))
        node = node.next

    if ('名詞', '一般') in w_classes or ('名詞', '固有名詞') in w_classes:
        if (('動詞', '自立') in w_classes or
            ('形容詞', '自立') in w_classes or
            ('名詞', '形容動詞語幹') in w_classes or
            ('名詞', 'サ変接続') in w_classes):
            
            return (text, document[1])

    return None


def statistics_update():
    """summary以外の項目の更新"""
    

    #Statistics1week.objects.all().delete()
    
    # date検索でt_date__range=[s,e]の場合はs,eともにutc時間で指定しないと数が合わなくなる
    ## t_date__date=d で1日指定の場合は自動でutc時間に変換されるよう。問題なく取得できる
    dt_now = datetime.datetime.now()
    e_date = datetime.datetime(dt_now.year,
                              dt_now.month, 
                              dt_now.day, 0, 0, 0, 0,tzinfo=datetime.timezone.utc) - datetime.timedelta(hours=9)
    s_date = e_date - datetime.timedelta(days=7)
    print('date:{0}-{1}'.format(s_date,e_date))  

    title_nos = list(Official_names.objects.filter(title=True,index__gte=1).values_list('index',flat=True))
    chara_nos = list(Official_names.objects.filter(title=False,index__gte=1).values_list('index',flat=True))
    print('titles:',title_nos)
    print('charas',chara_nos)

    
    #DBから本文取得
    ## 最大14日程度目安

    # 全キャラ取得すると１時間以上かかるため絞り込み必要
    ## tableにキャラクターだけでなくアニメレコードも必要(全キャラからsumが出来ないため)
    
    for chara_no in chara_nos:
        print('chara:{0}'.format(chara_no))

        keys = ['4_count_d1','3_count_d1','0_count_d1','1_count_d1','4_count_d2','3_count_d2','0_count_d2','1_count_d2','4_count_d3','3_count_d3','0_count_d3','1_count_d3','4_count_d4','3_count_d4','0_count_d4','1_count_d4','4_count_d5','3_count_d5','0_count_d5','1_count_d5','4_count_d6','3_count_d6','0_count_d6','1_count_d6','4_count_d7','3_count_d7','0_count_d7','1_count_d7']
        values = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        d = dict(zip(keys, values))   
          
        allobj = Tweetdata2.objects.filter(Q(spam=False),
                                            Q(s_class=0) | Q(s_class=1) | Q(s_class=3) | Q(s_class=4),
                                            Q(t_date__range=[s_date,e_date]),
                                            Q(character1=chara_no) | 
                                            Q(character2=chara_no) | 
                                            Q(character3=chara_no) | 
                                            Q(character4=chara_no) | 
                                            Q(character5=chara_no)).only('t_date','s_class')
        li = list(allobj.values_list('t_date','s_class')) # tupleのリストとして取り出す

        for k in range(1,8):
            search_date_from = e_date - datetime.timedelta(days=k)
            search_date_until = search_date_from + datetime.timedelta(days=1)
            for c in range(0,5):
                if c == 2:
                    continue
                d['{0}_count_d{1}'.format(c, k)] = len([l[0] for l in li 
                                                        if l[0] >= search_date_from
                                                        and l[0] <= search_date_until
                                                        and l[1] == c
                                                        ])
                
        print('d:',d)
        print('data saving..')
        obj, created = Statistics1week.objects.update_or_create(
                        official_name_id=chara_no,
                        defaults={'s_date':s_date,'e_date':e_date,'p2_count_d1':d['4_count_d1'],'p1_count_d1':d['3_count_d1'],'n1_count_d1':d['1_count_d1'],'n2_count_d1':d['0_count_d1'],'p2_count_d2':d['4_count_d2'],'p1_count_d2':d['3_count_d2'],'n1_count_d2':d['1_count_d2'],'n2_count_d2':d['0_count_d2'],'p2_count_d3':d['4_count_d3'],'p1_count_d3':d['3_count_d3'],'n1_count_d3':d['1_count_d3'],'n2_count_d3':d['0_count_d3'],'p2_count_d4':d['4_count_d4'],'p1_count_d4':d['3_count_d4'],'n1_count_d4':d['1_count_d4'],'n2_count_d4':d['0_count_d4'],'p2_count_d5':d['4_count_d5'],'p1_count_d5':d['3_count_d5'],'n1_count_d5':d['1_count_d5'],'n2_count_d5':d['0_count_d5'],'p2_count_d6':d['4_count_d6'],'p1_count_d6':d['3_count_d6'],'n1_count_d6':d['1_count_d6'],'n2_count_d6':d['0_count_d6'],'p2_count_d7':d['4_count_d7'],'p1_count_d7':d['3_count_d7'],'n1_count_d7':d['1_count_d7'],'n2_count_d7':d['0_count_d7']}
                        )
        if created == True:
            print("added new record.")
        else:
            print("updated record.")
    
    for title_no in title_nos:
        print('title:{0}'.format(title_no))        

        keys = ['4_count_d1','3_count_d1','0_count_d1','1_count_d1','4_count_d2','3_count_d2','0_count_d2','1_count_d2','4_count_d3','3_count_d3','0_count_d3','1_count_d3','4_count_d4','3_count_d4','0_count_d4','1_count_d4','4_count_d5','3_count_d5','0_count_d5','1_count_d5','4_count_d6','3_count_d6','0_count_d6','1_count_d6','4_count_d7','3_count_d7','0_count_d7','1_count_d7']
        values = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        d = dict(zip(keys, values))        
        
        allobj = Tweetdata2.objects.filter(Q(spam=False),
                                    Q(s_class=0) | Q(s_class=1) | Q(s_class=3) | Q(s_class=4),
                                    Q(t_date__range=[s_date,e_date]),
                                    Q(title1=title_no) | 
                                    Q(title2=title_no) | 
                                    Q(title3=title_no)).only('t_date','s_class')
        li = list(allobj.values_list('t_date','s_class')) # tupleのリストとして取り出す

        
        for k in range(1,8):
            search_date_from = e_date - datetime.timedelta(days=k)
            search_date_until = search_date_from + datetime.timedelta(days=1)

            for c in range(0,5):
                if c == 2:
                    continue
                #print("accesing DB:{0}..".format(char_no[1]))                
                d['{0}_count_d{1}'.format(c, k)] = len([l[0] for l in li 
                                                        if l[0] >= search_date_from
                                                        and l[0] <= search_date_until
                                                        and l[1] == c
                                                        ])
                #print('done')
        
        print(d)
        print('data saving..')
        obj, created = Statistics1week.objects.update_or_create(
                        official_name_id=title_no,
                        defaults={'s_date':s_date,'e_date':e_date,'p2_count_d1':d['4_count_d1'],'p1_count_d1':d['3_count_d1'],'n1_count_d1':d['1_count_d1'],'n2_count_d1':d['0_count_d1'],'p2_count_d2':d['4_count_d2'],'p1_count_d2':d['3_count_d2'],'n1_count_d2':d['1_count_d2'],'n2_count_d2':d['0_count_d2'],'p2_count_d3':d['4_count_d3'],'p1_count_d3':d['3_count_d3'],'n1_count_d3':d['1_count_d3'],'n2_count_d3':d['0_count_d3'],'p2_count_d4':d['4_count_d4'],'p1_count_d4':d['3_count_d4'],'n1_count_d4':d['1_count_d4'],'n2_count_d4':d['0_count_d4'],'p2_count_d5':d['4_count_d5'],'p1_count_d5':d['3_count_d5'],'n1_count_d5':d['1_count_d5'],'n2_count_d5':d['0_count_d5'],'p2_count_d6':d['4_count_d6'],'p1_count_d6':d['3_count_d6'],'n1_count_d6':d['1_count_d6'],'n2_count_d6':d['0_count_d6'],'p2_count_d7':d['4_count_d7'],'p1_count_d7':d['3_count_d7'],'n1_count_d7':d['1_count_d7'],'n2_count_d7':d['0_count_d7']}
                        )
        if created == True:
            print("added new record.")
        else:
            print("updated record.")
        
    print("done.")
    return 'Success.'


def clean_summary():
    ### Tweetdata2から要約クリア ###
    
    
    dt_now = datetime.datetime.now()
    e_date = datetime.datetime(dt_now.year,
                              dt_now.month, 
                              dt_now.day, 0, 0, 0, 0,tzinfo=datetime.timezone.utc) - datetime.timedelta(hours=9)
    s_date = e_date - datetime.timedelta(days=7)
    
    data = Tweetdata2.objects.filter(Q(spam=False),
                                     Q(t_date__range=[s_date,e_date]),
                                       summary_brand_id__gte=1,
                                       ).only('id','summary_brand_id').order_by('id') #
    print('len(data):',len(data))
    update_list = []
    for obj in data:
       
        obj.summary_brand_id = 0
        update_list.append(obj)
        
    print("deleting tweetdata2 summarys..")
    data.bulk_update(update_list,
                    fields=['summary_brand_id',
                            #'summary_text'
                            ],
                    batch_size=5000
                    ) 
    print("done.")
    

                                                           
    return 'done.'

    
def sumupdate():
    
    
    dt_now = datetime.datetime.now()
    e_date = datetime.datetime(dt_now.year,
                              dt_now.month, 
                              dt_now.day, 0, 0, 0, 0,tzinfo=datetime.timezone.utc) - datetime.timedelta(hours=9)
    s_date = e_date - datetime.timedelta(days=7)
    print('date:{0}-{1}'.format(s_date,e_date))  

    # 全キャラ名取得
    keywords = list(Keywords.objects.all().values_list('keyword', flat=True))
    print('keywords:',keywords)
    print("done.")
    
    title_nos = list(Official_names.objects.filter(title=True,index__gte=1).values_list('index',flat=True))
    chara_nos = list(Official_names.objects.filter(title=False,index__gte=1).values_list('index',flat=True))
    print('titles:',title_nos)
    print('charas',chara_nos)


    for cnt in range(2):
        if cnt == 0:
            target_nos = title_nos
        else:
            target_nos = chara_nos
                
        for target_no in target_nos:
            print("accesing DB:{0}".format(target_no))
            #DBから本文取得
            if cnt == 0:                
                data = Tweetdata2.objects.filter(Q(spam=False),
                                                 Q(summary_brand_id=0),# 他のアニメで要約されていない
                                                 Q(t_date__range=[s_date,e_date]),
                                                 Q(title1=target_no) | Q(title2=target_no) | Q(title3=target_no),
                                                 # title1のみ（他も見ると複数アニメの要約が一緒になってしまう
                                                   ).only('id',
                                                          's_class',
                                                          'content',
                                                          't_id',
                                                          'u_id',
                                                          'summary_brand_id',
                                                          'summary_no'
                                                          ).order_by('id') # 何らかのキーで並び替えないとbulk updateが正しい順序でupdateできないらしい
            #DBから本文取得
            if cnt == 1:                
                data = Tweetdata2.objects.filter(Q(spam=False),
                                                 Q(summary_brand_id=0),# 他のアニメで要約されていない
                                                 Q(t_date__range=[s_date,e_date]),
                                                 Q(character1=target_no) | Q(character2=target_no) | Q(character3=target_no) | Q(character4=target_no) | Q(character5=target_no),
                                                 # title1のみ（他も見ると複数アニメの要約が一緒になってしまう
                                                   ).only('id',
                                                          's_class',
                                                          'content',
                                                          't_id',
                                                          'u_id',
                                                          'summary_brand_id',
                                                          'summary_no'
                                                          ).order_by('id') # 何らかのキーで並び替えないとbulk updateが正しい順序でupdateできないらしい
        
           
                                                      
            allobj = list(data.values())                                                  
            print("done. len:{0}".format(len(allobj)))
        
        # 要約取得2
            print("take summarys..")
            sim_texts_all = [] #posi, nega計
            for pn in range(2): # 0:posi, 1:nega
                if pn == 0:
                    #p1,p2合計
                    documents = [(obj['content'],obj['t_id'],obj['u_id']) for obj in allobj if obj['s_class'] in [3,4]]
                    documents = get_unique_list(documents,2) # u_id重複削除
                    documents = [(doc[0],doc[1]) for doc in documents]
                if pn == 1:
                    #n1,n2合計
                    documents = [(obj['content'],obj['t_id'],obj['u_id']) for obj in allobj if obj['s_class'] in [0,1]]
                    documents = get_unique_list(documents,2) # u_id重複削除
                    documents = [(doc[0],doc[1]) for doc in documents]    
                # 前処理＋主語・述語が含まれる投稿にしぼる
                tagger = MeCab.Tagger(r'-u C:\Users\yusuk\wikidump_20220429.dic')
                docs_cleaned = []
                for d in documents:
                    tmp = cleaning(d, tagger) # tupleで返却される
                    if tmp != None:
                        docs_cleaned.append(tmp)
                #documents = [cleaning(d, tagger) for d in documents] # 前処理
                docs_cleaned = get_unique_list(docs_cleaned,0)
                
                numd = len(docs_cleaned)
                print('docs_cleaned len:',numd)
                
                if numd < 30:
                    print('No enough data.')
                    sim_texts = [None for i in range(20)]

                else:
                    docs_cleaned = docs_cleaned[:10000] #3万程度でメモリ爆発する
                    sim_texts = summary_cos.get_sim(docs_cleaned, cos = 0.45, dup_degree = 0.2, t_id=True)
    
                    topics = summary_cos.get_topics(sim_texts, cos= 0.6, dup_degree = 0.2)
    
                    for i,topic in enumerate(topics):
                        sim_texts[i] = [topic] + sim_texts[i]
                    # topicがないグループは除く
                    sim_texts = [sim_text for sim_text in sim_texts if sim_text[0] != '']
                    sim_texts = sim_texts[:20] # top20
                    
                    # 20に満たない場合はNoneで埋める
                    sim_length = len(sim_texts)

                    for k in range(20 - sim_length):
                        sim_texts.append(None)
                
                sim_texts_all += sim_texts
                
                
            '''
            # tweetdata2　テーブル更新
            all_ids = [obj['t_id'] for obj in allobj]
            
            summary_no_updates = []
            for i in all_ids:
                breakflag = False
                for k,sim_text in enumerate(sim_texts_all):
                    for sim in sim_text[1:]: # 0番目は要約のみ,1番目以降に(tweet,id)～
                        if i == sim[1]:
                            summary_no_updates.append(k + 1)
                            breakflag = True
                            break
                    if breakflag == True:
                        break
                if breakflag == False:
                    summary_no_updates.append(0)
                    
    
            update_list = []
            for summary_no_update,obj in zip(summary_no_updates,data):
               
                obj.summary_no = summary_no_update
                update_list.append(obj)
    
            print('bulk update..')
            # コピーを取得した時と同じ順序でないと正しい順番でbulk updateできない
            data.bulk_update(update_list,
                             fields=['summary_no',
                                     ],
                             batch_size=5000
                             )
            
            best_summarys = [sim_text[0] for sim_text in sim_texts]
            
            '''    

            # tweetdata2　テーブル更新(bulk updateなし)
            best_summarys = []
            for i,sim_text in enumerate(sim_texts_all):
                if sim_text == None:
                    best_summarys.append(None)
                    continue
                else:
                    best_summarys.append(sim_text.pop(0))
                # summary_no 更新
                for sim in sim_text:
                    obj = Tweetdata2.objects.get(t_id = sim[1])
                    obj.summary_brand_id = target_no
                    obj.summary_no = i + 1
                    obj.save()
                    

                    
            # Summary テーブル更新
            print("Summarys update..")
    
            obj, created = Summarys.objects.update_or_create(
                        official_name_id = target_no,
                        defaults={
                        'summary_text1' : best_summarys[0],
                        'summary_text2' : best_summarys[1],
                        'summary_text3' : best_summarys[2],
                        'summary_text4' : best_summarys[3],
                        'summary_text5' : best_summarys[4],            
                        'summary_text6' : best_summarys[5],
                        'summary_text7' : best_summarys[6],
                        'summary_text8' : best_summarys[7],
                        'summary_text9' : best_summarys[8],
                        'summary_text10' : best_summarys[9],
                        'summary_text11' : best_summarys[10],
                        'summary_text12' : best_summarys[11],
                        'summary_text13' : best_summarys[12],
                        'summary_text14' : best_summarys[13],
                        'summary_text15' : best_summarys[14],
                        'summary_text16' : best_summarys[15],
                        'summary_text17' : best_summarys[16],
                        'summary_text18' : best_summarys[17],
                        'summary_text19' : best_summarys[18],
                        'summary_text20' : best_summarys[19],
                        #以下nega
                        'summary_text21' : best_summarys[20],
                        'summary_text22' : best_summarys[21],
                        'summary_text23' : best_summarys[22],
                        'summary_text24' : best_summarys[23],
                        'summary_text25' : best_summarys[24],            
                        'summary_text26' : best_summarys[25],
                        'summary_text27' : best_summarys[26],
                        'summary_text28' : best_summarys[27],
                        'summary_text29' : best_summarys[28],
                        'summary_text30' : best_summarys[29],
                        'summary_text31' : best_summarys[30],
                        'summary_text32' : best_summarys[31],
                        'summary_text33' : best_summarys[32],
                        'summary_text34' : best_summarys[33],
                        'summary_text35' : best_summarys[34],
                        'summary_text36' : best_summarys[35],
                        'summary_text37' : best_summarys[36],
                        'summary_text38' : best_summarys[37],
                        'summary_text39' : best_summarys[38],
                        'summary_text40' : best_summarys[39],
                        }
                        )
            if created == True:
                print("added new record.")
            else:
                print("updated record.")
                
            print('all done:{0}'.format(target_no))        
      
        
      
        
      
        
        '''
    # 要約取得
        print("take summarys..")
        documents = [(obj['content'],obj['t_id']) for obj in allobj if obj['s_class'] == 4]
        documents = [(cleaning(d[0]),d[1]) for d in documents] # 前処理
        documents = [d for d in documents if len(d[0])<=80]
        documents = get_unique_list(documents,0)
        
        if documents == None:
            print('No p2 data.')
            continue
        
        numd = len(documents)
        print('len(p2):',numd)

        if len(documents) == 0:
            print('No p2 data.')
            continue
        else:
            
            if numd > 1000:
                random.shuffle(documents)
                documents = documents[:500]
            elif numd < 100:
                # p2少ない場合p1も合わせる
                documents_p1 = [(obj['content'],obj['t_id']) for obj in allobj if obj['s_class'] == 3]
                #documents_p1 = data.filter(s_class=3).values_list('content', 't_id') # タプルで返却される

                documents_p1 = [(cleaning(d[0]),d[1]) for d in documents_p1] # 前処理
                documents_p1 = [d for d in documents_p1 if len(d[0])<=80]
                documents_p1 = get_unique_list(documents_p1,0)
                if documents_p1 == None:
                    return 'No p1&p2 data.'
                print('len(p1):',len(documents_p1))
                documents += documents_p1
                random.shuffle(documents)                
                documents = documents[:500]
                numd = len(documents)
                if numd == 0:
                    return 'No p1&p2 data.'
        
            num_topics = round(math.log(numd,5))
            tmp_summarys = []
            for i in range(1): # 仮で1回.最終的には3回実施に変更
                print('{0}回目取得開始'.format(i+1))
                result = take_summary(keywords,documents,maxlength=50,num_topics=num_topics,num_summary=5)
                if len(result) > 0:
                    tmp_summarys.append(result)
           
            summarys = [s for s in tmp_summarys if len(s) >= 3] # 要約数は最低3つ

            if len(summarys) == 0: # 最低３つ無ければ要約数の条件なし
                summarys = tmp_summarys

            # 最大投稿数を持つ要約を選ぶ    
            max_posts = 0
            best_summarys = []
            for summary in summarys:
                num_posts = sum([s['投稿数'] for s in summary])
                if num_posts > max_posts:
                    best_summarys = summary
                    max_posts = num_posts
        print('bestsummarys:')
        pprint.pprint(best_summarys)
        print('max_posts:',max_posts)
    
        # t_id取得    
        t_ids = [obj['t_id'] for obj in allobj] 
        #t_ids = list(data.values_list("t_id", flat=True))
        
        summary_no_updates =[]
        #summary_text_updates = []
        for t_id in t_ids:
            breakflag = False
            for k,best_summary in enumerate(best_summarys):
                for org in best_summary['原文']:
                    if t_id == org[1]:
                        summary_no_updates.append(k+1)
                        #summary_text_updates.append(best_summary['要約'])
                        breakflag = True
                        break
                if breakflag == True:
                    break
            if breakflag == False: # 要約ではない投稿の場合
                summary_no_updates.append(0)
                #summary_text_updates.append(None)            
                
        if len([s for s in summary_no_updates if s > 0]) != max_posts:
            return 'ERROR!(id numbers:{0} does not match with summary numbers)'.format(len([s for s in summary_no_updates if s > 0]))
        if len(data) != len(summary_no_updates):
            return 'ERROR!(summary_update != data)'
        
        print("DB update..")
        update_list = []
        print("making update_list..")
        
        for summary_no_update,obj in zip(summary_no_updates,data):
           
            obj.summary_no = summary_no_update
            update_list.append(obj)
    
        print('done.')
        print('bulk update..')
        # コピーを取得した時と同じ順序でないと正しい順番でbulk updateできない
        
        data.bulk_update(update_list,
                         fields=['summary_no',
                                 ],
                         batch_size=5000
                         )
        
        print('done.')
        
        # Summary更新
        print("Summarys update..")

        obj, created = Summarys.objects.update_or_create(
                    official_name_id = title_no,
                    defaults={
                    'summary_text1' : best_summarys[0]['要約'] if len(best_summarys) >= 1 else None,
                    'summary_text2' : best_summarys[1]['要約'] if len(best_summarys) >= 2 else None,
                    'summary_text3' : best_summarys[2]['要約'] if len(best_summarys) >= 3 else None,
                    'summary_text4' : best_summarys[3]['要約'] if len(best_summarys) >= 4 else None,
                    'summary_text5' : best_summarys[4]['要約'] if len(best_summarys) >= 5 else None,
                    'summary_text6' : best_summarys[5]['要約'] if len(best_summarys) >= 6 else None,
                    'summary_text7' : best_summarys[6]['要約'] if len(best_summarys) >= 7 else None,
                    'summary_text8' : best_summarys[7]['要約'] if len(best_summarys) >= 8 else None,
                    'summary_text9' : best_summarys[8]['要約'] if len(best_summarys) >= 9 else None,
                    'summary_text10' : best_summarys[9]['要約'] if len(best_summarys) >= 10 else None,
                    'summary_text11' : best_summarys[10]['要約'] if len(best_summarys) >= 11 else None,
                    'summary_text12' : best_summarys[11]['要約'] if len(best_summarys) >= 12 else None,
                    'summary_text13' : best_summarys[12]['要約'] if len(best_summarys) >= 13 else None,
                    'summary_text14' : best_summarys[13]['要約'] if len(best_summarys) >= 14 else None,
                    'summary_text15' : best_summarys[14]['要約'] if len(best_summarys) >= 15 else None,
                    'summary_text16' : best_summarys[15]['要約'] if len(best_summarys) >= 16 else None,
                    'summary_text17' : best_summarys[16]['要約'] if len(best_summarys) >= 17 else None,
                    'summary_text18' : best_summarys[17]['要約'] if len(best_summarys) >= 18 else None,
                    'summary_text19' : best_summarys[18]['要約'] if len(best_summarys) >= 19 else None,
                    'summary_text20' : best_summarys[19]['要約'] if len(best_summarys) >= 20 else None,
                    }
                    )
        if created == True:
            print("added new record.")
        else:
            print("updated record.")
                
        print('all done:{0}'.format(title_no))
        '''
        
 
        
    return "done."    


def clean_trend():
    ### Tweetdata2からtrendクリア ###
    
    
    dt_now = datetime.datetime.now()
    e_date = datetime.datetime(dt_now.year,
                              dt_now.month, 
                              dt_now.day, 0, 0, 0, 0,tzinfo=datetime.timezone.utc) - datetime.timedelta(hours=9)
    s_date = e_date - datetime.timedelta(days=7)
    
    data = Tweetdata2.objects.filter(Q(spam=False),
                                     Q(t_date__range=[s_date,e_date]),
                                       trend_no__gte=1,
                                       ).only('id','trend_no').order_by('id') #
    print('len(data):',len(data))
    update_list = []
    for obj in data:
       
        obj.trend_no = 0
        update_list.append(obj)
        
    print("deleting tweetdata2 trends..")
    data.bulk_update(update_list,
                    fields=['trend_no',
                            ],
                    batch_size=5000
                    ) 
    print("done.")
    

                                                           
    return 'done.'


def trend_update():

    dt_now = datetime.datetime.now()
    e_date = datetime.datetime(dt_now.year,
                              dt_now.month, 
                              dt_now.day, 0, 0, 0, 0,tzinfo=datetime.timezone.utc) - datetime.timedelta(hours=9)
    s_date = e_date - datetime.timedelta(days=7)
    print('date:{0}-{1}'.format(s_date,e_date))  

    # 全キャラ名取得
    keywords = list(Keywords.objects.all().values_list('keyword', flat=True))
    print('keywords:',keywords)
    print("done.")
    
    title_nos = list(Official_names.objects.filter(title=True,index__gte=1).values_list('index',flat=True))
    chara_nos = list(Official_names.objects.filter(title=False,index__gte=1).values_list('index',flat=True))
    print('titles:',title_nos)
    print('charas',chara_nos)


    for cnt in range(2):
        if cnt == 0:
            target_nos = title_nos
        else:
            target_nos = chara_nos
                
        for target_no in target_nos:
            print("accesing DB:{0}".format(target_no))
                #DBから本文取得
            if cnt == 0:
                data = Tweetdata2.objects.filter(Q(spam=False),
                                                 Q(trend_no=0),
                                                 Q(s_class=0) | Q(s_class=1) | Q(s_class=3) | Q(s_class=4),
                                                 Q(t_date__range=[s_date,e_date]),
                                                 Q(title1=target_no) | Q(title2=target_no) | Q(title3=target_no),
                                                   ).only('id',
                                                          't_id',
                                                          'hashtag',
                                                          'trend_no',
                                                          ).order_by('id') # 何らかのキーで並び替えないとbulk updateが正しい順序でupdateできないらしい
            else:
                data = Tweetdata2.objects.filter(Q(spam=False),
                                                 Q(trend_no=0),
                                                 Q(s_class=0) | Q(s_class=1) | Q(s_class=3) | Q(s_class=4),
                                                 Q(t_date__range=[s_date,e_date]),
                                                 Q(character1=target_no) | Q(character2=target_no) | Q(character3=target_no) | Q(character4=target_no) | Q(character5=target_no),
                                                   ).only('id',
                                                          't_id',
                                                          'hashtag',
                                                          'trend_no',
                                                          ).order_by('id') # 何らかのキーで並び替えないとbulk updateが正しい順序でupdateできないらしい
        
                                                          
                                                      
            allobj = list(data.values())                                                  
            print("done. len:{0}".format(len(allobj)))
        
            # trend取得
            print("take trends..")
    
            # ハッシュタグ取得    
            hashtags = [(obj['t_id'],obj['hashtag']) for obj in allobj]
            # hashtags=[(id,'[a]'),(id2,'[a,b]'),...] 各要素はstrなのでリストに戻す
            
            hashtags_list=[]
    
            for h in hashtags:
            
                if h[1] != str([]): # 初期データはハッシュタグ None
                                         ## 空欄と"'"は除外(ハッシュタグ途中に出現した場合？)
                    li = h[1].replace("'","").replace(" ","")[1:-1].split(",")
                    li = [l for l in li if len(l) <= 30] # modelは30字未満
                    
                    hashtags_list.append((h[0],li))
    
                else:
                    continue
    
            # hashtagsを展開して1次元リスト化、要素カウント        
            c = collections.Counter(list(itertools.chain.from_iterable([h[1] for h in hashtags_list])))
            trend_words=[]
    
            # 一旦top10のみ表示
            ## トレンド10個未満の場合
            if len(c)<10:
                pass
            else:
                for i in range(10): 
                    # top10に該当するt_id取得
                    update_ids = []
                    for h in hashtags_list:
                        if c.most_common()[i][0] in h[1]:
                            update_ids.append(h[0])
                            
                    trend_words.append((c.most_common()[i][0],update_ids))
            '''
            ##現状tweetdataのtrend_noは未使用。updateはなし
            
            # tweetdata2　テーブル更新
            all_ids = [obj['t_id'] for obj in allobj]
            
            trend_no_updates = []
            for i in all_ids:
                breakflag = False
                for k,trend_word in enumerate(trend_words):
                    if i in trend_word[1]:
                        trend_no_updates.append(k + 1)
                        breakflag = True
                        break
                if breakflag == False:
                    trend_no_updates.append(0)
    
            update_list = []
            for trend_no_update,obj in zip(trend_no_updates,data):
               
                obj.trend_no = trend_no_update
                update_list.append(obj)
        
            print('bulk update..')
            # コピーを取得した時と同じ順序でないと正しい順番でbulk updateできない
            data.bulk_update(update_list,
                             fields=['trend_no',
                                     ],
                             batch_size=5000
                             )
            
            #print("trendwords",trend_words)                    
            '''
            # Summary テーブル更新
            print("Trends update..")
    
            obj, created = Trends.objects.update_or_create(
                        official_name_id = target_no,
                        defaults={
                        'trend1' : trend_words[0][0] if len(trend_words) >= 1 else None,
                        'trend1_count' : len(trend_words[0][1]) if len(trend_words) >= 1 else None,
                        'trend2' : trend_words[1][0] if len(trend_words) >= 2 else None,
                        'trend2_count' : len(trend_words[1][1]) if len(trend_words) >= 2 else None,
                        'trend3' : trend_words[2][0] if len(trend_words) >= 3 else None,
                        'trend3_count' : len(trend_words[2][1]) if len(trend_words) >= 3 else None,
                        'trend4' : trend_words[3][0] if len(trend_words) >= 4 else None,
                        'trend4_count' : len(trend_words[3][1]) if len(trend_words) >= 4 else None,
                        'trend5' : trend_words[4][0] if len(trend_words) >= 5 else None,
                        'trend5_count' : len(trend_words[4][1]) if len(trend_words) >= 5 else None,
                        'trend6' : trend_words[5][0] if len(trend_words) >= 6 else None,
                        'trend6_count' : len(trend_words[5][1]) if len(trend_words) >= 6 else None,
                        'trend7' : trend_words[6][0] if len(trend_words) >= 7 else None,
                        'trend7_count' : len(trend_words[6][1]) if len(trend_words) >= 7 else None,
                        'trend8' : trend_words[7][0] if len(trend_words) >= 8 else None,
                        'trend8_count' : len(trend_words[7][1]) if len(trend_words) >= 8 else None,
                        'trend9' : trend_words[8][0] if len(trend_words) >= 9 else None,
                        'trend9_count' : len(trend_words[8][1]) if len(trend_words) >= 9 else None,
                        'trend10' : trend_words[9][0] if len(trend_words) >= 10 else None,
                        'trend10_count' : len(trend_words[9][1]) if len(trend_words) >= 10 else None,
                        }
                        )
            if created == True:
                print("added new record.")
            else:
                print("updated record.")
                
            print('all done:{0}'.format(target_no))        
      
    


def make_wordcloud():

    
    dt_now = datetime.datetime.now()
    e_date = datetime.datetime(dt_now.year,
                              dt_now.month, 
                              dt_now.day, 0, 0, 0, 0,tzinfo=datetime.timezone.utc) - datetime.timedelta(hours=9)
    s_date = e_date - datetime.timedelta(days=7)
    print('date:{0}-{1}'.format(s_date,e_date))  
    
    title_nos = list(Official_names.objects.filter(title=True,index__gte=1).values_list('index','official_name'))
    chara_nos = list(Official_names.objects.filter(title=False,index__gte=1).values_list('index','official_name'))
    print('titles:',title_nos)
    print('charas',chara_nos) 

    
    for cnt in range(2):
        if cnt == 0:
            target_nos = title_nos
        else:
            target_nos = chara_nos
                
        for target_no in target_nos:
            
            print("making wordcloud:{0}".format(target_no[1]))
                #DBから本文取得
            
            if cnt == 0:
                data = Tweetdata2.objects.filter(Q(spam=False),
                                                 Q(t_date__range=[s_date,e_date]),
                                                 Q(s_class=0) | Q(s_class=1) | Q(s_class=3) | Q(s_class=4),
                                                 Q(title1=target_no[0]) | Q(title2=target_no[0]) | Q(title3=target_no[0]),
                                                   ).only('id',
                                                          's_class',
                                                          'wakachi'
                                                          ).order_by('id') # 何らかのキーで並び替えないとbulk updateが正しい順序でupdateできないらしい
            else:
                data = Tweetdata2.objects.filter(Q(spam=False),
                                                 Q(t_date__range=[s_date,e_date]),
                                                 Q(s_class=0) | Q(s_class=1) | Q(s_class=3) | Q(s_class=4),
                                                 Q(character1=target_no[0]) | Q(character2=target_no[0]) | Q(character3=target_no[0]) | Q(character4=target_no[0]) | Q(character5=target_no[0]),
                                                   ).only('id',
                                                          's_class',
                                                          'wakachi'
                                                          ).order_by('id') # 何らかのキーで並び替えないとbulk updateが正しい順序でupdateできないらしい
    
                                                      
            allobj = list(data.values())                                                  
            print("done. len:{0}".format(len(allobj)))
        # wordcloud
            print("making wordcloud..")
            wakachi = [obj['wakachi'] for obj in allobj if obj['wakachi'] != None]
        
            if len(wakachi) < 50:
                print("投稿不足")
                continue
                
            else:
                # マスクを作成する
                #path = r'static\sentiment\image\wordcloud\{0}.png'.format(anime)
                if cnt == 0:
                    path = os.path.join(BASE_DIR, 'static\image\wordcloud\org_anime\{0}.png'.format(target_no[1]))
                else:
                    path = os.path.join(BASE_DIR, 'static\image\wordcloud\org_character\{0}.png'.format(target_no[1]))
    
                try:
                    mask_array = np.array(Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),path)))
                except FileNotFoundError as e:
                    print(e)
                    mask_array = None
                # ↓まとまったらlabelsaveに移動
                adj_stopwords = ['多い','少ない','まじ','マジ','可能','大変','よろしい','宜しい','気軽','幸い','失礼','ぽい','うい','欲しい','やすい','づらい','にくい','ない','無い','いい','良い','よい','やばい','っぽい'] 
                noun_stopwords = ['アマプラ','特典','ガン','次','回','御伽','キャンペーン','全巻','アニメ','漫画','単品','月額','感想','円','出し手','感じ','自分','私','僕','コミック','キャラ','子','人','定期','作品','ランキング','ネトフリ','なじみ','気','あと']
                #wordcloud = WordCloud(mask=mask_array, background_color='white', colormap='bone', contour_width=3, contour_color='gray')        
                wordcloud = WordCloud(colormap='brg',
                                      width=400,
                                      height=400,
                                      min_font_size=9,
                                      max_words=50,
            
                                      contour_width=0.001,
                                      contour_color='powderblue',
                                      font_path=r"C:/Users/yusuk/AppData/Local/Microsoft/Windows/Fonts/NotoSansJP-Light.otf",
                                      mask=mask_array,
                                      background_color='white',
                                      stopwords=adj_stopwords + noun_stopwords,
                                      collocations=False)
                
                wordcloud = wordcloud.generate(' '.join(wakachi))
                # file保存
                #ftime = re.sub("[- :\.]","_",str(datetime.datetime.now()))
                fname = '{0}_wc'.format(target_no[1])
                fname = r'{0}.png'.format(fname)
                #print('fname:',fname)
                #print('aa:',r'sentiment\image\wordcloud\anime\png\{0}'.format(fname))
                if cnt == 0:
                    wordcloud = wordcloud.to_file(os.path.join(BASE_DIR, r'static\image\wordcloud\result\anime\png\{0}'.format(fname)))
                else:
                    wordcloud = wordcloud.to_file(os.path.join(BASE_DIR, r'static\image\wordcloud\result\character\png\{0}'.format(fname)))
                
                '''
                # PILで表示する
                image_array = wordcloud.to_array()
                img = Image.fromarray(image_array)
                
                buf = io.BytesIO()
                img.save(buf,format='png')
                s = buf.getvalue()
                s = base64.b64encode(s).decode()
                buf.close()
                plt.cla()
                fname = s
                '''

    return "success."  


PREF = [re.compile('北海道|札幌|hokkaido|sapporo'),re.compile('青森|aomori'),re.compile('岩手|盛岡|iwate|morioka'),re.compile('宮城|仙台|miyagi|sendai'),re.compile('秋田|akita'),re.compile('山形|yamagata'),re.compile('福島|fukushima'),re.compile('茨城|水戸|ibaraki|mito'),re.compile('栃木|宇都宮|tochigi|utunomiya'),re.compile('群馬|前橋|gunma|maebashi'),re.compile('埼玉|さいたま|saitama'),re.compile('千葉|chiba'),re.compile('東京|tokyo|新宿|渋谷|千代田区|世田谷区'),re.compile('神奈川|横浜|kanagawa|yokohama'),re.compile('新潟|niigata'),re.compile('富山|toyama'),re.compile('石川|金沢|ishikawa|kanazawa'),re.compile('福井|fukui'),re.compile('山梨|甲府|yamanashi|kofu'),re.compile('長野|nagano'),re.compile('岐阜|gihu'),re.compile('静岡|shizuoka'),re.compile('愛知|名古屋|aichi|nagoya'),re.compile('三重|mie|tsu'),re.compile('滋賀|大津|shiga|otsu'),re.compile('京都|kyoto'),re.compile('大阪|osaka'),re.compile('兵庫|神戸|hyogo'),re.compile('奈良|nara'),re.compile('和歌山|wakayama'),re.compile('鳥取|tottori'),re.compile('島根|松江|shimane|matsue'),re.compile('岡山|okayama'),re.compile('広島|hiroshima'),re.compile('山口|yamaguchi'),re.compile('徳島|tokushima'),re.compile('香川|高松|kagawa|takamatsu'),re.compile('愛媛|松山|ehime|matsuyama'),re.compile('高知|kouchi'),re.compile('福岡|fukuoka'),re.compile('佐賀|saga'),re.compile('長崎|nagasaki'),re.compile('熊本|kumamoto'),re.compile('大分|oita'),re.compile('宮崎|miyazaki'),re.compile('鹿児島|kagoshima'),re.compile('沖縄|那覇|okinawa|naha'),re.compile('関東|kanto'),re.compile('関西|kansai'),re.compile('東北|tohoku'),re.compile('四国|shokoku'),re.compile('九州|kyushu'),re.compile('日本|japan'),re.compile('世界|world'),re.compile('地球|earth'),re.compile('宇宙|universe')]               
        
def prefectures_update():
    
    print("accessing the spreadsheet..",end='')
    gc = gspread.service_account()
    #ファイルオープン
    sh = gc.open_by_key('1b-89Ynrpek39vny4sPfkaYqNp-WYLZJ6txAjaEAld9I') # anime_keywords
    worksheet = sh.worksheet('pref')

    
    # pref
    indexes = [i for i in worksheet.col_values(1)]
    indexes.pop(0)
    prefectures = [i for i in worksheet.col_values(2)]
    prefectures.pop(0)    
    
    print(prefectures)
  
    print("deleting DB..")
    
    Prefectures.objects.all().delete()
    
    print("done.")
    
    print('bulk update..')                                              
    update_list = []
    for index,pref in zip(indexes,prefectures):
        update_list.append(Prefectures(prefecture = pref,
                                       id = index,
                                          ))

        
    Prefectures.objects.bulk_create(update_list)


    print("done.")


    return 'success.'
    
def set_prefectures():

    dt_now = datetime.datetime.now()
    e_date = datetime.datetime(dt_now.year,
                              dt_now.month, 
                              dt_now.day, 0, 0, 0, 0,tzinfo=datetime.timezone.utc) - datetime.timedelta(hours=9)
    s_date = e_date - datetime.timedelta(days=7)
    print('date:{0}-{1}'.format(s_date,e_date))  



    
    data = Tweetdata2.objects.filter(Q(spam=False),
                                     Q(t_date__range=[s_date,e_date]),
                                     # title1のみ（他も見ると複数アニメの要約が一緒になってしまう
                                       ).only('id',
                                              'location',
                                              'prefecture'
                                              ).order_by('id') # 何らかのキーで並び替えないとbulk updateが正しい順序でupdateできないらしい

                                              
    allobj = list(data.values())                                                  
    print("done. len:{0}".format(len(allobj)))

# prefecture取得
    locations =  [obj['location'] for obj in allobj if obj['location'] != None]    
    print(locations[:100])
    print("getting prefs..")
    pref_ids=[]
    for loc in locations:
        if loc in ["",None]:
            pref_ids.append(None)
            continue
        loc = loc.lower()
        for k,p in enumerate(PREF):
            if p.search(loc):
                pref_ids.append(k+1)
                break
            if k + 1 == len(PREF):
                # 何も該当しない場合
                pref_ids.append(None)
        
    print('done.')
    
    print('bulk update..')
    update_list = []
    for pref_id, obj in zip(pref_ids,data):
        obj.prefecture = pref_id
        update_list.append(obj)

    data.bulk_update(update_list,
                     fields=['prefecture'
                             ],
                     batch_size=5000
                     )        
    print('done.')
    return 'success.'


if __name__=='__main__':

    days = int(input("days:"))
    '''
    # 一覧表更新
    msg = official_names_update()
    print(msg)
    msg = keywords_update()
    print(msg)
    
    
    
    # ラベル、スパム,title,chara,形態素更新
    msg=dataupdate(days) 
    print(msg)
    
    # 1週間統計作成(要約以外)
    msg=statistics_update()
    print(msg)
    '''
    #要約作成
    msg=clean_summary()
    print(msg)
    
    msg=sumupdate()
    print(msg)
    
    #trend作成
    msg=clean_trend()
    print(msg)
    
    msg=trend_update()
    print(msg)
    
    # wordcloudイメージ作成
    msg=make_wordcloud()
    print(msg)
    
    
    #msg=prefectures_update()
    #print(msg)
    
    
    msg=set_prefectures()
    print(msg)
    
