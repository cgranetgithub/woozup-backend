from doc import authdoc

from tastypie import fields
from tastypie.http import HttpUnauthorized, HttpForbidden, HttpBadRequest
from tastypie.utils import trailing_slash
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.serializers import Serializer
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import ApiKeyAuthentication

from django.db.models import Q
from django.conf.urls import url
from django.utils.timezone import is_naive 

from event import push
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

class EventResource(ModelResource):
    event_type = fields.ToOneField(EventTypeResource, 'event_type',
                                   full=True)
    participants = fields.ToManyField(ProfileResource, 'participants',
                                      full=True, null=True)
    owner = fields.ToOneField(ProfileResource, 'owner',
                                      full=True, null=True)
    class Meta:
        serializer = MyDateSerializer()
        resource_name = 'event'
        queryset = Event.objects.all()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'put', 'delete']
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
    
    def obj_create(self, bundle, **kwargs):
        #force owner to the authorized user
        kwargs['owner'] = bundle.request.user.userprofile
        return super(EventResource, self).obj_create(bundle, **kwargs)

    #def get_object_list(self, request):
        #myfriends = get_user_friends(request.user.userprofile)
        #events = Event.objects.filter(
                                #Q( owner__user__in=myfriends )
                              #| Q( owner__user=request.user )
                              #| Q( participants__user=request.user )
                              #).distinct()
        #return events

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<event_id>\w[\w/-]*)/join%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('join'), name="api_join"),
            url(r"^(?P<resource_name>%s)/(?P<event_id>\w[\w/-]*)/leave%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('leave'), name="api_leave"),
            url(r"^(?P<resource_name>%s)/attending%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('attending'), name="api_attending"),
            url(r"^(?P<resource_name>%s)/not_attending%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('not_attending'), name="api_not_attending"),
        ]

    def join(self, request, **kwargs):
        """ Join an event.
        Note: we need this API for security reason (instead of doing a PUT),
        to avoid someone to manipulate events directly with a PUT        
        """
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        #self.throttle_check(request)
        if request.user and request.user.is_authenticated():
            try:
                event = Event.objects.get(id=kwargs['event_id'])
                if request.user is not event.owner.user:
                    #participants = [ i['id'] for i in event.participants.values() ]
                    #if request.user.id not in participants:
                    if request.user.userprofile not in event.participants.all():
                        event.participants.add(request.user.userprofile)
                        event.save()
                        push.participant_joined(request.user.userprofile,
                                                event)
                        return self.create_response(request,
                                                    {u'success': True})
                    else:
                        return self.create_response(
                                request, 
                                {u'reason': u'You are already a participant'},
                                HttpForbidden)
                else:
                    return self.create_response(
                                request, 
                                {u'reason': u'You cannot join your own event'},
                                HttpForbidden)
            except Event.DoesNotExist:
                return self.create_response(request, 
                                            {u'reason': u'Event not found'},
                                            HttpForbidden)
            else:
                return self.create_response(request, 
                                            {u'reason': u'Unexpected'},
                                            HttpForbidden)
        else:
            return self.create_response(
                                    request,
                                    {u'reason': u"You are not authenticated"},
                                    HttpUnauthorized )
    
    def leave(self, request, **kwargs):
        """ Leave an event.
        Note: we need this API for security reason (instead of doing a PUT),
        to avoid someone to manipulate events directly with a PUT        
        """
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        #self.throttle_check(request)
        if request.user and request.user.is_authenticated():
            try:
                event = Event.objects.get(id=kwargs['event_id'])
                if request.user is not event.owner.user:
                    #participants = [ i['id'] for i in event.participants.values() ]
                    #if request.user.id in participants:
                    if request.user.userprofile in event.participants.all():
                        event.participants.remove(request.user.userprofile)
                        event.save()
                        push.participant_left(request.user.userprofile, event)
                        return self.create_response(request,
                                                    {u'success': True})
                    else:
                        return self.create_response(
                                request, 
                                {u'reason': u'You are not a participant'},
                                HttpForbidden)
                else:
                    return self.create_response(
                            request, 
                            {u'reason': u'You cannot leave your own event'},
                            HttpForbidden)
            except Event.DoesNotExist:
                return self.create_response(request, 
                                            {u'reason': u'Event not found'},
                                            HttpForbidden)
            else:
                return self.create_response(request, 
                                            {u'reason': u'Unexpected'},
                                            HttpForbidden)
        else:
            return self.create_response(
                                    request,
                                    {u'reason': u"You are not authenticated"},
                                    HttpUnauthorized )

    def attending(self, request, **kwargs):
        """ Get list of events the user attends."""
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        self.log_throttled_access(request)
        if request.user and request.user.is_authenticated():
            try:
                events = Event.objects.filter(
                                          Q( owner__user=request.user )
                                        | Q( participants__user=request.user )
                                        ).distinct()
                objects = []
                for result in events:
                    bundle = self.build_bundle(obj=result, request=request)
                    bundle = self.full_dehydrate(bundle)
                    objects.append(bundle)
                object_list = { 'objects': objects, }
                return self.create_response(request, object_list)
            except Event.DoesNotExist:
                return self.create_response(request,
                                            {u'reason': u'Event not found'},
                                            HttpForbidden)
            else:
                return self.create_response(request,
                                            {u'reason': u'Unexpected'},
                                            HttpForbidden)
        else:
            return self.create_response(
                                    request,
                                    {u'reason': u"You are not authenticated"},
                                    HttpUnauthorized )

    def not_attending(self, request, **kwargs):
        """ Get list of events the user does not attend."""
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        self.log_throttled_access(request)
        if request.user and request.user.is_authenticated():
            try:
                myfriends = get_user_friends(request.user.userprofile)
                events = Event.objects.filter(owner__in=myfriends
                                     ).exclude(
                                          Q( owner__user=request.user )
                                        | Q(participants__user=request.user)
                                     ).distinct()
                objects = []
                for result in events:
                    bundle = self.build_bundle(obj=result, request=request)
                    bundle = self.full_dehydrate(bundle)
                    objects.append(bundle)
                object_list = { 'objects': objects, }
                return self.create_response(request, object_list)
            except Event.DoesNotExist:
                return self.create_response(request,
                                            {u'reason': u'Event not found'},
                                            HttpForbidden)
            else:
                return self.create_response(request,
                                            {u'reason': u'Unexpected'},
                                            HttpForbidden)
        else:
            return self.create_response(
                                    request,
                                    {u'reason': u"You are not authenticated"},
                                    HttpUnauthorized )
