from django.conf.urls import patterns, include, url
from django.contrib import admin
from tastypie.api import Api
from event.api import EventCategoryResource, EventTypeResource, EventResource

admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(EventResource())
v1_api.register(EventTypeResource())
v1_api.register(EventCategoryResource())

urlpatterns = patterns('',
    url(r'^api/'  , include(v1_api.urls)),
    url(r'^admin/', include(admin.site.urls)),
)
