from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from event.models import EventCategory, EventType, Event

class EventCategoryResource(ModelResource):
    class Meta:
        resource_name = 'category'
        queryset = EventCategory.objects.all()
        allowed_methods = ['get']

class EventTypeResource(ModelResource):
    category = fields.ToManyField(EventCategoryResource, 'category')
    class Meta:
        resource_name = 'type'
        queryset = EventType.objects.all()
        allowed_methods = ['get']
	filtering = {
		    'category': ALL_WITH_RELATIONS,
		    }

class EventResource(ModelResource):
    type = fields.ToOneField(EventTypeResource, 'event_type')
    class Meta:
        resource_name = 'event'
        queryset = Event.objects.all()
        allowed_methods = ['get']
        filtering = {
                    'type'      : ALL_WITH_RELATIONS,
                    'start_date': ALL,
                    'start_time': ALL,
                    'position'  : ALL,
                    }
