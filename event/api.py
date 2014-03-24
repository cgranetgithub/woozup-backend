from tastypie.resources import ModelResource
from event.models import EventCategory


class EventCategoryResource(ModelResource):
    class Meta:
        queryset = EventCategory.objects.all()
        resource_name = 'category'
