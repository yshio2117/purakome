# -*- coding: utf-8 -*-

from django.urls import path
from . import views
from django.views.generic.base import RedirectView

#app_name = 'sum_app'

urlpatterns = [
#######################全index削除後、あるいはadsense後に末尾スラッシュを追記のこと
 
   

    path(r'sentiment/anime/character/<str:name>/search',views.posts_character,name='character_posts'), # 各pn詳細ページ
    path(r'sentiment/anime/character/<str:name>/<str:pn>',views.pn_details,name='character_pn_details'), # 旧pn詳細ページ(character)
    path(r'sentiment/anime/character/<str:name>',views.character,name='character'), # 各キャラページ

    # quiz
    path(r'sentiment/anime/quiz/q-<int:number>/answer/',views.answers,name='answers'),    
    path(r'sentiment/anime/quiz/q-<int:number>/',views.questions,name='questions'),  
    path(r'sentiment/anime/quiz/result/',views.result,name='result'), 
    path(r'sentiment/anime/quiz/',views.quiz_index,name='quiz_index'), # 本番はsentiment除外

    path(r'sentiment/anime/<str:name>/search',views.showdetail,name='posts'), # 各pn詳細ページ
    path(r'sentiment/anime/search',views.search,name='search'), # 旧pn詳細ページ

    #path(r'sentiment/anime/<str:name>/<str:pn>',views.pn_details,name='pn_details'), # 各pn詳細ページ

    path(r'sentiment/anime/<str:name>/<int:episode>/docs/',views.showdetail,name='detail_anime'), # 各pn詳細ページ

    path(r'sentiment/anime/<str:name>/',views.anime_weeks,name='anime'), # (OA中)各アニメページ →OA終了後はsummaryにリダイレクト
    path(r'sentiment/anime/<str:name>/<int:episode>/',views.anime_episode,name='anime_episode'), # (OA終了後)各話アニメページ.最もコンテンツが多い&ランキング上位のページにcanonical
   
    path(r'sentiment/anime/',views.index,name='index'),

### johnnys
    path(r'sentiment/johnnys/<slug:name>/<slug:episode>/docs/',views.showdetail,name='detail_johnnys'), # 各pn詳細ペー

    path(r'sentiment/johnnys/<slug:name>/<slug:episode>/',views.j_event,name='j_event'),
###

    path(r'sentiment/contact/',views.InquiryView.as_view(),name='contact'),
    path(r'sentiment/inquiry/', RedirectView.as_view(url='https://purakome.net/sentiment/contact/', permanent=True)),
    #path(r'sentiment/inquiry/',views.inquiry,name='inquiry'), # 旧お問い合わせ
    

    path(r'sentiment/sitepolicy/',views.sitepolicy,name='sitepolicy'), # サイトポリシー
    path(r'sentiment/aboutus/',views.aboutus,name='aboutus'), # プロフィール
    path(r'sentiment/comment/reply/', views.reply_page, name="reply"),
    path(r"sentiment/exec-ajax/<slug:name>/<slug:episode>/<slug:loc>/", views.exec_ajax, name='exec_ajax'), # ajax

    path(r'sentiment/',views.sentiment_demo,name='sentiment_demo'),
    #purakome/sentiment/はindexに移動
    #path(r'sentiment/',views.tmp_redirect2,name='tmp_redirect2'),
    path(r'',views.toppage,name='toppage'),

   
]
