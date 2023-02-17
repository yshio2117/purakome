# Create your views here.
from django.template.loader import render_to_string
from django.db.models import CharField,Q,Max
from django.db.models.functions import Length
# mail関連
from django.views import generic
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.text import slugify
from django.http import HttpResponse,JsonResponse,Http404
from django.shortcuts import render,redirect,get_object_or_404
from .models import Tweetdata2,Statistics1week,Official_names,Keywords,Prefectures,Summarys,Trend_ranks,Pref_ranks,Frequentwords,Longevents,Abouts,Oadates,Fanarts,Comment,Categorys,Quiz,Tweetdata3

from .forms import SummaryForm,ReasonForm,DateForm,CharacterForm,AnimeForm,GetTweetForm,GenSheetForm,InquiryForm,pn_detailForm,summarizeForm,keywordForm,CommentForm

import datetime,itertools,collections,re,unicodedata,neologdn,random,csv,os,json

# 日付の警告を無視
import warnings
warnings.filterwarnings('ignore')

from .gettweets2 import collect_tweet_realtime
from django.utils import timezone

#wordcloud
from wordcloud import WordCloud
from PIL import Image
import io,base64

SPC = re.compile("-")
MIN_SHOW = 100 # ページ最小表示数(pcount)
STV = re.compile(r"処女|チンポ|ちんちん|ちんこ|ちんぽ|きんたま|アナル|陰部|オナホ|シコり|シコる|シコれ|シコった|キチガイ|ガイジ|殺す|殺せ|殺し|殺さ|殺そ|ころす|ころせ|ころした|死ね|おっぱい|オッパイ|まんこ|マンコ|オナニ|射精|風俗")

#以下feed.pyから引用. topページ(def index)で使用
def item_title(item,ep_l):
    try:
        i = [e['url'] for e in ep_l].index(item)
    except IndexError:
        pass
    else:
        return ep_l[i]['episode']['title']


def item_description(item,ep_l):

    try:
        i = [e['url'] for e in ep_l].index(item)
    except IndexError:
        return '***'
    else:       
        description = 'ポジティブな意見上位:'
        # summary text 5つを一旦表示
        sum_texts = list(Summarys.objects.values_list('summary_text1',
                              'summary_text2',
                              'summary_text3',
                              'summary_text4',
                              'summary_text5',
                              ).get(post=slugify('{0} {1}'.format(ep_l[i]['index'],ep_l[i]['episode']['num']))
                                    ))
        for j in range(5):
            if sum_texts[j] != None:
                description += '{}位'.format(j+1) + sum_texts[j]
                description += ','
                
        return description + '...'
    
def item_pubdate(item,ep_l):
    try:
        #print(item)
        i = [e['url'] for e in ep_l].index(item)
    except IndexError as e:
        #print(e)
        pass
    else:       
        #print('ok')
        return ep_l[i]['up_date']

def item_link(item,ep_l):

    try:
        i = [e['url'] for e in ep_l].index(item)
    except IndexError:
        pass
    else:     
        if ep_l[i]['episode']['num'] > 0:
            return r"https://purakome.net/sentiment/anime/{0}/{1}/".format(ep_l[i]['url'],ep_l[i]['episode']['num'])
        else:
            return r"https://purakome.net/sentiment/anime/{0}/".format(ep_l[i]['url'])

##############

def safetext(text):
    
    return False if STV.search(text) != None else True


def index(request):
    
    #if request.META.get("HTTP_HOST") == r'purakome.com':
        #return HttpResponse(status=410)

# 最新記事
    autumn_l = [
        'SpyxFamily',
        'kokyu',
        'yamanosusume',
        'mushikaburihime',
        'mobpsycho100-3',
        'shippona',
        'fuukoi-anime',
        'cooldoji',
        'bluelock',
        'shinmai-renkin',
        'jojo-stone-ocean',
        ]
    indexes = [Official_names.objects.get(url_name=s).index for s in autumn_l]
    ep_l = []
    for k,index in enumerate(indexes):

        oadates = Oadates.objects.values(
                    'episode1',
                    'episode2',
                    'episode3',
                    'episode4',
                    'episode5',
                    'episode6',
                    'episode7',
                    'episode8',
                    'episode9',
                    'episode10',
                    'episode11',
                    'episode12',
                    'episode13',
                    'episode14',
                    'episode15',
                    'episode16',
                    'episode17',
                    'episode18',
                    'episode19',
                    'episode20',
                    'episode21',
                    'episode22',
                    'episode23',
                    'episode24',
                    'episode25',
                    'episode26',
                    'episode27',
                    'episode28',
                    'episode29',
                    'episode30',

                    'title_tag1',
                    'title_tag2',
                    'title_tag3',
                    'title_tag4',
                    'title_tag5',
                    'title_tag6',
                    'title_tag7',
                    'title_tag8',
                    'title_tag9',
                    'title_tag10',
                    'title_tag11',
                    'title_tag12',
                    'title_tag13',
                    'title_tag14',
                    'title_tag15',
                    'title_tag16',
                    'title_tag17',
                    'title_tag18',
                    'title_tag19',
                    'title_tag20',
                    'title_tag21',
                    'title_tag22',
                    'title_tag23',
                    'title_tag24',
                    'title_tag25',
                    'title_tag26',
                    'title_tag27',
                    'title_tag28',
                    'title_tag29',
                    'title_tag30',
                    ).get(official_name_id=index)

        tmp = []
        for j in range(30,-1,-1):
            if Statistics1week.objects.filter(post=slugify('{0} {1}'.format(index,j))).exists():
                if j > 0 and oadates['title_tag{0}'.format(j)] != None:
                    title_tag = oadates['title_tag{0}'.format(j)] + Official_names.objects.get(index=index).short_name + '-' + str(j) + '話のポジネガ評価・感想まとめ|ぷらこめ'
                elif j > 0 and oadates['title_tag{0}'.format(j)] == None:
                    title_tag = Official_names.objects.get(index=index).short_name + '-' + str(j) + '話のポジネガ評価・感想まとめ|ぷらこめ'
                else: # 冬アニメ
                    title_tag = Official_names.objects.get(index=index).title_name + '-のポジネガ評価・感想まとめ|ぷらこめ'
                tmp= {
                        'url':autumn_l[k],
                        'index':index,
                        'up_date':Statistics1week.objects.only('up_date').get(post=slugify('{0} {1}'.format(index,j))).up_date,
                        'episode':{
                        'num':j,
                        'title':title_tag
                        }
                     }
                break
        ep_l.append(tmp)

    # update最新順に並び替え
    ep_l = sorted(ep_l,key=lambda x: x['up_date'],reverse=True)

    latest_l = []
    for item in ep_l:
        latest_l.append({'title':item_title(item['url'],ep_l),
                        'description':item_description(item['url'],ep_l).replace(",","<br>").replace("ポジティブな意見上位",r"<font style='font-weight:bold;'>【ポジティブな意見上位】</font><br>"),
                        'pubdate':item_pubdate(item['url'],ep_l),
                        'link':item_link(item['url'],ep_l),
                        'url':item['url'],#アイキャッチ画像用
                        'episode':item['episode']['num'],
                        })

#ランキング
    target_nos = list(Official_names.objects.filter(kind=0,
                                                    index__gte=1,
                                                    hidden=False,
                                                    past=False
                                                    ).values_list('index',
                                                                  'official_name',
                                                                  'url_name',
                                                                  'title_name',
                                                                  'kind',
                                                                  'short_name',
                                                                  ))
    
    
    title_rank = []
    chara_rank = []
    op_rank = []
    ed_rank = []
    cv_rank = []
    #pcount_rank = [] # グラフ用
    #print("statistics access")
    # 高評価アニメ
    for target_no in target_nos:
        if target_no[4] == 0:
            
            latest_post = 0
            for j in range(30,0,-1):
                post = slugify('{0} {1}'.format(target_no[0],j))  
                if Summarys.objects.filter(post=post).exists():
                    latest_post = post
                    break # 最新話見つかった時点で抜ける
            if latest_post == 0: # どのepiも見つからない場合表示なし
                continue
            
        else: # アニメ以外
            latest_post = slugify('{0} {1}'.format(target_no[0],0)) # 一旦episode=0 
        # 統計取得
        try:
            statistics = Statistics1week.objects.only(
                            'p1_count_d1',
                            'p1_count_d2',
                            'p1_count_d3',
                            'p1_count_d4',
                            'p1_count_d5',
                            'p1_count_d6',
                            'p1_count_d7',
                           'p2_count_d1',
                           'p2_count_d2',
                           'p2_count_d3',
                           'p2_count_d4',
                           'p2_count_d5',
                           'p2_count_d6',
                           'p2_count_d7',
                            'n1_count_d1',
                            'n1_count_d2',
                            'n1_count_d3',
                            'n1_count_d4',
                            'n1_count_d5',
                            'n1_count_d6',
                            'n1_count_d7',
                            'n2_count_d1',
                            'n2_count_d2',
                            'n2_count_d3',
                            'n2_count_d4',
                            'n2_count_d5',
                            'n2_count_d6',
                            'n2_count_d7',
                            ).get(post=latest_post)
    
        except Statistics1week.DoesNotExist as e:
            #print(e)
            continue

        # 統計取得
        p1count = sum([
                statistics.p1_count_d1,
                statistics.p1_count_d2,
                statistics.p1_count_d3,
                statistics.p1_count_d4,
                statistics.p1_count_d5,
                statistics.p1_count_d6,
                statistics.p1_count_d7,
                ])
        p2count = sum([
                statistics.p2_count_d1,
                statistics.p2_count_d2,
                statistics.p2_count_d3,
                statistics.p2_count_d4,
                statistics.p2_count_d5,
                statistics.p2_count_d6,
                statistics.p2_count_d7
                ])
        pcount = p1count + p2count
        if pcount < MIN_SHOW:
            continue                  
        n1count = sum([
                statistics.n1_count_d1,
                statistics.n1_count_d2,
                statistics.n1_count_d3,
                statistics.n1_count_d4,
                statistics.n1_count_d5,
                statistics.n1_count_d6,
                statistics.n1_count_d7,
                ])
        n2count = sum([
                statistics.n2_count_d1,
                statistics.n2_count_d2,
                statistics.n2_count_d3,
                statistics.n2_count_d4,
                statistics.n2_count_d5,
                statistics.n2_count_d6,
                statistics.n2_count_d7
                ])
        #pcount_rank.append({'brand':SPC.sub(" ",target_no[5]),
        #                    'pcount':pcount,
        #                        })
        
        # sum取得
        try:
          
            record_summary = Summarys.objects.only(
                                              'summary_text1',
                                               'summary_text2',
                                               'summary_text3',
                                               'summary_text4',
                                               'summary_text5',
                                               'summary_text21',
                                               'summary_text22',
                                               'summary_text23',
                                               'summary_text24',
                                               'summary_text25',
                                               ).get(post=latest_post)
                                                 
        except Summarys.DoesNotExist as e:
            #print(e)
            pass # 要約がない場合も表示なし
        else:

            if target_no[4] == 0: # anime

                title_rank.append({'pcount': pcount,
                                   'p1count':p1count,
                                   'p2count':p2count,
                                   'n1count':n1count,
                                   'n2count':n2count,
                                   '満足度':(pcount/(pcount+n1count+n2count))*100,
                                   'brand':SPC.sub(" ",target_no[5]),
                                   'url':target_no[2],
                                   'episode':latest_post.split('-')[1],
                                   'summarys':record_summary,
                                   }) 
    #print('done')

    title_rank = sorted(title_rank, key=lambda x:x['満足度'], reverse=True) # 満足度順に並び替え
    #chara_rank = sorted(chara_rank, key=lambda x:x['満足度'], reverse=True) # 満足度順に並び替え
    #op_rank = sorted(op_rank, key=lambda x:x['満足度'], reverse=True) # 満足度順に並び替え
    #ed_rank = sorted(ed_rank, key=lambda x:x['満足度'], reverse=True) # 満足度順に並び替え
    #cv_rank = sorted(cv_rank, key=lambda x:x['満足度'], reverse=True) # 満足度順に並び替え

    #pcount_rank = sorted(pcount_rank, key=lambda x:x['pcount'], reverse=True)

    params = {
        'title':'プラコメ',
        'title_rank':title_rank[:10],
        #'chara_rank':chara_rank[:20],
        #'op_rank':op_rank[:10],
        #'ed_rank':ed_rank[:10],
        #'cv_rank':cv_rank[:10],
        #'pcount_rank':pcount_rank[:10],
        'e_date': Statistics1week.objects.filter(episode=0).aggregate(Max('e_date'))['e_date__max'].date(),
        'latest_l':latest_l,
        }

    return render(request,'sentiment/anime/index.html',params)


def search(request):
    #if request.META.get("HTTP_HOST") == r'purakome.com':
        #return HttpResponse(status=410)
 
    key = request.GET.get('q')
    #print('q:',key)
    key_forsearch = unicodedata.normalize('NFKC',key.lower()).strip() # 正規化
    key_forsearch = re.sub(r" +"," ",key_forsearch) # 単語間のスペース数を揃える
    if key_forsearch == '': #空白のみは検索なし
        params = {
                  'title':'プラコメ',
                  'key':key,
                  'possibles':[],
                  'result':0,
                  }    
        return render(request,'sentiment/anime/search.html',params)


    try:
        record = Keywords.objects.get(keyword=key_forsearch,domestic=False)
    except Keywords.DoesNotExist:
        pass
        #print('{0} not exists.'.format(key))
    else:
        record = Official_names.objects.get(index=record.official_name_id)
        
        if record.hidden == False:
            print('move to page:{0}:'.format(key))

            if record.kind == 0:
                return redirect('anime', record.url_name)


    # keyword一覧に見つからない場合は近似検索,リスト候補出力
    
    keylist = key_forsearch.split(" ") # スペースが含まれたら分割,and検索
    keylist = list(set(keylist))
    possibles = []

    # AND検索
    #クエリを初期化
    query = Q()
    for k in keylist:
        # AND検索の場合は&を、OR検索の場合は|を使用する。
        query &= Q(keyword__icontains=k)
    
    official_name_ids = Keywords.objects.filter(query).values_list('official_name_id', flat=True)
    official_name_ids = list(set(official_name_ids))

    for official_name_id in official_name_ids:
               
        record = Official_names.objects.get(index=official_name_id)
        if record.hidden == True or record.kind in [10,11]:
            continue
        # charaが属するタイトルのurl
        if record.kind != 0:
            # chara名の代わりにタイトルを検索結果に表示
            try:
                anime_record = Official_names.objects.get(official_name=record.title_name,
                                                    hidden=False
                                                    )
            except Official_names.DoesNotExist as e:
                #print(e)
                continue
            
            title_url = anime_record.url_name
        else:
            title_url = None
            
            
        possibles.append({'kind':record.kind,
                          'title_name':record.title_name,
                          'title_url':title_url, 
                          'official_name':SPC.sub(" ",record.official_name),
                          'url_name':record.url_name,
                          })

           
    params = {
              'title':'プラコメ',
              'key':key,
              'possibles':possibles,
              'result':len(possibles),
              }
    
    return render(request,'sentiment/anime/search.html',params)


def anime_weeks(request,name):



    try:
        record = Official_names.objects.values('index',
                                               'kind',
                                               'title_name',
                                               'hidden',
                                               'past',
                                               'short_name',
                                               'series',
                                               ).get(url_name=name)
    except Official_names.DoesNotExist as e:
        return HttpResponse(status=410)
        raise Http404("Page does not exist.") 

    if record['kind'] != 0 or record['hidden'] == True:
        return HttpResponse(status=410)
        raise Http404("Page does not exist.") 

#    if request.META.get("HTTP_HOST") == r'purakome.com':
#        return HttpResponse(status=410)
   
    if record['past'] == True: # 春アニメはweeksが無いのでepisode=0を表示
        return anime_episode(request,name,0)

    if record['series'] == False:
        #print('to latest page')
        # 最新話にリダイレクト
        latest_ep = None
        for i in range(0,31):
            if Summarys.objects.filter(post = slugify('{0} {1}'.format(record['index'],i))).exists():
                latest_ep = i
                break
        #print('latest ep',latest_ep)
        if latest_ep != None:
            return anime_episode(request,name,latest_ep)
        else:
            return HttpResponse(status=404)

    title_rank = []

    try:
        oadates = Oadates.objects.values(
                        'episode1',
                        'episode2',
                        'episode3',
                        'episode4',
                        'episode5',
                        'episode6',
                        'episode7',
                        'episode8',
                        'episode9',
                        'episode10',
                        'episode11',
                        'episode12',
                        'episode13',
                        'episode14',
                        'episode15',
                        'episode16',
                        'episode17',
                        'episode18',
                        'episode19',
                        'episode20',
                        'episode21',
                        'episode22',
                        'episode23',
                        'episode24',
                        'episode25',
                        'episode26',
                        'episode27',
                        'episode28',
                        'episode29',
                        'episode30',
                        'episode_title1',
                        'episode_title2',
                        'episode_title3',
                        'episode_title4',
                        'episode_title5',
                        'episode_title6',
                        'episode_title7',
                        'episode_title8',
                        'episode_title9',
                        'episode_title10',
                        'episode_title11',
                        'episode_title12',
                        'episode_title13',
                        'episode_title14',
                        'episode_title15',
                        'episode_title16',
                        'episode_title17',
                        'episode_title18',
                        'episode_title19',
                        'episode_title20',
                        'episode_title21',
                        'episode_title22',
                        'episode_title23',
                        'episode_title24',
                        'episode_title25',
                        'episode_title26',
                        'episode_title27',
                        'episode_title28',
                        'episode_title29',
                        'episode_title30',
                        ).get(official_name_id=record['index'])

    except Oadates.DoesNotExist as e:
        return HttpResponse(status=410)

    else:
        #print('oadates',oadates)
        episode_summed = []
        for i in range(1,31):
            post = slugify('{0} {1}'.format(record['index'],i))
            if Statistics1week.objects.filter(post=post).exists():
                #print('ok')
                episode_summed.append({
                                  'post':post,
                                  'episode_date':oadates['episode{0}'.format(i)],
                                  'episode_title':oadates['episode_title{0}'.format(i)]
                                  })

        if len(episode_summed) == 0:
            return HttpResponse(status=410)
        #print('episode summed',episode_summed)
    for ep in episode_summed:

        statistics = Statistics1week.objects.values('p2_count_d1', 'p1_count_d1','n2_count_d1', 'n1_count_d1',
                                            'p2_count_d2', 'p1_count_d2','n2_count_d2', 'n1_count_d2',
                                            'p2_count_d3', 'p1_count_d3','n2_count_d3', 'n1_count_d3',
                                            'p2_count_d4', 'p1_count_d4','n2_count_d4', 'n1_count_d4',
                                            'p2_count_d5', 'p1_count_d5','n2_count_d5', 'n1_count_d5',
                                            'p2_count_d6', 'p1_count_d6','n2_count_d6', 'n1_count_d6',
                                            'p2_count_d7', 'p1_count_d7','n2_count_d7', 'n1_count_d7',
                                            ).get(post=ep['post'])

        record_summary = Summarys.objects.values_list(
                                            'summary_text1',
                                             'summary_text2',
                                             'summary_text3',
                                             'summary_text4',
                                             'summary_text5',
                                             'summary_text21',
                                             'summary_text22',
                                             'summary_text23',
                                             'summary_text24',
                                             'summary_text25',
                                              ).get(post=ep['post'])

        p1count = sum([statistics['p1_count_d{0}'.format(d)] for d in range(1,8)])
        p2count = sum([statistics['p2_count_d{0}'.format(d)] for d in range(1,8)])
        n1count = sum([statistics['n1_count_d{0}'.format(d)] for d in range(1,8)])
        n2count = sum([statistics['n2_count_d{0}'.format(d)] for d in range(1,8)])

        pcount = p1count + p2count

        title_rank.append({'pcount':  pcount,
                           'p1count':p1count,
                           'p2count':p2count,
                           'n1count':n1count,
                           'n2count':n2count,
                           '満足度':(pcount/(pcount+n1count+n2count))*100,
                           'title':'第'+str(ep['post'].split('-')[1])+'話 -'+ep['episode_title'] + '-' if ep['episode_title'] else '第'+str(ep['post'].split('-')[1])+'話',
                           'url':name,
                           'ep':ep['post'].split('-')[1],
                           'summarys':record_summary,
                           })

    chara_rank = []
    op_rank = []
    ed_rank = []
    cv_rank = []
    target_nos = list(Official_names.objects.filter(title_name=record['title_name'],
                                                    kind__in=[1,2,3,4]
                                                       ).values_list('index',
                                                                    'official_name',
                                                                    'url_name',
                                                                    'title_name',
                                                                    'kind'))

    for target_no in target_nos:
        post = slugify('{0} {1}'.format(target_no[0],0))
        try:
            statistics = Statistics1week.objects.values('p2_count_d1', 'p1_count_d1','n2_count_d1', 'n1_count_d1',
                                                'p2_count_d2', 'p1_count_d2','n2_count_d2', 'n1_count_d2',
                                                'p2_count_d3', 'p1_count_d3','n2_count_d3', 'n1_count_d3',
                                                'p2_count_d4', 'p1_count_d4','n2_count_d4', 'n1_count_d4',
                                                'p2_count_d5', 'p1_count_d5','n2_count_d5', 'n1_count_d5',
                                                'p2_count_d6', 'p1_count_d6','n2_count_d6', 'n1_count_d6',
                                                'p2_count_d7', 'p1_count_d7','n2_count_d7', 'n1_count_d7',
                                                ).get(post=post)
        except Statistics1week.DoesNotExist as e:
            #print(e)
            continue
        try:
            record_summary = Summarys.objects.values_list(
                                            'summary_text1',
                                             'summary_text2',
                                             'summary_text3',
                                             'summary_text4',
                                             'summary_text5',
                                             'summary_text21',
                                              'summary_text22',
                                              'summary_text23',
                                              'summary_text24',
                                              'summary_text25',
                                              ).get(post=post)
        except Summarys.DoesNotExist as e:
            #print(e)
            continue
        p1count = sum([statistics['p1_count_d{0}'.format(d)] for d in range(1,8)])
        p2count = sum([statistics['p2_count_d{0}'.format(d)] for d in range(1,8)])
        n1count = sum([statistics['n1_count_d{0}'.format(d)] for d in range(1,8)])
        n2count = sum([statistics['n2_count_d{0}'.format(d)] for d in range(1,8)])

        pcount = p1count + p2count

        if pcount >= 100:

            if target_no[4] == 1: # chara

                chara_rank.append({'pcount': pcount,
                                   'p1count':p1count,
                                   'p2count':p2count,
                                   'n1count':n1count,
                                   'n2count':n2count,
                                   '満足度':(pcount/(pcount+n1count+n2count))*100,
                                   'chara':SPC.sub(" ",target_no[1]),
                                   'url':target_no[2],
                                   # animeのURL
                                   'title_url':Official_names.objects.get(official_name=target_no[3]).url_name,
                                   'summarys':record_summary,
                                    })
            elif target_no[4] == 2: # op
                op_rank.append({'pcount': pcount,
                                   'p1count':p1count,
                                   'p2count':p2count,
                                   'n1count':n1count,
                                   'n2count':n2count,
                                   '満足度':(pcount/(pcount+n1count+n2count))*100,
                                   'op':SPC.sub(" ",target_no[1]),
                                   'url':target_no[2],
                                   # animeのURL
                                   'title_url':Official_names.objects.get(official_name=target_no[3]).url_name,
                                   'summarys':record_summary,
                                    })
            elif target_no[4] == 3: # op
                ed_rank.append({'pcount': pcount,
                                   'p1count':p1count,
                                   'p2count':p2count,
                                   'n1count':n1count,
                                   'n2count':n2count,
                                   '満足度':(pcount/(pcount+n1count+n2count))*100,
                                   'ed':SPC.sub(" ",target_no[1]),
                                   'url':target_no[2],
                                   # animeのURL
                                   'title_url':Official_names.objects.get(official_name=target_no[3]).url_name,
                                   'summarys':record_summary,
                                    })

            elif target_no[4] == 4: # cv
                cv_rank.append({'pcount':  pcount,
                                   'p1count':p1count,
                                   'p2count':p2count,
                                   'n1count':n1count,
                                   'n2count':n2count,
                                   '満足度':(pcount/(pcount+n1count+n2count))*100,
                                   'cv':SPC.sub(" ",target_no[1]),
                                   'url':target_no[2],
                                   # animeのURL
                                   'title_url':Official_names.objects.get(official_name=target_no[3]).url_name,
                                   'summarys':record_summary,
                                    })

    title_rank = sorted(title_rank, key=lambda x:x['満足度'], reverse=True) # 満足度順に並び替え
    chara_rank = sorted(chara_rank, key=lambda x:x['満足度'], reverse=True) if len(chara_rank) > 0 else None# 満足度順に並び替え
    op_rank = sorted(op_rank, key=lambda x:x['満足度'], reverse=True) if len(op_rank) > 0 else None # 満足度順に並び替え
    ed_rank = sorted(ed_rank, key=lambda x:x['満足度'], reverse=True) if len(ed_rank) > 0 else None # 満足度順に並び替え
    cv_rank = sorted(cv_rank, key=lambda x:x['満足度'], reverse=True) if len(cv_rank) > 0 else None # 満足度順に並び替え

    params = {
        'title':'プラコメ',
        'title_rank':title_rank,
        'chara_rank':chara_rank,
        'op_rank':op_rank,
        'ed_rank':ed_rank,
        'cv_rank':cv_rank,
        'name':name,
        'title_name':record['title_name'],
        'short_name':record['short_name'],
        }

    return render(request,'sentiment/anime/anime_weeks.html',params)


# handling reply, reply view
def reply_page(request):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = request.POST.get('post_id')  # from hidden input
            #print('post-id',post_id)
            parent_id = request.POST.get('parent')  # from hidden input
            post_url = request.POST.get('post_url')  # from hidden input

            #print('posturl',post_url)
            reply = form.save(commit=False)
            #print('AAAAAAAAAAAAA',Statistics1week.objects.get(id=post_id).post)
            reply.target = Statistics1week.objects.get(id=post_id).post
            reply.parent = Comment(id=parent_id)

            reply.save()
            return redirect(post_url+'#cm'+str(reply.id))
    return redirect("/")


