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

from event.models import EventCategory, EventType, Event, Comment
from userprofile.api import UserResource
from link.api import ContactResource
from userprofile.utils import get_friends
from django.contrib.auth import get_user_model

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
        always_return_data = True

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
        always_return_data = True

#class AbstractEventResource(ModelResource):
    #event_type = fields.ToOneField(EventTypeResource, 'event_type',
                                      #full=True)
    #participants = fields.ToManyField(UserResource, 'participants',
                                      #full=True, null=True)
    #invitees = fields.ManyToManyField(UserResource, 'invitees',
                                      #full=True, null=True)
    #owner = fields.ToOneField(UserResource, 'owner', full=True, null=True)
    #class Meta:
        #abstract = True
        #serializer = MyDateSerializer()
        #queryset = Event.objects.all()
        #list_allowed_methods = ['get']
        #detail_allowed_methods = ['get']
        #filtering = {
                    ##'owner'       : ALL_WITH_RELATIONS,
                    #'event_type' : ALL_WITH_RELATIONS,
                    #'start'      : ALL,
                    #'position'   : ALL,
                    #'canceled'   : ALL,
                    ##'participants': ALL_WITH_RELATIONS,
                    #}
        #ordering = ['start']
        #authorization  = DjangoAuthorization()
        #authentication = ApiKeyAuthentication()
        #always_return_data = True

