from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import ApiKeyAuthentication
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Record
from event.models import Event
from userprofile.api import UserResource
from event.api import AllEventsResource
from userprofile.utils import get_friends

class RecordResource(ModelResource):
    user = fields.ToOneField(UserResource, 'user', full=True)
    refering_event = fields.ToOneField(AllEventsResource, 'refering_event', full=True, null=True)
    refering_user = fields.ToOneField(UserResource, 'refering_user', full=True, null=True)
    class Meta:
        resource_name = 'record'
        queryset = Record.objects.all()
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        allowed_methods = ['get']

    def get_object_list(self, request):
        user = request.user
        me = get_user_model().objects.filter(id=user.id)
        myfriends = get_friends(user)
        concerned = me | myfriends
        #concerned = myfriends
        my_events = Event.objects.filter(owner=user)
        friend_events = Event.objects.filter(owner__in=myfriends
                             ).filter( Q(invitees=None)
                                     | Q(invitees__in=[user])
                             )
        events = my_events | friend_events
        events_records = Record.objects.filter(refering_event__in=events)
        people_records = Record.objects.filter(
                        Q(user__in=concerned) | Q(refering_user__in=concerned)
                        ).filter(refering_event=None)
        records = events_records | people_records
        return records.distinct()