def exec_ajax(request,name,episode,loc):
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        
        json = {"error":False, }
    
    
        record = Official_names.objects.values('index',
                                               'kind',
                                               'title_name',
                                               'hidden',
                                               'past',
                                               'short_name',
                                               ).get(url_name=name)
        post = slugify('{0} {1}'.format(record['index'],episode))
        
        statistics = Statistics1week.objects.values('s_date',
                                                    'e_date'
                                                   ).get(post=post)

        s_date = statistics['s_date']
        e_date = statistics['e_date']
        
        summary = None
    # 要約取得
        if loc[:4] in ['sump','sumn']:
            if loc[:4] == 'sump':
                sum_num = int(loc[4])
            else:
                sum_num = 20 + int(loc[4])

            sum_obj = list(Tweetdata2.objects.filter(
                                                t_date__range=(s_date,e_date),# 7日前~1日前まで
                                                sum_title_id=record['index'],
                                                sum_title_text=sum_num,
                                                ).values('t_id',
                                                        'u_id',
                                                        't_date',
                                                        'content',
                                                        's_name',
                                                        'u_name',
                                                        'p_image',
                                                        's_class',
                                                        't_id_char',
                                                        'entities_display_url',
                                                        'entities_url',
                                                        'media_url',
                                                        'media_url_truncated',
                                                        'sum_title_text',
                                                        'hashtag'
                                                        ).order_by('media_url'))
            # 要約文
            summary_texts = Summarys.objects.only(
                                                   "summary_text{0}".format(sum_num),
                                                   ).get(post=post)
    
            # ポジネガ両方ともsummarysに入れる.
            summary = {'要約':summary_texts,
                        '原文':sum_obj[3:] # 0~2は表示済み
                        }
    
        
        params = {
            "summary":summary,
            }
        content = render_to_string("sentiment/ajax_content.html",params,request)
        json["content"] = content
    
        return JsonResponse(json)
        
    else: # ダイレクトでURL指定された場合
        return HttpResponse(status=404)


def j_event(request,name,episode=0):

    pn_counts_date=[] # 投稿日付（グラフ横軸)
    locations=[]
    '''
    CharField.register_lookup(Length, 'length') #  registered as a transform
    
    character_filter = request.POST.get('character_filter')
    anime_filter = request.POST.get('anime_filter')
    anime_filter2 = request.POST.get('Search')
    '''

    try:        
        record = Official_names.objects.values('index',
                                               'kind',
                                               'title_name',
                                               'hidden',
                                               'past',
                                               'short_name',
                                               ).get(url_name=name)

    except Official_names.DoesNotExist as e:
        return HttpResponse(status=410)
        raise Http404("Page does not exist.")
    
    if record['kind'] != 10 or record['hidden'] == True: # charaページにアクセスしようとした場合
        return HttpResponse(status=410)
        raise Http404("Page does not exist.")
    
### purakome.com to purakome.net    
    #if request.META.get("HTTP_HOST") == r'purakome.com':
        #return HttpResponse(status=410)
###

    #print('requestpath',request.path) # 春アニメで sentiment/anime/kimetsu/0/でアクセスできてしまうのを防ぐ
    if episode == 0 and request.path[-3:] == r'/0/':
        return redirect(r'https://purakome.net/sentiment/anime/{0}/'.format(name),permanent=True)

# コメント
    post = slugify('{0} {1}'.format(record['index'],episode))
    #print('post2',post)

    post_sta=get_object_or_404(Statistics1week,post=post)

    #print('post   id',post_sta.id)
    # List of active comments for this post
    comments = Comment.objects.filter(target=post_sta.post,
                                      #parent_id=None,
                                      active=True)
    new_comment = None

    comment_form = CommentForm()
    if request.method == 'POST':
        #print('POST')
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.target = post_sta.post
            # Save the comment to the database
            new_comment.save()
            # redirect to same page and focus on that comment
            '''
            if episode == 0:
                return redirect(r'sentiment/anime/{0}/'.format(name)+'#'+str(new_comment.id))
            elif episode > 0:
                return redirect(r'sentiment/anime/{0}/{1}/'.format(name,episode)+'#'+str(new_comment.id))
            '''
        else:
            comment_form = CommentForm()


# statisticsと日時取得        
    #print("statistics access")
    try:
        statistics = Statistics1week.objects.values('s_date','e_date','p2_count_d1', 'p1_count_d1','n2_count_d1', 'n1_count_d1',
                                        'p2_count_d2', 'p1_count_d2','n2_count_d2', 'n1_count_d2',
                                        'p2_count_d3', 'p1_count_d3','n2_count_d3', 'n1_count_d3',
                                        'p2_count_d4', 'p1_count_d4','n2_count_d4', 'n1_count_d4',
                                        'p2_count_d5', 'p1_count_d5','n2_count_d5', 'n1_count_d5',
                                        'p2_count_d6', 'p1_count_d6','n2_count_d6', 'n1_count_d6',
                                        'p2_count_d7', 'p1_count_d7','n2_count_d7', 'n1_count_d7',
                                        'p_tweet1_id','p_tweet2_id','p_tweet3_id','p_tweet4_id',
                                        'p_tweet5_id','p_tweet6_id','p_tweet7_id','p_tweet8_id',
                                        'p_tweet9_id','p_tweet10_id',
                                        'n_tweet1_id','n_tweet2_id','n_tweet3_id','n_tweet4_id',
                                        'n_tweet5_id','n_tweet6_id','n_tweet7_id','n_tweet8_id',
                                        'n_tweet9_id','n_tweet10_id'
                                        ).get(post=post)    

    except Statistics1week.DoesNotExist as e:
        #print(e)
        return HttpResponse(status=410)


    s_date = statistics['s_date']
    e_date = statistics['e_date']
    #print('s_date',s_date)
    #print('e_date',e_date)

    p2_counts=[0,0,0,0,0,0]# 日付ごとの投稿数(グラフ縦軸)
    p1_counts=[0,0,0,0,0,0]# 日付ごとの投稿数(グラフ縦軸)
    n1_counts=[0,0,0,0,0,0]# 日付ごとの投稿数(グラフ縦軸)
    n2_counts=[0,0,0,0,0,0]
    pn_counts_date=[] # 投稿日付（グラフ横軸)
    for i in range(6):
        p2_counts[i] = statistics['p2_count_d{0}'.format(6-i)]
        p1_counts[i] = statistics['p1_count_d{0}'.format(6-i)]
        n2_counts[i] = statistics['n2_count_d{0}'.format(6-i)]
        n1_counts[i] = statistics['n1_count_d{0}'.format(6-i)]


    for i in range(6):
        d = (e_date + datetime.timedelta(hours=9)).date() - datetime.timedelta(days = 5 - i)
        pn_counts_date.append(str(d.month)+'月'+str(d.day)+'日')

    p2_num = sum(p2_counts)
    p1_num = sum(p1_counts)
    p_num = p2_num + p1_num

    '''
    if p_num < MIN_SHOW:
        return HttpResponse(status=410)
        raise Http404("Page does not exist.")
    '''
    n2_num = sum(n2_counts)
    n1_num = sum(n1_counts)
    n_num = n2_num + n1_num

# news取得       
    long_event_dic = Longevents.objects.filter(
                                              #(Q(date_s__lte=e_date) & Q(date_e__gte=s_date)) | (Q(date_e__gte=s_date) & Q(date_s__lte=e_date)),
                                               Q(official_name_id=record['index']),
                                               #Q(date_s__range=(s_date,e_date)) | Q(date_e__range=(s_date,e_date)),
                                               
                                               # 1週間の最後の日付よりもイベントの開始日付が遅い場合は該当外
                                               # イベントの終了日付が1週間の最初の日付よりも早い場合は該当外
                                               Q(title__isnull=False), # titleが空欄以外
                                               ).values( 
                                                        #'official_name',
                                                        #'url',
                                                        'title',
                                                        'date_s',
                                                        'date_e',
                                                        'time_s',
                                                        'time_e',
                                                        'weekday',
                                                        'media',
                                                        'channel',
                                                        'title'
                                                         )[:5]


# category
    category=[{'p2count':0,'p1count':0,'n1count':0,'n2count':0,
               'p2data':[],'p1data':[],'n1data':[],'n2data':[],
               'freqs':[],'category_name':[],'keys':''} for i in range(8)]
    try:
        c_data = Categorys.objects.only(
                                'name_c1',
                                'name_c2',
                                'name_c3',
                                'name_c4',
                                'name_c5',
                                'name_c6',
                                'name_c7',
                                'name_c8',
                                'freqs_c1',
                                'freqs_c2',
                                'freqs_c3',
                                'freqs_c4',
                                'freqs_c5',
                                'freqs_c6',
                                'freqs_c7',
                                'freqs_c8',
                                'keys_c1',
                                'keys_c2',
                                'keys_c3',
                                'keys_c4',
                                'keys_c5',
                                'keys_c6',
                                'keys_c7',
                                'keys_c8',
                                'p2count_c1',
                                'p1count_c1',
                                'n1count_c1',
                                'n2count_c1',
                                'p2count_c2',
                                'p1count_c2',
                                'n1count_c2',
                                'n2count_c2',
                                'p2count_c3',
                                'p1count_c3',
                                'n1count_c3',
                                'n2count_c3',
                                'p2count_c4',
                                'p1count_c4',
                                'n1count_c4',
                                'n2count_c4',
                                'p2count_c5',
                                'p1count_c5',
                                'n1count_c5',
                                'n2count_c5',

                                'p2data1_c1',
                                'p2data2_c1',
                                'p2data3_c1',
                                'p2data4_c1',
                                'p2data5_c1',
                                'p1data1_c1',
                                'p1data2_c1',
                                'p1data3_c1',
                                'p1data4_c1',
                                'p1data5_c1',
                                'n1data1_c1',
                                'n1data2_c1',
                                'n1data3_c1',
                                'n1data4_c1',
                                'n1data5_c1',
                                'n2data1_c1',
                                'n2data2_c1',
                                'n2data3_c1',
                                'n2data4_c1',
                                'n2data5_c1',

                                'p2data1_c2',
                                'p2data2_c2',
                                'p2data3_c2',
                                'p2data4_c2',
                                'p2data5_c2',
                                'p1data1_c2',
                                'p1data2_c2',
                                'p1data3_c2',
                                'p1data4_c2',
                                'p1data5_c2',
                                'n1data1_c2',
                                'n1data2_c2',
                                'n1data3_c2',
                                'n1data4_c2',
                                'n1data5_c2',
                                'n2data1_c2',
                                'n2data2_c2',
                                'n2data3_c2',
                                'n2data4_c2',
                                'n2data5_c2',

                                'p2data1_c3',
                                'p2data2_c3',
                                'p2data3_c3',
                                'p2data4_c3',
                                'p2data5_c3',
                                'p1data1_c3',
                                'p1data2_c3',
                                'p1data3_c3',
                                'p1data4_c3',
                                'p1data5_c3',
                                'n1data1_c3',
                                'n1data2_c3',
                                'n1data3_c3',
                                'n1data4_c3',
                                'n1data5_c3',
                                'n2data1_c3',
                                'n2data2_c3',
                                'n2data3_c3',
                                'n2data4_c3',
                                'n2data5_c3',

                                'p2data1_c4',
                                'p2data2_c4',
                                'p2data3_c4',
                                'p2data4_c4',
                                'p2data5_c4',
                                'p1data1_c4',
                                'p1data2_c4',
                                'p1data3_c4',
                                'p1data4_c4',
                                'p1data5_c4',
                                'n1data1_c4',
                                'n1data2_c4',
                                'n1data3_c4',
                                'n1data4_c4',
                                'n1data5_c4',
                                'n2data1_c4',
                                'n2data2_c4',
                                'n2data3_c4',
                                'n2data4_c4',
                                'n2data5_c4',

                                'p2data1_c5',
                                'p2data2_c5',
                                'p2data3_c5',
                                'p2data4_c5',
                                'p2data5_c5',
                                'p1data1_c5',
                                'p1data2_c5',
                                'p1data3_c5',
                                'p1data4_c5',
                                'p1data5_c5',
                                'n1data1_c5',
                                'n1data2_c5',
                                'n1data3_c5',
                                'n1data4_c5',
                                'n1data5_c5',
                                'n2data1_c5',
                                'n2data2_c5',
                                'n2data3_c5',
                                'n2data4_c5',
                                'n2data5_c5',
                                
                                'p2data1_c6',
                                'p2data2_c6',
                                'p2data3_c6',
                                'p2data4_c6',
                                'p2data5_c6',
                                'p1data1_c6',
                                'p1data2_c6',
                                'p1data3_c6',
                                'p1data4_c6',
                                'p1data5_c6',
                                'n1data1_c6',
                                'n1data2_c6',
                                'n1data3_c6',
                                'n1data4_c6',
                                'n1data5_c6',
                                'n2data1_c6',
                                'n2data2_c6',
                                'n2data3_c6',
                                'n2data4_c6',
                                'n2data5_c6',
                                
                                'p2data1_c7',
                                'p2data2_c7',
                                'p2data3_c7',
                                'p2data4_c7',
                                'p2data5_c7',
                                'p1data1_c7',
                                'p1data2_c7',
                                'p1data3_c7',
                                'p1data4_c7',
                                'p1data5_c7',
                                'n1data1_c7',
                                'n1data2_c7',
                                'n1data3_c7',
                                'n1data4_c7',
                                'n1data5_c7',
                                'n2data1_c7',
                                'n2data2_c7',
                                'n2data3_c7',
                                'n2data4_c7',
                                'n2data5_c7',
                                
                                'p2data1_c8',
                                'p2data2_c8',
                                'p2data3_c8',
                                'p2data4_c8',
                                'p2data5_c8',
                                'p1data1_c8',
                                'p1data2_c8',
                                'p1data3_c8',
                                'p1data4_c8',
                                'p1data5_c8',
                                'n1data1_c8',
                                'n1data2_c8',
                                'n1data3_c8',
                                'n1data4_c8',
                                'n1data5_c8',
                                'n2data1_c8',
                                'n2data2_c8',
                                'n2data3_c8',
                                'n2data4_c8',
                                'n2data5_c8',
                                 ).get(post=post)
    except Categorys.DoesNotExist as e:
        category=None

    else:
    # cat1
        category[0]['p2count'] = c_data.p2count_c1
        category[0]['p1count'] = c_data.p1count_c1
        category[0]['n1count'] = c_data.n1count_c1
        category[0]['n2count'] = c_data.n2count_c1

        category[0]['p2data'].append(c_data.p2data1_c1)
        category[0]['p1data'].append(c_data.p1data1_c1)
        category[0]['n1data'].append(c_data.n1data1_c1)
        category[0]['n2data'].append(c_data.n2data1_c1)

        category[0]['p2data'].append(c_data.p2data2_c1)
        category[0]['p1data'].append(c_data.p1data2_c1)
        category[0]['n1data'].append(c_data.n1data2_c1)
        category[0]['n2data'].append(c_data.n2data2_c1)

        category[0]['p2data'].append(c_data.p2data3_c1)
        category[0]['p1data'].append(c_data.p1data3_c1)
        category[0]['n1data'].append(c_data.n1data3_c1)
        category[0]['n2data'].append(c_data.n2data3_c1)

        category[0]['p2data'].append(c_data.p2data4_c1)
        category[0]['p1data'].append(c_data.p1data4_c1)
        category[0]['n1data'].append(c_data.n1data4_c1)
        category[0]['n2data'].append(c_data.n2data4_c1)

        category[0]['p2data'].append(c_data.p2data5_c1)
        category[0]['p1data'].append(c_data.p1data5_c1)
        category[0]['n1data'].append(c_data.n1data5_c1)
        category[0]['n2data'].append(c_data.n2data5_c1)

        category[0]['freqs'] = json.loads(c_data.freqs_c1) if c_data.freqs_c1 not in [None,''] else None
        category[0]['category_name'] = c_data.name_c1
        category[0]['keys'] = c_data.keys_c1
    # cat2
        category[1]['p2count'] = c_data.p2count_c2
        category[1]['p1count'] = c_data.p1count_c2
        category[1]['n1count'] = c_data.n1count_c2
        category[1]['n2count'] = c_data.n2count_c2

        category[1]['p2data'].append(c_data.p2data1_c2)
        category[1]['p1data'].append(c_data.p1data1_c2)
        category[1]['n1data'].append(c_data.n1data1_c2)
        category[1]['n2data'].append(c_data.n2data1_c2)

        category[1]['p2data'].append(c_data.p2data2_c2)
        category[1]['p1data'].append(c_data.p1data2_c2)
        category[1]['n1data'].append(c_data.n1data2_c2)
        category[1]['n2data'].append(c_data.n2data2_c2)

        category[1]['p2data'].append(c_data.p2data3_c2)
        category[1]['p1data'].append(c_data.p1data3_c2)
        category[1]['n1data'].append(c_data.n1data3_c2)
        category[1]['n2data'].append(c_data.n2data3_c2)

        category[1]['p2data'].append(c_data.p2data4_c2)
        category[1]['p1data'].append(c_data.p1data4_c2)
        category[1]['n1data'].append(c_data.n1data4_c2)
        category[1]['n2data'].append(c_data.n2data4_c2)

        category[1]['p2data'].append(c_data.p2data5_c2)
        category[1]['p1data'].append(c_data.p1data5_c2)
        category[1]['n1data'].append(c_data.n1data5_c2)
        category[1]['n2data'].append(c_data.n2data5_c2)

        category[1]['freqs'] = json.loads(c_data.freqs_c2) if c_data.freqs_c2 not in [None,''] else None
        category[1]['category_name'] = c_data.name_c2
        category[1]['keys'] = c_data.keys_c2
    # cat3
        category[2]['p2count'] = c_data.p2count_c3
        category[2]['p1count'] = c_data.p1count_c3
        category[2]['n1count'] = c_data.n1count_c3
        category[2]['n2count'] = c_data.n2count_c3

        category[2]['p2data'].append(c_data.p2data1_c3)
        category[2]['p1data'].append(c_data.p1data1_c3)
        category[2]['n1data'].append(c_data.n1data1_c3)
        category[2]['n2data'].append(c_data.n2data1_c3)

        category[2]['p2data'].append(c_data.p2data2_c3)
        category[2]['p1data'].append(c_data.p1data2_c3)
        category[2]['n1data'].append(c_data.n1data2_c3)
        category[2]['n2data'].append(c_data.n2data2_c3)

        category[2]['p2data'].append(c_data.p2data3_c3)
        category[2]['p1data'].append(c_data.p1data3_c3)
        category[2]['n1data'].append(c_data.n1data3_c3)
        category[2]['n2data'].append(c_data.n2data3_c3)

        category[2]['p2data'].append(c_data.p2data4_c3)
        category[2]['p1data'].append(c_data.p1data4_c3)
        category[2]['n1data'].append(c_data.n1data4_c3)
        category[2]['n2data'].append(c_data.n2data4_c3)

        category[2]['p2data'].append(c_data.p2data5_c3)
        category[2]['p1data'].append(c_data.p1data5_c3)
        category[2]['n1data'].append(c_data.n1data5_c3)
        category[2]['n2data'].append(c_data.n2data5_c3)

        category[2]['freqs'] = json.loads(c_data.freqs_c3) if c_data.freqs_c3 not in [None,''] else None
        category[2]['category_name'] = c_data.name_c3
        category[2]['keys'] = c_data.keys_c3
    # cat4
        category[3]['p2count'] = c_data.p2count_c4
        category[3]['p1count'] = c_data.p1count_c4
        category[3]['n1count'] = c_data.n1count_c4
        category[3]['n2count'] = c_data.n2count_c4

        category[3]['p2data'].append(c_data.p2data1_c4)
        category[3]['p1data'].append(c_data.p1data1_c4)
        category[3]['n1data'].append(c_data.n1data1_c4)
        category[3]['n2data'].append(c_data.n2data1_c4)

        category[3]['p2data'].append(c_data.p2data2_c4)
        category[3]['p1data'].append(c_data.p1data2_c4)
        category[3]['n1data'].append(c_data.n1data2_c4)
        category[3]['n2data'].append(c_data.n2data2_c4)

        category[3]['p2data'].append(c_data.p2data3_c4)
        category[3]['p1data'].append(c_data.p1data3_c4)
        category[3]['n1data'].append(c_data.n1data3_c4)
        category[3]['n2data'].append(c_data.n2data3_c4)

        category[3]['p2data'].append(c_data.p2data4_c4)
        category[3]['p1data'].append(c_data.p1data4_c4)
        category[3]['n1data'].append(c_data.n1data4_c4)
        category[3]['n2data'].append(c_data.n2data4_c4)

        category[3]['p2data'].append(c_data.p2data5_c4)
        category[3]['p1data'].append(c_data.p1data5_c4)
        category[3]['n1data'].append(c_data.n1data5_c4)
        category[3]['n2data'].append(c_data.n2data5_c4)

        category[3]['freqs'] = json.loads(c_data.freqs_c4) if c_data.freqs_c4 not in [None,''] else None
        category[3]['category_name'] = c_data.name_c4
        category[3]['keys'] = c_data.keys_c4
    # cat5
        category[4]['p2count'] = c_data.p2count_c5
        category[4]['p1count'] = c_data.p1count_c5
        category[4]['n1count'] = c_data.n1count_c5
        category[4]['n2count'] = c_data.n2count_c5

        category[4]['p2data'].append(c_data.p2data1_c5)
        category[4]['p1data'].append(c_data.p1data1_c5)
        category[4]['n1data'].append(c_data.n1data1_c5)
        category[4]['n2data'].append(c_data.n2data1_c5)

        category[4]['p2data'].append(c_data.p2data2_c5)
        category[4]['p1data'].append(c_data.p1data2_c5)
        category[4]['n1data'].append(c_data.n1data2_c5)
        category[4]['n2data'].append(c_data.n2data2_c5)

        category[4]['p2data'].append(c_data.p2data3_c5)
        category[4]['p1data'].append(c_data.p1data3_c5)
        category[4]['n1data'].append(c_data.n1data3_c5)
        category[4]['n2data'].append(c_data.n2data3_c5)

        category[4]['p2data'].append(c_data.p2data4_c5)
        category[4]['p1data'].append(c_data.p1data4_c5)
        category[4]['n1data'].append(c_data.n1data4_c5)
        category[4]['n2data'].append(c_data.n2data4_c5)

        category[4]['p2data'].append(c_data.p2data5_c5)
        category[4]['p1data'].append(c_data.p1data5_c5)
        category[4]['n1data'].append(c_data.n1data5_c5)
        category[4]['n2data'].append(c_data.n2data5_c5)

        category[4]['freqs'] = json.loads(c_data.freqs_c5) if c_data.freqs_c5 not in [None,''] else None
        category[4]['category_name'] = c_data.name_c5
        category[4]['keys'] = c_data.keys_c5

    # cat5
        category[5]['p2count'] = c_data.p2count_c6
        category[5]['p1count'] = c_data.p1count_c6
        category[5]['n1count'] = c_data.n1count_c6
        category[5]['n2count'] = c_data.n2count_c6

        category[5]['p2data'].append(c_data.p2data1_c6)
        category[5]['p1data'].append(c_data.p1data1_c6)
        category[5]['n1data'].append(c_data.n1data1_c6)
        category[5]['n2data'].append(c_data.n2data1_c6)

        category[5]['p2data'].append(c_data.p2data2_c6)
        category[5]['p1data'].append(c_data.p1data2_c6)
        category[5]['n1data'].append(c_data.n1data2_c6)
        category[5]['n2data'].append(c_data.n2data2_c6)

        category[5]['p2data'].append(c_data.p2data3_c6)
        category[5]['p1data'].append(c_data.p1data3_c6)
        category[5]['n1data'].append(c_data.n1data3_c6)
        category[5]['n2data'].append(c_data.n2data3_c6)

        category[5]['p2data'].append(c_data.p2data4_c6)
        category[5]['p1data'].append(c_data.p1data4_c6)
        category[5]['n1data'].append(c_data.n1data4_c6)
        category[5]['n2data'].append(c_data.n2data4_c6)

        category[5]['p2data'].append(c_data.p2data5_c6)
        category[5]['p1data'].append(c_data.p1data5_c6)
        category[5]['n1data'].append(c_data.n1data5_c6)
        category[5]['n2data'].append(c_data.n2data5_c6)

        category[5]['freqs'] = json.loads(c_data.freqs_c6) if c_data.freqs_c6 not in [None,''] else None
        category[5]['category_name'] = c_data.name_c6
        category[5]['keys'] = c_data.keys_c6
        
    # cat5
        category[6]['p2count'] = c_data.p2count_c7
        category[6]['p1count'] = c_data.p1count_c7
        category[6]['n1count'] = c_data.n1count_c7
        category[6]['n2count'] = c_data.n2count_c7

        category[6]['p2data'].append(c_data.p2data1_c7)
        category[6]['p1data'].append(c_data.p1data1_c7)
        category[6]['n1data'].append(c_data.n1data1_c7)
        category[6]['n2data'].append(c_data.n2data1_c7)

        category[6]['p2data'].append(c_data.p2data2_c7)
        category[6]['p1data'].append(c_data.p1data2_c7)
        category[6]['n1data'].append(c_data.n1data2_c7)
        category[6]['n2data'].append(c_data.n2data2_c7)

        category[6]['p2data'].append(c_data.p2data3_c7)
        category[6]['p1data'].append(c_data.p1data3_c7)
        category[6]['n1data'].append(c_data.n1data3_c7)
        category[6]['n2data'].append(c_data.n2data3_c7)

        category[6]['p2data'].append(c_data.p2data4_c7)
        category[6]['p1data'].append(c_data.p1data4_c7)
        category[6]['n1data'].append(c_data.n1data4_c7)
        category[6]['n2data'].append(c_data.n2data4_c7)

        category[6]['p2data'].append(c_data.p2data5_c7)
        category[6]['p1data'].append(c_data.p1data5_c7)
        category[6]['n1data'].append(c_data.n1data5_c7)
        category[6]['n2data'].append(c_data.n2data5_c7)

        category[6]['freqs'] = json.loads(c_data.freqs_c7) if c_data.freqs_c7 not in [None,''] else None
        category[6]['category_name'] = c_data.name_c7
        category[6]['keys'] = c_data.keys_c7
        
    # cat5
        category[7]['p2count'] = c_data.p2count_c8
        category[7]['p1count'] = c_data.p1count_c8
        category[7]['n1count'] = c_data.n1count_c8
        category[7]['n2count'] = c_data.n2count_c8

        category[7]['p2data'].append(c_data.p2data1_c8)
        category[7]['p1data'].append(c_data.p1data1_c8)
        category[7]['n1data'].append(c_data.n1data1_c8)
        category[7]['n2data'].append(c_data.n2data1_c8)

        category[7]['p2data'].append(c_data.p2data2_c8)
        category[7]['p1data'].append(c_data.p1data2_c8)
        category[7]['n1data'].append(c_data.n1data2_c8)
        category[7]['n2data'].append(c_data.n2data2_c8)

        category[7]['p2data'].append(c_data.p2data3_c8)
        category[7]['p1data'].append(c_data.p1data3_c8)
        category[7]['n1data'].append(c_data.n1data3_c8)
        category[7]['n2data'].append(c_data.n2data3_c8)

        category[7]['p2data'].append(c_data.p2data4_c8)
        category[7]['p1data'].append(c_data.p1data4_c8)
        category[7]['n1data'].append(c_data.n1data4_c8)
        category[7]['n2data'].append(c_data.n2data4_c8)

        category[7]['p2data'].append(c_data.p2data5_c8)
        category[7]['p1data'].append(c_data.p1data5_c8)
        category[7]['n1data'].append(c_data.n1data5_c8)
        category[7]['n2data'].append(c_data.n2data5_c8)

        category[7]['freqs'] = json.loads(c_data.freqs_c8) if c_data.freqs_c8 not in [None,''] else None
        category[7]['category_name'] = c_data.name_c8
        category[7]['keys'] = c_data.keys_c8
        # None除去
        for i in range(8):
            if category[i]['freqs'] == None:
                category[i] = None
                continue
            category[i]['p2data'] = [d for d in category[i]['p2data'] if d != None]
            category[i]['p1data'] = [d for d in category[i]['p1data'] if d != None]
            category[i]['n1data'] = [d for d in category[i]['n1data'] if d != None]
            category[i]['n2data'] = [d for d in category[i]['n2data'] if d != None]

