"""django_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

from .sitemaps import (
    StaticViewSitemap,
    AnimeSitemap,
   
)
from .feeds import (
    LatestFeed,
)

sitemaps = {
    'static': StaticViewSitemap,
    'anime': AnimeSitemap,
}

urlpatterns = [

    path('adbum/', admin.site.urls),

    path('sentiment/anime/feed/', LatestFeed()),

    path('', include('sentiment.urls')),

    path('sitemap3.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap3'),

    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    # 手動の場合
    #path('sitemap_del.xml', TemplateView.as_view(template_name='sitemap_del.xml', content_type='application/xml')),
    #path('sitemap2.xml', sitemap, {'sitemaps': sitemaps2}, name='sitemap2'),
    path('ads.txt', TemplateView.as_view(template_name='ads.txt', content_type='text/plain')),
    path('feed/', LatestFeed()),
]
