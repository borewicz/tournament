from django.conf.urls import url
from . import views

"""
URL patterns used by 'spierdon' app.
"""
urlpatterns = [
    # url(r'^ranking/', views.ranking, name='ranking'),
    url(r'^tournament/(?P<tournament_id>[0-9]+)/detail/', views.detail, name='detail'),
    url(r'^tournament/(?P<tournament_id>[0-9]+)/join/', views.join, name='join'),
    # url(r'^challenge/new/', views.add_challenge, name='add_challange'),
    # url(r'^challenges/', views.get_challenges, name='get_challenges'),
    url(r'^', views.index, name='index'),
]