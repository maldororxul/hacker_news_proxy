"""Project level routing"""
__author__ = 'ke.mizonov'
from django.urls import include, path


urlpatterns = [
    path('', include('hacker_news.urls')),
]