# pref取得
    prefs_c = []
    prefs_m = [] # map用 
    n_prefs_c = None
    n_prefs_m = None
    #print('getting prefs..')
    
    try:        
        prefs_obj = Pref_ranks.objects.values('pref1_name',
                                            'pref2_name',
                                            'pref3_name',
                                            'pref4_name',
                                            'pref5_name',
                                            'pref6_name',
                                            'pref7_name',
                                            'pref8_name',
                                            'pref9_name',
                                            'pref10_name',
                                            'pref1_count',
                                            'pref2_count',
                                            'pref3_count',
                                            'pref4_count',
                                            'pref5_count',
                                            'pref6_count',
                                            'pref7_count',
                                            'pref8_count',
                                            'pref9_count',
                                            'pref10_count',
                                            # 以下n
                                            'pref11_name',
                                            'pref12_name',
                                            'pref13_name',
                                            'pref14_name',
                                            'pref15_name',
                                            'pref16_name',
                                            'pref17_name',
                                            'pref18_name',
                                            'pref19_name',
                                            'pref20_name',
                                            'pref11_count',
                                            'pref12_count',
                                            'pref13_count',
                                            'pref14_count',
                                            'pref15_count',
                                            'pref16_count',
                                            'pref17_count',
                                            'pref18_count',
                                            'pref19_count',
                                            'pref20_count',                                            
                                           ).get(post=post)
    except Pref_ranks.DoesNotExist as e:
        pass
        #print(e)
    else:
        # 炎上マップなし
        if prefs_obj['pref11_name'] == None:
            # 要約,投稿数,ツイートを辞書型に変換
            for i in range(10):
                if prefs_obj['pref{0}_name'.format(i + 1)] == None:
                    prefs_c.append((None,0))
                else:
                    prefs_c.append((prefs_obj['pref{0}_name'.format(i + 1)], prefs_obj['pref{0}_count'.format(i + 1)]))
    ### map用 ##########           
                try:
                    
                    map_id=Prefectures.objects.only('map_id').get(prefecture=prefs_obj['pref{0}_name'.format(i + 1)]).map_id
                    prefs_m.append((map_id, prefs_obj['pref{0}_count'.format(i + 1)]))
    
                except Prefectures.DoesNotExist:
                    prefs_m.append((None,0))
            
            n_prefs_c = None
            n_prefs_m = None
            
        # 炎上マップあり   
        else:
            n_prefs_c = []
            n_prefs_m = []
            # positiveマップ
            for i in range(10):
                if prefs_obj['pref{0}_name'.format(i + 1)] == None:
                    prefs_c.append((None,0))
                else:
                    prefs_c.append((prefs_obj['pref{0}_name'.format(i + 1)], prefs_obj['pref{0}_count'.format(i + 1)]))
    ### map用 ##########           
                try:
                    
                    map_id=Prefectures.objects.only('map_id').get(prefecture=prefs_obj['pref{0}_name'.format(i + 1)]).map_id
                    prefs_m.append((map_id, prefs_obj['pref{0}_count'.format(i + 1)]))
    
                except Prefectures.DoesNotExist:
                    prefs_m.append((None,0))
            # negativeマップ
            for i in range(10,20):
                if prefs_obj['pref{0}_name'.format(i + 1)] == None:
                    n_prefs_c.append(('',0))
                else:
                    n_prefs_c.append((prefs_obj['pref{0}_name'.format(i + 1)], prefs_obj['pref{0}_count'.format(i + 1)]))
    ### map用 ##########           
                try:
                    
                    map_id=Prefectures.objects.only('map_id').get(prefecture=prefs_obj['pref{0}_name'.format(i + 1)]).map_id
                    n_prefs_m.append((map_id, prefs_obj['pref{0}_count'.format(i + 1)]))
    
                except Prefectures.DoesNotExist:
                    n_prefs_m.append((None,0))


# frequency取得
 
    try:
        freqs_obj = Frequentwords.objects.values_list('freq1','freq2','freq3','freq4','freq5','freq6','freq7','freq8','freq9','freq10','freq11','freq12','freq13','freq14','freq15','freq16','freq17','freq18','freq19','freq20','freq21','freq22','freq23','freq24','freq25','freq26','freq27','freq28','freq29','freq30','freq31','freq32','freq33','freq34','freq35','freq36','freq37','freq38','freq39','freq40','freq41','freq42','freq43','freq44','freq45','freq46','freq47','freq48','freq49','freq50',
                                                      'freq1_count','freq2_count','freq3_count','freq4_count','freq5_count','freq6_count','freq7_count','freq8_count','freq9_count','freq10_count','freq11_count','freq12_count','freq13_count','freq14_count','freq15_count','freq16_count','freq17_count','freq18_count','freq19_count','freq20_count','freq21_count','freq22_count','freq23_count','freq24_count','freq25_count','freq26_count','freq27_count','freq28_count','freq29_count','freq30_count','freq31_count','freq32_count','freq33_count','freq34_count','freq35_count','freq36_count','freq37_count','freq38_count','freq39_count','freq40_count','freq41_count','freq42_count','freq43_count','freq44_count','freq45_count','freq46_count','freq47_count','freq48_count','freq49_count','freq50_count'
                                                      ).get(post=post)

    except Frequentwords.DoesNotExist as e:
        freqs_obj = None

    
    period_start = (s_date + datetime.timedelta(hours = 9)).date()
    period_end = (e_date + datetime.timedelta(hours = 9)).date()

# 要約取得

    sum_obj = Tweetdata2.objects.filter(
                                        t_date__range=(s_date,e_date),# 7日前~1日前まで
                                        sum_title_id=record['index'],
                                        sum_title_text__in=[1,2,3,4,5,21,22,23,24,25],
                                        ).values('t_id',
                                                'u_id',
                                                't_date',
                                                'content',
                                                's_name',
                                                'u_name',
                                                'p_image',
                                                's_class',
                                                't_id_char',
                                                'entities_display_url',
                                                'entities_url',
                                                'media_url',
                                                'media_url_truncated',
                                                'sum_title_text',
                                                'hashtag'
                                                ).order_by('media_url')

    # 要約文(1~20)を取得
    try:
        summary_texts = Summarys.objects.values_list(
# positive
                                               'summary_text1',
                                               'summary_text2',
                                               'summary_text3',
                                               'summary_text4',
                                               'summary_text5',
# nega
                                               'summary_text21',
                                               'summary_text22',
                                               'summary_text23',
                                               'summary_text24',
                                               'summary_text25',

                                               'related1_id',
                                               'related2_id',
                                               'related3_id',
                                               'related4_id',
                                               'related5_id',

                                               ).get(post=post)

    except Summarys.DoesNotExist as e:
        return HttpResponse(status=404)

    else:

        # 要約に選ばれたツイート取得
        contents = [[] for i in range(40)] # 0-19positive,20-39negative
        for obj in sum_obj:
            #if safetext(obj['content']):
            contents[obj['sum_title_text'] - 1].append(obj)



        summarys = []
        n_summarys = []
        # 要約,投稿数,ツイートを辞書型に変換
        for i in range(0, 5):
            if summary_texts[i] == None:
                continue
            else:

                summarys.append({'要約':summary_texts[i],
                                 '投稿数':len(contents[i]),
                                 '原文':contents[i][:3],
                                 }
                                )
        # 後で合流した要約の場合投稿数がずれる可能性あるので
        summarys = sorted(summarys,key=lambda x: x['投稿数'],reverse=True)

        for i in range(5, 10):
            if summary_texts[i] == None:
                continue
            else:

                n_summarys.append({'要約':summary_texts[i],
                                   '投稿数':len(contents[15+i]), #20以降
                                   '原文':contents[15+i][:3],
                                  }) # 各要約30投稿のみ表示
        n_summarys = sorted(n_summarys,key=lambda x: x['投稿数'],reverse=True)

        sum_description='' #descriptionおよびツイート共有テキスト用
        for k,s in enumerate(reversed(summarys)):#逆順で5位から見せる
            sum_description += '{0}位:'.format(len(summarys)-k) + s['要約'] + ','
        sum_description = sum_description[:-1] # 最後の,除去

        n_sum_description='' # 現状未使用
        for k,s in enumerate(n_summarys):
            n_sum_description += '{0}位:'.format(len(summarys)-k) + s['要約'] + ','
        n_sum_description = n_sum_description[:-1] # 最後の,除去
          
        # 類似ブランド
        relates = []
        for related_no in summary_texts[10:]:
            if related_no == 0:
                continue
            try:
                related_record = Official_names.objects.get(index=related_no)
            except:
                continue
            if related_record.hidden == True:
                continue
            # 一時的に1話と0話(春アニメ)のみ検索
            related_post = slugify('{0} {1}'.format(related_no,1))
            try:
                statistics = Statistics1week.objects.only(   
                                        'p1_count_d1',
                                        'p1_count_d2',
                                        'p1_count_d3',
                                        'p1_count_d4',
                                        'p1_count_d5',
                                        'p1_count_d6',
                                        'p1_count_d7',
                                        'p2_count_d1',
                                        'p2_count_d2',
                                        'p2_count_d3',
                                        'p2_count_d4',
                                        'p2_count_d5',
                                        'p2_count_d6',
                                        'p2_count_d7',
                                        ).get(post=related_post)
            except Statistics1week.DoesNotExist as e:
                #print(e)
                related_post = slugify('{0} {1}'.format(related_no,0))
                try:
                    statistics = Statistics1week.objects.only(   
                                            'p1_count_d1',
                                            'p1_count_d2',
                                            'p1_count_d3',
                                            'p1_count_d4',
                                            'p1_count_d5',
                                            'p1_count_d6',
                                            'p1_count_d7',
                                            'p2_count_d1',
                                            'p2_count_d2',
                                            'p2_count_d3',
                                            'p2_count_d4',
                                            'p2_count_d5',
                                            'p2_count_d6',
                                            'p2_count_d7',
                                            ).get(post=related_post)
                except Statistics1week.DoesNotExist as e:
                    #print(e)  
                    continue

            # 要約も取得
            summary_exists = True
            try:
                record_summary = Summarys.objects.only(
                                                'summary_text1',
                                                'summary_text2',
                                                'summary_text3',
                                                'summary_text4',
                                                'summary_text5',
                                                 ).get(post=related_post)            
            except Summarys.DoesNotExist as e:
                #print(e)
                summary_exists = False
                
            else:
                pcount = sum([
                        statistics.p1_count_d1,                                            
                        statistics.p1_count_d2,                                            
                        statistics.p1_count_d3,                                            
                        statistics.p1_count_d4,                                            
                        statistics.p1_count_d5,                                            
                        statistics.p1_count_d6,                                            
                        statistics.p1_count_d7,
                        statistics.p2_count_d1,                                            
                        statistics.p2_count_d2,                                            
                        statistics.p2_count_d3,                                            
                        statistics.p2_count_d4,                                            
                        statistics.p2_count_d5,                                            
                        statistics.p2_count_d6,                                            
                        statistics.p2_count_d7
                        ])
                if pcount < 10:
                    continue # 50未満は非表示
                relates.append({'pcount':pcount,
                                'brand':related_record.official_name,
                                'url':related_record.url_name,
                               'summarys':[record_summary.summary_text1 if summary_exists else None,
                                        record_summary.summary_text2 if summary_exists else None,
                                        record_summary.summary_text3 if summary_exists else None,
                                        record_summary.summary_text4 if summary_exists else None,
                                        record_summary.summary_text5 if summary_exists else None
                                        ]                                     
                               })   
# animeページ用　キャラランキング
    # 高評価キャラ
    chara_rank = []
    op_rank = []
    ed_rank = []
    cv_rank = []
    chara_syokai = []
    op_syokai = []
    ed_syokai = []
    cv_syokai= []
    chara_nos = list(Official_names.objects.filter(
                                                   #title=False,
                                                   kind=11,
                                                   title_name=record['title_name'],
                                                   ).values_list('index','official_name','kind','url_name'))

    for chara_no in chara_nos:
        chara_syokai.append(SPC.sub(" ",chara_no[1]))

        chara_post = slugify('{0} {1}'.format(chara_no[0],episode))
        try:
            statistics = Statistics1week.objects.only(
                                       'p1_count_d1',
                                        'p1_count_d2',
                                        'p1_count_d3',
                                        'p1_count_d4',
                                        'p1_count_d5',
                                        'p1_count_d6',
                                        'p1_count_d7',
                                       'p2_count_d1',
                                       'p2_count_d2',
                                       'p2_count_d3',
                                       'p2_count_d4',
                                       'p2_count_d5',
                                       'p2_count_d6',
                                       'p2_count_d7',
                                       ).get(post=chara_post)
        except Statistics1week.DoesNotExist as e:
            #print(e)
            continue

        # 要約も取得

        try:
            record_summary = Summarys.objects.values_list(
                                              'summary_text1',
                                               'summary_text2',
                                               'summary_text3',
                                               'summary_text4',
                                               'summary_text5',
                                               ).get(post=chara_post)
        except Summarys.DoesNotExist as e:
            #print(e)
            continue

        else:
            pcount = sum([
                    statistics.p1_count_d1,
                    statistics.p1_count_d2,
                    statistics.p1_count_d3,
                    statistics.p1_count_d4,
                    statistics.p1_count_d5,
                    statistics.p1_count_d6,
                    statistics.p1_count_d7,
                    statistics.p2_count_d1,
                    statistics.p2_count_d2,
                    statistics.p2_count_d3,
                    statistics.p2_count_d4,
                    statistics.p2_count_d5,
                    statistics.p2_count_d6,
                    statistics.p2_count_d7
                    ])
            #if pcount < MIN_SHOW:
            if pcount < 50:
                continue # 50未満は非表示


            # charaの場合
            # charaの場合
            chara_rank.append({'pcount':pcount,
                               'brand':SPC.sub(" ",chara_no[1]),
                               'url':chara_no[3],
                               'anime_url':name,
                               'summarys':record_summary,
                               })

    chara_rank = sorted(chara_rank, key=lambda x:x['pcount'], reverse=True) # pcount順に並び替え
    chara_syokai = sorted(chara_syokai,reverse=True) if len(chara_syokai) > 0 else None

# Abouts
    try:
        about = Abouts.objects.values('story','p_soukatsu','n_soukatsu').get(official_name_id=record['index'])  
    except Abouts.DoesNotExist as e:
        #print(e)
        about = None
# Oadates
    try:
        oadates = Oadates.objects.values(
                        'episode1',
                        'episode2',
                        'episode3',
                        'episode4',
                        'episode5',
                        'episode6',
                        'episode7',
                        'episode8',
                        'episode9',
                        'episode10',
                        'episode11',
                        'episode12',
                        'episode13',
                        'episode14',
                        'episode15',
                        'episode16',
                        'episode17',
                        'episode18',
                        'episode19',
                        'episode20',
                        'episode21',
                        'episode22',
                        'episode23',
                        'episode24',
                        'episode25',
                        'episode26',
                        'episode27',
                        'episode28',
                        'episode29',
                        'episode30',
                        'episode_title1',
                        'episode_title2',
                        'episode_title3',
                        'episode_title4',
                        'episode_title5',
                        'episode_title6',
                        'episode_title7',
                        'episode_title8',
                        'episode_title9',
                        'episode_title10',
                        'episode_title11',
                        'episode_title12',
                        'episode_title13',
                        'episode_title14',
                        'episode_title15',
                        'episode_title16',
                        'episode_title17',
                        'episode_title18',
                        'episode_title19',
                        'episode_title20',
                        'episode_title21',
                        'episode_title22',
                        'episode_title23',
                        'episode_title24',
                        'episode_title25',
                        'episode_title26',
                        'episode_title27',
                        'episode_title28',
                        'episode_title29',
                        'episode_title30',                        
                        'title_tag1',
                        'title_tag2',
                        'title_tag3',
                        'title_tag4',
                        'title_tag5',
                        'title_tag6',
                        'title_tag7',
                        'title_tag8',
                        'title_tag9',
                        'title_tag10',
                        'title_tag11',
                        'title_tag12',
                        'title_tag13',
                        'title_tag14',
                        'title_tag15',
                        'title_tag16',
                        'title_tag17',
                        'title_tag18',
                        'title_tag19',
                        'title_tag20',
                        'title_tag21',
                        'title_tag22',
                        'title_tag23',
                        'title_tag24',
                        'title_tag25',
                        'title_tag26',
                        'title_tag27',
                        'title_tag28',
                        'title_tag29',
                        'title_tag30',
                        'outline1',
                        'outline2',
                        'outline3',
                        'outline4',
                        'outline5',
                        'outline6',
                        'outline7',
                        'outline8',
                        'outline9',
                        'outline10',
                        'outline11',
                        'outline12',
                        'outline13',
                        'outline14',
                        'outline15',
                        'outline16',
                        'outline17',
                        'outline18',
                        'outline19',
                        'outline20',
                        'outline21',
                        'outline22',
                        'outline23',
                        'outline24',
                        'outline25',
                        'outline26',
                        'outline27',
                        'outline28',
                        'outline29',
                        'outline30',
                        ).get(official_name_id=record['index'])

    except Oadates.DoesNotExist as e:
        #print(e)
        oadates = None        
        title_tag = None
        outline = None
    else:
        title_tag = oadates['title_tag{0}'.format(episode)] if episode != 0 else None
        title_episode = oadates['episode_title{0}'.format(episode)]
        outline = oadates['outline{0}'.format(episode)] if episode != 0 else None
        oadates = [{
                    'episode':oadates['episode{0}'.format(i)], # 日付
                    'episode_title':oadates['episode_title{0}'.format(i)], # サブタイトル
                    'link_exist':True if Summarys.objects.filter(post = slugify('{0} {1}'.format(record['index'],i))).exists() else False,
                    } for i in range(1,31)]

                                     
    #print(oadates)
    if oadates[0]['episode'] == None or oadates[0]['episode_title'] == None:
        oadates = None

 
    prevlink = False    
    
    
# fanart
    try:
        # 各週で取得        
        fanarts_id = list(Fanarts.objects.values_list(
                                                  'fan_art1_id',
                                                  'fan_art2_id',
                                                  'fan_art3_id',
                                                  'fan_art4_id',
                                                  'fan_art5_id',
                                                  'fan_art6_id',
                                                  'fan_art7_id',
                                                  'fan_art8_id',
                                                  'fan_art9_id',
                                                  'fan_art10_id',
                                                 ).get(post=post))
        
    except Fanarts.DoesNotExist as e:
        #print(e)
        fanarts = None
    else:
        tmp_l = []
        for f in fanarts_id:
            if f != None:
                tmp_l.append(f)
            else:
                #break
                continue
        fanarts_id = tmp_l
        #print('fanarts id',fanarts_id)
        if len(fanarts_id) in [0,1]:
            fanarts = None
        else:
            fanarts = Tweetdata2.objects.only('t_id',
                                                'media_url',
                                                'media_url_truncated',
                                                'u_id',
                                                'p_image',
                                                ).filter(
                                                t_id__in=fanarts_id
                                                )[:10]
    #print("ok")
    params = {
            'category':category,

            'title':'プラコメ',
            'data_num':p_num + n_num,
            'p_num':p_num,
            'n_num':n_num,
            'p2_num':p2_num,
            'n2_num':n2_num,
            'p1_num':p1_num,
            'n1_num':n1_num,    
            'p2_counts':p2_counts,
            'p1_counts':p1_counts,            
            'n1_counts':n1_counts,
            'n2_counts':n2_counts,
            'pn_counts_date':json.dumps(pn_counts_date),
            'pn_counts_date_text':pn_counts_date,   
            'period_start':period_start,
            'period_end':period_end,
            'locations':prefs_c,
            'locations_map':prefs_m,
            'n_locations':n_prefs_c,
            'n_locations_map':n_prefs_m,

            'trend_obj':None,
            'freqs_obj':freqs_obj,

            'name':name,
            'title_name':SPC.sub(" ",record['title_name']),
            'summarys':summarys[:5],
            'n_summarys':n_summarys[:5],
            'events':long_event_dic,
            'chara_rank':chara_rank,
            'op_rank':op_rank,
            'ed_rank':ed_rank,
            'cv_rank':cv_rank,
            'chara_syokai':chara_syokai,
            'op_syokai':op_syokai,            
            'ed_syokai':ed_syokai,            
            'cv_syokai':cv_syokai,
            'relates':relates,
            'about':about,
            'short_name':SPC.sub(' ',record['short_name']),
            'past':record['past'], #tmp
            'oadates':oadates,
            'episode':episode,
            'title_episode':title_episode,
            'prevlink':prevlink,
            'title_tag':title_tag,
            'fanarts':fanarts,
            'post':post_sta,
            'comments': comments,
            'comment_form':comment_form,
            'outline':outline,
            'n_sum_description':n_sum_description,
            'sum_description':sum_description,
        }

    return render(request,'sentiment/johnnys/johnnys.html',params)



def chk_media(dic):
    return True if dic['media_url'] != None else False


def anime_episode2(request,name,episode=0):

    pn_counts_date=[] # 投稿日付（グラフ横軸)
    locations=[]
    '''
    CharField.register_lookup(Length, 'length') #  registered as a transform
    
    character_filter = request.POST.get('character_filter')
    anime_filter = request.POST.get('anime_filter')
    anime_filter2 = request.POST.get('Search')
    '''

    try:        
        record = Official_names.objects.values('index',
                                               'kind',
                                               'title_name',
                                               'hidden',
                                               'past',
                                               'short_name',
                                               ).get(url_name=name)

    except Official_names.DoesNotExist as e:
        return HttpResponse(status=410)
        raise Http404("Page does not exist.")
    
    if record['kind'] != 0 or record['hidden'] == True: # charaページにアクセスしようとした場合
        return HttpResponse(status=410)
        raise Http404("Page does not exist.")
    
### purakome.com to purakome.net    
    #if request.META.get("HTTP_HOST") == r'purakome.com':
        #return HttpResponse(status=410)
###

    #print('requestpath',request.path) # 春アニメで sentiment/anime/kimetsu/0/でアクセスできてしまうのを防ぐ
    if episode == 0 and request.path[-3:] == r'/0/':
        return redirect(r'https://purakome.net/sentiment/anime/{0}/'.format(name),permanent=True)

# コメント
    post = slugify('{0} {1}'.format(record['index'],episode))
    #print('post2',post)

    post_sta=get_object_or_404(Statistics1week,post=post)

    #print('post   id',post_sta.id)
    # List of active comments for this post
    comments = Comment.objects.filter(target=post_sta.post,
                                      #parent_id=None,
                                      active=True)
    new_comment = None

    comment_form = CommentForm()
    if request.method == 'POST':
        #print('POST')
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.target = post_sta.post
            # Save the comment to the database
            new_comment.save()
            # redirect to same page and focus on that comment
            '''
            if episode == 0:
                return redirect(r'sentiment/anime/{0}/'.format(name)+'#'+str(new_comment.id))
            elif episode > 0:
                return redirect(r'sentiment/anime/{0}/{1}/'.format(name,episode)+'#'+str(new_comment.id))
            '''
        else:
            comment_form = CommentForm()


# statisticsと日時取得        
    #print("statistics access")
    try:

        statistics = Statistics1week.objects.values('s_date','e_date','p2_count_d1', 'p1_count_d1','n2_count_d1', 'n1_count_d1',
                                            'p2_count_d2', 'p1_count_d2','n2_count_d2', 'n1_count_d2',
                                            'p2_count_d3', 'p1_count_d3','n2_count_d3', 'n1_count_d3',
                                            'p2_count_d4', 'p1_count_d4','n2_count_d4', 'n1_count_d4',
                                            'p2_count_d5', 'p1_count_d5','n2_count_d5', 'n1_count_d5',
                                            'p2_count_d6', 'p1_count_d6','n2_count_d6', 'n1_count_d6',
                                            'p2_count_d7', 'p1_count_d7','n2_count_d7', 'n1_count_d7',
                                            'ep_tweet1_id','ep_tweet2_id','ep_tweet3_id','ep_tweet4_id',
                                            'ep_tweet5_id','ep_tweet6_id','ep_tweet7_id','ep_tweet8_id',
                                            'ep_tweet9_id','ep_tweet10_id',
                                            'en_tweet1_id','en_tweet2_id','en_tweet3_id','en_tweet4_id',
                                            'en_tweet5_id','en_tweet6_id','en_tweet7_id','en_tweet8_id',
                                            'en_tweet9_id','en_tweet10_id'
                                            ).get(post=post)

    except Statistics1week.DoesNotExist as e:
        #print(e)
        return HttpResponse(status=410)


    s_date = statistics['s_date']
    e_date = statistics['e_date']
    #print('s_date',s_date)
    #print('e_date',e_date)

    p2_counts=[0,0,0,0,0,0]# 日付ごとの投稿数(グラフ縦軸)
    p1_counts=[0,0,0,0,0,0]# 日付ごとの投稿数(グラフ縦軸)
    n1_counts=[0,0,0,0,0,0]# 日付ごとの投稿数(グラフ縦軸)
    n2_counts=[0,0,0,0,0,0]
    pn_counts_date=[] # 投稿日付（グラフ横軸)
    for i in range(6):
        p2_counts[i] = statistics['p2_count_d{0}'.format(6-i)]
        p1_counts[i] = statistics['p1_count_d{0}'.format(6-i)]
        n2_counts[i] = statistics['n2_count_d{0}'.format(6-i)]
        n1_counts[i] = statistics['n1_count_d{0}'.format(6-i)]


    for i in range(6):
        d = (e_date + datetime.timedelta(hours=9)).date() - datetime.timedelta(days = 5 - i)
        pn_counts_date.append(str(d.month)+'月'+str(d.day)+'日')

    p2_num = sum(p2_counts)
    p1_num = sum(p1_counts)
    p_num = p2_num + p1_num

    '''
    if p_num < MIN_SHOW:
        return HttpResponse(status=410)
        raise Http404("Page does not exist.")
    '''
    n2_num = sum(n2_counts)
    n1_num = sum(n1_counts)
    n_num = n2_num + n1_num

