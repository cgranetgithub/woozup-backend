from django.conf.urls import url, include
from rest_framework import routers
from userprofile.drf import UserViewSet, NewFriendsViewSet
from event.drf import EventCategoryViewSet, EventTypeViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'friends/new', NewFriendsViewSet, 'new-friends')
router.register(r'category', EventCategoryViewSet)
router.register(r'event_type', EventTypeViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^drf/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
]
