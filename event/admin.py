from django.contrib import admin
from event.models import EventCategory, EventType, Event

admin.site.register(EventCategory)
admin.site.register(EventType)
admin.site.register(Event)