# eng data
    en_index = []
    en_reaction = []
    ep_reaction = []
 
    for i in range(10):
        if statistics['en_tweet{0}_id'.format(i+1)]!=None:
            en_index.append(statistics['en_tweet{0}_id'.format(i+1)])
        if statistics['ep_tweet{0}_id'.format(i+1)]!=None:
            en_index.append(statistics['ep_tweet{0}_id'.format(i+1)])

    if len(en_index) > 0:
        e_reaction = Tweetdata2.objects.filter(
                                            t_id__in=en_index,
                                            ).values('t_id',
                                                    'u_id',
                                                    't_date',
                                                    'content',
                                                    's_name',
                                                    'u_name',
                                                    'p_image',
                                                    's_class',
                                                    't_id_char',
                                                    'entities_display_url',
                                                    'entities_url',
                                                    'media_url',
                                                    'media_url_truncated',
                                                    'sum_title_text',
                                                    'hashtag',
                                                    'translate',
                                                    )

        for r in e_reaction:
            if r['s_class'] == 1:
                en_reaction.append(r)
            elif r['s_class'] == 3:
                ep_reaction.append(r)

# news取得       
    long_event_dic = Longevents.objects.filter(
                                              (Q(date_s__lte=e_date) & Q(date_e__gte=s_date)) | (Q(date_e__gte=s_date) & Q(date_s__lte=e_date)),
                                               Q(official_name_id=record['index']),
                                               #Q(date_s__range=(s_date,e_date)) | Q(date_e__range=(s_date,e_date)),
                                               
                                               # 1週間の最後の日付よりもイベントの開始日付が遅い場合は該当外
                                               # イベントの終了日付が1週間の最初の日付よりも早い場合は該当外
                                               Q(title__isnull=False), # titleが空欄以外
                                               ).values( 
                                                        #'official_name',
                                                        #'url',
                                                        'title',
                                                        'date_s',
                                                        'date_e',
                                                        'time_s',
                                                        'time_e',
                                                        'weekday',
                                                        'media',
                                                        'channel',
                                                        'title'
                                                         )[:5]


# category
    category=[{'p2count':0,'p1count':0,'n1count':0,'n2count':0,
               'p2data':[],'p1data':[],'n1data':[],'n2data':[],
               'freqs':[],'category_name':[],'keys':''} for i in range(8)]
    try:
        c_data = Categorys.objects.only(
                                'name_c1',
                                'name_c2',
                                'name_c3',
                                'name_c4',
                                'name_c5',
                                'name_c6',
                                'name_c7',
                                'name_c8',
                                'freqs_c1',
                                'freqs_c2',
                                'freqs_c3',
                                'freqs_c4',
                                'freqs_c5',
                                'freqs_c6',
                                'freqs_c7',
                                'freqs_c8',
                                'keys_c1',
                                'keys_c2',
                                'keys_c3',
                                'keys_c4',
                                'keys_c5',
                                'keys_c6',
                                'keys_c7',
                                'keys_c8',
                                'p2count_c1',
                                'p1count_c1',
                                'n1count_c1',
                                'n2count_c1',
                                'p2count_c2',
                                'p1count_c2',
                                'n1count_c2',
                                'n2count_c2',
                                'p2count_c3',
                                'p1count_c3',
                                'n1count_c3',
                                'n2count_c3',
                                'p2count_c4',
                                'p1count_c4',
                                'n1count_c4',
                                'n2count_c4',
                                'p2count_c5',
                                'p1count_c5',
                                'n1count_c5',
                                'n2count_c5',

                                'p2data1_c1',
                                'p2data2_c1',
                                'p2data3_c1',
                                'p2data4_c1',
                                'p2data5_c1',
                                'p1data1_c1',
                                'p1data2_c1',
                                'p1data3_c1',
                                'p1data4_c1',
                                'p1data5_c1',
                                'n1data1_c1',
                                'n1data2_c1',
                                'n1data3_c1',
                                'n1data4_c1',
                                'n1data5_c1',
                                'n2data1_c1',
                                'n2data2_c1',
                                'n2data3_c1',
                                'n2data4_c1',
                                'n2data5_c1',

                                'p2data1_c2',
                                'p2data2_c2',
                                'p2data3_c2',
                                'p2data4_c2',
                                'p2data5_c2',
                                'p1data1_c2',
                                'p1data2_c2',
                                'p1data3_c2',
                                'p1data4_c2',
                                'p1data5_c2',
                                'n1data1_c2',
                                'n1data2_c2',
                                'n1data3_c2',
                                'n1data4_c2',
                                'n1data5_c2',
                                'n2data1_c2',
                                'n2data2_c2',
                                'n2data3_c2',
                                'n2data4_c2',
                                'n2data5_c2',

                                'p2data1_c3',
                                'p2data2_c3',
                                'p2data3_c3',
                                'p2data4_c3',
                                'p2data5_c3',
                                'p1data1_c3',
                                'p1data2_c3',
                                'p1data3_c3',
                                'p1data4_c3',
                                'p1data5_c3',
                                'n1data1_c3',
                                'n1data2_c3',
                                'n1data3_c3',
                                'n1data4_c3',
                                'n1data5_c3',
                                'n2data1_c3',
                                'n2data2_c3',
                                'n2data3_c3',
                                'n2data4_c3',
                                'n2data5_c3',

                                'p2data1_c4',
                                'p2data2_c4',
                                'p2data3_c4',
                                'p2data4_c4',
                                'p2data5_c4',
                                'p1data1_c4',
                                'p1data2_c4',
                                'p1data3_c4',
                                'p1data4_c4',
                                'p1data5_c4',
                                'n1data1_c4',
                                'n1data2_c4',
                                'n1data3_c4',
                                'n1data4_c4',
                                'n1data5_c4',
                                'n2data1_c4',
                                'n2data2_c4',
                                'n2data3_c4',
                                'n2data4_c4',
                                'n2data5_c4',

                                'p2data1_c5',
                                'p2data2_c5',
                                'p2data3_c5',
                                'p2data4_c5',
                                'p2data5_c5',
                                'p1data1_c5',
                                'p1data2_c5',
                                'p1data3_c5',
                                'p1data4_c5',
                                'p1data5_c5',
                                'n1data1_c5',
                                'n1data2_c5',
                                'n1data3_c5',
                                'n1data4_c5',
                                'n1data5_c5',
                                'n2data1_c5',
                                'n2data2_c5',
                                'n2data3_c5',
                                'n2data4_c5',
                                'n2data5_c5',
                                
                                'p2data1_c6',
                                'p2data2_c6',
                                'p2data3_c6',
                                'p2data4_c6',
                                'p2data5_c6',
                                'p1data1_c6',
                                'p1data2_c6',
                                'p1data3_c6',
                                'p1data4_c6',
                                'p1data5_c6',
                                'n1data1_c6',
                                'n1data2_c6',
                                'n1data3_c6',
                                'n1data4_c6',
                                'n1data5_c6',
                                'n2data1_c6',
                                'n2data2_c6',
                                'n2data3_c6',
                                'n2data4_c6',
                                'n2data5_c6',
                                
                                'p2data1_c7',
                                'p2data2_c7',
                                'p2data3_c7',
                                'p2data4_c7',
                                'p2data5_c7',
                                'p1data1_c7',
                                'p1data2_c7',
                                'p1data3_c7',
                                'p1data4_c7',
                                'p1data5_c7',
                                'n1data1_c7',
                                'n1data2_c7',
                                'n1data3_c7',
                                'n1data4_c7',
                                'n1data5_c7',
                                'n2data1_c7',
                                'n2data2_c7',
                                'n2data3_c7',
                                'n2data4_c7',
                                'n2data5_c7',
                                
                                'p2data1_c8',
                                'p2data2_c8',
                                'p2data3_c8',
                                'p2data4_c8',
                                'p2data5_c8',
                                'p1data1_c8',
                                'p1data2_c8',
                                'p1data3_c8',
                                'p1data4_c8',
                                'p1data5_c8',
                                'n1data1_c8',
                                'n1data2_c8',
                                'n1data3_c8',
                                'n1data4_c8',
                                'n1data5_c8',
                                'n2data1_c8',
                                'n2data2_c8',
                                'n2data3_c8',
                                'n2data4_c8',
                                'n2data5_c8',
                                 ).get(post=post)
    except Categorys.DoesNotExist as e:
        category=None

    else:
    # cat1
        category[0]['p2count'] = c_data.p2count_c1
        category[0]['p1count'] = c_data.p1count_c1
        category[0]['n1count'] = c_data.n1count_c1
        category[0]['n2count'] = c_data.n2count_c1

        category[0]['p2data'].append(c_data.p2data1_c1)
        category[0]['p1data'].append(c_data.p1data1_c1)
        category[0]['n1data'].append(c_data.n1data1_c1)
        category[0]['n2data'].append(c_data.n2data1_c1)

        category[0]['p2data'].append(c_data.p2data2_c1)
        category[0]['p1data'].append(c_data.p1data2_c1)
        category[0]['n1data'].append(c_data.n1data2_c1)
        category[0]['n2data'].append(c_data.n2data2_c1)

        category[0]['p2data'].append(c_data.p2data3_c1)
        category[0]['p1data'].append(c_data.p1data3_c1)
        category[0]['n1data'].append(c_data.n1data3_c1)
        category[0]['n2data'].append(c_data.n2data3_c1)

        category[0]['p2data'].append(c_data.p2data4_c1)
        category[0]['p1data'].append(c_data.p1data4_c1)
        category[0]['n1data'].append(c_data.n1data4_c1)
        category[0]['n2data'].append(c_data.n2data4_c1)

        category[0]['p2data'].append(c_data.p2data5_c1)
        category[0]['p1data'].append(c_data.p1data5_c1)
        category[0]['n1data'].append(c_data.n1data5_c1)
        category[0]['n2data'].append(c_data.n2data5_c1)

        category[0]['freqs'] = json.loads(c_data.freqs_c1) if c_data.freqs_c1 not in [None,''] else None
        category[0]['category_name'] = c_data.name_c1
        category[0]['keys'] = c_data.keys_c1
    # cat2
        category[1]['p2count'] = c_data.p2count_c2
        category[1]['p1count'] = c_data.p1count_c2
        category[1]['n1count'] = c_data.n1count_c2
        category[1]['n2count'] = c_data.n2count_c2

        category[1]['p2data'].append(c_data.p2data1_c2)
        category[1]['p1data'].append(c_data.p1data1_c2)
        category[1]['n1data'].append(c_data.n1data1_c2)
        category[1]['n2data'].append(c_data.n2data1_c2)

        category[1]['p2data'].append(c_data.p2data2_c2)
        category[1]['p1data'].append(c_data.p1data2_c2)
        category[1]['n1data'].append(c_data.n1data2_c2)
        category[1]['n2data'].append(c_data.n2data2_c2)

        category[1]['p2data'].append(c_data.p2data3_c2)
        category[1]['p1data'].append(c_data.p1data3_c2)
        category[1]['n1data'].append(c_data.n1data3_c2)
        category[1]['n2data'].append(c_data.n2data3_c2)

        category[1]['p2data'].append(c_data.p2data4_c2)
        category[1]['p1data'].append(c_data.p1data4_c2)
        category[1]['n1data'].append(c_data.n1data4_c2)
        category[1]['n2data'].append(c_data.n2data4_c2)

        category[1]['p2data'].append(c_data.p2data5_c2)
        category[1]['p1data'].append(c_data.p1data5_c2)
        category[1]['n1data'].append(c_data.n1data5_c2)
        category[1]['n2data'].append(c_data.n2data5_c2)

        category[1]['freqs'] = json.loads(c_data.freqs_c2) if c_data.freqs_c2 not in [None,''] else None
        category[1]['category_name'] = c_data.name_c2
        category[1]['keys'] = c_data.keys_c2
    # cat3
        category[2]['p2count'] = c_data.p2count_c3
        category[2]['p1count'] = c_data.p1count_c3
        category[2]['n1count'] = c_data.n1count_c3
        category[2]['n2count'] = c_data.n2count_c3

        category[2]['p2data'].append(c_data.p2data1_c3)
        category[2]['p1data'].append(c_data.p1data1_c3)
        category[2]['n1data'].append(c_data.n1data1_c3)
        category[2]['n2data'].append(c_data.n2data1_c3)

        category[2]['p2data'].append(c_data.p2data2_c3)
        category[2]['p1data'].append(c_data.p1data2_c3)
        category[2]['n1data'].append(c_data.n1data2_c3)
        category[2]['n2data'].append(c_data.n2data2_c3)

        category[2]['p2data'].append(c_data.p2data3_c3)
        category[2]['p1data'].append(c_data.p1data3_c3)
        category[2]['n1data'].append(c_data.n1data3_c3)
        category[2]['n2data'].append(c_data.n2data3_c3)

        category[2]['p2data'].append(c_data.p2data4_c3)
        category[2]['p1data'].append(c_data.p1data4_c3)
        category[2]['n1data'].append(c_data.n1data4_c3)
        category[2]['n2data'].append(c_data.n2data4_c3)

        category[2]['p2data'].append(c_data.p2data5_c3)
        category[2]['p1data'].append(c_data.p1data5_c3)
        category[2]['n1data'].append(c_data.n1data5_c3)
        category[2]['n2data'].append(c_data.n2data5_c3)

        category[2]['freqs'] = json.loads(c_data.freqs_c3) if c_data.freqs_c3 not in [None,''] else None
        category[2]['category_name'] = c_data.name_c3
        category[2]['keys'] = c_data.keys_c3
    # cat4
        category[3]['p2count'] = c_data.p2count_c4
        category[3]['p1count'] = c_data.p1count_c4
        category[3]['n1count'] = c_data.n1count_c4
        category[3]['n2count'] = c_data.n2count_c4

        category[3]['p2data'].append(c_data.p2data1_c4)
        category[3]['p1data'].append(c_data.p1data1_c4)
        category[3]['n1data'].append(c_data.n1data1_c4)
        category[3]['n2data'].append(c_data.n2data1_c4)

        category[3]['p2data'].append(c_data.p2data2_c4)
        category[3]['p1data'].append(c_data.p1data2_c4)
        category[3]['n1data'].append(c_data.n1data2_c4)
        category[3]['n2data'].append(c_data.n2data2_c4)

        category[3]['p2data'].append(c_data.p2data3_c4)
        category[3]['p1data'].append(c_data.p1data3_c4)
        category[3]['n1data'].append(c_data.n1data3_c4)
        category[3]['n2data'].append(c_data.n2data3_c4)

        category[3]['p2data'].append(c_data.p2data4_c4)
        category[3]['p1data'].append(c_data.p1data4_c4)
        category[3]['n1data'].append(c_data.n1data4_c4)
        category[3]['n2data'].append(c_data.n2data4_c4)

        category[3]['p2data'].append(c_data.p2data5_c4)
        category[3]['p1data'].append(c_data.p1data5_c4)
        category[3]['n1data'].append(c_data.n1data5_c4)
        category[3]['n2data'].append(c_data.n2data5_c4)

        category[3]['freqs'] = json.loads(c_data.freqs_c4) if c_data.freqs_c4 not in [None,''] else None
        category[3]['category_name'] = c_data.name_c4
        category[3]['keys'] = c_data.keys_c4
    # cat5
        category[4]['p2count'] = c_data.p2count_c5
        category[4]['p1count'] = c_data.p1count_c5
        category[4]['n1count'] = c_data.n1count_c5
        category[4]['n2count'] = c_data.n2count_c5

        category[4]['p2data'].append(c_data.p2data1_c5)
        category[4]['p1data'].append(c_data.p1data1_c5)
        category[4]['n1data'].append(c_data.n1data1_c5)
        category[4]['n2data'].append(c_data.n2data1_c5)

        category[4]['p2data'].append(c_data.p2data2_c5)
        category[4]['p1data'].append(c_data.p1data2_c5)
        category[4]['n1data'].append(c_data.n1data2_c5)
        category[4]['n2data'].append(c_data.n2data2_c5)

        category[4]['p2data'].append(c_data.p2data3_c5)
        category[4]['p1data'].append(c_data.p1data3_c5)
        category[4]['n1data'].append(c_data.n1data3_c5)
        category[4]['n2data'].append(c_data.n2data3_c5)

        category[4]['p2data'].append(c_data.p2data4_c5)
        category[4]['p1data'].append(c_data.p1data4_c5)
        category[4]['n1data'].append(c_data.n1data4_c5)
        category[4]['n2data'].append(c_data.n2data4_c5)

        category[4]['p2data'].append(c_data.p2data5_c5)
        category[4]['p1data'].append(c_data.p1data5_c5)
        category[4]['n1data'].append(c_data.n1data5_c5)
        category[4]['n2data'].append(c_data.n2data5_c5)

        category[4]['freqs'] = json.loads(c_data.freqs_c5) if c_data.freqs_c5 not in [None,''] else None
        category[4]['category_name'] = c_data.name_c5
        category[4]['keys'] = c_data.keys_c5

    # cat5
        category[5]['p2count'] = c_data.p2count_c6
        category[5]['p1count'] = c_data.p1count_c6
        category[5]['n1count'] = c_data.n1count_c6
        category[5]['n2count'] = c_data.n2count_c6

        category[5]['p2data'].append(c_data.p2data1_c6)
        category[5]['p1data'].append(c_data.p1data1_c6)
        category[5]['n1data'].append(c_data.n1data1_c6)
        category[5]['n2data'].append(c_data.n2data1_c6)

        category[5]['p2data'].append(c_data.p2data2_c6)
        category[5]['p1data'].append(c_data.p1data2_c6)
        category[5]['n1data'].append(c_data.n1data2_c6)
        category[5]['n2data'].append(c_data.n2data2_c6)

        category[5]['p2data'].append(c_data.p2data3_c6)
        category[5]['p1data'].append(c_data.p1data3_c6)
        category[5]['n1data'].append(c_data.n1data3_c6)
        category[5]['n2data'].append(c_data.n2data3_c6)

        category[5]['p2data'].append(c_data.p2data4_c6)
        category[5]['p1data'].append(c_data.p1data4_c6)
        category[5]['n1data'].append(c_data.n1data4_c6)
        category[5]['n2data'].append(c_data.n2data4_c6)

        category[5]['p2data'].append(c_data.p2data5_c6)
        category[5]['p1data'].append(c_data.p1data5_c6)
        category[5]['n1data'].append(c_data.n1data5_c6)
        category[5]['n2data'].append(c_data.n2data5_c6)

        category[5]['freqs'] = json.loads(c_data.freqs_c6) if c_data.freqs_c6 not in [None,''] else None
        category[5]['category_name'] = c_data.name_c6
        category[5]['keys'] = c_data.keys_c6
        
    # cat5
        category[6]['p2count'] = c_data.p2count_c7
        category[6]['p1count'] = c_data.p1count_c7
        category[6]['n1count'] = c_data.n1count_c7
        category[6]['n2count'] = c_data.n2count_c7

        category[6]['p2data'].append(c_data.p2data1_c7)
        category[6]['p1data'].append(c_data.p1data1_c7)
        category[6]['n1data'].append(c_data.n1data1_c7)
        category[6]['n2data'].append(c_data.n2data1_c7)

        category[6]['p2data'].append(c_data.p2data2_c7)
        category[6]['p1data'].append(c_data.p1data2_c7)
        category[6]['n1data'].append(c_data.n1data2_c7)
        category[6]['n2data'].append(c_data.n2data2_c7)

        category[6]['p2data'].append(c_data.p2data3_c7)
        category[6]['p1data'].append(c_data.p1data3_c7)
        category[6]['n1data'].append(c_data.n1data3_c7)
        category[6]['n2data'].append(c_data.n2data3_c7)

        category[6]['p2data'].append(c_data.p2data4_c7)
        category[6]['p1data'].append(c_data.p1data4_c7)
        category[6]['n1data'].append(c_data.n1data4_c7)
        category[6]['n2data'].append(c_data.n2data4_c7)

        category[6]['p2data'].append(c_data.p2data5_c7)
        category[6]['p1data'].append(c_data.p1data5_c7)
        category[6]['n1data'].append(c_data.n1data5_c7)
        category[6]['n2data'].append(c_data.n2data5_c7)

        category[6]['freqs'] = json.loads(c_data.freqs_c7) if c_data.freqs_c7 not in [None,''] else None
        category[6]['category_name'] = c_data.name_c7
        category[6]['keys'] = c_data.keys_c7
        
    # cat5
        category[7]['p2count'] = c_data.p2count_c8
        category[7]['p1count'] = c_data.p1count_c8
        category[7]['n1count'] = c_data.n1count_c8
        category[7]['n2count'] = c_data.n2count_c8

        category[7]['p2data'].append(c_data.p2data1_c8)
        category[7]['p1data'].append(c_data.p1data1_c8)
        category[7]['n1data'].append(c_data.n1data1_c8)
        category[7]['n2data'].append(c_data.n2data1_c8)

        category[7]['p2data'].append(c_data.p2data2_c8)
        category[7]['p1data'].append(c_data.p1data2_c8)
        category[7]['n1data'].append(c_data.n1data2_c8)
        category[7]['n2data'].append(c_data.n2data2_c8)

        category[7]['p2data'].append(c_data.p2data3_c8)
        category[7]['p1data'].append(c_data.p1data3_c8)
        category[7]['n1data'].append(c_data.n1data3_c8)
        category[7]['n2data'].append(c_data.n2data3_c8)

        category[7]['p2data'].append(c_data.p2data4_c8)
        category[7]['p1data'].append(c_data.p1data4_c8)
        category[7]['n1data'].append(c_data.n1data4_c8)
        category[7]['n2data'].append(c_data.n2data4_c8)

        category[7]['p2data'].append(c_data.p2data5_c8)
        category[7]['p1data'].append(c_data.p1data5_c8)
        category[7]['n1data'].append(c_data.n1data5_c8)
        category[7]['n2data'].append(c_data.n2data5_c8)

        category[7]['freqs'] = json.loads(c_data.freqs_c8) if c_data.freqs_c8 not in [None,''] else None
        category[7]['category_name'] = c_data.name_c8
        category[7]['keys'] = c_data.keys_c8
        # None除去
        for i in range(8):
            if category[i]['freqs'] == None:
                category[i] = None
                continue
            category[i]['p2data'] = [d for d in category[i]['p2data'] if d != None]
            category[i]['p1data'] = [d for d in category[i]['p1data'] if d != None]
            category[i]['n1data'] = [d for d in category[i]['n1data'] if d != None]
            category[i]['n2data'] = [d for d in category[i]['n2data'] if d != None]

# pref取得
    prefs_c = []
    prefs_m = [] # map用 
    n_prefs_c = None
    n_prefs_m = None
    #print('getting prefs..')
    
    try:        
        prefs_obj = Pref_ranks.objects.values('pref1_name',
                                            'pref2_name',
                                            'pref3_name',
                                            'pref4_name',
                                            'pref5_name',
                                            'pref6_name',
                                            'pref7_name',
                                            'pref8_name',
                                            'pref9_name',
                                            'pref10_name',
                                            'pref1_count',
                                            'pref2_count',
                                            'pref3_count',
                                            'pref4_count',
                                            'pref5_count',
                                            'pref6_count',
                                            'pref7_count',
                                            'pref8_count',
                                            'pref9_count',
                                            'pref10_count',
                                            # 以下n
                                            'pref11_name',
                                            'pref12_name',
                                            'pref13_name',
                                            'pref14_name',
                                            'pref15_name',
                                            'pref16_name',
                                            'pref17_name',
                                            'pref18_name',
                                            'pref19_name',
                                            'pref20_name',
                                            'pref11_count',
                                            'pref12_count',
                                            'pref13_count',
                                            'pref14_count',
                                            'pref15_count',
                                            'pref16_count',
                                            'pref17_count',
                                            'pref18_count',
                                            'pref19_count',
                                            'pref20_count',                                            
                                           ).get(post=post)
    except Pref_ranks.DoesNotExist as e:
        pass
        #print(e)
    else:
        # 炎上マップなし
        if prefs_obj['pref11_name'] == None:
            # 要約,投稿数,ツイートを辞書型に変換
            for i in range(10):
                if prefs_obj['pref{0}_name'.format(i + 1)] == None:
                    prefs_c.append((None,0))
                else:
                    prefs_c.append((prefs_obj['pref{0}_name'.format(i + 1)], prefs_obj['pref{0}_count'.format(i + 1)]))
    ### map用 ##########           
                try:
                    
                    map_id=Prefectures.objects.only('map_id').get(prefecture=prefs_obj['pref{0}_name'.format(i + 1)]).map_id
                    prefs_m.append((map_id, prefs_obj['pref{0}_count'.format(i + 1)]))
    
                except Prefectures.DoesNotExist:
                    prefs_m.append((None,0))
            
            n_prefs_c = None
            n_prefs_m = None
            
        # 炎上マップあり   
        else:
            n_prefs_c = []
            n_prefs_m = []
            # positiveマップ
            for i in range(10):
                if prefs_obj['pref{0}_name'.format(i + 1)] == None:
                    prefs_c.append((None,0))
                else:
                    prefs_c.append((prefs_obj['pref{0}_name'.format(i + 1)], prefs_obj['pref{0}_count'.format(i + 1)]))
    ### map用 ##########           
                try:
                    
                    map_id=Prefectures.objects.only('map_id').get(prefecture=prefs_obj['pref{0}_name'.format(i + 1)]).map_id
                    prefs_m.append((map_id, prefs_obj['pref{0}_count'.format(i + 1)]))
    
                except Prefectures.DoesNotExist:
                    prefs_m.append((None,0))
            # negativeマップ
            for i in range(10,20):
                if prefs_obj['pref{0}_name'.format(i + 1)] == None:
                    n_prefs_c.append(('',0))
                else:
                    n_prefs_c.append((prefs_obj['pref{0}_name'.format(i + 1)], prefs_obj['pref{0}_count'.format(i + 1)]))
    ### map用 ##########           
                try:
                    
                    map_id=Prefectures.objects.only('map_id').get(prefecture=prefs_obj['pref{0}_name'.format(i + 1)]).map_id
                    n_prefs_m.append((map_id, prefs_obj['pref{0}_count'.format(i + 1)]))
    
                except Prefectures.DoesNotExist:
                    n_prefs_m.append((None,0))


# frequency取得
 
    try:
        freqs_obj = Frequentwords.objects.values_list('freq1','freq2','freq3','freq4','freq5','freq6','freq7','freq8','freq9','freq10','freq11','freq12','freq13','freq14','freq15','freq16','freq17','freq18','freq19','freq20','freq21','freq22','freq23','freq24','freq25','freq26','freq27','freq28','freq29','freq30','freq31','freq32','freq33','freq34','freq35','freq36','freq37','freq38','freq39','freq40','freq41','freq42','freq43','freq44','freq45','freq46','freq47','freq48','freq49','freq50',
                                                      'freq1_count','freq2_count','freq3_count','freq4_count','freq5_count','freq6_count','freq7_count','freq8_count','freq9_count','freq10_count','freq11_count','freq12_count','freq13_count','freq14_count','freq15_count','freq16_count','freq17_count','freq18_count','freq19_count','freq20_count','freq21_count','freq22_count','freq23_count','freq24_count','freq25_count','freq26_count','freq27_count','freq28_count','freq29_count','freq30_count','freq31_count','freq32_count','freq33_count','freq34_count','freq35_count','freq36_count','freq37_count','freq38_count','freq39_count','freq40_count','freq41_count','freq42_count','freq43_count','freq44_count','freq45_count','freq46_count','freq47_count','freq48_count','freq49_count','freq50_count'
                                                      ).get(post=post)

    except Frequentwords.DoesNotExist as e:
        freqs_obj = None

    
    period_start = (s_date + datetime.timedelta(hours = 9)).date()
    period_end = (e_date + datetime.timedelta(hours = 9)).date()

