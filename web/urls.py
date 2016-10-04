from django.conf.urls import url
from . import views

urlpatterns = [
    #url(r'^emails/$', views.emails),
    url(r'^users/$', views.users),
    url(r'^events/$', views.events),
]
