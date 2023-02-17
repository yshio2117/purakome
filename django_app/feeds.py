from django.contrib import admin
from django.contrib.syndication.views import Feed
from django.urls import reverse
from sentiment.models import Official_names,Statistics1week,Oadates,Summarys
import urllib.parse, datetime
from django.utils.text import slugify

summer_weeks = [
        'kanokari',
        'kami-kuzu',
        'lycoris-recoil',
        'rwby',
        'engage-kiss',
        'utawarerumono',
        'luminous',
        'you-zitsu',
        'tenseikenja',
        'overlord',
        'tsurekano',
        'tokyo-mew-mew',
        'isekaiojisan',
        'miabyss',
        'jashinchan',
        'shinepost',
        'kumichomusume',
        'soreayu',
        'shadowshouse',
        'extreme-hearts',
        'vermeilingold',
        'isekai-harem',
        'yofukashi-no-uta',
        'isekai-yakkyoku',
        'maousama',
        'maid-ga-ayashii',
        'fuuto',
        'teppen',
        'primadoll',
        'hoshinosamidare',
        'SpyxFamily',
        'kokyu',
        'yamanosusume',
        'mushikaburihime',
        'mobpsycho100-3',
        'shippona',
        'fuukoi-anime',
        'cooldoji',
        'bluelock',
        'jojo-stone-ocean',
          ]
indexes_summer = [Official_names.objects.get(url_name=s).index for s in summer_weeks]

ep_l = []
for k,index in enumerate(indexes_summer):
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
                    'url':summer_weeks[k],
                    'index':index,
                    'up_date':Statistics1week.objects.only('up_date').get(post=slugify('{0} {1}'.format(index,j))).up_date,
                    'episode':{
                    'num':j, 
                    'title':title_tag,
                    }
                 }
            break

    ep_l.append(tmp)

ep_l = sorted(ep_l,key=lambda x: x['up_date'],reverse=True)
summer_weeks = [ep['url'] for ep in ep_l]


class LatestFeed(Feed):

    title = 'ポジネガ探偵ぷらこめ | アニメ評判調査'
    link = 'https://purakome.net/sentiment/anime/'
    description = "最新情報配信"

    def items(self):
        return summer_weeks

    def item_title(self, item):
        try:
            i = [e['url'] for e in ep_l].index(item)
        except IndexError:
            pass
        else:
            return ep_l[i]['episode']['title']


    def item_description(self, item):
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
        
    def item_pubdate(self,item):
        try:
            i = [e['url'] for e in ep_l].index(item)
        except IndexError:
            pass
        else:       
            return ep_l[i]['up_date']


    def item_link(self, item):

        try:
            i = [e['url'] for e in ep_l].index(item)
        except IndexError:
            pass
        else: 
            if ep_l[i]['episode']['num'] > 0:
                return r"https://purakome.net/sentiment/anime/{0}/{1}/".format(ep_l[i]['url'],ep_l[i]['episode']['num'])
            else:
                return r"https://purakome.net/sentiment/anime/{0}/".format(ep_l[i]['url'])
      