# 要約取得

    sum_obj = Tweetdata2.objects.filter(
                                        t_date__range=(s_date,e_date),# 7日前~1日前まで
                                        sum_title_id=record['index'],
                                        sum_title_text__in=[1,2,3,4,5,21,22,23,24,25],
                                        ).values('t_id',
                                                'u_id',
                                                't_date',
                                                'content',
                                                's_name',
                                                'u_name',
                                                'p_image',
                                                's_class',
                                                't_id_char',
                                                'entities_display_url',
                                                'entities_url',
                                                'media_url',
                                                'media_url_truncated',
                                                'sum_title_text',
                                                'hashtag',
                                                ).order_by('media_url')

    # 要約文(1~20)を取得
    try:
        summary_texts = Summarys.objects.values_list(
# positive
                                               'summary_text1',
                                               'summary_text2',
                                               'summary_text3',
                                               'summary_text4',
                                               'summary_text5',
# nega
                                               'summary_text21',
                                               'summary_text22',
                                               'summary_text23',
                                               'summary_text24',
                                               'summary_text25',

                                               'related1_id',
                                               'related2_id',
                                               'related3_id',
                                               'related4_id',
                                               'related5_id',

                                               ).get(post=post)

    except Summarys.DoesNotExist as e:
        return HttpResponse(status=404)

    else:

        # 要約に選ばれたツイート取得
        contents = [[] for i in range(40)] # 0-19positive,20-39negative
        for obj in sum_obj:
            #if safetext(obj['content']):
            contents[obj['sum_title_text'] - 1].append(obj)



        summarys = []
        n_summarys = []
        # 要約,投稿数,ツイートを辞書型に変換
        for i in range(0, 5):
            if summary_texts[i] == None:
                continue
            else:

                summarys.append({'要約':summary_texts[i],
                                 '投稿数':len(contents[i]),
                                 '原文':contents[i][:3],
                                 }
                                )
        # 後で合流した要約の場合投稿数がずれる可能性あるので
        summarys = sorted(summarys,key=lambda x: x['投稿数'],reverse=True)

        for i in range(5, 10):
            if summary_texts[i] == None:
                continue
            else:

                n_summarys.append({'要約':summary_texts[i],
                                   '投稿数':len(contents[15+i]), #20以降
                                   '原文':contents[15+i][:3],
                                   }) # 各要約30投稿のみ表示
        n_summarys = sorted(n_summarys,key=lambda x: x['投稿数'],reverse=True)
          
        sum_description='' #descriptionおよびツイート共有テキスト用
        for k,s in enumerate(reversed(summarys)):#逆順で5位から見せる
            sum_description += '{0}位:'.format(len(summarys)-k) + s['要約'] + ','
        sum_description = sum_description[:-1] # 最後の,除去

        n_sum_description='' # 現状未使用
        for k,s in enumerate(n_summarys):
            n_sum_description += '{0}位:'.format(len(summarys)-k) + s['要約'] + ','
        n_sum_description = n_sum_description[:-1] # 最後の,除去

        # 類似ブランド
        relates = []
        for related_no in summary_texts[10:]:
            if related_no == 0:
                continue
            try:
                related_record = Official_names.objects.get(index=related_no)
            except:
                continue
            if related_record.hidden == True:
                continue
            # 一時的に1話と0話(春アニメ)のみ検索
            related_post = slugify('{0} {1}'.format(related_no,1))
            try:
                statistics = Statistics1week.objects.only(   
                                        'p1_count_d1',
                                        'p1_count_d2',
                                        'p1_count_d3',
                                        'p1_count_d4',
                                        'p1_count_d5',
                                        'p1_count_d6',
                                        'p1_count_d7',
                                        'p2_count_d1',
                                        'p2_count_d2',
                                        'p2_count_d3',
                                        'p2_count_d4',
                                        'p2_count_d5',
                                        'p2_count_d6',
                                        'p2_count_d7',
                                        ).get(post=related_post)
            except Statistics1week.DoesNotExist as e:
                #print(e)
                related_post = slugify('{0} {1}'.format(related_no,0))
                try:
                    statistics = Statistics1week.objects.only(   
                                            'p1_count_d1',
                                            'p1_count_d2',
                                            'p1_count_d3',
                                            'p1_count_d4',
                                            'p1_count_d5',
                                            'p1_count_d6',
                                            'p1_count_d7',
                                            'p2_count_d1',
                                            'p2_count_d2',
                                            'p2_count_d3',
                                            'p2_count_d4',
                                            'p2_count_d5',
                                            'p2_count_d6',
                                            'p2_count_d7',
                                            ).get(post=related_post)
                except Statistics1week.DoesNotExist as e:
                    #print(e)  
                    continue

            # 要約も取得
            summary_exists = True
            try:
                record_summary = Summarys.objects.only(
                                                'summary_text1',
                                                'summary_text2',
                                                'summary_text3',
                                                'summary_text4',
                                                'summary_text5',
                                                 ).get(post=related_post)            
            except Summarys.DoesNotExist as e:
                #print(e)
                summary_exists = False
                
            else:
                pcount = sum([
                        statistics.p1_count_d1,                                            
                        statistics.p1_count_d2,                                            
                        statistics.p1_count_d3,                                            
                        statistics.p1_count_d4,                                            
                        statistics.p1_count_d5,                                            
                        statistics.p1_count_d6,                                            
                        statistics.p1_count_d7,
                        statistics.p2_count_d1,                                            
                        statistics.p2_count_d2,                                            
                        statistics.p2_count_d3,                                            
                        statistics.p2_count_d4,                                            
                        statistics.p2_count_d5,                                            
                        statistics.p2_count_d6,                                            
                        statistics.p2_count_d7
                        ])
                if pcount < 10:
                    continue # 50未満は非表示
                relates.append({'pcount':pcount,
                                'brand':related_record.official_name,
                                'url':related_record.url_name,
                               'summarys':[record_summary.summary_text1 if summary_exists else None,
                                        record_summary.summary_text2 if summary_exists else None,
                                        record_summary.summary_text3 if summary_exists else None,
                                        record_summary.summary_text4 if summary_exists else None,
                                        record_summary.summary_text5 if summary_exists else None
                                        ]                                     
                               })   
# animeページ用　キャラランキング
    # 高評価キャラ
    chara_rank = []
    op_rank = []
    ed_rank = []
    cv_rank = []
    chara_syokai = []
    op_syokai = []
    ed_syokai = []
    cv_syokai= []
    chara_nos = list(Official_names.objects.filter(
                                                   #title=False,
                                                   kind__in=[1,2,3,4],
                                                   title_name=record['title_name'],
                                                   ).values_list('index','official_name','kind','url_name'))

    for chara_no in chara_nos:

        if chara_no[2] == 1:
            chara_syokai.append(SPC.sub(" ",chara_no[1]))
        elif chara_no[2] == 2:
            op_syokai.append(SPC.sub(" ",chara_no[1]))
        elif chara_no[2] == 3:
            ed_syokai.append(SPC.sub(" ",chara_no[1]))
        elif chara_no[2] == 4:
            cv_syokai.append(SPC.sub(" ",chara_no[1]))

        chara_post = slugify('{0} {1}'.format(chara_no[0],0))
        try:
            statistics = Statistics1week.objects.only(
                                       'p1_count_d1',
                                        'p1_count_d2',
                                        'p1_count_d3',
                                        'p1_count_d4',
                                        'p1_count_d5',
                                        'p1_count_d6',
                                        'p1_count_d7',
                                       'p2_count_d1',
                                       'p2_count_d2',
                                       'p2_count_d3',
                                       'p2_count_d4',
                                       'p2_count_d5',
                                       'p2_count_d6',
                                       'p2_count_d7',
                                       ).get(post=chara_post)
        except Statistics1week.DoesNotExist as e:
            #print(e)
            continue

        # 要約も取得

        try:
            record_summary = Summarys.objects.values_list(
                                              'summary_text1',
                                               'summary_text2',
                                               'summary_text3',
                                               'summary_text4',
                                               'summary_text5',
                                               ).get(post=chara_post)
        except Summarys.DoesNotExist as e:
            #print(e)
            continue

        else:
            pcount = sum([
                    statistics.p1_count_d1,
                    statistics.p1_count_d2,
                    statistics.p1_count_d3,
                    statistics.p1_count_d4,
                    statistics.p1_count_d5,
                    statistics.p1_count_d6,
                    statistics.p1_count_d7,
                    statistics.p2_count_d1,
                    statistics.p2_count_d2,
                    statistics.p2_count_d3,
                    statistics.p2_count_d4,
                    statistics.p2_count_d5,
                    statistics.p2_count_d6,
                    statistics.p2_count_d7
                    ])
            #if pcount < MIN_SHOW:
            if pcount < 50:
                continue # 50未満は非表示


            # charaの場合
            if chara_no[2] == 1:
                chara_rank.append({'pcount':pcount,
                                   'brand':SPC.sub(" ",chara_no[1]),
                                   'url':chara_no[3],
                                   'anime_url':name,
                                   'summarys':record_summary,
                                   })
            # opの場合
            elif chara_no[2] == 2:
                op_rank.append({'pcount':pcount,
                                'brand':SPC.sub(" ",chara_no[1]),
                                'url':chara_no[3],
                                'anime_url':name,
                                'summarys':record_summary,
                                })
            # edの場合
            elif chara_no[2] == 3:
                ed_rank.append({'pcount':pcount,
                                'brand':SPC.sub(" ",chara_no[1]),
                                'url':chara_no[3],
                                'anime_url':name,
                                   'summarys':record_summary,
                                })
            # cvの場合
            elif chara_no[2] == 4:
                cv_rank.append({'pcount':pcount,
                                'brand':SPC.sub(" ",chara_no[1]),
                                'url':chara_no[3],
                                'anime_url':name,
                                   'summarys':record_summary,
                                })

    chara_rank = sorted(chara_rank, key=lambda x:x['pcount'], reverse=True) # pcount順に並び替え
    op_rank = sorted(op_rank, key=lambda x:x['pcount'], reverse=True) # pcount順に並び替え
    ed_rank = sorted(ed_rank, key=lambda x:x['pcount'], reverse=True) # pcount順に並び替え
    cv_rank = sorted(cv_rank, key=lambda x:x['pcount'], reverse=True) # pcount順に並び替え

    chara_syokai = sorted(chara_syokai,reverse=True) if len(chara_syokai) > 0 else None
    op_syokai = sorted(op_syokai,reverse=True) if len(op_syokai) > 0 else None
    ed_syokai = sorted(ed_syokai,reverse=True) if len(ed_syokai) > 0 else None
    cv_syokai = sorted(cv_syokai,reverse=True) if len(cv_syokai) > 0 else None

# Abouts
    try:
        about = Abouts.objects.values('story','p_soukatsu','n_soukatsu').get(official_name_id=record['index'])  
    except Abouts.DoesNotExist as e:
        #print(e)
        about = None
# Oadates
    try:
        oadates = Oadates.objects.values(
                        'episode1',
                        'episode2',
                        'episode3',
                        'episode4',
                        'episode5',
                        'episode6',
                        'episode7',
                        'episode8',
                        'episode9',
                        'episode10',
                        'episode11',
                        'episode12',
                        'episode13',
                        'episode14',
                        'episode15',
                        'episode16',
                        'episode17',
                        'episode18',
                        'episode19',
                        'episode20',
                        'episode21',
                        'episode22',
                        'episode23',
                        'episode24',
                        'episode25',
                        'episode26',
                        'episode27',
                        'episode28',
                        'episode29',
                        'episode30',
                        'episode_title1',
                        'episode_title2',
                        'episode_title3',
                        'episode_title4',
                        'episode_title5',
                        'episode_title6',
                        'episode_title7',
                        'episode_title8',
                        'episode_title9',
                        'episode_title10',
                        'episode_title11',
                        'episode_title12',
                        'episode_title13',
                        'episode_title14',
                        'episode_title15',
                        'episode_title16',
                        'episode_title17',
                        'episode_title18',
                        'episode_title19',
                        'episode_title20',
                        'episode_title21',
                        'episode_title22',
                        'episode_title23',
                        'episode_title24',
                        'episode_title25',
                        'episode_title26',
                        'episode_title27',
                        'episode_title28',
                        'episode_title29',
                        'episode_title30',                        
                        'title_tag1',
                        'title_tag2',
                        'title_tag3',
                        'title_tag4',
                        'title_tag5',
                        'title_tag6',
                        'title_tag7',
                        'title_tag8',
                        'title_tag9',
                        'title_tag10',
                        'title_tag11',
                        'title_tag12',
                        'title_tag13',
                        'title_tag14',
                        'title_tag15',
                        'title_tag16',
                        'title_tag17',
                        'title_tag18',
                        'title_tag19',
                        'title_tag20',
                        'title_tag21',
                        'title_tag22',
                        'title_tag23',
                        'title_tag24',
                        'title_tag25',
                        'title_tag26',
                        'title_tag27',
                        'title_tag28',
                        'title_tag29',
                        'title_tag30',
                        ).get(official_name_id=record['index'])

    except Oadates.DoesNotExist as e:
        #print(e)
        oadates = None        
        title_tag = None
    else:
        title_tag = oadates['title_tag{0}'.format(episode)] if episode != 0 else None
        oadates = [{
                    'episode':oadates['episode{0}'.format(i)], # 日付
                    'episode_title':oadates['episode_title{0}'.format(i)], # サブタイトル
                    'link_exist':True if Summarys.objects.filter(post = slugify('{0} {1}'.format(record['index'],i))).exists() else False,
                    } for i in range(1,31)]

                                     
        #print(oadates)
        if oadates[0]['episode'] == None or oadates[0]['episode_title'] == None:
            oadates = None

    title_episode = 0 # title用のepisode (第~話)
    prevlink = False    
    
    
    if oadates != None:
        if record['past'] == True:
            title_episode = 0
        elif episode == 0:
            #リアルタイムに該当するepisode取得
            for i in range(0,30):
                if oadates[i]['episode'] == s_date:
                    title_episode = i + 1
                    break 
        else:
            title_episode = episode # >0
        
            
        # 第2話以降で、前回のエピソードのページがある?
        if title_episode >= 2:
            if oadates[title_episode-2]['link_exist']:
                prevlink = True

# fanart
    try:
        # 各週で取得        
        fanarts_id = list(Fanarts.objects.values_list(
                                                  'fan_art1_id',
                                                  'fan_art2_id',
                                                  'fan_art3_id',
                                                  'fan_art4_id',
                                                  'fan_art5_id',
                                                  'fan_art6_id',
                                                  'fan_art7_id',
                                                  'fan_art8_id',
                                                  'fan_art9_id',
                                                  'fan_art10_id',
                                                 ).get(post=post))
        
    except Fanarts.DoesNotExist as e:
        #print(e)
        fanarts = None
    else:
        tmp_l = []
        for f in fanarts_id:
            if f != None:
                tmp_l.append(f)
            else:
                #break
                continue
        fanarts_id = tmp_l
        #print('fanarts id',fanarts_id)
        if len(fanarts_id) in [0,1]:
            fanarts = None
        else:
            fanarts = Tweetdata2.objects.only('t_id',
                                                'media_url',
                                                'media_url_truncated',
                                                'u_id',
                                                'p_image',
                                                ).filter(
                                                t_id__in=fanarts_id
                                                )[:10]
    #print("ok")
    params = {
            'category':category,

            'title':'プラコメ',
            'data_num':p_num + n_num,
            'p_num':p_num,
            'n_num':n_num,
            'p2_num':p2_num,
            'n2_num':n2_num,
            'p1_num':p1_num,
            'n1_num':n1_num,    
            'p2_counts':p2_counts,
            'p1_counts':p1_counts,            
            'n1_counts':n1_counts,
            'n2_counts':n2_counts,
            'pn_counts_date':json.dumps(pn_counts_date),
            'pn_counts_date_text':pn_counts_date,   
            'period_start':period_start,
            'period_end':period_end,
            'locations':prefs_c,
            'locations_map':prefs_m,
            'n_locations':n_prefs_c,
            'n_locations_map':n_prefs_m,

            'trend_obj':None,
            'freqs_obj':freqs_obj,

            'name':name,
            'title_name':SPC.sub(" ",record['title_name']),
            'summarys':summarys[:5],
            'n_summarys':n_summarys[:5],
            'events':long_event_dic,
            'chara_rank':chara_rank,
            'op_rank':op_rank,
            'ed_rank':ed_rank,
            'cv_rank':cv_rank,
            'chara_syokai':chara_syokai,
            'op_syokai':op_syokai,            
            'ed_syokai':ed_syokai,            
            'cv_syokai':cv_syokai,
            'relates':relates,
            'about':about,
            'short_name':SPC.sub(' ',record['short_name']),
            'past':record['past'], #tmp
            'oadates':oadates,
            'episode':episode,
            'title_episode':title_episode,
            'prevlink':prevlink,
            'title_tag':title_tag,
            'fanarts':fanarts,
            'post':post_sta,
            'comments': comments,
            'comment_form':comment_form,
            'ep_reaction':ep_reaction if len(ep_reaction) > 0 else None,
            'en_reaction':en_reaction if len(en_reaction) > 0 else None,
            'n_sum_description':n_sum_description,
            'sum_description':sum_description,
        }

    return render(request,'sentiment/anime/anime2.html',params)



def anime_episode(request,name,episode=0):
    
    #if request.method == 'POST' and 'Search' in request.POST:
        #print('Search:',request.POST('Search'))

    ''' 
    form = DateForm()
    form2 = CharacterForm()
    form3 = AnimeForm()
    '''
    pn_counts_date=[] # 投稿日付（グラフ横軸)
    locations=[]
    '''
    CharField.register_lookup(Length, 'length') #  registered as a transform
    
    character_filter = request.POST.get('character_filter')
    anime_filter = request.POST.get('anime_filter')
    anime_filter2 = request.POST.get('Search')
    '''

    try:        
        record = Official_names.objects.values('index',
                                               'kind',
                                               'title_name',
                                               'hidden',
                                               'past',
                                               'short_name',
                                               ).get(url_name=name)

    except Official_names.DoesNotExist as e:
        return HttpResponse(status=410)
        raise Http404("Page does not exist.")
    
    if record['kind'] != 0 or record['hidden'] == True: # charaページにアクセスしようとした場合
        return HttpResponse(status=410)
        raise Http404("Page does not exist.")
    
### purakome.com to purakome.net    
    #if request.META.get("HTTP_HOST") == r'purakome.com':
        #return HttpResponse(status=410)
###

    #print('requestpath',request.path) # 春アニメで sentiment/anime/kimetsu/0/でアクセスできてしまうのを防ぐ
    if episode == 0 and request.path[-3:] == r'/0/':
        return redirect(r'https://purakome.net/sentiment/anime/{0}/'.format(name),permanent=True)

# コメント
    post = slugify('{0} {1}'.format(record['index'],episode))
    #print('post',post)

    if Categorys.objects.filter(post=post).exists():
        #print('MOVING TO CATEGORY..')
        return anime_episode2(request=request,name=name,episode=episode)

    post_sta=get_object_or_404(Statistics1week,post=post)

    #print('post   id',post_sta.id)
    # List of active comments for this post
    comments = Comment.objects.filter(target=post_sta.post,
                                      #parent_id=None,
                                      active=True)
    new_comment = None

    comment_form = CommentForm()
    if request.method == 'POST':
        #print('POST')
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.target = post_sta.post
            # Save the comment to the database
            new_comment.save()
            # redirect to same page and focus on that comment
            '''
            if episode == 0:
                return redirect(r'sentiment/anime/{0}/'.format(name)+'#'+str(new_comment.id))
            elif episode > 0:
                return redirect(r'sentiment/anime/{0}/{1}/'.format(name,episode)+'#'+str(new_comment.id))
            '''
        else:
            comment_form = CommentForm()


# statisticsと日時取得        
    #print("statistics access")
    try:
        statistics = Statistics1week.objects.values('s_date','e_date','p2_count_d1', 'p1_count_d1','n2_count_d1', 'n1_count_d1',
                                        'p2_count_d2', 'p1_count_d2','n2_count_d2', 'n1_count_d2',
                                        'p2_count_d3', 'p1_count_d3','n2_count_d3', 'n1_count_d3',
                                        'p2_count_d4', 'p1_count_d4','n2_count_d4', 'n1_count_d4',
                                        'p2_count_d5', 'p1_count_d5','n2_count_d5', 'n1_count_d5',
                                        'p2_count_d6', 'p1_count_d6','n2_count_d6', 'n1_count_d6',
                                        'p2_count_d7', 'p1_count_d7','n2_count_d7', 'n1_count_d7',
                                        'p_tweet1_id','p_tweet2_id','p_tweet3_id','p_tweet4_id',
                                        'p_tweet5_id','p_tweet6_id','p_tweet7_id','p_tweet8_id',
                                        'p_tweet9_id','p_tweet10_id',
                                        'n_tweet1_id','n_tweet2_id','n_tweet3_id','n_tweet4_id',
                                        'n_tweet5_id','n_tweet6_id','n_tweet7_id','n_tweet8_id',
                                        'n_tweet9_id','n_tweet10_id'
                                        ).get(post=post)    

    except Statistics1week.DoesNotExist as e:
        #print(e)
        return HttpResponse(status=410)


    s_date = statistics['s_date']
    e_date = statistics['e_date']
    #print('s_date',s_date)
    #print('e_date',e_date)

    p2_counts=[0,0,0,0,0,0]# 日付ごとの投稿数(グラフ縦軸)
    p1_counts=[0,0,0,0,0,0]# 日付ごとの投稿数(グラフ縦軸)
    n1_counts=[0,0,0,0,0,0]# 日付ごとの投稿数(グラフ縦軸)
    n2_counts=[0,0,0,0,0,0]
    pn_counts_date=[] # 投稿日付（グラフ横軸)
    for i in range(6):
        p2_counts[i] = statistics['p2_count_d{0}'.format(6-i)]
        p1_counts[i] = statistics['p1_count_d{0}'.format(6-i)]
        n2_counts[i] = statistics['n2_count_d{0}'.format(6-i)]
        n1_counts[i] = statistics['n1_count_d{0}'.format(6-i)]


    for i in range(6):
        d = (e_date + datetime.timedelta(hours=9)).date() - datetime.timedelta(days = 5 - i)
        pn_counts_date.append(str(d.month)+'月'+str(d.day)+'日')

    p2_num = sum(p2_counts)
    p1_num = sum(p1_counts)
    p_num = p2_num + p1_num

    '''
    if p_num < MIN_SHOW:
        return HttpResponse(status=410)
        raise Http404("Page does not exist.")
    '''
    n2_num = sum(n2_counts)
    n1_num = sum(n1_counts)
    n_num = n2_num + n1_num

# news取得       
    long_event_dic = Longevents.objects.filter(
                                              (Q(date_s__lte=e_date) & Q(date_e__gte=s_date)) | (Q(date_e__gte=s_date) & Q(date_s__lte=e_date)),
                                               Q(official_name_id=record['index']),
                                               #Q(date_s__range=(s_date,e_date)) | Q(date_e__range=(s_date,e_date)),
                                               
                                               # 1週間の最後の日付よりもイベントの開始日付が遅い場合は該当外
                                               # イベントの終了日付が1週間の最初の日付よりも早い場合は該当外
                                               Q(title__isnull=False), # titleが空欄以外
                                               ).values( 
                                                        #'official_name',
                                                        #'url',
                                                        'title',
                                                        'date_s',
                                                        'date_e',
                                                        'time_s',
                                                        'time_e',
                                                        'weekday',
                                                        'media',
                                                        'channel',
                                                        'title'
                                                         )[:5]

          
# pn10投稿データ取得
    pn_data = []
    pn_data_index = []
    
    for i in range(10):
        if statistics['n_tweet{0}_id'.format(i+1)]!='':
            pn_data_index.append(statistics['n_tweet{0}_id'.format(i+1)])
        if statistics['p_tweet{0}_id'.format(i+1)]!='':
            pn_data_index.append(statistics['p_tweet{0}_id'.format(i+1)])


    pn_data = Tweetdata2.objects.only('t_id',
                                        'u_id',
                                        't_date',
                                        'content',
                                        's_name',
                                        'u_name',
                                        'p_image',
                                        's_class',
                                        't_id_char',
                                        'entities_display_url',
                                        'entities_url',
                                        'media_url',
                                        'media_url_truncated',
                                        'hashtag'
                                         ).filter(t_id__in=pn_data_index)  
    trend_obj = None  
    '''
# trend取得
    # trend(1~10)を取得
    trend_word = []
    trend_word_count = []
    
    
    try:        
        trend_obj = Trend_ranks.objects.values_list('trend1',
                                            'trend2',
                                            'trend3',
                                            'trend4',
                                            'trend5',
                                            'trend6',
                                            'trend7',
                                            'trend8',
                                            'trend9',
                                            'trend10',
                                            'trend1_count',
                                            'trend2_count',
                                            'trend3_count',
                                            'trend4_count',
                                            'trend5_count',
                                            'trend6_count',
                                            'trend7_count',
                                            'trend8_count',
                                            'trend9_count',
                                            'trend10_count',
                                           ).get(post=post)
    except Trend_ranks.DoesNotExist as e:
        trend_obj = None
        #print(e)
    '''
