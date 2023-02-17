# -*- coding: utf-8 -*-

from django.urls import path
from . import views

app_name = 'mecab'

urlpatterns = [
    
   # mecab関連
    path(r'gen-katsuyo/',views.addword,name='addword'),
    #path(r'',views.toppage,name='toppage'),

    ]
