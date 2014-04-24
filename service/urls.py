from django.conf.urls import patterns, include, url
from django.contrib import admin

from tastypie.api import Api

from link.api import LinkResource
from event.api import EventCategoryResource, EventTypeResource, EventResource
from userprofile.api import UserResource, AuthResource

admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(EventResource())
v1_api.register(EventTypeResource())
v1_api.register(EventCategoryResource())
v1_api.register(UserResource())
v1_api.register(AuthResource())
v1_api.register(LinkResource())

urlpatterns = patterns('',
    url(r'^api/'  , include(v1_api.urls)),
    url(r'^admin/', include(admin.site.urls)),
)
