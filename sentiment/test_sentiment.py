# -*- coding: utf-8 -*-

import unittest
from ast import literal_eval
from django.http import HttpRequest

import os, sys, django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')  # DJANGO_SETTINGS_MODULEにプロジェクトのsettings.pyのを指定します。
django.setup()

from sentiment.models import Tweetdata2,Statistics1week,Official_names,Keywords,Prefectures,Summarys,Trend_ranks,Pref_ranks,Frequentwords,Longevents,Abouts,Oadates # 利用したいモデルをインポートします。
from sentiment import views


class TestStringMethods(unittest.TestCase):
    
    Is=[]
    Os=[]

    @classmethod
    def setUpClass(cls):
        print('*** 全体前処理 ***')

    @classmethod
    def tearDownClass(cls):
        print('*** 全体後処理 ***')
 
    def setUp(self):
        print('+ テスト前処理')
 
    def tearDown(self):
        print('+ テスト後処理')
    
    def test_index(self):
        """index コーディングtest"""
        #urls = Official_names.objects.all()

        request = HttpRequest()

        response = views.index(request)
        print('アニメTOP(sentiment/anime),[{0}]'.format(response.status_code))
        self.assertEqual(200,response.status_code)


    def test_jevent(self):
        """ j_eventでジャニーズのみが正しく表示されるか"""

        allrecord = Official_names.objects.all()

        ja40x = [] #johnnys
        ja200 = []

        #春アニメ,秋アニメ１つチェック
        title40x = [Official_names.objects.get(official_name="ブルーロック"),Official_names.objects.get(official_name="美少女戦士セーラームーン")]
        #以下一つのみ
        chara40x = [Official_names.objects.get(official_name="セーラーサターン")]
        op40x = [Official_names.objects.get(official_name="明け星")]
        ed40x = [Official_names.objects.get(official_name="朝が来る")]
        cv40x = [Official_names.objects.get(official_name="三石-琴乃(月野-うさぎ)")]
        jm40x = [Official_names.objects.get(official_name="松倉-海斗")] #johnnys member

        for r in allrecord:
            if r.kind == 10:
                if r.hidden == False:
                    ja200.append(r)
                else:
                    ja40x.append(r)


        print("number of 200 johnnys title : {0}".format(len(ja200)))
        print("number of 40x johnnys title : {0}".format(len(ja40x)))
        for i in range(2):
            if i == 0: # 200確認
                target_l = ja200
            else: # 404,410確認
                target_l = ja40x + title40x + chara40x + op40x + ed40x + cv40x + jm40x
            for t in target_l:
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
                        ).get(official_name_id=t.index)

                oadates = [{'episode':i,
                        'link_exist':True if Summarys.objects.filter(post="{0}-{1}".format(t.index,i)).exists() else False,
                        } for i in range(1,31)]
                chk_eps = [d['episode'] for d in oadates if d['link_exist'] == True]
                # johnnysは数少ないので全ep確認
                for chk_ep in chk_eps:

                    request = HttpRequest()
                    #print(request)
                    request.META['SERVER_NAME'] = "purakome.net"
                    request.META['SERVER_PORT'] = "443"
                    if i == 0:
                        print(t.official_name,chk_ep,end=",")
                        response = views.j_event(request,t.url_name,chk_ep)
                        print("[",response.status_code,"]")
                        self.assertEqual(response.status_code,200)
                    else:       
                        print(t.official_name,chk_ep,end=",")  
                        response = views.j_event(request,t.url_name,chk_ep)
                        print("[",response.status_code,"]")
                        self.assertIn(response.status_code,[404,410])        
 
    
    def test_anime_episode(self):
        allrecord = Official_names.objects.all()
        title200 = []
        title40x = []
        #以下一つのみ
        chara40x = [Official_names.objects.get(official_name="セーラーサターン")]
        op40x = [Official_names.objects.get(official_name="明け星")]
        ed40x = [Official_names.objects.get(official_name="朝が来る")]
        cv40x = [Official_names.objects.get(official_name="三石-琴乃(月野-うさぎ)")]
        ja40x = [Official_names.objects.get(official_name="Travis-Japan")] #johnnys
        jm40x = [Official_names.objects.get(official_name="松倉-海斗")] #johnnys member

        for r in allrecord:
            if r.kind == 0:
                if r.hidden == False:
                    title200.append(r)
                else:
                    title40x.append(r)
        print("number of 200 title : {0}".format(len(title200)))
        print("number of 40x title : {0}".format(len(title40x)))
        for i in range(2):
            if i == 0: # 200確認
                target_l = title200
            else: # 404,410確認
                target_l = title40x + chara40x + op40x + ed40x + cv40x + ja40x + jm40x
            for t in target_l:
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
                        ).get(official_name_id=t.index)

                oadates = [{'episode':i,
                        'link_exist':True if Summarys.objects.filter(post="{0}-{1}".format(t.index,i)).exists() else False,
                        } for i in range(1,31)]
                chk_ep = [d['episode'] for d in oadates if d['link_exist'] == True]
                if len(chk_ep) == 0:
                    chk_ep = 0
                else:
                    chk_ep = chk_ep[-1] # 一旦最新のepisodeのみチェック

                request = HttpRequest()
                #print(request)
                request.META['SERVER_NAME'] = "purakome.net"
                request.META['SERVER_PORT'] = "443"
                if i == 0:
                    print(t.official_name,chk_ep,end=",")
                    response = views.anime_episode(request,t.url_name,chk_ep)
                    print("[",response.status_code,"]")
                    self.assertEqual(response.status_code,200)
                else:       
                    print(t.official_name,chk_ep,end=",")  
                    response = views.anime_episode(request,t.url_name,chk_ep)
                    print("[",response.status_code,"]")
                    self.assertIn(response.status_code,[404,410])        
    

if __name__ == '__main__':
    unittest.main()