# pref取得
    prefs_c = []
    prefs_m = [] # map用 
    n_prefs_c = None
    n_prefs_m = None
    #print('getting prefs..')
    
    try:        
        prefs_obj = Pref_ranks.objects.values('pref1_name',
                                            'pref2_name',
                                            'pref3_name',
                                            'pref4_name',
                                            'pref5_name',
                                            'pref6_name',
                                            'pref7_name',
                                            'pref8_name',
                                            'pref9_name',
                                            'pref10_name',
                                            'pref1_count',
                                            'pref2_count',
                                            'pref3_count',
                                            'pref4_count',
                                            'pref5_count',
                                            'pref6_count',
                                            'pref7_count',
                                            'pref8_count',
                                            'pref9_count',
                                            'pref10_count',
                                            # 以下n
                                            'pref11_name',
                                            'pref12_name',
                                            'pref13_name',
                                            'pref14_name',
                                            'pref15_name',
                                            'pref16_name',
                                            'pref17_name',
                                            'pref18_name',
                                            'pref19_name',
                                            'pref20_name',
                                            'pref11_count',
                                            'pref12_count',
                                            'pref13_count',
                                            'pref14_count',
                                            'pref15_count',
                                            'pref16_count',
                                            'pref17_count',
                                            'pref18_count',
                                            'pref19_count',
                                            'pref20_count',                                            
                                           ).get(post=post)
    except Pref_ranks.DoesNotExist as e:
        pass
        #print(e)
    else:
        # 炎上マップなし
        if prefs_obj['pref11_name'] == None:
            # 要約,投稿数,ツイートを辞書型に変換
            for i in range(10):
                if prefs_obj['pref{0}_name'.format(i + 1)] == None:
                    prefs_c.append((None,0))
                else:
                    prefs_c.append((prefs_obj['pref{0}_name'.format(i + 1)], prefs_obj['pref{0}_count'.format(i + 1)]))
    ### map用 ##########           
                try:
                    
                    map_id=Prefectures.objects.only('map_id').get(prefecture=prefs_obj['pref{0}_name'.format(i + 1)]).map_id
                    prefs_m.append((map_id, prefs_obj['pref{0}_count'.format(i + 1)]))
    
                except Prefectures.DoesNotExist:
                    prefs_m.append((None,0))
            
            n_prefs_c = None
            n_prefs_m = None
            
        # 炎上マップあり   
        else:
            n_prefs_c = []
            n_prefs_m = []
            # positiveマップ
            for i in range(10):
                if prefs_obj['pref{0}_name'.format(i + 1)] == None:
                    prefs_c.append((None,0))
                else:
                    prefs_c.append((prefs_obj['pref{0}_name'.format(i + 1)], prefs_obj['pref{0}_count'.format(i + 1)]))
    ### map用 ##########           
                try:
                    
                    map_id=Prefectures.objects.only('map_id').get(prefecture=prefs_obj['pref{0}_name'.format(i + 1)]).map_id
                    prefs_m.append((map_id, prefs_obj['pref{0}_count'.format(i + 1)]))
    
                except Prefectures.DoesNotExist:
                    prefs_m.append((None,0))
            # negativeマップ
            for i in range(10,20):
                if prefs_obj['pref{0}_name'.format(i + 1)] == None:
                    n_prefs_c.append(('',0))
                else:
                    n_prefs_c.append((prefs_obj['pref{0}_name'.format(i + 1)], prefs_obj['pref{0}_count'.format(i + 1)]))
    ### map用 ##########           
                try:
                    
                    map_id=Prefectures.objects.only('map_id').get(prefecture=prefs_obj['pref{0}_name'.format(i + 1)]).map_id
                    n_prefs_m.append((map_id, prefs_obj['pref{0}_count'.format(i + 1)]))
    
                except Prefectures.DoesNotExist:
                    n_prefs_m.append((None,0))


# frequency取得
 
    try:
        freqs_obj = Frequentwords.objects.values_list('freq1','freq2','freq3','freq4','freq5','freq6','freq7','freq8','freq9','freq10','freq11','freq12','freq13','freq14','freq15','freq16','freq17','freq18','freq19','freq20','freq21','freq22','freq23','freq24','freq25','freq26','freq27','freq28','freq29','freq30','freq31','freq32','freq33','freq34','freq35','freq36','freq37','freq38','freq39','freq40','freq41','freq42','freq43','freq44','freq45','freq46','freq47','freq48','freq49','freq50',
                                                      'freq1_count','freq2_count','freq3_count','freq4_count','freq5_count','freq6_count','freq7_count','freq8_count','freq9_count','freq10_count','freq11_count','freq12_count','freq13_count','freq14_count','freq15_count','freq16_count','freq17_count','freq18_count','freq19_count','freq20_count','freq21_count','freq22_count','freq23_count','freq24_count','freq25_count','freq26_count','freq27_count','freq28_count','freq29_count','freq30_count','freq31_count','freq32_count','freq33_count','freq34_count','freq35_count','freq36_count','freq37_count','freq38_count','freq39_count','freq40_count','freq41_count','freq42_count','freq43_count','freq44_count','freq45_count','freq46_count','freq47_count','freq48_count','freq49_count','freq50_count'
                                                      ).get(post=post)

    except Frequentwords.DoesNotExist as e:
        freqs_obj = None

    
    period_start = (s_date + datetime.timedelta(hours = 9)).date()
    period_end = (e_date + datetime.timedelta(hours = 9)).date()
# 検索用日付 
    #s_date = s_date.date() - datetime.timedelta(days = 7) 
# 要約取得
    sum_obj = Tweetdata2.objects.filter(
                                        t_date__range=(s_date,e_date),# 7日前~1日前まで
                                        sum_title_id=record['index'],
                                        ).values('t_id',
                                                          'u_id',
                                                          't_date',
                                                          'content',
                                                          's_name',
                                                          'u_name',
                                                          'p_image',
                                                          's_class',
                                                          't_id_char',
                                                          'entities_display_url',
                                                          'entities_url',
                                                          'media_url',
                                                          'media_url_truncated',
                                                          'sum_title_text',
                                                          'hashtag'
                                                          )
        
    # 要約文(1~20)を取得
    try:        
        summary_texts = Summarys.objects.values_list(
# positive
                                               'summary_text1',
                                               'summary_text2',
                                               'summary_text3',
                                               'summary_text4',
                                               'summary_text5',
                                               'summary_text6',
                                               'summary_text7',
                                               'summary_text8',
                                               'summary_text9',
                                               'summary_text10',
                                               'summary_text11',
                                               'summary_text12',
                                               'summary_text13',
                                               'summary_text14',
                                               'summary_text15',
                                               'summary_text16',
                                               'summary_text17',
                                               'summary_text18',
                                               'summary_text19',
                                               'summary_text20',
# nega
                                               'summary_text21',
                                               'summary_text22',
                                               'summary_text23',
                                               'summary_text24',
                                               'summary_text25',
                                               'summary_text26',
                                               'summary_text27',
                                               'summary_text28',
                                               'summary_text29',
                                               'summary_text30',
                                               'summary_text31',
                                               'summary_text32',
                                               'summary_text33',
                                               'summary_text34',
                                               'summary_text35',
                                               'summary_text36',
                                               'summary_text37',
                                               'summary_text38',
                                               'summary_text39',
                                               'summary_text40',
                                               'related1_id',
                                               'related2_id',
                                               'related3_id',
                                               'related4_id',
                                               'related5_id',
                                              ).get(post=post)

    except Summarys.DoesNotExist as e:
        return HttpResponse(status=410)

    else:
        #print('sumary_tests',summary_texts)
        
        # 要約に選ばれたツイート取得
        contents = [[] for i in range(40)] # 0-4positive,5-9negative 
        for obj in sum_obj:
            contents[obj['sum_title_text'] - 1].append(obj)
            
                # contents = [[obj,obj..](summary1のobj),[obj,obj,obj..](summary2のobj),..]
        #print('contents',contents)
        
        summarys = []
        n_summarys = []
        # 要約,投稿数,ツイートを辞書型に変換
        for i in range(0, 20):
            if summary_texts[i] == None:
                continue
            else:
                summarys.append({'要約':summary_texts[i],
                                 '投稿数':len(contents[i]),
                                 '原文':sorted(contents[i], key=lambda x:chk_media(x),reverse=True)[:6] if len(contents[i]) > 6 else contents[i]
                                })     
        summarys = sorted(summarys,key=lambda x: x['投稿数'],reverse=True)
        for i in range(20, 40):
            if summary_texts[i] == None:
                continue
            else:
                #print('a',summary_texts[i])
                n_summarys.append({'要約':summary_texts[i],
                                   '投稿数':len(contents[i]), #20以降
                                   '原文':contents[i][:6]
                                  })     
                #print(n_summarys)   
        n_summarys = sorted(n_summarys,key=lambda x: x['投稿数'],reverse=True)
        # 類似ブランド
        relates = []
        for related_no in summary_texts[40:]:
            if related_no == 0:
                continue
            try:
                related_record = Official_names.objects.get(index=related_no)
            except:
                continue
            if related_record.hidden == True:
                continue
            # 一時的に1話と0話(春アニメ)のみ検索
            related_post = slugify('{0} {1}'.format(related_no,1))
            try:
                statistics = Statistics1week.objects.only(   
                                        'p1_count_d1',
                                        'p1_count_d2',
                                        'p1_count_d3',
                                        'p1_count_d4',
                                        'p1_count_d5',
                                        'p1_count_d6',
                                        'p1_count_d7',
                                        'p2_count_d1',
                                        'p2_count_d2',
                                        'p2_count_d3',
                                        'p2_count_d4',
                                        'p2_count_d5',
                                        'p2_count_d6',
                                        'p2_count_d7',
                                        ).get(post=related_post)
            except Statistics1week.DoesNotExist as e:
                #print(e)
                related_post = slugify('{0} {1}'.format(related_no,0))
                try:
                    statistics = Statistics1week.objects.only(   
                                            'p1_count_d1',
                                            'p1_count_d2',
                                            'p1_count_d3',
                                            'p1_count_d4',
                                            'p1_count_d5',
                                            'p1_count_d6',
                                            'p1_count_d7',
                                            'p2_count_d1',
                                            'p2_count_d2',
                                            'p2_count_d3',
                                            'p2_count_d4',
                                            'p2_count_d5',
                                            'p2_count_d6',
                                            'p2_count_d7',
                                            ).get(post=related_post)
                except Statistics1week.DoesNotExist as e:
                    #print(e)  
                    continue

            # 要約も取得
            summary_exists = True
            try:
                record_summary = Summarys.objects.only(
                                                'summary_text1',
                                                'summary_text2',
                                                'summary_text3',
                                                'summary_text4',
                                                'summary_text5',
                                                 ).get(post=related_post)            
            except Summarys.DoesNotExist as e:
                #print(e)
                summary_exists = False
                
            else:
                pcount = sum([
                        statistics.p1_count_d1,                                            
                        statistics.p1_count_d2,                                            
                        statistics.p1_count_d3,                                            
                        statistics.p1_count_d4,                                            
                        statistics.p1_count_d5,                                            
                        statistics.p1_count_d6,                                            
                        statistics.p1_count_d7,
                        statistics.p2_count_d1,                                            
                        statistics.p2_count_d2,                                            
                        statistics.p2_count_d3,                                            
                        statistics.p2_count_d4,                                            
                        statistics.p2_count_d5,                                            
                        statistics.p2_count_d6,                                            
                        statistics.p2_count_d7
                        ])
                if pcount < 10:
                    continue # 50未満は非表示
                relates.append({'pcount':pcount,
                                'brand':related_record.official_name,
                                'url':related_record.url_name,
                               'summarys':[record_summary.summary_text1 if summary_exists else None,
                                        record_summary.summary_text2 if summary_exists else None,
                                        record_summary.summary_text3 if summary_exists else None,
                                        record_summary.summary_text4 if summary_exists else None,
                                        record_summary.summary_text5 if summary_exists else None
                                        ]                                     
                               })   
# animeページ用　キャラランキング
    # 高評価キャラ
    chara_rank = []
    op_rank = []
    ed_rank = []
    cv_rank = []
    chara_syokai = []
    op_syokai = []
    ed_syokai = []
    cv_syokai= []
    chara_nos = list(Official_names.objects.filter(
                                                   #title=False,
                                                   kind__in=[1,2,3,4],
                                                   title_name=record['title_name'],
                                                   ).values_list('index','official_name','kind','url_name'))

    for chara_no in chara_nos:

        if chara_no[2] == 1:
            chara_syokai.append(SPC.sub(" ",chara_no[1]))
        elif chara_no[2] == 2:
            op_syokai.append(SPC.sub(" ",chara_no[1]))
        elif chara_no[2] == 3:
            ed_syokai.append(SPC.sub(" ",chara_no[1]))
        elif chara_no[2] == 4:
            cv_syokai.append(SPC.sub(" ",chara_no[1]))

        chara_post = slugify('{0} {1}'.format(chara_no[0],0))
        try:
            statistics = Statistics1week.objects.only(
                                       'p1_count_d1',
                                        'p1_count_d2',
                                        'p1_count_d3',
                                        'p1_count_d4',
                                        'p1_count_d5',
                                        'p1_count_d6',
                                        'p1_count_d7',
                                       'p2_count_d1',
                                       'p2_count_d2',
                                       'p2_count_d3',
                                       'p2_count_d4',
                                       'p2_count_d5',
                                       'p2_count_d6',
                                       'p2_count_d7',
                                       ).get(post=chara_post)
        except Statistics1week.DoesNotExist as e:
            #print(e)
            continue

        # 要約も取得

        try:
            record_summary = Summarys.objects.values_list(
                                              'summary_text1',
                                               'summary_text2',
                                               'summary_text3',
                                               'summary_text4',
                                               'summary_text5',
                                               ).get(post=chara_post)
        except Summarys.DoesNotExist as e:
            #print(e)
            continue

        else:
            pcount = sum([
                    statistics.p1_count_d1,
                    statistics.p1_count_d2,
                    statistics.p1_count_d3,
                    statistics.p1_count_d4,
                    statistics.p1_count_d5,
                    statistics.p1_count_d6,
                    statistics.p1_count_d7,
                    statistics.p2_count_d1,
                    statistics.p2_count_d2,
                    statistics.p2_count_d3,
                    statistics.p2_count_d4,
                    statistics.p2_count_d5,
                    statistics.p2_count_d6,
                    statistics.p2_count_d7
                    ])
            #if pcount < MIN_SHOW:
            if pcount < 50:
                continue # 50未満は非表示


            # charaの場合
            if chara_no[2] == 1:
                chara_rank.append({'pcount':pcount,
                                   'brand':SPC.sub(" ",chara_no[1]),
                                   'url':chara_no[3],
                                   'anime_url':name,
                                   'summarys':record_summary,
                                   })
            # opの場合
            elif chara_no[2] == 2:
                op_rank.append({'pcount':pcount,
                                'brand':SPC.sub(" ",chara_no[1]),
                                'url':chara_no[3],
                                'anime_url':name,
                                'summarys':record_summary,
                                })
            # edの場合
            elif chara_no[2] == 3:
                ed_rank.append({'pcount':pcount,
                                'brand':SPC.sub(" ",chara_no[1]),
                                'url':chara_no[3],
                                'anime_url':name,
                                   'summarys':record_summary,
                                })
            # cvの場合
            elif chara_no[2] == 4:
                cv_rank.append({'pcount':pcount,
                                'brand':SPC.sub(" ",chara_no[1]),
                                'url':chara_no[3],
                                'anime_url':name,
                                   'summarys':record_summary,
                                })

    chara_rank = sorted(chara_rank, key=lambda x:x['pcount'], reverse=True) # pcount順に並び替え
    op_rank = sorted(op_rank, key=lambda x:x['pcount'], reverse=True) # pcount順に並び替え
    ed_rank = sorted(ed_rank, key=lambda x:x['pcount'], reverse=True) # pcount順に並び替え
    cv_rank = sorted(cv_rank, key=lambda x:x['pcount'], reverse=True) # pcount順に並び替え

    chara_syokai = sorted(chara_syokai,reverse=True) if len(chara_syokai) > 0 else None
    op_syokai = sorted(op_syokai,reverse=True) if len(op_syokai) > 0 else None
    ed_syokai = sorted(ed_syokai,reverse=True) if len(ed_syokai) > 0 else None
    cv_syokai = sorted(cv_syokai,reverse=True) if len(cv_syokai) > 0 else None

# Abouts
    try:
        about = Abouts.objects.values('story','p_soukatsu','n_soukatsu').get(official_name_id=record['index'])  
    except Abouts.DoesNotExist as e:
        #print(e)
        about = None
# Oadates
    try:
        oadates = Oadates.objects.values(
                        'episode1',
                        'episode2',
                        'episode3',
                        'episode4',
                        'episode5',
                        'episode6',
                        'episode7',
                        'episode8',
                        'episode9',
                        'episode10',
                        'episode11',
                        'episode12',
                        'episode13',
                        'episode14',
                        'episode15',
                        'episode16',
                        'episode17',
                        'episode18',
                        'episode19',
                        'episode20',
                        'episode21',
                        'episode22',
                        'episode23',
                        'episode24',
                        'episode25',
                        'episode26',
                        'episode27',
                        'episode28',
                        'episode29',
                        'episode30',
                        'episode_title1',
                        'episode_title2',
                        'episode_title3',
                        'episode_title4',
                        'episode_title5',
                        'episode_title6',
                        'episode_title7',
                        'episode_title8',
                        'episode_title9',
                        'episode_title10',
                        'episode_title11',
                        'episode_title12',
                        'episode_title13',
                        'episode_title14',
                        'episode_title15',
                        'episode_title16',
                        'episode_title17',
                        'episode_title18',
                        'episode_title19',
                        'episode_title20',
                        'episode_title21',
                        'episode_title22',
                        'episode_title23',
                        'episode_title24',
                        'episode_title25',
                        'episode_title26',
                        'episode_title27',
                        'episode_title28',
                        'episode_title29',
                        'episode_title30',                        
                        'title_tag1',
                        'title_tag2',
                        'title_tag3',
                        'title_tag4',
                        'title_tag5',
                        'title_tag6',
                        'title_tag7',
                        'title_tag8',
                        'title_tag9',
                        'title_tag10',
                        'title_tag11',
                        'title_tag12',
                        'title_tag13',
                        'title_tag14',
                        'title_tag15',
                        'title_tag16',
                        'title_tag17',
                        'title_tag18',
                        'title_tag19',
                        'title_tag20',
                        'title_tag21',
                        'title_tag22',
                        'title_tag23',
                        'title_tag24',
                        'title_tag25',
                        'title_tag26',
                        'title_tag27',
                        'title_tag28',
                        'title_tag29',
                        'title_tag30',
                        ).get(official_name_id=record['index'])

    except Oadates.DoesNotExist as e:
        #print(e)
        oadates = None        
        title_tag = None
    else:
        title_tag = oadates['title_tag{0}'.format(episode)] if episode != 0 else None
        oadates = [{
                    'episode':oadates['episode{0}'.format(i)], # 日付
                    'episode_title':oadates['episode_title{0}'.format(i)], # サブタイトル
                    'link_exist':True if Summarys.objects.filter(post = slugify('{0} {1}'.format(record['index'],i))).exists() else False,
                    } for i in range(1,31)]

                                     
        #print(oadates)
        if oadates[0]['episode'] == None or oadates[0]['episode_title'] == None:
            oadates = None

    title_episode = 0 # title用のepisode (第~話)
    prevlink = False    
    
    
    if oadates != None:
        if record['past'] == True:
            title_episode = 0
        elif episode == 0:
            #リアルタイムに該当するepisode取得
            for i in range(0,30):
                if oadates[i]['episode'] == s_date:
                    title_episode = i + 1
                    break 
        else:
            title_episode = episode # >0
        
            
        # 第2話以降で、前回のエピソードのページがある?
        if title_episode >= 2:
            if oadates[title_episode-2]['link_exist']:
                prevlink = True

# fanart
    try:
        # 各週で取得        
        fanarts_id = list(Fanarts.objects.values_list(
                                                  'fan_art1_id',
                                                  'fan_art2_id',
                                                  'fan_art3_id',
                                                  'fan_art4_id',
                                                  'fan_art5_id',
                                                  'fan_art6_id',
                                                  'fan_art7_id',
                                                  'fan_art8_id',
                                                  'fan_art9_id',
                                                  'fan_art10_id',
                                                 ).get(post=post))
        
    except Fanarts.DoesNotExist as e:
        #print(e)
        fanarts = None
    else:
        tmp_l = []
        for f in fanarts_id:
            if f != None:
                tmp_l.append(f)
            else:
                #break
                continue
        fanarts_id = tmp_l
        #print('fanarts id',fanarts_id)
        if len(fanarts_id) in [0,1]:
            fanarts = None
        else:
            fanarts = Tweetdata2.objects.only('t_id',
                                                'media_url',
                                                'media_url_truncated',
                                                'u_id',
                                                'p_image',
                                                ).filter(
                                                t_id__in=fanarts_id
                                                )[:10]
        
    params = {
            'title':'プラコメ',
            'pn_data':pn_data,
            'data_num':p_num + n_num,
            'p_num':p_num,
            'n_num':n_num,
            'p2_num':p2_num,
            'n2_num':n2_num,
            'p1_num':p1_num,
            'n1_num':n1_num,    
            'p2_counts':p2_counts,
            'p1_counts':p1_counts,            
            'n1_counts':n1_counts,
            'n2_counts':n2_counts,
            'pn_counts_date':json.dumps(pn_counts_date),
            'pn_counts_date_text':pn_counts_date,   
            'period_start':period_start,
            'period_end':period_end,
            'locations':prefs_c,
            'locations_map':prefs_m,
            'n_locations':n_prefs_c,
            'n_locations_map':n_prefs_m,

            'trend_obj':trend_obj,
            'freqs_obj':freqs_obj,

            'name':name,
            'title_name':SPC.sub(" ",record['title_name']),
            'summarys':summarys,
            'n_summarys':n_summarys,
            'events':long_event_dic,
            'chara_rank':chara_rank,
            'op_rank':op_rank,
            'ed_rank':ed_rank,
            'cv_rank':cv_rank,
            'chara_syokai':chara_syokai,
            'op_syokai':op_syokai,            
            'ed_syokai':ed_syokai,            
            'cv_syokai':cv_syokai,
            'relates':relates,
            'about':about,
            'short_name':SPC.sub(' ',record['short_name']),
            'past':record['past'], #tmp
            'oadates':oadates,
            'episode':episode,
            'title_episode':title_episode,
            'prevlink':prevlink,
            'title_tag':title_tag,
            'fanarts':fanarts,
            'post':post_sta,
            'comments': comments,
            'comment_form':comment_form,
        }

    return render(request,'sentiment/anime/anime.html',params)


def character(request,name):
    return HttpResponse(status=410)
    raise Http404("Page does not exist.")    
    
    #if request.method == 'POST' and 'Search' in request.POST:
        #print('Search:',request.POST('Search'))

    
    form = DateForm()
    form2 = CharacterForm()
    form3 = AnimeForm()

    pn_counts_date=[] # 投稿日付（グラフ横軸)
    locations=[]
    CharField.register_lookup(Length, 'length') #  registered as a transform
    
    character_filter = request.POST.get('character_filter')
    anime_filter = request.POST.get('anime_filter')
    anime_filter2 = request.POST.get('Search')


    try:        
        record = Official_names.objects.values('index',
                                               'kind',
                                               'title_name',
                                               'hidden'
                                               ).get(url_name=name)

    except Official_names.DoesNotExist as e:
        return HttpResponse(status=410)
        #raise Http404("Page does not exist.")
    
    if record['kind'] != 1 or record['hidden'] == True: # animeページにアクセスしようとした場合
        return HttpResponse(status=410)
        #raise Http404("Page does not exist.")
    
    
# statisticsと日時取得        
    #print("statistics access")
    statistics = Statistics1week.objects.values('s_date','e_date','p2_count_d1', 'p1_count_d1','n2_count_d1', 'n1_count_d1',
                                        'p2_count_d2', 'p1_count_d2','n2_count_d2', 'n1_count_d2',
                                        'p2_count_d3', 'p1_count_d3','n2_count_d3', 'n1_count_d3',
                                        'p2_count_d4', 'p1_count_d4','n2_count_d4', 'n1_count_d4',
                                        'p2_count_d5', 'p1_count_d5','n2_count_d5', 'n1_count_d5',
                                        'p2_count_d6', 'p1_count_d6','n2_count_d6', 'n1_count_d6',
                                        'p2_count_d7', 'p1_count_d7','n2_count_d7', 'n1_count_d7',
                                        'p_tweet1_id','p_tweet2_id','p_tweet3_id','p_tweet4_id',
                                        'p_tweet5_id','p_tweet6_id','p_tweet7_id','p_tweet8_id',
                                        'p_tweet9_id','p_tweet10_id',
                                        'n_tweet1_id','n_tweet2_id','n_tweet3_id','n_tweet4_id',
                                        'n_tweet5_id','n_tweet6_id','n_tweet7_id','n_tweet8_id',
                                        'n_tweet9_id','n_tweet10_id'
                                        ).get(official_name_id=record['index'])    
    #statistics = list(Statistics1week.objects.get(title=title_no,character=0).values()) # titleはfilter,charaはgetで取得
    #print("done")

    s_date = statistics['s_date']
    e_date = statistics['e_date']
    #print('s_date',s_date)
    #print('e_date',e_date)

    p2_counts=[0,0,0,0,0,0,0]# 日付ごとの投稿数(グラフ縦軸)
    p1_counts=[0,0,0,0,0,0,0]# 日付ごとの投稿数(グラフ縦軸)
    n1_counts=[0,0,0,0,0,0,0]# 日付ごとの投稿数(グラフ縦軸)
    n2_counts=[0,0,0,0,0,0,0]    

    for i in range(7):
        p2_counts[i] = statistics['p2_count_d{0}'.format(7-i)]
        p1_counts[i] = statistics['p1_count_d{0}'.format(7-i)]
        n2_counts[i] = statistics['n2_count_d{0}'.format(7-i)]
        n1_counts[i] = statistics['n1_count_d{0}'.format(7-i)]
            

    for i in range(7):
        d = (e_date + datetime.timedelta(hours=9)).date() - datetime.timedelta(days = 6 - i)
        pn_counts_date.append(str(d.month)+'月'+str(d.day)+'日')

    p2_num = sum(p2_counts)
    p1_num = sum(p1_counts)
    p_num = p2_num + p1_num

    if p_num < MIN_SHOW:
        return HttpResponse(status=410)
        raise Http404("Page does not exist.")
    
    n2_num = sum(n2_counts)
    n1_num = sum(n1_counts)
    n_num = n2_num + n1_num

# news取得       
    long_event_dic = Longevents.objects.filter(
                                              (Q(date_s__lte=e_date) & Q(date_e__gte=s_date)) | (Q(date_e__gte=s_date) & Q(date_s__lte=e_date)),
                                               Q(official_name_id=record['index']),
                                               #Q(date_s__range=(s_date,e_date)) | Q(date_e__range=(s_date,e_date)),
                                               
                                               # 1週間の最後の日付よりもイベントの開始日付が遅い場合は該当外
                                               # イベントの終了日付が1週間の最初の日付よりも早い場合は該当外
                                               Q(title__isnull=False), # titleが空欄以外
                                               ).values( 
                                                        #'official_name',
                                                        #'url',
                                                        'title',
                                                        'date_s',
                                                        'date_e',
                                                        'time_s',
                                                        'time_e',
                                                        'weekday',
                                                        'media',
                                                        'channel',
                                                        'title'
                                                         )[:5]


# pn10投稿データ取得
    n_data = [Tweetdata2.objects.values().get(t_id = statistics['n_tweet{0}_id'.format(i + 1)]) for i in range(10) if statistics['n_tweet{0}_id'.format(i + 1)] != '']
    p_data = [Tweetdata2.objects.values().get(t_id = statistics['p_tweet{0}_id'.format(i + 1)]) for i in range(10) if statistics['p_tweet{0}_id'.format(i + 1)] != '']
              
