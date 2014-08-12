from django.conf.urls import patterns, include, url
from django.contrib import admin

from tastypie.api import Api

from link.api import *
from event.api import *
from userprofile.api import *
#from service.notification import GCMDeviceAuthenticatedResource

def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True

admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(EventResource())
v1_api.register(EventTypeResource())
v1_api.register(EventCategoryResource())
v1_api.register(ProfileResource())
v1_api.register(PositionResource())
v1_api.register(UserResource())
v1_api.register(AuthResource())
#v1_api.register(GCMDeviceAuthenticatedResource())
v1_api.register(LinkResource())
v1_api.register(InviteResource())
v1_api.register(ContactResource())

urlpatterns = patterns('',
    url(r'^api/'  , include(v1_api.urls)),
    url(r'^admin/', include(admin.site.urls)),
)

if module_exists('tastypie_swagger'):
    urlpatterns += patterns('',
                            url(r'api/doc/', include('tastypie_swagger.urls', 
                                                namespace='tastypie_swagger')))
