from django.views.generic import RedirectView
from django.conf.urls import include, url
from django.contrib import admin

import drf
from tastypie.api import Api

from link.api import *
from event.api import *
from userprofile.api import *
from journal.api import *
from web.views import home, profile, stats, notif

from service.settings.prod import STATIC_URL
#from service.notification import GCMDeviceAuthenticatedResource

#def module_exists(module_name):
    #try:
        #__import__(module_name)
    #except ImportError:
        #return False
    #else:
        #return True

v1_api = Api(api_name='v1')
v1_api.register(MyAgendaResource())
v1_api.register(MyEventsResource())
v1_api.register(FriendsEventsResource())
v1_api.register(AllEventsResource())
v1_api.register(EventResource())
v1_api.register(EventTypeResource())
v1_api.register(EventCategoryResource())
v1_api.register(ProfileResource())
v1_api.register(PositionResource())
v1_api.register(UserResource())
v1_api.register(MyFriendsResource())
v1_api.register(SuggestionsResource())
v1_api.register(PendingFriendsResource())
v1_api.register(NewFriendsResource())
v1_api.register(AuthResource())
v1_api.register(ContactResource())
v1_api.register(InviteResource())
v1_api.register(LinkResource())
v1_api.register(RecordResource())
v1_api.register(CommentResource())
v1_api.register(CommentsResource())
#v1_api.register(GCMDeviceAuthenticatedResource())

urlpatterns = [
    url(r'^$', home),
    url(r'^api/'  , include(v1_api.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/', profile),
    url(r'^web/', include('web.urls')),
    # usual web static files
    url(r'^favicon.ico$', RedirectView.as_view(url=STATIC_URL+'favicon.ico')),
    url(r'^apple-touch-icon-precomposed.png$', RedirectView.as_view(url=STATIC_URL+'icon.png')),
    url(r'^apple-touch-icon.png$', RedirectView.as_view(url=STATIC_URL+'icon.png')),
    url(r'^robots.txt$', RedirectView.as_view(url=STATIC_URL+'robots.txt')),
    #url(r'^register-by-token/(?P<backend>[^/]+)/$', register_by_access_token),
    url(r'^stats/$', stats),
    url(r'^notif/$', notif),
    #url(r'^logout/$', social_logout),
]

urlpatterns += drf.urlpatterns

#if module_exists('tastypie_swagger'):
    #urlpatterns += [
        #url(r'api/doc/', include('tastypie_swagger.urls',
                                 #namespace='v1_api_tastypie_swagger'),
                         #kwargs={
                            #"tastypie_api_module":v1_api,
                            #"namespace":"v1_api_tastypie_swagger",
                            #"version": "0.1"}
        #)
    #]