# trend取得
    # trend(1~10)を取得
    trend_word = []
    trend_word_count = []
    
    
    try:        
        trends_obj = Trend_ranks.objects.values('trend1',
                                            'trend2',
                                            'trend3',
                                            'trend4',
                                            'trend5',
                                            'trend6',
                                            'trend7',
                                            'trend8',
                                            'trend9',
                                            'trend10',
                                            'trend1_count',
                                            'trend2_count',
                                            'trend3_count',
                                            'trend4_count',
                                            'trend5_count',
                                            'trend6_count',
                                            'trend7_count',
                                            'trend8_count',
                                            'trend9_count',
                                            'trend10_count',
                                           ).get(official_name_id=record['index'])
    except Trend_ranks.DoesNotExist as e:
        pass
        #print(e)
    else:
        
        # 要約,投稿数,ツイートを辞書型に変換
        for i in range(10):
            if trends_obj['trend{0}'.format(i + 1)] == None:
                continue            
            trend_word.append(trends_obj['trend{0}'.format(i + 1)])
            trend_word_count.append(trends_obj['trend{0}_count'.format(i + 1)])

    shortage = 10 - len(trend_word)
    if shortage > 0:
        for i in range(shortage):
            trend_word.append('')
            trend_word_count.append(0)

# pref取得
    prefs_c = []
    
    #print('getting prefs..')
    
    try:        
        prefs_obj = Pref_ranks.objects.values('pref1',
                                            'pref2',
                                            'pref3',
                                            'pref4',
                                            'pref5',
                                            'pref6',
                                            'pref7',
                                            'pref8',
                                            'pref9',
                                            'pref10',
                                            'pref1_count',
                                            'pref2_count',
                                            'pref3_count',
                                            'pref4_count',
                                            'pref5_count',
                                            'pref6_count',
                                            'pref7_count',
                                            'pref8_count',
                                            'pref9_count',
                                            'pref10_count',
                                           ).get(official_name_id=record['index'])
    except Pref_ranks.DoesNotExist as e:
        pass
        #print(e)
    else:
        
        # 要約,投稿数,ツイートを辞書型に変換
        for i in range(10):
            if prefs_obj['pref{0}'.format(i + 1)] == None:
                continue
            #prefs.append(prefs_obj['pref{0}'.format(i + 1)])
            #prefs_c.append(prefs_obj['pref{0}_count'.format(i + 1)])
            prefs_c.append((prefs_obj['pref{0}'.format(i + 1)], prefs_obj['pref{0}_count'.format(i + 1)]))
    
    shortage = 10 - len(prefs_c)
    if shortage > 0:
        for i in range(shortage):
            prefs_c.append(('',0))

# frequency取得
    freqs_c = []

    try:        
        freqs_obj = Frequentwords.objects.values_list(
                                                    'freq1',
                                                    'freq1_count',
                                                    'freq2',
                                                    'freq2_count',
                                                    'freq3',
                                                    'freq3_count',
                                                    'freq4',
                                                    'freq4_count',
                                                    'freq5',
                                                    'freq5_count',
                                                    'freq6',
                                                    'freq6_count',
                                                    'freq7',
                                                    'freq7_count',
                                                    'freq8',
                                                    'freq8_count',
                                                    'freq9',
                                                    'freq9_count',
                                                    'freq10',
                                                    'freq10_count',
                                                    
                                                    'freq11',
                                                    'freq11_count',
                                                    'freq12',
                                                    'freq12_count',
                                                    'freq13',
                                                    'freq13_count',
                                                    'freq14',
                                                    'freq14_count',
                                                    'freq15',
                                                    'freq15_count',
                                                    'freq16',
                                                    'freq16_count',
                                                    'freq17',
                                                    'freq17_count',
                                                    'freq18',
                                                    'freq18_count',
                                                    'freq19',
                                                    'freq19_count',
                                                    'freq20',
                                                    'freq20_count',
                                                    
                                                    'freq21',
                                                    'freq21_count',
                                                    'freq22',
                                                    'freq22_count',
                                                    'freq23',
                                                    'freq23_count',
                                                    'freq24',
                                                    'freq24_count',
                                                    'freq25',
                                                    'freq25_count',
                                                    'freq26',
                                                    'freq26_count',
                                                    'freq27',
                                                    'freq27_count',
                                                    'freq28',
                                                    'freq28_count',
                                                    'freq29',
                                                    'freq29_count',
                                                    'freq30',
                                                    'freq30_count',
                                                    
                                                    'freq31',
                                                    'freq31_count',
                                                    'freq32',
                                                    'freq32_count',
                                                    'freq33',
                                                    'freq33_count',
                                                    'freq34',
                                                    'freq34_count',
                                                    'freq35',
                                                    'freq35_count',
                                                    'freq36',
                                                    'freq36_count',
                                                    'freq37',
                                                    'freq37_count',
                                                    'freq38',
                                                    'freq38_count',
                                                    'freq39',
                                                    'freq39_count',
                                                    'freq40',
                                                    'freq40_count',
                                                    
                                                    'freq41',
                                                    'freq41_count',
                                                    'freq42',
                                                    'freq42_count',
                                                    'freq43',
                                                    'freq43_count',
                                                    'freq44',
                                                    'freq44_count',
                                                    'freq45',
                                                    'freq45_count',
                                                    'freq46',
                                                    'freq46_count',
                                                    'freq47',
                                                    'freq47_count',
                                                    'freq48',
                                                    'freq48_count',
                                                    'freq49',
                                                    'freq49_count',
                                                    'freq50',
                                                    'freq50_count',
                                                    ).get(official_name_id=record['index'])
    except Frequentwords.DoesNotExist as e:
        pass
        #print(e)
        
    else:
        
        for i in range(50):
            if freqs_obj[i * 2] == None:
                break
            freqs_c.append((freqs_obj[i * 2], freqs_obj[i * 2 + 1]))
        
    #print(freqs_c)
# 2週間分遡る
    s_date = s_date.date() - datetime.timedelta(days = 7)
        
# 要約取得
    sum_obj = Tweetdata2.objects.filter(
                                        #t_date__range=(s_date,e_date),# 7日前~1日前まで
                                        summary_title_id=record['index'],
                                        ).values('t_id',
                                                          'u_id',
                                                          't_date',
                                                          'content',
                                                          's_name',
                                                          'media_url',
                                                          'u_name',
                                                          'p_image',
                                                          's_class',
                                                          't_id_char',
                                                          'entities_display_url',
                                                          'entities_url',
                                                          'sum_title_text'
                                                          )
        
    # 要約文(1~20)を取得
    try:        
        summary_texts = Summarys.objects.values_list('summary_text1',
                                               'summary_text2',
                                               'summary_text3',
                                               'summary_text4',
                                               'summary_text5',
                                               'summary_text6',
                                               'summary_text7',
                                               'summary_text8',
                                               'summary_text9',
                                               'summary_text10',
                                               'summary_text21',
                                               'summary_text22',
                                               'summary_text23',
                                               'summary_text24',
                                               'summary_text25',
                                               'summary_text26',
                                               'summary_text27',
                                               'summary_text28',
                                               'summary_text29',
                                               'summary_text30',
                                               'related1_id',
                                               'related2_id',
                                               'related3_id',
                                               'related4_id',
                                               'related5_id',
                                               ).get(official_name_id=record['index'])                                                 

    except Summarys.DoesNotExist as e:
        #print(e)
        summarys = []
        n_summarys = []
        relates = []
    else:
        #print('sumary_tests',summary_texts)
        
        # 要約に選ばれたツイート取得
        contents = [[] for i in range(40)] # 0-4positive,5-9negative 
        for obj in sum_obj:
            contents[obj['sum_title_text'] - 1].append(obj)
                # contents = [[obj,obj..](summary1のobj),[obj,obj,obj..](summary2のobj),..]
        #print('contents',contents)
        
        summarys = []
        n_summarys = []
        # 要約,投稿数,ツイートを辞書型に変換
        for i in range(0, 10):
            if summary_texts[i] == None:
                break
            else:
                summarys.append({'要約':summary_texts[i],
                                 '投稿数':len(contents[i]),
                                 '原文':contents[i][:30]
                                })     
        for i in range(10, 20):
            if summary_texts[i] == None:
                break
            else:
                #print('a',summary_texts[i])
                n_summarys.append({'要約':summary_texts[i],
                                   '投稿数':len(contents[10 + i]), #20以降
                                   '原文':contents[10 + i][:30]
                                  })     
                #print(n_summarys)   

        # 類似ブランド
        relates = []
        for related_no in summary_texts[21:]:
            if related_no == 0:
                continue
            
            try:
                related_record = Official_names.objects.get(index=related_no)
            except:
                continue
            if related_record.hidden == True:
                continue

            try:             
                statistics = Statistics1week.objects.get(official_name_id=related_no)
            except Statistics1week.DoesNotExist as e:
                pass
                #print(e)        
            else:
                pcount = sum([
                        statistics.p1_count_d1,                                            
                        statistics.p1_count_d2,                                            
                        statistics.p1_count_d3,                                            
                        statistics.p1_count_d4,                                            
                        statistics.p1_count_d5,                                            
                        statistics.p1_count_d6,                                            
                        statistics.p1_count_d7,
                        statistics.p2_count_d1,                                            
                        statistics.p2_count_d2,                                            
                        statistics.p2_count_d3,                                            
                        statistics.p2_count_d4,                                            
                        statistics.p2_count_d5,                                            
                        statistics.p2_count_d6,                                            
                        statistics.p2_count_d7
                        ])
                if pcount < MIN_SHOW:
                    continue # 50未満は非表示
                relates.append({'pcount':pcount,
                                'brand':related_record.official_name
                               })            
    #print(relates)
    
   
    #print('chara_rank',chara_rank[:10])
    params = {
            'title':'プラコメ',
            #'data':data,
            'p_data':p_data,
            'n_data':n_data,
            'data_num':p_num + n_num,
            'p_num':p_num,
            'n_num':n_num,
            'p2_num':p2_num,
            'n2_num':n2_num,
            'p1_num':p1_num,
            'n1_num':n1_num,   
            'p2_counts':p2_counts,
            'p1_counts':p1_counts,            
            'n1_counts':n1_counts,
            'n2_counts':n2_counts,
            'pn_counts_date':json.dumps(pn_counts_date),
            'pn_counts_date_text':pn_counts_date,   
            'period_start':s_date,
            'period_end':pn_counts_date[6],
            'locations':prefs_c,
            'frequentwords':freqs_c,
                 
            'trend_word':trend_word,
            'trend_word_count':trend_word_count,
            #'fname':fname,
            
            'character_filter':character_filter,
            'name':name,
            'title_name':record['title_name'],
            'form':form,
            'form2':form2,
            'form3':form3,
            'summarys':summarys,
            'n_summarys':n_summarys,
            'events':long_event_dic,
            #'chara_rank':chara_rank,
            'relates':relates,
        }

    return render(request,'sentiment/anime/character/character.html',params)


    
def get_unique_list(seq,index):
    """リスト(タプル)のリストで入れ子のindex番目の要素の重複を削除する
    例：i==0 [(1,2),(3,4),(1,3)]→[(1,2),(3,4)]
       i==1 [(1,2),(3,4),(2,2)]→[(1,2),(3,4)]
    """
    
    if index + 1 > len(seq[0]):
        print("index error(index is over than len(seq).)")
        return None
    
    seen = []
    return [x for x in seq if x[index] not in seen and not seen.append(x[index])]  


def showdetail(request,name,episode=0):


### purakome.com to purakome.net    
    #if request.META.get("HTTP_HOST") == r'purakome.com':
        #return HttpResponse(status=410)
###


    try:
        record = Official_names.objects.values('index',
                                               'kind',
                                               'title_name',
                                               'hidden',
                                               'past',
                                               'short_name',
                                               ).get(url_name=name)
    except Official_names.DoesNotExist as e:
        return HttpResponse(status=404)
    if record['kind'] not in [0,10] or record['hidden'] == True: # charaページにアクセスしようとした場合
        return HttpResponse(status=404)

    
    if record['kind'] == 0:
        params=get_documents(request,name,episode,record,kind=0)
        return render(request,'sentiment/anime/detail_anime.html',params)
        
    elif record['kind'] == 10:
        params=get_documents(request,name,episode,record,kind=10)
        return render(request,'sentiment/johnnys/detail_johnnys.html',params)


def get_documents(request,name,episode,record,kind):
    #return HttpResponse(status=410)
    #raise Http404("Page does not exist.")

    post = slugify('{0} {1}'.format(record['index'],episode))


    s_class = []
    form = pn_detailForm(request.GET)
    form2 = summarizeForm(request.GET)
    form3 = keywordForm() # 値は保持しない

    very_positive = request.GET.get('very_positive') # 'on'/None
    positive = request.GET.get('positive')
    very_negative = request.GET.get('very_negative')
    negative = request.GET.get('negative')
    summarize = request.GET.get('summarize')
    #print('episode',episode)

    if positive != None:
        s_class.append(3)
    if very_positive != None:
        s_class.append(4)
    if negative != None:
        s_class.append(1)
    if very_negative != None:
        s_class.append(0)

    if s_class == []:
        s_class = [3,4,1,0]

# 日時取得
    #print("statistics access")

    try:
        statistics = Statistics1week.objects.values('s_date',
                                                    'e_date',
                                                   ).get(post=post)
    except Statistics1week.DoesNotExist as e:
        #print(e)
        return HttpResponse(status=410)

    #print("done")

    s_date = statistics['s_date']
    e_date = statistics['e_date']

    
    summarys = [] #p,n両方の要約を入れる
    data = []
    if summarize != None:
        keyword=''
# 要約取得 (要約されない投稿は一旦表示なし)
        sum_obj = Tweetdata2.objects.filter(
                                            t_date__range=(s_date,e_date),# 7日前~1日前まで
                                            sum_title_id=record['index'],
                                            ).values('t_id',
                                                    'u_id',
                                                    't_date',
                                                    'content',
                                                    's_name',
                                                    'media_url',
                                                    'u_name',
                                                    'p_image',
                                                    's_class',
                                                    't_id_char',
                                                    'entities_display_url',
                                                    'entities_url',
                                                    'media_url',
                                                    'media_url_truncated',
                                                    'sum_title_text',
                                                    'hashtag'
                                                    )


        # 要約文(all)を取得
        try:
            summary_texts = Summarys.objects.values_list(
                                                   'summary_text1',
                                                   'summary_text2',
                                                   'summary_text3',
                                                   'summary_text4',
                                                   'summary_text5',
                                                   'summary_text6',
                                                   'summary_text7',
                                                   'summary_text8',
                                                   'summary_text9',
                                                   'summary_text10',
                                                   'summary_text11',
                                                   'summary_text12',
                                                   'summary_text13',
                                                   'summary_text14',
                                                   'summary_text15',
                                                   'summary_text16',
                                                   'summary_text17',
                                                   'summary_text18',
                                                   'summary_text19',
                                                   'summary_text20',

                                                   'summary_text21',
                                                   'summary_text22',
                                                   'summary_text23',
                                                   'summary_text24',
                                                   'summary_text25',
                                                   'summary_text26',
                                                   'summary_text27',
                                                   'summary_text28',
                                                   'summary_text29',
                                                   'summary_text30',
                                                   'summary_text31',
                                                   'summary_text32',
                                                   'summary_text33',
                                                   'summary_text34',
                                                   'summary_text35',
                                                   'summary_text36',
                                                   'summary_text37',
                                                   'summary_text38',
                                                   'summary_text39',
                                                   'summary_text40',
                                                   ).get(post=post)

        except Summarys.DoesNotExist as e:
            return HttpResponse(status=410)
            summarys = []
            n_summarys = []
        else:
            #print('sumary_tests',summary_texts)

            # 要約に選ばれたツイート取得
            contents = [[] for i in range(40)] # 0-4positive,5-9negative
            for obj in sum_obj:
                if safetext(obj['content']):
                    contents[obj['sum_title_text'] - 1].append(obj)

            summarys = []
            n_summarys = []


            if very_positive != None or positive != None:
            # 要約,投稿数,ツイートを辞書型に変換
                for i in range(0, 20):
                    if summary_texts[i] == None:
                        continue
                    else:
                        summarys.append({'要約':summary_texts[i],
                                         '投稿数':len(contents[i]),
                                         '原文':contents[i]
                                         }
                                        )
                # 後で合流した要約の場合投稿数がずれる可能性あるので
                summarys = sorted(summarys,key=lambda x: x['投稿数'],reverse=True)

            if very_negative != None or negative != None:
                for i in range(20, 40):
                    if summary_texts[i] == None:
                        continue
                    else:
                        n_summarys.append({'要約':summary_texts[i],
                                           #'投稿数':len(contents[15 + i]), #20以降
                                           #'原文':contents[15 + i][:30]
                                           '投稿数':len(contents[i]), #20以降
                                           '原文':contents[i]
                                           }) # 各要約30投稿のみ表示
                n_summarys = sorted(n_summarys,key=lambda x: x['投稿数'],reverse=True)
    else: # summarize なしの場合は全投稿表示
        #クエリを初期化
        query = Q()    
        query.add(Q(spam=False), Q.AND)
        query.add(Q(s_class__in=s_class), Q.AND)
        query.add(Q(t_date__range=[s_date,e_date]), Q.AND)
        query.add(Q(title1=record['index']) | Q(title2=record['index']) | Q(title3=record['index']), Q.AND)
    
        keyword = request.GET.get('keyword')
        #print('keyword',keyword)
        if keyword in [None,'']:
            keyword = ''
            pass
        else:
            key_forsearch = unicodedata.normalize('NFKC',keyword.lower()).strip() # 正規化
            key_forsearch = re.sub(r" +"," ",key_forsearch) # 単語間のスペース数を揃える       

            keylist_or = key_forsearch.split(",")
            keylist_or = list(set(keylist_or))
            #print('keylist_or',keylist_or)
            #keylist_or = ['a','b c','d e']
            query2 = Q() # or条件を入れる
            for key_or in keylist_or:
                if re.search(" ",key_or):# &条件が含まれる場合
                    keylist_and = key_or.split(" ")
                    query3 = Q() # &条件を入れる
                    for key_and in keylist_and:
                        query3.add(Q(wakachi__icontains=key_and),Q.AND)
                    query2.add(query3,Q.OR)

                else:
                    query2.add(Q(wakachi__icontains=key_or),Q.OR)
                    
            query.add(query2,Q.AND)

        summarys = []
        n_summarys = []
        #print("getting posts..")

        data = Tweetdata2.objects.only(
                                        't_id',
                                        'u_id',
                                        't_date',
                                        'content',
                                        's_name',
                                        'media_url',
                                        'u_name',
                                        'p_image',
                                        's_class',
                                        't_id_char',
                                        'entities_display_url',
                                        'entities_url',
                                        'media_url',
                                        'media_url_truncated',
                                        'sum_title_text',
                                        'hashtag'
                                        ).filter(query)[:20]

        #print("done.")

# 頻出語（サイドバー
    try:
        freqs_obj = Frequentwords.objects.values_list('freq1','freq2','freq3','freq4','freq5','freq6','freq7','freq8','freq9','freq10','freq11','freq12','freq13','freq14','freq15','freq16','freq17','freq18','freq19','freq20','freq21','freq22','freq23','freq24','freq25','freq26','freq27','freq28','freq29','freq30','freq31','freq32','freq33','freq34','freq35','freq36','freq37','freq38','freq39','freq40','freq41','freq42','freq43','freq44','freq45','freq46','freq47','freq48','freq49','freq50',
                                                      'freq1_count','freq2_count','freq3_count','freq4_count','freq5_count','freq6_count','freq7_count','freq8_count','freq9_count','freq10_count','freq11_count','freq12_count','freq13_count','freq14_count','freq15_count','freq16_count','freq17_count','freq18_count','freq19_count','freq20_count','freq21_count','freq22_count','freq23_count','freq24_count','freq25_count','freq26_count','freq27_count','freq28_count','freq29_count','freq30_count','freq31_count','freq32_count','freq33_count','freq34_count','freq35_count','freq36_count','freq37_count','freq38_count','freq39_count','freq40_count','freq41_count','freq42_count','freq43_count','freq44_count','freq45_count','freq46_count','freq47_count','freq48_count','freq49_count','freq50_count'
                                                      ).get(post=post)

    except Frequentwords.DoesNotExist as e:
        freqs_obj = None
        
        
    period_start = (s_date + datetime.timedelta(hours = 9)).date()
    period_end = (e_date + datetime.timedelta(hours = 9)).date()


    data_num = len(data)

    if data_num == 20:
        datalimit = True
    else:
        datalimit = False


    params = {
            'title':'プラコメ',
            'pnmsg':'ツイート一覧',
            'data':data,
            'data_num':data_num if data_num > 0 else sum([s['投稿数'] for s in summarys]),
            'datalimit':datalimit,
            'summarys':summarys,
            'n_summarys':n_summarys,

            'period_start':period_start,
            'period_end':period_end,
            'name':name,
            'title_name':SPC.sub(" ",record['title_name']),
            'short_name':SPC.sub(' ',record['short_name']),
            'form':form,
            'form2':form2,
            'form3':form3,
            'keyword':keyword,
            'episode':episode,
            'freqs_obj':freqs_obj,            
        }

    return params

 
def posts_character(request,name):
    return HttpResponse(status=410)
    raise Http404("Page does not exist.")
    s_class = []
    form = pn_detailForm(request.GET)
    form2 = summarizeForm(request.GET)
    form3 = keywordForm() # 値は保持しない

    very_positive = request.GET.get('very_positive') # 'on'/None
    positive = request.GET.get('positive')
    very_negative = request.GET.get('very_negative')
    negative = request.GET.get('negative')
    summarize = request.GET.get('summarize')
    keyword = request.GET.get('keyword')
    if keyword == None:
        keyword = ''
    
   
    if positive != None:
        s_class.append(3)    
    if very_positive != None:
        s_class.append(4)
    if negative != None:
        s_class.append(1)
    if very_negative != None:
        s_class.append(0)
        
    if s_class == []:
        s_class = [3,4,1,0]
    
    try:        
        record = Official_names.objects.values('index',
                                               'kind',
                                               'title_name',
                                               'hidden'
                                               ).get(official_name=name)
    except Official_names.DoesNotExist as e:
        #print(e) 
        #print(name)
        return HttpResponse(status=410)
        raise Http404("Page does not exist.") 
    if record['kind'] != 1 or record['hidden'] == True: # アニメページにアクセスしようとした場合
        return HttpResponse(status=410)
        raise Http404("Page does not exist.")  

# 日時取得        
    #print("statistics access")
    # pカウント取るのはadsense取るまでの一時処理
    statistics = Statistics1week.objects.values('s_date','e_date',
                                                'p2_count_d1', 'p1_count_d1',
                                                'p2_count_d2', 'p1_count_d2',
                                                'p2_count_d3', 'p1_count_d3',
                                                'p2_count_d4', 'p1_count_d4',
                                                'p2_count_d5', 'p1_count_d5',
                                                'p2_count_d6', 'p1_count_d6',
                                                'p2_count_d7', 'p1_count_d7',
                                               ).get(official_name_id=record['index'])    
    #print("done")

#一時処理------------
    p2_counts=[0,0,0,0,0,0,0]# 
    p1_counts=[0,0,0,0,0,0,0]# 

    for i in range(7):
        p2_counts[i] = statistics['p2_count_d{0}'.format(7-i)]
        p1_counts[i] = statistics['p1_count_d{0}'.format(7-i)]

    p_num = sum(p2_counts) + sum(p1_counts)

    if p_num < MIN_SHOW:
        return HttpResponse(status=410)
        raise Http404("Page does not exist.")
#------------
    
    s_date = statistics['s_date']
    e_date = statistics['e_date']
    #print('s_date',s_date)
    #print('e_date',e_date)

    summarys = [] #p,n両方の要約を入れる
    data = []
    if summarize != None:

# 要約取得 (要約されない投稿は一旦表示なし)
        sum_obj = Tweetdata2.objects.filter(
                                            #t_date__range=(s_date,e_date),# 7日前~1日前まで
                                            summary_title_id=record['index'],
                                            ).values('t_id',
                                                    'u_id',
                                                    't_date',
                                                    'content',
                                                    's_name',
                                                    'media_url',
                                                    'u_name',
                                                    'p_image',
                                                    's_class',
                                                    't_id_char',
                                                    'entities_display_url',
                                                    'entities_url',
                                                    'sum_title_text'
                                                    )


        # 要約文(all)を取得
        try:        
            summary_texts = Summarys.objects.values_list(
                                                   'summary_text1',
                                                   'summary_text2',
                                                   'summary_text3',
                                                   'summary_text4',
                                                   'summary_text5',
                                                   'summary_text6',
                                                   'summary_text7',
                                                   'summary_text8',
                                                   'summary_text9',
                                                   'summary_text10',
                                                   'summary_text11',
                                                   'summary_text12',
                                                   'summary_text13',
                                                   'summary_text14',
                                                   'summary_text15',
                                                   'summary_text16',
                                                   'summary_text17',
                                                   'summary_text18',
                                                   'summary_text19',
                                                   'summary_text20', 

                                                   'summary_text21',
                                                   'summary_text22',
                                                   'summary_text23',
                                                   'summary_text24',
                                                   'summary_text25',
                                                   'summary_text26',
                                                   'summary_text27',
                                                   'summary_text28',
                                                   'summary_text29',
                                                   'summary_text30',
                                                   'summary_text31',
                                                   'summary_text32',
                                                   'summary_text33',
                                                   'summary_text34',
                                                   'summary_text35',
                                                   'summary_text36',
                                                   'summary_text37',
                                                   'summary_text38',
                                                   'summary_text39',
                                                   'summary_text40',                                                   
                                                   ).get(official_name_id=record['index'])
    
        except Summarys.DoesNotExist as e:
            pass
            #print(e)
      
        else:
            #print('sumary_tests',summary_texts)
            
            # 要約に選ばれたツイート取得
            contents = [[] for i in range(40)] # 0-4positive,5-9negative 
            for obj in sum_obj:
                contents[obj['sum_title_text'] - 1].append(obj)
                    # contents = [[obj,obj..](summary1のobj),[obj,obj,obj..](summary2のobj),..]
            #print('contents',contents)
            

            
            if very_positive != None or positive != None:
            # 要約,投稿数,ツイートを辞書型に変換
                for i in range(0, 20):
                    if summary_texts[i] == None:
                        break
                    else:
                        summarys.append({'要約':summary_texts[i],
                                         '投稿数':len(contents[i]),
                                         '原文':contents[i]
                                         }
                                        )     
            if very_negative != None or negative != None:                        
                for i in range(20, 40):
                    if summary_texts[i] == None:
                        break
                    else:
                        #print('a',summary_texts[i])
                        summarys.append({'要約':summary_texts[i],
                                           '投稿数':len(contents[i]), #20以降
                                           '原文':contents[i]
                                           })      
                        #print(n_summarys)
            summarys = sorted(summarys, key=lambda x:x['投稿数'], reverse=True) # 投稿数順に並び替え    
            #print(summarys)
                
    else: # summarize なしの場合は全投稿表示  
         
        #print("getting posts..")

        data = Tweetdata2.objects.only(
                                            's_class',
                                            't_id',
                                            'u_id',
                                            't_date',
                                            'content',
                                            's_name',
                                            'media_url',
                                            'u_name',
                                            'p_image',
                                            't_id_char',
                                            'entities_url',
                                            'entities_display_url',
                                            'media_url_truncated',
                                            ).filter(#Q(spam=False),
                                                     Q(s_class__in=s_class),
                                                     #Q(t_date__range=[s_date,e_date]),
                                                     Q(character1=record['index']) | Q(character2=record['index']) | Q(character3=record['index']) | Q(character4=record['index']) | Q(character5=record['index']),
                                                     Q(content__icontains=keyword)
                                                             )[:500]
           
        #print("done.")        
                                 
    pn_counts_date = []
    for i in range(7):
        d = datetime.datetime.today().date() - datetime.timedelta(days = 7 - i)
        pn_counts_date.append(str(d.month)+'月'+str(d.day)+'日')                                             
    #print(len(data))

    data_num = len(data)
    
    if data_num == 500:
        datalimit = True
    else:
        datalimit = False
   
    params = {
            'title':'プラコメ',
            'pnmsg':'ツイート一覧',
         
            'data':data,
            'data_num':data_num if data_num > 0 else sum([s['投稿数'] for s in summarys]),
            'datalimit':datalimit,
            'summarys':summarys,

            'period_start':pn_counts_date[0],
            'period_end':pn_counts_date[6],
            'name':name,
            'title_name':record['title_name'],    
            'form':form,
            'form2':form2,
            'form3':form3,
            'keyword':keyword,
        }

     
    return render(request,'sentiment/anime/character/character_posts.html',params)
     
    
