from django.conf.urls import url
from . import views

"""
URL patterns used by 'spierdon' app.
"""
urlpatterns = [
    url(r'^sponsors/add', views.add_sponsor, name='add_sponsor'),
    url(r'^tournament/new', views.create, name='create'),
    url(r'^tournament/match/(?P<match_id>[0-9]+)/update', views.update_match, name='update_match'),
    url(r'^tournament/search', views.search, name='search'),
    url(r'^tournament/current', views.current, name='current'),
    url(r'^tournament/(?P<tournament_id>[0-9]+)/detail', views.detail, name='detail'),
    url(r'^tournament/(?P<tournament_id>[0-9]+)/join', views.join, name='join'),
    url(r'^tournament/(?P<tournament_id>[0-9]+)/edit', views.edit, name='edit'),
    # url(r'^challenges/', views.get_challenges, name='get_challenges'),
    url(r'^', views.index, name='index'),
]