class EventResource(ModelResource):
    event_type = fields.ToOneField(EventTypeResource, 'event_type',
                                      full=True)
    participants = fields.ToManyField(UserResource, 'participants',
                                      full=True, null=True)
    invitees = fields.ManyToManyField(UserResource, 'invitees',
                                      full=True, null=True)
    contacts = fields.ManyToManyField(ContactResource, 'contacts',
                                      full=True, null=True)
    owner = fields.ToOneField(UserResource, 'owner', full=True, null=True)
    class Meta:
        resource_name = 'event'
        serializer = MyDateSerializer()
        queryset = Event.objects.all()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'delete']
        filtering = {
                    #'owner'       : ALL_WITH_RELATIONS,
                    'event_type' : ALL_WITH_RELATIONS,
                    'start'      : ALL,
                    'position'   : ALL,
                    'canceled'   : ALL,
                    #'participants': ALL_WITH_RELATIONS,
                    }
        ordering = ['start']
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True

    def get_object_list(self, request):
        user = request.user
        mine = Event.objects.filter(owner=user)
        invited_to = Event.objects.filter(invitees__in=[user])
        events = mine | invited_to
        return events.distinct()

    def obj_create(self, bundle, **kwargs):
        kwargs['owner'] = bundle.request.user
        return super(EventResource, self).obj_create(bundle, **kwargs)

    def obj_delete(self, bundle, **kwargs):
        if not hasattr(bundle.obj, 'delete'):
            try:
                bundle.obj = self.obj_get(bundle=bundle, **kwargs)
            except ObjectDoesNotExist:
                raise NotFound("""A model instance matching the provided
                    arguments could not be found.""")
        self.authorized_delete_detail(self.get_object_list(bundle.request),
                                      bundle)
        bundle.obj.canceled = True
        bundle.obj.save(update_fields=['canceled'])

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
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        event_id = kwargs['event_id']
        (req, data, status) = apifn.join(request, event_id)
        return self.create_response(req, data, status)

    def leave(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        event_id = kwargs['event_id']
        (req, data, status) = apifn.leave(request, event_id)
        return self.create_response(req, data, status)

class AllEventsResource(EventResource):
    class Meta(EventResource.Meta):
        resource_name = 'events/all'

    #def get_object_list(self, request):
        #user = request.user
        ##me = get_user_model().objects.filter(id=user.id)
        #mine = Event.objects.filter(owner=user)
        ## restrict result to my friends' events
        #myfriends = get_friends(user)
        #friend_events = Event.objects.filter(owner__in=myfriends
                             #).filter( Q(invitees=None)
                                     #| Q(invitees__in=[user])
                             #)
        ##owners = me | myfriends
        ##events = Event.objects.filter(owner__in=owners).distinct()
        #events = mine | friend_events
        #return events.distinct()

class MyAgendaResource(EventResource):
    class Meta(EventResource.Meta):
        resource_name = 'events/agenda'

    def get_object_list(self, request):
        # restrict result to my events + the events I go to
        mine = Event.objects.filter(owner=request.user)
        participation = request.user.events_as_participant.all()
        events = mine | participation
        return events.distinct()

class MyEventsResource(EventResource):
    class Meta(EventResource.Meta):
        resource_name = 'events/mine'
        #list_allowed_methods = ['get', 'post']
        #detail_allowed_methods = ['get', 'put', 'delete']

    #def obj_create(self, bundle, **kwargs):
        ##force owner to the authorized user
        #kwargs['owner'] = bundle.request.user
        #return super(MyEventsResource, self).obj_create(bundle, **kwargs)

    #def obj_delete(self, bundle, **kwargs):
        #if not hasattr(bundle.obj, 'delete'):
            #try:
                #bundle.obj = self.obj_get(bundle=bundle, **kwargs)
            #except ObjectDoesNotExist:
                #raise NotFound("A model instance matching the provided arguments could not be found.")
        #self.authorized_delete_detail(self.get_object_list(bundle.request), bundle)
        #bundle.obj.canceled = True
        #bundle.obj.save(update_fields=['canceled'])

    #def get_object_list(self, request):
        ## restrict result to my events
        #events = Event.objects.filter(owner=request.user)
        #return events

class FriendsEventsResource(EventResource):
    class Meta(EventResource.Meta):
        resource_name = 'events/friends'

    #def get_object_list(self, request):
        #user = request.user
        ## restrict result to my friends' events
        #myfriends = get_friends(user)
        #events = Event.objects.filter(owner__in=myfriends
                             #).filter( Q(invitees=None)
                                     #| Q(invitees__in=[user])
                             #).distinct()
        ## filter by distance TODO add an option for filtering
        ##if user.position.last:
            ##events = events.filter(location_coords__distance_lte=(
                                            ##user.position.last, D(km=100)))
        #return events

# DEPRECATED
class CommentsResource(ModelResource):
    author = fields.ToOneField(UserResource, 'author', full=True)
    event = fields.ToOneField(AllEventsResource, 'event', full=True)
    class Meta:
        resource_name = 'comments'
        queryset = Comment.objects.all()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'put', 'delete']
        ordering = ['-updated_at']
        filtering = {
                    'event': ALL_WITH_RELATIONS,
                    }
        always_return_data = True
        authentication = ApiKeyAuthentication()
        authorization  = DjangoAuthorization()

    #def get_object_list(self, request):
        #queryset = Comment.objects.all()
        #return queryset

    def obj_create(self, bundle, **kwargs):
        #force owner to the authorized user
        kwargs['author'] = bundle.request.user
        return super(CommentResource, self).obj_create(bundle, **kwargs)

class CommentResource(ModelResource):
    author = fields.ToOneField(UserResource, 'author', full=True)
    event = fields.ToOneField(EventResource, 'event', full=True)
    class Meta:
        resource_name = 'comment'
        queryset = Comment.objects.all()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'put', 'delete']
        ordering = ['-updated_at']
        filtering = {
                    'event': ALL_WITH_RELATIONS,
                    }
        always_return_data = True
        authentication = ApiKeyAuthentication()
        authorization  = DjangoAuthorization()

    #def get_object_list(self, request):
        #queryset = Comment.objects.all()
        #return queryset

    def obj_create(self, bundle, **kwargs):
        #force owner to the authorized user
        kwargs['author'] = bundle.request.user
        return super(CommentResource, self).obj_create(bundle, **kwargs)