def pn_details(request,name,pn):
    return HttpResponse(status=410) 
    raise Http404("Page does not exist.")
    '''
    try:        
        record = Official_names.objects.values('index',
                                               'title',
                                               'title_name'
                                               ).get(official_name=name)
    except Official_names.DoesNotExist as e:
        #print(e) 
        return render(request,'sentiment/500.html')
 

    #print('p or n:',pn)
    if pn == 'positives':
        search_label1 = 3
        search_label2 = 4
        pnmsg = '満足/とても満足ツイート一覧'
    else:
        search_label1 = 0
        search_label2 = 1
        pnmsg = '不満/とても不満ツイート一覧'
      
# 6日分のデータ取得
# 日時取得        
    #print("statistics access")
    statistics = Statistics1week.objects.values('s_date','e_date'
                                               ).get(official_name_id=record['index'])    
    #print("done")
    s_date = statistics['s_date']
    e_date = statistics['e_date']
    #print('s_date',s_date)
    #print('e_date',e_date)
    
    #print("getting posts..")
    if record['title'] == True:
        p_data = Tweetdata2.objects.only(
                                        's_class',
                                        't_id',
                                        'u_id',
                                        't_date',
                                        'content',
                                        's_name',
                                        'media_url',
                                        'u_name',
                                        'p_image',
                                        't_id_char',
                                        'entities_url',
                                        'entities_display_url',
                                        'media_url_truncated',
                                        ).filter(#Q(spam=False),
                                                 Q(s_class=search_label1) | Q(s_class=search_label2),
                                                 #Q(t_date__range=[s_date,e_date]),
                                                 Q(title1=record['index']) | Q(title2=record['index']) | Q(title3=record['index'])
                                                         )   
    else:
        p_data = Tweetdata2.objects.only(
                                        's_class',
                                        't_id',
                                        'u_id',
                                        't_date',
                                        'content',
                                        's_name',
                                        'media_url',
                                        'u_name',
                                        'p_image',
                                        't_id_char',
                                        'entities_url',
                                        'entities_display_url',
                                        'media_url_truncated',
                                        ).filter(#Q(spam=False),
                                                 Q(s_class=search_label1) | Q(s_class=search_label2),
                                                 #Q(t_date__range=[s_date,e_date]),
                                                 Q(character1=record['index']) | Q(character2=record['index']) | Q(character3=record['index']) | Q(character4=record['index']) | Q(character5=record['index'])
                                                         )         
        
    #print("done.")                                         
    pn_counts_date = []
    for i in range(7):
        d = datetime.datetime.today().date() - datetime.timedelta(days = 7 - i)
        pn_counts_date.append(str(d.month)+'月'+str(d.day)+'日')                                             
    #print(len(p_data))
    

    
    params = {
            'title':'プラコメ',
            'pnmsg':pnmsg,
            'p_data':p_data[:200],
            'data_num':len(p_data),
            'period_start':pn_counts_date[0],
            'period_end':pn_counts_date[6],
            'name':name,
            'title_name':record['title_name'],
        }

    if record['title'] == True:   
        return render(request,'sentiment/anime/pn_details.html',params)
    else:
        return render(request,'sentiment/anime/character/character_pn_details.html',params)    
    '''

def inquiry(request):

    return HttpResponse(status=410)


class InquiryView(generic.FormView):
    template_name = 'sentiment/inquiry.html'
    form_class = InquiryForm
    success_url = reverse_lazy('contact')
    
    def form_valid(self, form): # バリデーションをすべて通ったら実施される
        form.send_email()
        messages.success(self.request,'メッセージを送信しました。') # 送信後のメッセージ
        return super().form_valid(form)


def sitepolicy(request):
    
    #if request.META.get("HTTP_HOST") == r'purakome.com':
        #return redirect(r'https://purakome.net/sentiment/sitepolicy/',permanent=True)

    return render(request,'sentiment/sitepolicy.html')


def aboutus(request):

    #if request.META.get("HTTP_HOST") == r'purakome.com':
        #return redirect(r'https://purakome.net/sentiment/aboutus/',permanent=True)
    
    return render(request,'sentiment/aboutus.html')


def quiz_index(request):

    #if request.META.get("HTTP_HOST") == r'purakome.com':
        #return HttpResponse(status=410)

    questions = []
    answers = []

    params = {
            'questions':questions,
            'answers':answers,
            'history':'',

        }
    return render(request,'sentiment/anime/quiz/quiz_index.html',params)


def questions(request, number):


    #if request.META.get("HTTP_HOST") == r'purakome.com':
        #return HttpResponse(status=410)


    if request.method == 'GET':
        t_ids = []
        questions = None
        answers = None
        question_i = (None,None)
        number = None
        score = None
        history = []
        level = None
        level_text = None
        q_text = None
        
    else:
        END_INDEX = re.compile(r"\[\d+\]")
        FAKE_KEY =re.compile(r"@+[@ ・]*")
        
        #print('number',number)
    
        if request.POST.get('anime_lv1'):
            kind = [0]
            level_text = '【アニメ編】'
            q_text = 'みんなどのアニメについて話しているのかな？'
            start = request.POST.get('anime_lv1').split(",") #(score, history, level)
        # start = "score,hisotry,level" ex."0,,1"
    
        elif request.POST.get('chara_lv1'):
            kind = [1]
            level_text = '【キャラクター初級編】'
            q_text = 'みんなどのアニメキャラクターについて話しているのかな？'
            #初級
            start = request.POST.get('chara_lv1').split(",") #(score, history, level)
        # start = "score,hisotry,level" ex."0,,1"
        elif request.POST.get('chara_lv2'):
            kind = [1]
            level_text = '【キャラクター上級編】'
            q_text = 'みんなどのアニメキャラクターについて話しているのかな？'
            #上級
            start = request.POST.get('chara_lv2').split(",")
        elif request.POST.get('oped_lv1'):
            kind = [2,3]
            level_text = '【アニメOP/ED曲編】'
            q_text = 'みんなどのアニメOP/ED曲について話しているのかな？'
            #上級
            start = request.POST.get('oped_lv1').split(",")
        elif request.POST.get('cv_lv1'):
            kind = [4]
            level_text = '【アニメ声優編】'
            q_text = 'みんなどの声優について話しているのかな？'
            #上級
            start = request.POST.get('cv_lv1').split(",")
            
        if number == 1:
            history = []
        else:
            history = start[1].split("-") # 解答済みの問題
    
        score = int(start[0])
        level = start[2] # anime_lv1, chara_lv1..
    
        exclude_l = [int(h) for h in history] + [329,341,786,860]# リコ(メイドインアビス)はリコリコが多く出てきてしまうため一旦除く
   
    # 静的に出題選択
        data_id = []
        record=None
        q_num = 10 # 出題ツイート数
        if level == "anime_lv1":#quizテーブルにはすべて出題可能なデータが入っている
            record=Quiz.objects.values().filter(Q(kind=0),
                                                Q(level=1),
                                                ~Q(official_name_id__in=exclude_l),
                                                )
        elif level == "chara_lv1":
            record=Quiz.objects.values().filter(Q(kind=1),
                                                Q(level=1),
                                                ~Q(official_name_id__in=exclude_l),
                                                )
        elif level == "chara_lv2":
            record=Quiz.objects.values().filter(Q(kind=1),
                                                Q(level=2),
                                                ~Q(official_name_id__in=exclude_l),
                                                )
            q_num = 5 # 長文5ツイート
        elif level == "oped_lv1":
            record=Quiz.objects.values().filter(Q(kind=2),
                                                Q(level=1),
                                                ~Q(official_name_id__in=exclude_l),
                                                )
        elif level == "cv_lv1":
            record=Quiz.objects.values().filter(Q(kind=4),
                                                Q(level=1),
                                                ~Q(official_name_id__in=exclude_l),
                                                )
         
        #print('len',len(record))
        # 問題を一つランダムにピックアップ
        choice_no = random.randint(0, len(record)-1)
        for i in range(1,31):
            if record[choice_no]['q_{0}_id'.format(i)]:
                data_id.append(record[choice_no]['q_{0}_id'.format(i)])
                
        random.shuffle(data_id)# 出題するt_id(5~10個)をシャッフル            
        #print('data_id',data_id) 
        data = Tweetdata2.objects.only( 
                                't_id',
                                't_date',
                                'content',
                                ).filter(t_id__in=data_id[:q_num])
        
        official_obj = Official_names.objects.only('official_name','quiz_key').get(index=record[choice_no]['official_name_id'])
    
        question_i = (record[choice_no]['official_name_id'],
                      official_obj.official_name
                      )
        # question_i = (1,'美少女戦士セーラームーン')
    
        keywords = official_obj.quiz_key
        #print('keywords',keywords)    
    
    # ダミー解答3つ選択
        choices = list(Official_names.objects.filter(#Q(title=False),
                                                       Q(kind__in=kind),
                                                       #Q(hidden=False),
                                                       #~Q(official_name__contains=' '),
                                                       ~Q(index__in=exclude_l),
                                                       ).values_list('index','official_name'))
    
    
    
    # 問題文のキーワードを隠す
        #print('data',data[0])
        questions = []
        t_ids = []
        for d in data:
            content = d.content
            content = re.sub(keywords,"@",content,0,re.IGNORECASE) # ['spyfamily','SPYFAMILY']
            # re.IGNORECASE入れてsubを使うと置換回数が1回になぜか設定されるため、0(無制限)で設定する
            #print('con',content)
            if FAKE_KEY.search(content):
                questions.append({'content':FAKE_KEY.sub(r"<font style='color:darkorange;'>OO</font>",content),'date':d.t_date})
                t_ids.append(d.t_id)
            # 正規表現ミスで一つも置換できなかった文は出題しない


    # answers作成
        choices.remove(question_i) # 出題除いた全indexからダミー解答３つ選ぶ
        answers = [question_i[1]] + [chara[1] for chara in random.sample(choices, k=3)]
    
        random.shuffle(answers) # 解答ボタンシャッフル
    
        history.append(str(question_i[0]))


    params = {
            't_ids': ",".join(t_ids), # idを文字列に
            'questions':questions,
            'answers':answers,
            'correct':question_i[1],
            'number':number,
            'score':score,
            'history':'-'.join(history),
            'level':level,
            'level_text':level_text,
            'q_text':q_text,

        }
    #print('params',params)
    return render(request,'sentiment/anime/quiz/questions.html',params)


def insert_tags(text,key,tag,casemix=True):
    """
        正規表現にマッチした箇所(単～複数)をhtmlタグで囲む
        text : text
        key :正規表現
        tag : htmlタグ
        case : true:正規表現 英字の大文字小文字を区別しない
               false:区別する
    """

    content = text # 上書きはしない
    if casemix == True:
        matched_iter = re.finditer(key,content,re.IGNORECASE)
    else:
        matched_iter = re.finditer(key,content)

    content = list(content) #一文字ずつのリストに        
    i = 0
    for w in matched_iter:
        content.insert(w.start()+i, tag)
        i += 1 # タグ加えた分右にずらず
        content.insert(w.end()+i, tag[0] + "/" + tag[1:])
        i += 1 # タグ加えた分右にずらず
    
    return "".join(content) # 文字列に戻して返却
      
            
def answers(request, number):

    #if request.META.get("HTTP_HOST") == r'purakome.com':
        #return HttpResponse(status=410)


    if request.method == 'GET':
        answer = None
        correct = None
        msg = None
        score = None
        records = None
        number = None
        history = None
        level = None
        fanarts = None
        level_text = None

    else:
        
        END_INDEX = re.compile(r"\[\d+\]")
    
        #print('number',number)
    
        if request.POST.get('answers0') != None:
            answer = request.POST.get('answers0')
        elif request.POST.get('answers1') != None:
            answer = request.POST.get('answers1')
        elif request.POST.get('answers2') != None:
            answer = request.POST.get('answers2')
        elif request.POST.get('answers3') != None:
            answer = request.POST.get('answers3')
    
        #print(answer)
        tmp = answer.split(",")
        answer = tmp[0]
        correct = tmp[1]
        score = int(tmp[2])
        history = tmp[3]
        level = tmp[4]
        level_text = tmp[5]
        data_id = tmp[6:]

        keywords = Official_names.objects.only('quiz_key').get(official_name=correct).quiz_key
      
    
        #print('ZZZ',keywords)
        records = [] # 解答ツイートのキャラ強調
        for d in data_id:
            record = Tweetdata2.objects.only('t_id',
                    'u_id',
                    't_date',
                    'content',
                    's_name',
                    'u_name',
                    'p_image',
                    's_class',
                    't_id_char',
                    'sum_title_text',
                    'hashtag',
                    ).get(t_id=d)
            # 正解を強調
            record.content = insert_tags(record.content,keywords,r"<b>",casemix=True)
            records.append(record)
            
        if answer == correct:
            msg = '正解!'
            score += 1
        else:
            msg = '残念..'
    
    # 画像取得
        correct_i = Official_names.objects.only('index').get(official_name=correct).index
        post=slugify('{0} {1}'.format(correct_i,0))
    
        try:
            fanarts_id = list(Fanarts.objects.values_list(
                                                  'fan_art1',
                                                  'fan_art2',
                                                  'fan_art3',
                                                  'fan_art4',
                                                  'fan_art5',
                                                  'fan_art6',
                                                  'fan_art7',
                                                  'fan_art8',
                                                  'fan_art9',
                                                  'fan_art10',
    
                                                  ).get(post=post))
        except Fanarts.DoesNotExist as e:
            #print(e)
            fanarts = None
        else:
            fanarts_id = [f for f in fanarts_id if f!=None]
            if len(fanarts_id) > 0:
                fanarts = Tweetdata2.objects.only('t_id',
                                                'media_url',
                                                'media_url_truncated',
                                                'u_id',
                                                'p_image',
                                                ).filter(t_id__in=fanarts_id,
                                                         )
            else:
                fanarts = None
    

    params = {
            'answer':answer,
            'correct':correct,
            'msg':msg,
            'score':score,
            'data':records,
            'number':number,
            'history':history,
            'level':level,
            'fanarts':fanarts,
            'level_text':level_text,
        }
    return render(request,'sentiment/anime/quiz/answers.html',params)


def result(request):

    #if request.META.get("HTTP_HOST") == r'purakome.com':
        #return HttpResponse(status=410)


    if request.method == 'GET':
        msg = None
        score = None
        score100 = None
        level_text = None
        post_sta = None
        comments = None
        comment_form = None

    else:
        # comment
        post_sta=get_object_or_404(Statistics1week,post=slugify('{0} {1}'.format(341,0)))
        #print('post   id',post_sta.id)
        # List of active comments for this post
        comments = Comment.objects.filter(target=post_sta.post,
                                          #parent_id=None,
                                          active=True)
        new_comment = None
        comment_form = CommentForm()
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.target = post_sta.post
            # Save the comment to the database
            new_comment.save()
            # redirect to same page and focus on that comment
        else:
            comment_form = CommentForm()



        answer = request.POST.get('result')
        tmp = answer.split(",")
        score = tmp[0]
        score100 = str(int(tmp[0])*20)
        level_text = tmp[1]
        msg = "あなたのスコア"
    params = {
            'msg':msg,
            'score':score,
            'score100':score100,
            'level_text':level_text,
            'post':post_sta,
            'comments': comments,
            'comment_form':comment_form,
        }
    return render(request,'sentiment/anime/quiz/result.html',params)


def toppage(request):

    #if request.META.get("HTTP_HOST") == r'purakome.com':
        #raise Http404("Page does not exist")

    msg=""
    params = {
            'msg':msg,
        }
    
    return render(request,'sentiment/toppage.html',params)


#def tmp_redirect(request):

#    if request.META.get("HTTP_HOST") == r'purakome.com': #301
#        raise Http404("Page does not exist")
#        #return HttpResponse(status=404)
#        #return redirect(r'https://purakome.net/sentiment/anime/',permanent=True)
#
#    return redirect('sentiment/anime/') # .netは302



def sentiment_demo(request):

    if request.method == "GET":
        params = {
                  'key':None,
                  'query':None,
                  'msg':None,

                'p2data':None,
                'p1data':None,
                'n1data':None,
                'n2data':None,
                'total':None,
                'fname':None,
                  }
    else:
        q = request.POST.get('talk')
        #print('original_query',q)
        reply_chk = request.POST.get('reply_chk')
        media_chk = request.POST.get('media_chk')
        content_chk = request.POST.get('content_chk')
        link_chk = request.POST.get('group_link_radios')
        # 正規化(小文字化はしない)
        q = unicodedata.normalize('NFKC',q.strip())
        q = re.sub(r'[ \s]+',' ',q)
        
        # 言語設定
        lang = 0
        if re.search(r"lang:[a-z][a-z]",q):
            if re.search(r"lang:ja",q): #言語指定ない場合日本語
                lang = 0
            elif re.search(r"lang:en",q):
                lang = 1
            # 日本語/英語以外が指定されている場合一旦エラー
            else:
                #print("CHOOSE JA or EN lang.")
                # ERROR処理
                params = {
                          'key':None,
                          'query':request.POST.get('talk'),
                          'msg':'サポートされていない言語です。',

                          'p2data':None,
                          'p1data':None,
                          'n1data':None,
                          'n2data':None,
                          'total':0,
                          'fname':None,
                          }
                return render(request,'sentiment/sentiment_demo.html',params)
        else:
            # 指定なければ日本語検索
            q += " lang:ja"

        # retweetsは必ず除外
        if re.search(r"-filter:retweets",q) == None:
            q += " -filter:retweets"
 
        if link_chk == 'all_tweets':
            pass
        elif link_chk == 'only_photos':
            if re.search(r'filter:images',q) == None:
                q += ' filter:images'
        elif link_chk == 'exclude_link':
            if re.search(r'\-filter:links',q) == None:
                q += ' -filter:links'

        ###パラメータ１０個超えるようならエラー返す処理記載###
        if len(re.findall(r' ',q)) > 9:
            # ERROR処理
            params = {
                      'key':None,
                      'query':request.POST.get('talk'),
                      'msg':'検索条件が多すぎます。10個未満にしてください。',
                      'p2data':None,
                      'p1data':None,
                      'n1data':None,
                      'n2data':None,
                      'total':0,
                      'fname':None,
                      }
            return render(request,'sentiment/sentiment_demo.html',params)

        # 引用符と括弧はスペースを前後に入れてsplitする
        q_l = [k for k in q.translate(str.maketrans({'(': ' ( ', ')': ' ) ','"':' " '})).split(' ') if k != '']

        # sql検索用に単語以外のoptionを除いたリスト作成(OR,引用符,括弧は残す)
        ope_rgx = re.compile(r'^-|:|\?')
        q_without_options = [k for k in q_l if not ope_rgx.search(k)]

        # 単語のみのリスト(html強調表示用)
        q_only_word = [k for k in q_without_options if not re.search(r'(OR)|"|\(|\)',k)]

        #print('q_only_word',q_only_word)

        content_sql = ''
        insert_l = [] #挿入する文字列
        insert_l_i = 0 # 挿入する文字列のindex

        if content_chk == 'y':

            quote_sql = ''
            quote_start = False
            orflg = False
            kakkoflg = False

            for k in q_without_options:
                if quote_start == True:
                    if k == '"':
                        if orflg == True:
                            content_sql += "OR content ilike %(c{0})s ".format(insert_l_i)
                            insert_l.append('%'+quote_sql.strip()+'%')
                            insert_l_i += 1
                            orflg = False
                        else:
                            content_sql += "AND content ilike %(c{0})s ".format(insert_l_i)
                            insert_l.append('%'+quote_sql.strip()+'%')
                            insert_l_i += 1

                        # quoteリセット
                        quote_sql = ''
                        quote_start = False

                    else:
                        # 引用符の中はOR等の全オペレータは単なる文字扱い
                        quote_sql += k + ' '

                elif k == '"' and quote_start == False:
                    # quote始まり
                    quote_start = True

                elif k == 'OR':
                    orflg = True
                elif k == '(':
                    kakkoflg = True
                    # 後にスペース入れてsql文に挿入
                    if orflg == True:
                        content_sql += 'OR ' + k + ' '
                        orflg = False
                    else:
                        content_sql += 'AND ' + k + ' '
                elif k == ')':
                    kakkoflg = False
                    content_sql +=  k + ' '


                # オペレータではない単語の場合
                # SQLインジェクション用にk(ユーザーが入力した文字列)はここでは代入しない
                else:
                    if orflg == True and kakkoflg == False:
                        content_sql += "OR content ilike %(c{0})s ".format(insert_l_i)
                        insert_l.append('%' + k + '%')
                        insert_l_i += 1

                    elif orflg == True and kakkoflg == True:
                        content_sql += " content ilike %(c{0})s ".format(insert_l_i)
                        insert_l.append('%' + k + '%')
                        insert_l_i += 1

                    elif orflg == False and kakkoflg == False:
                        content_sql += "AND content ilike %(c{0})s ".format(insert_l_i)
                        insert_l.append('%' + k + '%')
                        insert_l_i += 1

                    elif orflg == False and kakkoflg == True:
                        content_sql += " content ilike %(c{0})s ".format(insert_l_i)
                        insert_l.append('%' + k + '%')
                        insert_l_i += 1

                    orflg = False
                    kakkoflg = False

            # 先頭の'AND '除去
            content_sql = content_sql[4:]
            content_sql = re.sub(r' +',' ',content_sql)
            # リプライ除く場合
            if reply_chk == 'y':
                # NOTは先頭に記載（sql途中にORが入ると正しく除外されない)
                content_sql = "(" + content_sql + ") AND content not like %(c{0})s".format(insert_l_i)
                insert_l.append('%@%')
                insert_l_i += 1


        # 今日検索したクエリの中から検索
        dt_now = datetime.datetime.now()

        s_date = datetime.datetime(dt_now.year,
                                   dt_now.month,
                                   dt_now.day,
                                   00,00,00)
        e_date = datetime.datetime(dt_now.year,
                                   dt_now.month,
                                   dt_now.day,
                                   23,59,59)

        #print(s_date,e_date)

        if not Tweetdata3.objects.filter(up_date__range=[s_date,e_date],
                                      query=q,
                                      ).exists():

            status = collect_tweet_realtime(q,
                                             lang
                                             )# langはqに含まれるがDB保存用に整数で別途渡す

        if content_sql != '': #contentから@除外
            #print('content条件あり')
            # ユーザー入力値以外のcontentSQL文を作成
            sql = """SELECT
            t_id,
            t_date,
            s_name,
            u_name,
            p_image,
            s_class,
            t_id_char,
            entities_display_url,
            entities_url,
            media_url,
            media_url_truncated,
            wakachi
            FROM sentiment_tweetdata3
            WHERE
            {0} and
            up_date between %(s_date)s and %(e_date)s and
            query = %(query)s
            order by media_url_truncated {1} limit 200""".format(content_sql,"ASC" if media_chk == 'y' else "DESC")
        else:
            #print('content条件なし')
            sql = """SELECT
            t_id,
            t_date,
            s_name,
            u_name,
            p_image,
            s_class,
            t_id_char,
            entities_display_url,
            entities_url,
            media_url,
            media_url_truncated,
            wakachi
            FROM sentiment_tweetdata3
            WHERE
            up_date between %(s_date)s and %(e_date)s and
            query = %(query)s
            order by media_url_truncated {0} limit 200""".format("ASC" if media_chk == 'y' else "DESC")

        #print('sql',sql)
        q_params = {
                  "query":q,
                  "s_date":s_date,
                  "e_date":e_date,
                  }
        # contentのユーザー入力値をq_paramsに追加
        for i,w in enumerate(insert_l):
            q_params["c{0}".format(i)] = w
            
        #print('q_params',q_params)
        result = Tweetdata3.objects.raw(sql,q_params)
        #print(result)

        p2data = []
        p1data = []
        n1data = []
        n2data = []
        all_wakachi = ''
        for r in result:
            if r.s_class == 3:
                p1data.append(r)
            elif r.s_class == 4:
                p2data.append(r)
            elif r.s_class == 1:
                n1data.append(r)
            else:
                n2data.append(r)

            if r.wakachi != '': 
                all_wakachi += r.wakachi + ' '

        wordcloud = WordCloud(colormap='brg',
                              width=250,
                              height=250,
                              min_font_size=8,
                              #max_font_size=100,
                              max_words=50, # top50のみ表示
                              relative_scaling=0,
                              contour_width=0.001,
                              contour_color='powderblue',
                              font_path=r"/usr/share/fonts/NotoSansJP-Light.otf",
                              #mask=mask_array,
                              background_color='white',
                              #stopwords=adj_stopwords + noun_stopwords + default_stopwords,
                              collocations=False)

        wordcloud = wordcloud.generate(all_wakachi) # wakachiはスペース区切りでしか受け付けない
        # PILで表示する
        image_array = wordcloud.to_array()
        img = Image.fromarray(image_array)

        buf = io.BytesIO()
        img.save(buf,format='png')
        s = buf.getvalue()
        s = base64.b64encode(s).decode()
        buf.close()


        params = {
            'key':q_only_word, # 単語強調表示用.リストで渡す(大文字小文字区別あり)
            'query':request.POST.get('talk'),
            'msg':None,
            'p2data':p2data,
            'p1data':p1data,
            'n1data':n1data,
            'n2data':n2data,
            'total':len(result),
            'fname':s,
            }

    #print('param',params)
    return render(request,'sentiment/sentiment_demo.html',params)

