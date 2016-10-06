from rest_framework import serializers, viewsets
from event.models import EventCategory, EventType, Event

class EventCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventCategory
        #fields = ('username', 'first_name', 'last_name')

class EventCategoryViewSet(viewsets.ModelViewSet):
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer

class EventTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventType
        #fields = ('username', 'first_name', 'last_name')

class EventTypeViewSet(viewsets.ModelViewSet):
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer
