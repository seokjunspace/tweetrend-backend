from django.urls import path
from .views import api_get_tweets

urlpatterns = [
    path('tweets/<str:topic>', api_get_tweets),
]
