from django.conf.urls import patterns, include, url
from django.contrib import admin
from event.api import EventCategoryResource

admin.autodiscover()

category_resource = EventCategoryResource()

urlpatterns = patterns('',
    url(r'^api/'  , include(category_resource.urls)),
    url(r'^admin/', include(admin.site.urls)),
)
