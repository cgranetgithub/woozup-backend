from django.contrib.gis import admin
from userprofile.models import Profile, Position, Number

admin.site.register(Profile)
admin.site.register(Number)
admin.site.register(Position, admin.OSMGeoAdmin)
