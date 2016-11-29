from django.contrib.gis import admin
from event.models import EventCategory, EventType, Event, Comment

admin.site.register(EventCategory)
admin.site.register(EventType)
admin.site.register(Comment)
admin.site.register(Event, admin.OSMGeoAdmin)
