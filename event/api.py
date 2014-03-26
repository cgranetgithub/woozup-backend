from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from event.models import EventCategory, EventType

class EventCategoryResource(ModelResource):
    class Meta:
        queryset = EventCategory.objects.all()
        resource_name = 'category'

class EventTypeResource(ModelResource):
    category = fields.ToManyField(EventCategoryResource, 'category')
    class Meta:
        queryset = EventType.objects.all()
        resource_name = 'type'
	filtering = {
		    'category': ALL_WITH_RELATIONS,
		    }