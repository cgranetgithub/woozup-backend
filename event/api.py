from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import ApiKeyAuthentication

from django.db.models import Q
from django.contrib.auth.models import User

from event.models import EventCategory, EventType, Event

class EventCategoryResource(ModelResource):
    class Meta:
        resource_name = 'category'
        queryset = EventCategory.objects.all()
        allowed_methods = ['get']

class EventTypeResource(ModelResource):
    category = fields.ToManyField(EventCategoryResource,
                                  attribute='category', full=True)
    class Meta:
        resource_name = 'event_type'
        queryset = EventType.objects.all()
        allowed_methods = ['get']
        filtering = {
                    'category': ALL_WITH_RELATIONS,
                    }

class EventResource(ModelResource):
    event_type = fields.ToOneField(EventTypeResource,
                                   attribute='event_type', full=True)
    class Meta:
        resource_name = 'event'
        queryset = Event.objects.all()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'patch', 'delete']
        filtering = {
                    'event_type': ALL_WITH_RELATIONS,
                    'start'     : ALL,
                    'position'  : ALL,
                    }
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    def obj_create(self, bundle, **kwargs):
        user = User.objects.get(username=bundle.request.user.username)
        kwargs['owner'] = user #force owner to the authorized user
        return super(EventResource, self).obj_create(bundle, **kwargs)

    def get_object_list(self, request):
        myfriends = User.objects.filter(
                        ( Q(link_as_sender__sender    =request.user) | 
                          Q(link_as_sender__receiver  =request.user) | 
                          Q(link_as_receiver__sender  =request.user) | 
                          Q(link_as_receiver__receiver=request.user) ),
                        ( Q(link_as_sender__sender_status='ACC') & 
                          Q(link_as_sender__receiver_status='ACC') ) | 
                        ( Q(link_as_receiver__sender_status='ACC') & 
                          Q(link_as_receiver__receiver_status='ACC') ) )
        if not myfriends:
            myfriends = [request.user]
        return Event.objects.filter(
                                Q( owner__in=myfriends )
                              | Q( participants__id__exact=request.user.id ) )
