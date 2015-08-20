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

from event.models import EventCategory, EventType, Event
from userprofile.api import ProfileResource
from userprofile.models import get_user_friends
 
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
    participants = fields.ToManyField(ProfileResource, 'participants',
                                      full=True, null=True)
    owner = fields.ToOneField(ProfileResource, 'owner',
                                      full=True, null=True)
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


class EventResource(AbstractEventResource):
    class Meta(AbstractEventResource.Meta):
        resource_name = 'event'
    
class MyEventResource(AbstractEventResource):
    class Meta(AbstractEventResource.Meta):
        resource_name = 'myevent'
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'put', 'delete']

    def obj_create(self, bundle, **kwargs):
        #force owner to the authorized user
        kwargs['owner'] = bundle.request.user.userprofile
        return super(MyEventResource, self).obj_create(bundle, **kwargs)

    def get_object_list(self, request):
        events = Event.objects.filter(owner__user=request.user)
        return events

class FriendEventResource(AbstractEventResource):
    class Meta(AbstractEventResource.Meta):
        resource_name = 'friendevent'
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
        print request.user.userprofile
        myfriends = get_user_friends(request.user.userprofile)
        print myfriends
        events = Event.objects.filter(owner__in=myfriends).distinct()
        print events
        return events

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<event_id>\w[\w/-]*)/join%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('join'), name="api_join"),
            url(r"^(?P<resource_name>%s)/(?P<event_id>\w[\w/-]*)/leave%s$" %
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
        (req, data, status) = apifn.join(request)
        return self.create_response(req, data, status)
    
    def leave(self, request, **kwargs):
        """ Leave an event.
        Note: we need this API for security reason (instead of doing a PUT),
        to avoid someone to manipulate events directly with a PUT        
        """
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        (req, data, status) = apifn.leave(request)
        return self.create_response(req, data, status)
