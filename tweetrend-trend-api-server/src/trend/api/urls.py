from django.urls import path
from .views import *
urlpatterns = [
    path('api/total-counts/<str:topic>', api_get_total_count),
    path('api/user-counts/<str:topic>', api_get_user_count),
    path('api/retweet-counts/<str:topic>', api_get_retweet_count),
    path('api/region/<str:topic>', api_get_region_counts),
    path('api/reputation/<str:topic>', api_get_reputation),
    path('api/source/<str:topic>', api_get_source),
    path('api/relwords/<str:topic>', api_get_related_words),
]
