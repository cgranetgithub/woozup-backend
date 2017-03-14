from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home),
    url(r'^accounts/profile/', views.profile),
    #url(r'^emails/$', views.emails),
    url(r'^stats/$', views.stats),
    url(r'^notif/$', views.notif),
    url(r'^records/$', views.records),
]
