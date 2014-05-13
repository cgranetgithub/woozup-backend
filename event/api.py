from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import SessionAuthentication

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
        resource_name = 'type'
        queryset = EventType.objects.all()
        allowed_methods = ['get']
        filtering = {
                    'category': ALL_WITH_RELATIONS,
                    }

class EventResource(ModelResource):
    type = fields.ToOneField(EventTypeResource,
                             attribute='event_type', full=True)
    class Meta:
        resource_name = 'event'
        queryset = Event.objects.all()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
                    'type'      : ALL_WITH_RELATIONS,
                    'start_date': ALL,
                    'start_time': ALL,
                    'position'  : ALL,
                    }
        authorization  = DjangoAuthorization()
        authentication = SessionAuthentication()

    def obj_create(self, bundle, **kwargs):
        user = User.objects.get(username=bundle.request.user.username)
        kwargs['owner'] = user #force owner to the authorized user
        return super(EventResource, self).obj_create(bundle, **kwargs)
