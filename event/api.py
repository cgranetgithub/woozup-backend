from doc import authdoc

from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.serializers import Serializer
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import ApiKeyAuthentication

from django.db.models import Q
from django.conf.urls import url
from django.utils.timezone import is_naive
from django.contrib.gis.measure import D # ``D`` is a shortcut for ``Distance``

from event.models import EventCategory, EventType, Event
from userprofile.api import UserResource
from userprofile.models import ExtendedUser

import apifn

class MyDateSerializer(Serializer):
    """
    Our own serializer to format datetimes in ISO 8601 but with timezone
    offset.
    """
    def format_datetime(self, data):
        # If naive or rfc-2822, default behavior...
        if is_naive(data) or self.datetime_formatting == 'rfc-2822':
            return super(MyDateSerializer, self).format_datetime(data)
        return data.isoformat()

class EventCategoryResource(ModelResource):
    class Meta:
        resource_name = 'category'
        queryset = EventCategory.objects.all()
        allowed_methods = ['get']
        ordering = ['order']

class EventTypeResource(ModelResource):
    category = fields.ToManyField(EventCategoryResource, 'category',
                                  full=True)
    class Meta:
        resource_name = 'event_type'
        queryset = EventType.objects.all()
        allowed_methods = ['get']
        filtering = {
                    'category': ALL_WITH_RELATIONS,
                    }
        ordering = ['order']

class AbstractEventResource(ModelResource):
    event_type = fields.ToOneField(EventTypeResource, 'event_type',
                                      full=True)
    participants = fields.ToManyField(UserResource, 'participants',
                                      full=True, null=True)
    invitees = fields.ManyToManyField(UserResource, 'invitees',
                                      full=True, null=True)
    owner = fields.ToOneField(UserResource, 'owner', full=True, null=True)
    class Meta:
        abstract = True
        serializer = MyDateSerializer()
        queryset = Event.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        filtering = {
                    #'owner'       : ALL_WITH_RELATIONS,
                    'event_type'  : ALL_WITH_RELATIONS,
                    'start'       : ALL,
                    'position'    : ALL,
                    #'participants': ALL_WITH_RELATIONS,
                    }
        ordering = ['start']
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

class AllEventsResource(AbstractEventResource):
    class Meta(AbstractEventResource.Meta):
        resource_name = 'events/all'

    def get_object_list(self, request):
        user = request.user
        # restrict result to my events + my friends' events
        me = User.objects.filter(id=user.id)
        # mine = Event.objects.filter(owner__user=user)
        myfriends = ExtendedUser.objects.get(id=user.id).get_friends()
        # owners = list(myfriends.values_list('user_id', flat=True)) + [user.id]
        owners = me | myfriends
        events = Event.objects.filter(owner__in=owners).distinct()
        return events

class MyAgendaResource(AbstractEventResource):
    class Meta(AbstractEventResource.Meta):
        resource_name = 'events/agenda'

    def get_object_list(self, request):
        # restrict result to my events + the events I go to
        mine = Event.objects.filter(owner__user=request.user)
        participation = request.user.events_as_participant.all()
        events = mine | participation
        return events.distinct()

class MyEventsResource(AbstractEventResource):
    class Meta(AbstractEventResource.Meta):
        resource_name = 'events/mine'
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'put', 'delete']

    def obj_create(self, bundle, **kwargs):
        #force owner to the authorized user
        kwargs['owner'] = bundle.request.user
        return super(MyEventsResource, self).obj_create(bundle, **kwargs)

    def obj_delete(self, bundle, **kwargs):
        if not hasattr(bundle.obj, 'delete'):
            try:
                bundle.obj = self.obj_get(bundle=bundle, **kwargs)
            except ObjectDoesNotExist:
                raise NotFound("A model instance matching the provided arguments could not be found.")
        self.authorized_delete_detail(self.get_object_list(bundle.request), bundle)
        bundle.obj.canceled = True
        bundle.obj.save(update_fields=['canceled'])

    def get_object_list(self, request):
        # restrict result to my events
        events = Event.objects.filter(owner__user=request.user)
        return events

class FriendsEventsResource(AbstractEventResource):
    class Meta(AbstractEventResource.Meta):
        resource_name = 'events/friends'
        # for the doc:
        extra_actions = [
            {   u"name": u"join",
                u"http_method": u"POST",
                #"resource_type": "list",
                u"summary": u"""[Custom API] - Requires authentication<br><br>
User joins an event, that is, is added to the participant list.""",
                "fields": authdoc
            } ,
            {   u"name": u"leave",
                u"http_method": u"POST",
                #"resource_type": "list",
                u"summary": u"""[Custom API] - Requires authentication<br><br>
User leaves an event, that is, is removed from the participant list.""",
                "fields": authdoc
            } ,
        ]

    def get_object_list(self, request):
        user = request.user
        # restrict result to my friends' events
        myfriends = ExtendedUser.objects.get(id=user.id).get_friends()
        events = Event.objects.filter(owner__in=myfriends
                             ).filter( Q(invitees=None)
                                     | Q(invitees__in=[user])
                             ).distinct()
        # filter by distance TODO add an option for filtering
        #if user.position.last:
            #events = events.filter(location_coords__distance_lte=(
                                            #user.position.last, D(km=100)))
        return events

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/join/(?P<event_id>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('join'), name="api_join"),
            url(r"^(?P<resource_name>%s)/leave/(?P<event_id>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('leave'), name="api_leave"),
        ]

    def join(self, request, **kwargs):
        """ Join an event.
        Note: we need this API for security reason (instead of doing a PUT),
        to avoid someone to manipulate events directly with a PUT
        """
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        event_id = kwargs['event_id']
        (req, data, status) = apifn.join(request, event_id)
        return self.create_response(req, data, status)

    def leave(self, request, **kwargs):
        """ Leave an event.
        Note: we need this API for security reason (instead of doing a PUT),
        to avoid someone to manipulate events directly with a PUT
        """
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        event_id = kwargs['event_id']
        (req, data, status) = apifn.leave(request, event_id)
        return self.create_response(req, data, status)
