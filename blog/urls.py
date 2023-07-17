# -*- coding: utf-8 -*-

from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    
   # 雑記ブログ関連
    #path('',views.IndexView.as_view(),name='blog_index'),
    #path(r'tech/',views.IndexView.as_view(),name='tech_index'),
#    path(r'anime/',views.IndexView.as_view(),name='anime_index'),
    path(r'tech/<int:blog_id>/',views.tech_detail,name='tech_detail'),
    path(r'anime/<int:blog_id>/',views.anime_detail,name='anime_detail'),
    ]
