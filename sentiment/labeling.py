# coding: UTF-8

#from models import Tweetdata
#import classifier_sub
#import numpy as np
import tokenizer

import os, sys, django
sys.path.append('/home/yusuke/pydir/purakome')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')  # DJANGO_SETTINGS_MODULEにプロジェクトのsettings.pyのを指定します。
django.setup()

from sentiment.models import Tweetdata2,Statistics1week,Official_names,Keywords,Prefectures,Summarys,Trend_ranks,Pref_ranks,Frequentwords,Longevents,Abouts,Oadates,Fanarts # 利用したいモデルをインポートします。
from django.utils import timezone
from django.utils.text import slugify

# 日付の警告を無視
import warnings
warnings.filterwarnings('ignore')
from django.db.models import Q,Max
# id重複取得エラー
from django.db.utils import IntegrityError
import re

import datetime
#import MeCab
import itertools
import neologdn,unicodedata

import pprint
import random
import csv
#wordcloud
#from wordcloud import WordCloud
#from PIL import Image

# summary cos
#import summary_cos

import collections

# bert
#from transformers import pipeline, AutoTokenizer,AutoModelForSequenceClassification,BertTokenizer


import gspread
CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET =os.environ.get('CONSUMER_SECRET')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))# dkango_app/

class JST(datetime.tzinfo):
    def __repr__(self):
        return self.tzname(self)

    def utcoffset(self, dt):
        # ローカル時刻とUTCの差分に等しいtimedeltaを返す
        return datetime.timedelta(hours=9)

    def tzname(self, dt):
        # タイムゾーン名を返す
        return 'Asia/Tokyo'

    def dst(self, dt):
        # 夏時間を返す。有効でない場合はtimedelta(0)を返す
        return datetime.timedelta(0)





def get_unique_list(seq,index):
    """リスト(タプル)のリストで入れ子のindex番目の要素の重複を削除する
    例：i==0 [(1,2),(3,4),(1,3)]→[(1,2),(3,4)]
       i==1 [(1,2),(3,4),(2,2)]→[(1,2),(3,4)]
    """
    if len(seq) == 0:
        return []
    if index + 1 > len(seq[0]):
        print("index error(index is over than len(seq).)")
        return []

    seen = []
    return [x for x in seq if x[index] not in seen and not seen.append(x[index])]


def keywords_update():

    print("accessing the spreadsheet..",end='')
    gc = gspread.service_account()
    #ファイルオープン
    sh = gc.open_by_key('1b-89Ynrpek39vny4sPfkaYqNp-WYLZJ6txAjaEAld9I') # anime_keywords
    worksheet = sh.worksheet('index_summary')

    tmp = worksheet.col_values(1)
    tmp.pop(0)
    indexes = [int(i) for i in tmp]

    list_of_dicts = worksheet.get_all_records()

    for d in list_of_dicts:
        # keywordはカンマ区切りで複数あり
        ## 正規化して保存 (neologdn入れると日本語間のスペースが消える)
        d['keyword'] = unicodedata.normalize('NFKC',d['keyword'].lower()).strip().split(',') if d['keyword'] != '' else None
        d['i_keyword'] = unicodedata.normalize('NFKC',d['i_keyword'].lower()).strip().split(',') if d['i_keyword'] != '' else None

    if len(list_of_dicts) != len(indexes):
        return 'error: index!=list of dicts.'


    pairs = [(i,d['keyword'],d['i_keyword']) for i,d in zip(indexes,list_of_dicts)] # キーワード空欄(欠番)は除外


    print("deleting DB..")

    Keywords.objects.all().delete()


    print("done.")

    print('bulk update..')
    update_list = []
    for pair in pairs:
        if pair[1] != None:
            for key in pair[1]:
                update_list.append(Keywords(official_name_id = pair[0],
                                                 #正規表現の場合reprを使いraw文字列として保存する
                                                  keyword = key if key[0] != '|' else repr(key[1:]),
                                                  domestic = False
                                                  ))
        if pair[2] != None:
            for d_key in pair[2]:
                update_list.append(Keywords(official_name_id = pair[0],
                                                  keyword = d_key if d_key[0] != '|' else repr(d_key[1:]),
                                                  domestic = True
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

    list_of_dicts = worksheet.get_all_records()


    if len(list_of_dicts) != len(indexes):
        return 'error: index!=list of dicts.'

 
    
    for index,d in zip(indexes,list_of_dicts):
        obj, created = Official_names.objects.update_or_create(
            index = index,

            defaults={
                'kind' : int(d['title']),
                'url_name' : str(d['url']).strip(),
                'official_name' : str(d['official-name']).strip(),
                'title_name' : str(d['title-name']).strip(),
                'hidden' : True if d['hidden'] == 'TRUE' else False,
                'past' : True if d['END'] == 'TRUE' else False,
                'short_name' : str(d['short-name']).strip(),
                'series' : True if d['SERIES'] == 'TRUE' else False,
                'quiz_key' : str(d['quiz_keyword']) if d['quiz_keyword'] else None,

            }
        )
    


    print("done.")

    return 'success.'


def StrtoAwaretime(text):
    """ textは%Y/%m/%d %H:%M:%Sの形式"""

    return datetime.datetime.strptime(text,'%Y/%m/%d %H:%M:%S').replace(tzinfo=JST())


def Oadates_update():
    """ anime,johnnys両方のupdate"""

    
    print("accessing the spreadsheet..",end='')
    gc = gspread.service_account()
    #ファイルオープン
    sh = gc.open_by_key('1b-89Ynrpek39vny4sPfkaYqNp-WYLZJ6txAjaEAld9I') # anime_keywords

    worksheet_anime = sh.worksheet('anime_index')
    anime_dicts = worksheet_anime.get_all_records()
    
    worksheet_johnnys = sh.worksheet('johnnys_index')
    johnnys_dicts = worksheet_johnnys.get_all_records()



    # 正規化
    for d in anime_dicts:
        d['OA1'] = StrtoAwaretime(d['OA1'].strip()) if d['OA1'] != '' else None
        d['OA2'] = StrtoAwaretime(d['OA2'].strip()) if d['OA2'] != '' else None
        d['OA3'] = StrtoAwaretime(d['OA3'].strip()) if d['OA3'] != '' else None
        d['OA4'] = StrtoAwaretime(d['OA4'].strip()) if d['OA4'] != '' else None
        d['OA5'] = StrtoAwaretime(d['OA5'].strip()) if d['OA5'] != '' else None
        d['OA6'] = StrtoAwaretime(d['OA6'].strip()) if d['OA6'] != '' else None
        d['OA7'] = StrtoAwaretime(d['OA7'].strip()) if d['OA7'] != '' else None
        d['OA8'] = StrtoAwaretime(d['OA8'].strip()) if d['OA8'] != '' else None
        d['OA9'] = StrtoAwaretime(d['OA9'].strip()) if d['OA9'] != '' else None
        d['OA10'] = StrtoAwaretime(d['OA10'].strip()) if d['OA10'] != '' else None
        d['OA11'] = StrtoAwaretime(d['OA11'].strip()) if d['OA11'] != '' else None
        d['OA12'] = StrtoAwaretime(d['OA12'].strip()) if d['OA12'] != '' else None
        d['OA13'] = StrtoAwaretime(d['OA13'].strip()) if d['OA13'] != '' else None
        d['OA14'] = StrtoAwaretime(d['OA14'].strip()) if d['OA14'] != '' else None
        d['OA15'] = StrtoAwaretime(d['OA15'].strip()) if d['OA15'] != '' else None
        d['OA16'] = StrtoAwaretime(d['OA16'].strip()) if d['OA16'] != '' else None
        d['OA17'] = StrtoAwaretime(d['OA17'].strip()) if d['OA17'] != '' else None
        d['OA18'] = StrtoAwaretime(d['OA18'].strip()) if d['OA18'] != '' else None
        d['OA19'] = StrtoAwaretime(d['OA19'].strip()) if d['OA19'] != '' else None
        d['OA20'] = StrtoAwaretime(d['OA20'].strip()) if d['OA20'] != '' else None
        d['OA21'] = StrtoAwaretime(d['OA21'].strip()) if d['OA21'] != '' else None
        d['OA22'] = StrtoAwaretime(d['OA22'].strip()) if d['OA22'] != '' else None
        d['OA23'] = StrtoAwaretime(d['OA23'].strip()) if d['OA23'] != '' else None
        d['OA24'] = StrtoAwaretime(d['OA24'].strip()) if d['OA24'] != '' else None
        d['OA25'] = StrtoAwaretime(d['OA25'].strip()) if d['OA25'] != '' else None
        d['OA26'] = StrtoAwaretime(d['OA26'].strip()) if d['OA26'] != '' else None
        d['OA27'] = StrtoAwaretime(d['OA27'].strip()) if d['OA27'] != '' else None
        d['OA28'] = StrtoAwaretime(d['OA28'].strip()) if d['OA28'] != '' else None
        d['OA29'] = StrtoAwaretime(d['OA29'].strip()) if d['OA29'] != '' else None
        d['OA30'] = StrtoAwaretime(d['OA30'].strip()) if d['OA30'] != '' else None
    #datetime.datetime.strptime(d['OA1'].strip(),'%Y/%m/%d %H:%M:%S').replace(tzinfo=JST())
#    print(datetime.datetime.strptime(list_of_dicts[134]['OA1'],'%Y/%m/%d %H:%M:%S').replace(tzinfo=JST()))
        d['episode1'] = d['episode1'] if d['episode1'] != '' else None
        d['episode2'] = d['episode2'] if d['episode2'] != '' else None
        d['episode3'] = d['episode3'] if d['episode3'] != '' else None
        d['episode4'] = d['episode4'] if d['episode4'] != '' else None
        d['episode5'] = d['episode5'] if d['episode5'] != '' else None
        d['episode6'] = d['episode6'] if d['episode6'] != '' else None
        d['episode7'] = d['episode7'] if d['episode7'] != '' else None
        d['episode8'] = d['episode8'] if d['episode8'] != '' else None
        d['episode9'] = d['episode9'] if d['episode9'] != '' else None
        d['episode10'] = d['episode10'] if d['episode10'] != '' else None
        d['episode11'] = d['episode11'] if d['episode11'] != '' else None
        d['episode12'] = d['episode12'] if d['episode12'] != '' else None
        d['episode13'] = d['episode13'] if d['episode13'] != '' else None
        d['episode14'] = d['episode14'] if d['episode14'] != '' else None
        d['episode15'] = d['episode15'] if d['episode15'] != '' else None
        d['episode16'] = d['episode16'] if d['episode16'] != '' else None
        d['episode17'] = d['episode17'] if d['episode17'] != '' else None
        d['episode18'] = d['episode18'] if d['episode18'] != '' else None
        d['episode19'] = d['episode19'] if d['episode19'] != '' else None
        d['episode20'] = d['episode20'] if d['episode20'] != '' else None
        d['episode21'] = d['episode21'] if d['episode21'] != '' else None
        d['episode22'] = d['episode22'] if d['episode22'] != '' else None
        d['episode23'] = d['episode23'] if d['episode23'] != '' else None
        d['episode24'] = d['episode24'] if d['episode24'] != '' else None
        d['episode25'] = d['episode25'] if d['episode25'] != '' else None
        d['episode26'] = d['episode26'] if d['episode26'] != '' else None
        d['episode27'] = d['episode27'] if d['episode27'] != '' else None
        d['episode28'] = d['episode28'] if d['episode28'] != '' else None
        d['episode29'] = d['episode29'] if d['episode29'] != '' else None
        d['episode30'] = d['episode30'] if d['episode30'] != '' else None

        d['outline1'] = d['outline1'] if d['outline1'] != '' else None
        d['outline2'] = d['outline2'] if d['outline2'] != '' else None
        d['outline3'] = d['outline3'] if d['outline3'] != '' else None
        d['outline4'] = d['outline4'] if d['outline4'] != '' else None
        d['outline5'] = d['outline5'] if d['outline5'] != '' else None
        d['outline6'] = d['outline6'] if d['outline6'] != '' else None
        d['outline7'] = d['outline7'] if d['outline7'] != '' else None
        d['outline8'] = d['outline8'] if d['outline8'] != '' else None
        d['outline9'] = d['outline9'] if d['outline9'] != '' else None
        d['outline10'] = d['outline10'] if d['outline10'] != '' else None
        d['outline11'] = d['outline11'] if d['outline11'] != '' else None
        d['outline12'] = d['outline12'] if d['outline12'] != '' else None
        d['outline13'] = d['outline13'] if d['outline13'] != '' else None
        d['outline14'] = d['outline14'] if d['outline14'] != '' else None
        d['outline15'] = d['outline15'] if d['outline15'] != '' else None
        d['outline16'] = d['outline16'] if d['outline16'] != '' else None
        d['outline17'] = d['outline17'] if d['outline17'] != '' else None
        d['outline18'] = d['outline18'] if d['outline18'] != '' else None
        d['outline19'] = d['outline19'] if d['outline19'] != '' else None
        d['outline20'] = d['outline20'] if d['outline20'] != '' else None
        d['outline21'] = d['outline21'] if d['outline21'] != '' else None
        d['outline22'] = d['outline22'] if d['outline22'] != '' else None
        d['outline23'] = d['outline23'] if d['outline23'] != '' else None
        d['outline24'] = d['outline24'] if d['outline24'] != '' else None
        d['outline25'] = d['outline25'] if d['outline25'] != '' else None
        d['outline26'] = d['outline26'] if d['outline26'] != '' else None
        d['outline27'] = d['outline27'] if d['outline27'] != '' else None
        d['outline28'] = d['outline28'] if d['outline28'] != '' else None
        d['outline29'] = d['outline29'] if d['outline29'] != '' else None
        d['outline30'] = d['outline30'] if d['outline30'] != '' else None
        
    anime_index = [d['title-index'] for d in anime_dicts]

    # 正規化
    for d in johnnys_dicts:
        d['OA1'] = StrtoAwaretime(d['OA1'].strip()) if d['OA1'] != '' else None
        d['OA2'] = StrtoAwaretime(d['OA2'].strip()) if d['OA2'] != '' else None
        d['OA3'] = StrtoAwaretime(d['OA3'].strip()) if d['OA3'] != '' else None
        d['OA4'] = StrtoAwaretime(d['OA4'].strip()) if d['OA4'] != '' else None
        d['OA5'] = StrtoAwaretime(d['OA5'].strip()) if d['OA5'] != '' else None
        d['OA6'] = StrtoAwaretime(d['OA6'].strip()) if d['OA6'] != '' else None
        d['OA7'] = StrtoAwaretime(d['OA7'].strip()) if d['OA7'] != '' else None
        d['OA8'] = StrtoAwaretime(d['OA8'].strip()) if d['OA8'] != '' else None
        d['OA9'] = StrtoAwaretime(d['OA9'].strip()) if d['OA9'] != '' else None
        d['OA10'] = StrtoAwaretime(d['OA10'].strip()) if d['OA10'] != '' else None
        d['OA11'] = StrtoAwaretime(d['OA11'].strip()) if d['OA11'] != '' else None
        d['OA12'] = StrtoAwaretime(d['OA12'].strip()) if d['OA12'] != '' else None
        d['OA13'] = StrtoAwaretime(d['OA13'].strip()) if d['OA13'] != '' else None
        d['OA14'] = StrtoAwaretime(d['OA14'].strip()) if d['OA14'] != '' else None
        d['OA15'] = StrtoAwaretime(d['OA15'].strip()) if d['OA15'] != '' else None
        d['OA16'] = StrtoAwaretime(d['OA16'].strip()) if d['OA16'] != '' else None
        d['OA17'] = StrtoAwaretime(d['OA17'].strip()) if d['OA17'] != '' else None
        d['OA18'] = StrtoAwaretime(d['OA18'].strip()) if d['OA18'] != '' else None
        d['OA19'] = StrtoAwaretime(d['OA19'].strip()) if d['OA19'] != '' else None
        d['OA20'] = StrtoAwaretime(d['OA20'].strip()) if d['OA20'] != '' else None
        d['OA21'] = StrtoAwaretime(d['OA21'].strip()) if d['OA21'] != '' else None
        d['OA22'] = StrtoAwaretime(d['OA22'].strip()) if d['OA22'] != '' else None
        d['OA23'] = StrtoAwaretime(d['OA23'].strip()) if d['OA23'] != '' else None
        d['OA24'] = StrtoAwaretime(d['OA24'].strip()) if d['OA24'] != '' else None
        d['OA25'] = StrtoAwaretime(d['OA25'].strip()) if d['OA25'] != '' else None
        d['OA26'] = StrtoAwaretime(d['OA26'].strip()) if d['OA26'] != '' else None
        d['OA27'] = StrtoAwaretime(d['OA27'].strip()) if d['OA27'] != '' else None
        d['OA28'] = StrtoAwaretime(d['OA28'].strip()) if d['OA28'] != '' else None
        d['OA29'] = StrtoAwaretime(d['OA29'].strip()) if d['OA29'] != '' else None
        d['OA30'] = StrtoAwaretime(d['OA30'].strip()) if d['OA30'] != '' else None
    #datetime.datetime.strptime(d['OA1'].strip(),'%Y/%m/%d %H:%M:%S').replace(tzinfo=JST())
#    print(datetime.datetime.strptime(list_of_dicts[134]['OA1'],'%Y/%m/%d %H:%M:%S').replace(tzinfo=JST()))
        d['episode1'] = d['episode1'] if d['episode1'] != '' else None
        d['episode2'] = d['episode2'] if d['episode2'] != '' else None
        d['episode3'] = d['episode3'] if d['episode3'] != '' else None
        d['episode4'] = d['episode4'] if d['episode4'] != '' else None
        d['episode5'] = d['episode5'] if d['episode5'] != '' else None
        d['episode6'] = d['episode6'] if d['episode6'] != '' else None
        d['episode7'] = d['episode7'] if d['episode7'] != '' else None
        d['episode8'] = d['episode8'] if d['episode8'] != '' else None
        d['episode9'] = d['episode9'] if d['episode9'] != '' else None
        d['episode10'] = d['episode10'] if d['episode10'] != '' else None
        d['episode11'] = d['episode11'] if d['episode11'] != '' else None
        d['episode12'] = d['episode12'] if d['episode12'] != '' else None
        d['episode13'] = d['episode13'] if d['episode13'] != '' else None
        d['episode14'] = d['episode14'] if d['episode14'] != '' else None
        d['episode15'] = d['episode15'] if d['episode15'] != '' else None
        d['episode16'] = d['episode16'] if d['episode16'] != '' else None
        d['episode17'] = d['episode17'] if d['episode17'] != '' else None
        d['episode18'] = d['episode18'] if d['episode18'] != '' else None
        d['episode19'] = d['episode19'] if d['episode19'] != '' else None
        d['episode20'] = d['episode20'] if d['episode20'] != '' else None
        d['episode21'] = d['episode21'] if d['episode21'] != '' else None
        d['episode22'] = d['episode22'] if d['episode22'] != '' else None
        d['episode23'] = d['episode23'] if d['episode23'] != '' else None
        d['episode24'] = d['episode24'] if d['episode24'] != '' else None
        d['episode25'] = d['episode25'] if d['episode25'] != '' else None
        d['episode26'] = d['episode26'] if d['episode26'] != '' else None
        d['episode27'] = d['episode27'] if d['episode27'] != '' else None
        d['episode28'] = d['episode28'] if d['episode28'] != '' else None
        d['episode29'] = d['episode29'] if d['episode29'] != '' else None
        d['episode30'] = d['episode30'] if d['episode30'] != '' else None

        d['outline1'] = d['outline1'] if d['outline1'] != '' else None
        d['outline2'] = d['outline2'] if d['outline2'] != '' else None
        d['outline3'] = d['outline3'] if d['outline3'] != '' else None
        d['outline4'] = d['outline4'] if d['outline4'] != '' else None
        d['outline5'] = d['outline5'] if d['outline5'] != '' else None
        d['outline6'] = d['outline6'] if d['outline6'] != '' else None
        d['outline7'] = d['outline7'] if d['outline7'] != '' else None
        d['outline8'] = d['outline8'] if d['outline8'] != '' else None
        d['outline9'] = d['outline9'] if d['outline9'] != '' else None
        d['outline10'] = d['outline10'] if d['outline10'] != '' else None
        d['outline11'] = d['outline11'] if d['outline11'] != '' else None
        d['outline12'] = d['outline12'] if d['outline12'] != '' else None
        d['outline13'] = d['outline13'] if d['outline13'] != '' else None
        d['outline14'] = d['outline14'] if d['outline14'] != '' else None
        d['outline15'] = d['outline15'] if d['outline15'] != '' else None
        d['outline16'] = d['outline16'] if d['outline16'] != '' else None
        d['outline17'] = d['outline17'] if d['outline17'] != '' else None
        d['outline18'] = d['outline18'] if d['outline18'] != '' else None
        d['outline19'] = d['outline19'] if d['outline19'] != '' else None
        d['outline20'] = d['outline20'] if d['outline20'] != '' else None
        d['outline21'] = d['outline21'] if d['outline21'] != '' else None
        d['outline22'] = d['outline22'] if d['outline22'] != '' else None
        d['outline23'] = d['outline23'] if d['outline23'] != '' else None
        d['outline24'] = d['outline24'] if d['outline24'] != '' else None
        d['outline25'] = d['outline25'] if d['outline25'] != '' else None
        d['outline26'] = d['outline26'] if d['outline26'] != '' else None
        d['outline27'] = d['outline27'] if d['outline27'] != '' else None
        d['outline28'] = d['outline28'] if d['outline28'] != '' else None
        d['outline29'] = d['outline29'] if d['outline29'] != '' else None
        d['outline30'] = d['outline30'] if d['outline30'] != '' else None
        
    johnnys_index = [d['title-index'] for d in johnnys_dicts]
    

    worksheet = sh.worksheet('index_summary')

    tmp = worksheet.col_values(1)
    tmp.pop(0)
    indexes = [int(i) for i in tmp]

    list_of_dicts = worksheet.get_all_records()

    # 正規化
    for d in list_of_dicts:
        if d['title'] == 0:
            try: # anime_indexと合流
                i = anime_index.index(d['index'])
            except ValueError as e:
                print(e)
                return 'Error.'
            else:
                d['OA1'] = anime_dicts[i]['OA1']
                d['OA2'] = anime_dicts[i]['OA2']
                d['OA3'] = anime_dicts[i]['OA3']
                d['OA4'] = anime_dicts[i]['OA4']
                d['OA5'] = anime_dicts[i]['OA5']
                d['OA6'] = anime_dicts[i]['OA6']
                d['OA7'] = anime_dicts[i]['OA7']
                d['OA8'] = anime_dicts[i]['OA8']
                d['OA9'] = anime_dicts[i]['OA9']
                d['OA10'] = anime_dicts[i]['OA10']
                d['OA11'] = anime_dicts[i]['OA11']
                d['OA12'] = anime_dicts[i]['OA12']
                d['OA13'] = anime_dicts[i]['OA13']
                d['OA14'] = anime_dicts[i]['OA14']
                d['OA15'] = anime_dicts[i]['OA15']
                d['OA16'] = anime_dicts[i]['OA16']
                d['OA17'] = anime_dicts[i]['OA17']
                d['OA18'] = anime_dicts[i]['OA18']
                d['OA19'] = anime_dicts[i]['OA19']
                d['OA20'] = anime_dicts[i]['OA20']
                d['OA21'] = anime_dicts[i]['OA21']
                d['OA22'] = anime_dicts[i]['OA22']
                d['OA23'] = anime_dicts[i]['OA23']
                d['OA24'] = anime_dicts[i]['OA24']
                d['OA25'] = anime_dicts[i]['OA25']
                d['OA26'] = anime_dicts[i]['OA26']
                d['OA27'] = anime_dicts[i]['OA27']
                d['OA28'] = anime_dicts[i]['OA28']
                d['OA29'] = anime_dicts[i]['OA29']
                d['OA30'] = anime_dicts[i]['OA30']

                d['episode1'] = anime_dicts[i]['episode1']
                d['episode2'] = anime_dicts[i]['episode2']
                d['episode3'] = anime_dicts[i]['episode3']
                d['episode4'] = anime_dicts[i]['episode4']
                d['episode5'] = anime_dicts[i]['episode5']
                d['episode6'] = anime_dicts[i]['episode6']
                d['episode7'] = anime_dicts[i]['episode7']
                d['episode8'] = anime_dicts[i]['episode8']
                d['episode9'] = anime_dicts[i]['episode9']
                d['episode10'] = anime_dicts[i]['episode10']
                d['episode11'] = anime_dicts[i]['episode11']
                d['episode12'] = anime_dicts[i]['episode12']
                d['episode13'] = anime_dicts[i]['episode13']
                d['episode14'] = anime_dicts[i]['episode14']
                d['episode15'] = anime_dicts[i]['episode15']
                d['episode16'] = anime_dicts[i]['episode16']
                d['episode17'] = anime_dicts[i]['episode17']
                d['episode18'] = anime_dicts[i]['episode18']
                d['episode19'] = anime_dicts[i]['episode19']
                d['episode20'] = anime_dicts[i]['episode20']
                d['episode21'] = anime_dicts[i]['episode21']
                d['episode22'] = anime_dicts[i]['episode22']
                d['episode23'] = anime_dicts[i]['episode23']
                d['episode24'] = anime_dicts[i]['episode24']
                d['episode25'] = anime_dicts[i]['episode25']
                d['episode26'] = anime_dicts[i]['episode26']
                d['episode27'] = anime_dicts[i]['episode27']
                d['episode28'] = anime_dicts[i]['episode28']
                d['episode29'] = anime_dicts[i]['episode29']
                d['episode30'] = anime_dicts[i]['episode30']

                d['outline1'] = anime_dicts[i]['outline1']
                d['outline2'] = anime_dicts[i]['outline2']
                d['outline3'] = anime_dicts[i]['outline3']
                d['outline4'] = anime_dicts[i]['outline4']
                d['outline5'] = anime_dicts[i]['outline5']
                d['outline6'] = anime_dicts[i]['outline6']
                d['outline7'] = anime_dicts[i]['outline7']
                d['outline8'] = anime_dicts[i]['outline8']
                d['outline9'] = anime_dicts[i]['outline9']
                d['outline10'] = anime_dicts[i]['outline10']
                d['outline11'] = anime_dicts[i]['outline11']
                d['outline12'] = anime_dicts[i]['outline12']
                d['outline13'] = anime_dicts[i]['outline13']
                d['outline14'] = anime_dicts[i]['outline14']
                d['outline15'] = anime_dicts[i]['outline15']
                d['outline16'] = anime_dicts[i]['outline16']
                d['outline17'] = anime_dicts[i]['outline17']
                d['outline18'] = anime_dicts[i]['outline18']
                d['outline19'] = anime_dicts[i]['outline19']
                d['outline20'] = anime_dicts[i]['outline20']
                d['outline21'] = anime_dicts[i]['outline21']
                d['outline22'] = anime_dicts[i]['outline22']
                d['outline23'] = anime_dicts[i]['outline23']
                d['outline24'] = anime_dicts[i]['outline24']
                d['outline25'] = anime_dicts[i]['outline25']
                d['outline26'] = anime_dicts[i]['outline26']
                d['outline27'] = anime_dicts[i]['outline27']
                d['outline28'] = anime_dicts[i]['outline28']
                d['outline29'] = anime_dicts[i]['outline29']
                d['outline30'] = anime_dicts[i]['outline30']
                
        elif d['title'] == 10:
            try: 
                i = johnnys_index.index(d['index'])
            except ValueError as e:
                print(e)
                return 'Error.'
            else:
                d['OA1'] = johnnys_dicts[i]['OA1']
                d['OA2'] = johnnys_dicts[i]['OA2']
                d['OA3'] = johnnys_dicts[i]['OA3']
                d['OA4'] = johnnys_dicts[i]['OA4']
                d['OA5'] = johnnys_dicts[i]['OA5']
                d['OA6'] = johnnys_dicts[i]['OA6']
                d['OA7'] = johnnys_dicts[i]['OA7']
                d['OA8'] = johnnys_dicts[i]['OA8']
                d['OA9'] = johnnys_dicts[i]['OA9']
                d['OA10'] = johnnys_dicts[i]['OA10']
                d['OA11'] = johnnys_dicts[i]['OA11']
                d['OA12'] = johnnys_dicts[i]['OA12']
                d['OA13'] = johnnys_dicts[i]['OA13']
                d['OA14'] = johnnys_dicts[i]['OA14']
                d['OA15'] = johnnys_dicts[i]['OA15']
                d['OA16'] = johnnys_dicts[i]['OA16']
                d['OA17'] = johnnys_dicts[i]['OA17']
                d['OA18'] = johnnys_dicts[i]['OA18']
                d['OA19'] = johnnys_dicts[i]['OA19']
                d['OA20'] = johnnys_dicts[i]['OA20']
                d['OA21'] = johnnys_dicts[i]['OA21']
                d['OA22'] = johnnys_dicts[i]['OA22']
                d['OA23'] = johnnys_dicts[i]['OA23']
                d['OA24'] = johnnys_dicts[i]['OA24']
                d['OA25'] = johnnys_dicts[i]['OA25']
                d['OA26'] = johnnys_dicts[i]['OA26']
                d['OA27'] = johnnys_dicts[i]['OA27']
                d['OA28'] = johnnys_dicts[i]['OA28']
                d['OA29'] = johnnys_dicts[i]['OA29']
                d['OA30'] = johnnys_dicts[i]['OA30']

                d['episode1'] = johnnys_dicts[i]['episode1']
                d['episode2'] = johnnys_dicts[i]['episode2']
                d['episode3'] = johnnys_dicts[i]['episode3']
                d['episode4'] = johnnys_dicts[i]['episode4']
                d['episode5'] = johnnys_dicts[i]['episode5']
                d['episode6'] = johnnys_dicts[i]['episode6']
                d['episode7'] = johnnys_dicts[i]['episode7']
                d['episode8'] = johnnys_dicts[i]['episode8']
                d['episode9'] = johnnys_dicts[i]['episode9']
                d['episode10'] = johnnys_dicts[i]['episode10']
                d['episode11'] = johnnys_dicts[i]['episode11']
                d['episode12'] = johnnys_dicts[i]['episode12']
                d['episode13'] = johnnys_dicts[i]['episode13']
                d['episode14'] = johnnys_dicts[i]['episode14']
                d['episode15'] = johnnys_dicts[i]['episode15']
                d['episode16'] = johnnys_dicts[i]['episode16']
                d['episode17'] = johnnys_dicts[i]['episode17']
                d['episode18'] = johnnys_dicts[i]['episode18']
                d['episode19'] = johnnys_dicts[i]['episode19']
                d['episode20'] = johnnys_dicts[i]['episode20']
                d['episode21'] = johnnys_dicts[i]['episode21']
                d['episode22'] = johnnys_dicts[i]['episode22']
                d['episode23'] = johnnys_dicts[i]['episode23']
                d['episode24'] = johnnys_dicts[i]['episode24']
                d['episode25'] = johnnys_dicts[i]['episode25']
                d['episode26'] = johnnys_dicts[i]['episode26']
                d['episode27'] = johnnys_dicts[i]['episode27']
                d['episode28'] = johnnys_dicts[i]['episode28']
                d['episode29'] = johnnys_dicts[i]['episode29']
                d['episode30'] = johnnys_dicts[i]['episode30']

                d['outline1'] = johnnys_dicts[i]['outline1']
                d['outline2'] = johnnys_dicts[i]['outline2']
                d['outline3'] = johnnys_dicts[i]['outline3']
                d['outline4'] = johnnys_dicts[i]['outline4']
                d['outline5'] = johnnys_dicts[i]['outline5']
                d['outline6'] = johnnys_dicts[i]['outline6']
                d['outline7'] = johnnys_dicts[i]['outline7']
                d['outline8'] = johnnys_dicts[i]['outline8']
                d['outline9'] = johnnys_dicts[i]['outline9']
                d['outline10'] = johnnys_dicts[i]['outline10']
                d['outline11'] = johnnys_dicts[i]['outline11']
                d['outline12'] = johnnys_dicts[i]['outline12']
                d['outline13'] = johnnys_dicts[i]['outline13']
                d['outline14'] = johnnys_dicts[i]['outline14']
                d['outline15'] = johnnys_dicts[i]['outline15']
                d['outline16'] = johnnys_dicts[i]['outline16']
                d['outline17'] = johnnys_dicts[i]['outline17']
                d['outline18'] = johnnys_dicts[i]['outline18']
                d['outline19'] = johnnys_dicts[i]['outline19']
                d['outline20'] = johnnys_dicts[i]['outline20']
                d['outline21'] = johnnys_dicts[i]['outline21']
                d['outline22'] = johnnys_dicts[i]['outline22']
                d['outline23'] = johnnys_dicts[i]['outline23']
                d['outline24'] = johnnys_dicts[i]['outline24']
                d['outline25'] = johnnys_dicts[i]['outline25']
                d['outline26'] = johnnys_dicts[i]['outline26']
                d['outline27'] = johnnys_dicts[i]['outline27']
                d['outline28'] = johnnys_dicts[i]['outline28']
                d['outline29'] = johnnys_dicts[i]['outline29']
                d['outline30'] = johnnys_dicts[i]['outline30']
                
        else:
            d['OA1'] = None
            d['OA2'] = None
            d['OA3'] = None
            d['OA4'] = None
            d['OA5'] = None
            d['OA6'] = None
            d['OA7'] = None
            d['OA8'] = None
            d['OA9'] = None
            d['OA10'] = None
            d['OA11'] = None
            d['OA12'] = None
            d['OA13'] = None
            d['OA14'] = None
            d['OA15'] = None
            d['OA16'] = None
            d['OA17'] = None
            d['OA18'] = None
            d['OA19'] = None
            d['OA20'] = None
            d['OA21'] = None
            d['OA22'] = None
            d['OA23'] = None
            d['OA24'] = None
            d['OA25'] = None
            d['OA26'] = None
            d['OA27'] = None
            d['OA28'] = None
            d['OA29'] = None
            d['OA30'] = None

            d['episode1'] = None
            d['episode2'] = None
            d['episode3'] = None
            d['episode4'] = None
            d['episode5'] = None
            d['episode6'] = None
            d['episode7'] = None
            d['episode8'] = None
            d['episode9'] = None
            d['episode10'] = None
            d['episode11'] = None
            d['episode12'] = None
            d['episode13'] = None
            d['episode14'] = None
            d['episode15'] = None
            d['episode16'] = None
            d['episode17'] = None
            d['episode18'] = None
            d['episode19'] = None
            d['episode20'] = None
            d['episode21'] = None
            d['episode22'] = None
            d['episode23'] = None
            d['episode24'] = None
            d['episode25'] = None
            d['episode26'] = None
            d['episode27'] = None
            d['episode28'] = None
            d['episode29'] = None
            d['episode30'] = None

            d['outline1'] = None
            d['outline2'] = None
            d['outline3'] = None
            d['outline4'] = None
            d['outline5'] = None
            d['outline6'] = None
            d['outline7'] = None
            d['outline8'] = None
            d['outline9'] = None
            d['outline10'] = None
            d['outline11'] = None
            d['outline12'] = None
            d['outline13'] = None
            d['outline14'] = None
            d['outline15'] = None
            d['outline16'] = None
            d['outline17'] = None
            d['outline18'] = None
            d['outline19'] = None
            d['outline20'] = None
            d['outline21'] = None
            d['outline22'] = None
            d['outline23'] = None
            d['outline24'] = None
            d['outline25'] = None
            d['outline26'] = None
            d['outline27'] = None
            d['outline28'] = None
            d['outline29'] = None
            d['outline30'] = None
            
        d['title_tag1'] = d['title_tag1'].strip() if d['title_tag1'] != '' else None
        d['title_tag2'] = d['title_tag2'].strip() if d['title_tag2'] != '' else None
        d['title_tag3'] = d['title_tag3'].strip() if d['title_tag3'] != '' else None
        d['title_tag4'] = d['title_tag4'].strip() if d['title_tag4'] != '' else None
        d['title_tag5'] = d['title_tag5'].strip() if d['title_tag5'] != '' else None
        d['title_tag6'] = d['title_tag6'].strip() if d['title_tag6'] != '' else None
        d['title_tag7'] = d['title_tag7'].strip() if d['title_tag7'] != '' else None
        d['title_tag8'] = d['title_tag8'].strip() if d['title_tag8'] != '' else None
        d['title_tag9'] = d['title_tag9'].strip() if d['title_tag9'] != '' else None
        d['title_tag10'] = d['title_tag10'].strip() if d['title_tag10'] != '' else None
        d['title_tag11'] = d['title_tag11'].strip() if d['title_tag11'] != '' else None
        d['title_tag12'] = d['title_tag12'].strip() if d['title_tag12'] != '' else None
        d['title_tag13'] = d['title_tag13'].strip() if d['title_tag13'] != '' else None
        d['title_tag14'] = d['title_tag14'].strip() if d['title_tag14'] != '' else None
        d['title_tag15'] = d['title_tag15'].strip() if d['title_tag15'] != '' else None
        d['title_tag16'] = d['title_tag16'].strip() if d['title_tag16'] != '' else None
        d['title_tag17'] = d['title_tag17'].strip() if d['title_tag17'] != '' else None
        d['title_tag18'] = d['title_tag18'].strip() if d['title_tag18'] != '' else None
        d['title_tag19'] = d['title_tag19'].strip() if d['title_tag19'] != '' else None
        d['title_tag20'] = d['title_tag20'].strip() if d['title_tag20'] != '' else None
        d['title_tag21'] = d['title_tag21'].strip() if d['title_tag21'] != '' else None
        d['title_tag22'] = d['title_tag22'].strip() if d['title_tag22'] != '' else None
        d['title_tag23'] = d['title_tag23'].strip() if d['title_tag23'] != '' else None
        d['title_tag24'] = d['title_tag24'].strip() if d['title_tag24'] != '' else None
        d['title_tag25'] = d['title_tag25'].strip() if d['title_tag25'] != '' else None
        d['title_tag26'] = d['title_tag26'].strip() if d['title_tag26'] != '' else None
        d['title_tag27'] = d['title_tag27'].strip() if d['title_tag27'] != '' else None
        d['title_tag28'] = d['title_tag28'].strip() if d['title_tag28'] != '' else None
        d['title_tag29'] = d['title_tag29'].strip() if d['title_tag29'] != '' else None
        d['title_tag30'] = d['title_tag30'].strip() if d['title_tag30'] != '' else None



    if len(list_of_dicts) != len(indexes):
        return 'error: index!=list of dicts.'

    print("deleting ..")
    Oadates.objects.all().delete()

    print("updating ..")
    num = 0
    for d in list_of_dicts:

        obj = Oadates(official_name_id=d['index'],
                        episode1=d['OA1'],
                        episode2=d['OA2'],
                        episode3=d['OA3'],
                        episode4=d['OA4'],
                        episode5=d['OA5'],
                        episode6=d['OA6'],
                        episode7=d['OA7'],
                        episode8=d['OA8'],
                        episode9=d['OA9'],
                        episode10=d['OA10'],
                        episode11=d['OA11'],
                        episode12=d['OA12'],
                        episode13=d['OA13'],
                        episode14=d['OA14'],
                        episode15=d['OA15'],
                        episode16=d['OA16'],
                        episode17=d['OA17'],
                        episode18=d['OA18'],
                        episode19=d['OA19'],
                        episode20=d['OA20'],
                        episode21=d['OA21'],
                        episode22=d['OA22'],
                        episode23=d['OA23'],
                        episode24=d['OA24'],
                        episode25=d['OA25'],
                        episode26=d['OA26'],
                        episode27=d['OA27'],
                        episode28=d['OA28'],
                        episode29=d['OA29'],
                        episode30=d['OA30'],
                        episode_title1=d['episode1'],
                        episode_title2=d['episode2'],
                        episode_title3=d['episode3'],
                        episode_title4=d['episode4'],
                        episode_title5=d['episode5'],
                        episode_title6=d['episode6'],
                        episode_title7=d['episode7'],
                        episode_title8=d['episode8'],
                        episode_title9=d['episode9'],
                        episode_title10=d['episode10'],
                        episode_title11=d['episode11'],
                        episode_title12=d['episode12'],
                        episode_title13=d['episode13'],
                        episode_title14=d['episode14'],
                        episode_title15=d['episode15'],
                        episode_title16=d['episode16'],
                        episode_title17=d['episode17'],
                        episode_title18=d['episode18'],
                        episode_title19=d['episode19'],
                        episode_title20=d['episode20'],
                        episode_title21=d['episode21'],
                        episode_title22=d['episode22'],
                        episode_title23=d['episode23'],
                        episode_title24=d['episode24'],
                        episode_title25=d['episode25'],
                        episode_title26=d['episode26'],
                        episode_title27=d['episode27'],
                        episode_title28=d['episode28'],
                        episode_title29=d['episode29'],
                        episode_title30=d['episode30'],

                        title_tag1=d['title_tag1'],
                        title_tag2=d['title_tag2'],
                        title_tag3=d['title_tag3'],
                        title_tag4=d['title_tag4'],
                        title_tag5=d['title_tag5'],
                        title_tag6=d['title_tag6'],
                        title_tag7=d['title_tag7'],
                        title_tag8=d['title_tag8'],
                        title_tag9=d['title_tag9'],
                        title_tag10=d['title_tag10'],
                        title_tag11=d['title_tag11'],
                        title_tag12=d['title_tag12'],
                        title_tag13=d['title_tag13'],
                        title_tag14=d['title_tag14'],
                        title_tag15=d['title_tag15'],
                        title_tag16=d['title_tag16'],
                        title_tag17=d['title_tag17'],
                        title_tag18=d['title_tag18'],
                        title_tag19=d['title_tag19'],
                        title_tag20=d['title_tag20'],
                        title_tag21=d['title_tag21'],
                        title_tag22=d['title_tag22'],
                        title_tag23=d['title_tag23'],
                        title_tag24=d['title_tag24'],
                        title_tag25=d['title_tag25'],
                        title_tag26=d['title_tag26'],
                        title_tag27=d['title_tag27'],
                        title_tag28=d['title_tag28'],
                        title_tag29=d['title_tag29'],
                        title_tag30=d['title_tag30'],

                        outline1=d['outline1'],
                        outline2=d['outline2'],
                        outline3=d['outline3'],
                        outline4=d['outline4'],
                        outline5=d['outline5'],
                        outline6=d['outline6'],
                        outline7=d['outline7'],
                        outline8=d['outline8'],
                        outline9=d['outline9'],
                        outline10=d['outline10'],
                        outline11=d['outline11'],
                        outline12=d['outline12'],
                        outline13=d['outline13'],
                        outline14=d['outline14'],
                        outline15=d['outline15'],
                        outline16=d['outline16'],
                        outline17=d['outline17'],
                        outline18=d['outline18'],
                        outline19=d['outline19'],
                        outline20=d['outline20'],
                        outline21=d['outline21'],
                        outline22=d['outline22'],
                        outline23=d['outline23'],
                        outline24=d['outline24'],
                        outline25=d['outline25'],
                        outline26=d['outline26'],
                        outline27=d['outline27'],
                        outline28=d['outline28'],
                        outline29=d['outline29'],
                        outline30=d['outline30'],                        
                         )
        obj.save()
        num += 1


    print("{0} indexes saved.".format(num))

    return 'success.'


def set_events():


    print("accessing the spreadsheet..",end='')
    gc = gspread.service_account()
    #ファイルオープン
    sh = gc.open_by_key('1FwYHUSd9JWJHV0zsH3ZNy9c_27wcbTpp9siUbtRtgO8') # anime_schedule
    worksheet = sh.worksheet('long_schedule')

    list_of_dicts = worksheet.get_all_records()

    # 正規化
    for d in list_of_dicts:
        d['official_name'] = d['official_name'].strip() if d['official_name'] != '' else None
        d['url'] = d['url'].strip() if d['url'] != '' else None
        d['date_s'] = d['date_s'].strip() if d['date_s'] != '' else None
        d['date_e'] = d['date_e'].strip() if d['date_e'] != '' else None
        d['time_s'] = d['time_s'].strip() if d['time_s'] != '' else None
        d['time_e'] = d['time_e'].strip() if d['time_e'] != '' else None
        d['weekday'] = d['weekday'].strip() if d['weekday'] != '' else None
        d['media'] = d['media'].strip() if d['media'] != '' else None
        d['channel'] = d['channel'].strip() if d['channel'] != '' else None
        d['title'] = d['title'].strip() if d['title'] != '' else None

    print("deleting Longevents..")

    Longevents.objects.all().delete()


    print("updating Longevents..")
    num = 0
    for d in list_of_dicts:
        if d['official_name'] == '':
            break

        try:
            index = Official_names.objects.get(official_name=d['official_name']).index
        except Official_names.DoesNotExist as e:
            print('official_names may be wrong',d['official_name'])
            continue

        obj = Longevents(official_name_id=index,
                         title=d['title'],
                         url=d['url'],
                         date_s= datetime.datetime.strptime(d['date_s'], '%Y/%m/%d') if d['date_s'] != None else None,
                         # date_eが空欄の場合2023/12/31指定
                         date_e= datetime.datetime.strptime(d['date_e'], '%Y/%m/%d') if d['date_e'] != None else datetime.datetime.strptime('2023/12/31','%Y/%m/%d'),
                         time_s=d['time_s'],
                         time_e=d['time_e'],
                         weekday=d['weekday'],
                         media=d['media'] ,
                         channel=d['channel']
                         )
        obj.save()
        num += 1


    print("{0} events saved.".format(num))

    return 'success.'


if __name__=='__main__':

    # 一覧表更新
    
    msg = official_names_update()
    print(msg)

    msg = keywords_update()
    print(msg)

    # OA日付update
    msg=Oadates_update()
    print(msg)
    
    # schedule
    msg=set_events()
    print(msg)
