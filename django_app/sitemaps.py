from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from sentiment.models import Official_names,Statistics1week
import urllib.parse, datetime
from django.utils.text import slugify

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


purakome_top = ['purakome_top']
anime_top = ['anime_top']
johnnys_top = ['johnnys_top']

spring_animes = []
single_posts = []
series_posts = []
week_posts = []
for a in Official_names.objects.filter(kind__in=[0,10]):
    if a.hidden == True:
        continue
    eps = [k for k in range(1,31) if Statistics1week.objects.filter(post=slugify('{0} {1}'.format(a.index,k))).exists()]
    if eps == []:
        continue # 記事未作成の場合スキップ

    if a.past == True:
        spring_animes.append({'url_name':a.url_name,
                              'update':Statistics1week.objects.get(post=slugify('{0} {1}'.format(a.index,0))).up_date
                              })
    elif a.past==False and a.series==False:
        for ep in eps: # johnnysは複数あり
            single_posts.append({'url_name':a.url_name,
                                  'episodes':{'no':ep,
                                            'update':Statistics1week.objects.get(post=slugify('{0} {1}'.format(a.index,ep))).up_date
                                            },
                                  'kind':a.kind,
                                  })
    elif a.past==False and a.series==True:
        for ep in eps:
            series_posts.append({'url_name':a.url_name,
                                  'episodes':{'no':ep,
                                            'update':Statistics1week.objects.get(post=slugify('{0} {1}'.format(a.index,ep))).up_date
                                            },
                                  'kind':a.kind,
                                  })
        week_posts.append({'url_name':a.url_name,
                            'update':Statistics1week.objects.get(post=slugify('{0} {1}'.format(a.index,max(eps)))).up_date,
                            'kind':a.kind,
                            })


class AnimeSitemap(Sitemap):
    """
    ジャニーズも追加される
    注意:hidden = False & statisticsレコードがあれば自動的に追加される
    """
    #changefreq = "daily"
    protocol = 'https'

    def items(self):

        return purakome_top + anime_top + spring_animes + single_posts + series_posts + week_posts

    def location(self, obj):

        if obj in anime_top:
            return reverse('index')
        elif obj in purakome_top:
            return reverse('toppage')
        
        # johnnys topは未作成
        #elif obj == johnnys_top:
        #    return reverse('')

        elif obj in spring_animes:
            i = spring_animes.index(obj)
            return reverse('anime',kwargs={'name':spring_animes[i]['url_name']})
        elif obj in week_posts:
            i = week_posts.index(obj)
            if week_posts[i]['kind'] == 0:
                return reverse('anime',kwargs={'name':week_posts[i]['url_name']})
            elif week_posts[i]['kind'] == 10:
                pass # 現状テンプレ未作成
                #return reverse('',kwargs={'name':week_posts[i]['url_name']})

        elif obj in single_posts:
            i = single_posts.index(obj)
            if single_posts[i]['kind'] == 0:
                return reverse('anime_episode',kwargs={'name':single_posts[i]['url_name'],
                                                       'episode':single_posts[i]['episodes']['no']
                                                       }
                               )
            elif single_posts[i]['kind'] == 10:
                return reverse('j_event',kwargs={'name':single_posts[i]['url_name'],
                                                       'episode':single_posts[i]['episodes']['no']
                                                       }
                               )
            
        elif obj in series_posts:
            i = series_posts.index(obj)
            if series_posts[i]['kind'] == 0:
                return reverse('anime_episode', kwargs={'name': series_posts[i]['url_name'],
                                                        'episode':series_posts[i]['episodes']['no']
                                                        }
                               )
            elif series_posts[i]['kind'] == 10:
                pass # 未作成

    def lastmod(self, obj):
        if obj in anime_top:
            return datetime.datetime(2022,
                               12,
                               14,
                               00,00,00).replace(tzinfo=JST())
        elif obj in purakome_top:
            return datetime.datetime(2023,
                               2,
                               20,
                               00,00,00).replace(tzinfo=JST())
        
        elif obj in spring_animes:
            i = spring_animes.index(obj)
            return spring_animes[i]['update']
        elif obj in week_posts:
            i = week_posts.index(obj)
            return week_posts[i]['update']
        elif obj in single_posts:
            i = single_posts.index(obj)
            return single_posts[i]['episodes']['update'] 
        elif obj in series_posts:
            i = series_posts.index(obj)
            return series_posts[i]['episodes']['update']


class StaticViewSitemap(Sitemap):

    #changefreq = "never"
    #priority = 0.1 # default 0.5 サイト内の相対比較。googleでは無視らしい
    protocol = "https"

    def items(self):
        items = [
            'sitepolicy',
            #'inquiry',
            'aboutus',
            'quiz_index',
            'sentiment_demo',
            'mecab:addword',
            'mecab:addwiki',
        ]
        
        return items

    def lastmod(self, obj):
        if obj == 'quiz_index':
            return datetime.datetime(2022,
                               11,
                               22,
                               00,00,00).replace(tzinfo=JST())

        elif obj == 'sentiment_demo':
            return datetime.datetime(2023,
                               2,
                               1,
                               00,00,00).replace(tzinfo=JST())

        elif obj == 'mecab:addword':
            return datetime.datetime(2023,
                               2,
                               17,
                               00,00,00).replace(tzinfo=JST())
        elif obj == 'mecab:addwiki':
            return datetime.datetime(2023,
                               2,
                               20,
                               00,00,00).replace(tzinfo=JST())



    def location(self, obj):
        return reverse(obj)

        
        



