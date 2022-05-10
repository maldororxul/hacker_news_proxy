"""Routing for hacker_news app"""
from django.urls import re_path
from .views import HackerNews


urlpatterns = [
    re_path('.*', HackerNews.proxy, name='proxy')
]
