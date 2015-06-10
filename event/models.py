from django.contrib.gis.db import models
from service.utils import image_path

class EventCategory(models.Model):
    name       = models.CharField(max_length=50)
    short_name  = models.CharField(max_length=20)
    description = models.CharField(max_length=255)
    order       = models.PositiveSmallIntegerField(blank=True, null=True)
    image        = models.ImageField(upload_to='glyph')
    created_at  = models.DateTimeField(auto_now_add=True, help_text=u"""
autofield, not modifiable""")
    updated_at  = models.DateTimeField(auto_now=True, help_text=u"""
autofield, not modifiable""")
    def __unicode__(self):
        return self.name
 
class EventType(models.Model):
    name       = models.CharField(max_length=50)
    short_name  = models.CharField(max_length=20)
    description = models.CharField(max_length=255)
    category    = models.ManyToManyField(EventCategory)
    order       = models.PositiveSmallIntegerField(blank=True, null=True)
    image        = models.ImageField(upload_to='glyph',
                                    blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True, help_text=u"""
autofield, not modifiable""")
    updated_at  = models.DateTimeField(auto_now=True, help_text=u"""
autofield, not modifiable""")
    def __unicode__(self):
        return self.name

class Event(models.Model):
    name       = models.CharField(max_length=50, blank=True)
    comment    = models.CharField(max_length=255, blank=True)
    special    = models.BooleanField(default=False)
    public     = models.BooleanField(default=False)
    start      = models.DateTimeField()
    end        = models.DateTimeField(blank=True, null=True)
    event_type = models.ForeignKey(EventType)
    owner      = models.ForeignKey('userprofile.UserProfile',
                                   related_name='events_as_owner')
    closed     = models.BooleanField(default=False,
                    help_text=u"""if closed no more participants accepted""")
    p_limit    = models.IntegerField(blank=True, null=True,
                    help_text=u"""maximum number of participants""")
    position   = models.GeometryField(null=True, blank=True,
                    help_text=u"""Type: Geometry, Entry format: GeoJson 
(example: "{ 'type':'Point', 'coordinates':[125.6, 10.1] }")<br>""")
    image      = models.ImageField(upload_to=image_path,
                                   blank=True, null=True)
    participants = models.ManyToManyField('userprofile.UserProfile', 
                                          related_name='events_as_participant')
    created_at = models.DateTimeField(auto_now_add=True, help_text=u"""
autofield, not modifiable""")
    updated_at = models.DateTimeField(auto_now=True, help_text=u"""
autofield, not modifiable""")
    # overriding the default manager with a GeoManager instance.
    objects = models.GeoManager()

    def __unicode__(self):
        return u"%s (%s)"%(self.name, self.event_type)
    class Meta:
        unique_together = ('start', 'event_type', 'owner')
