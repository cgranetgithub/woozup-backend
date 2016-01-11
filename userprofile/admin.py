from django.contrib.gis import admin
from userprofile.models import UserProfile, UserPosition

admin.site.register(UserProfile)
admin.site.register(UserPosition, admin.OSMGeoAdmin)
