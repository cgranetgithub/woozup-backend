from django.db import models
from django.contrib.auth.models import User

from service.utils import image_path

class EventCategory(models.Model):
    title       = models.CharField(max_length=50)
    short_name  = models.CharField(max_length=20)
    description = models.CharField(max_length=255)
    order       = models.PositiveSmallIntegerField(blank=True, null=True)
    icon        = models.ImageField(upload_to='glyph')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.title
 
class EventType(models.Model):
    title       = models.CharField(max_length=50)
    short_name  = models.CharField(max_length=20)
    description = models.CharField(max_length=255)
    category    = models.ManyToManyField(EventCategory)
    order       = models.PositiveSmallIntegerField(blank=True, null=True)
    icon        = models.ImageField(upload_to='glyph',
                                    blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.title

class Event(models.Model):
    title        = models.CharField(max_length=50, blank=True)
    comment      = models.CharField(max_length=255, blank=True)
    special      = models.BooleanField(default=False)
    public       = models.BooleanField(default=False)
    start        = models.DateTimeField()
    end          = models.DateTimeField(blank=True, null=True)
    event_type   = models.ForeignKey(EventType)
    owner        = models.ForeignKey(User, related_name='events_as_owner')
    participants = models.ManyToManyField(User, 
                                          related_name='events_as_participant', 
                                          blank=True, null=True)
    position     = models.CharField(max_length=255) # !!! WARNING to be changed
    image        = models.ImageField(upload_to=image_path,
                                     blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.title + ' (' + unicode(self.event_type) + ')'
    class Meta:
        unique_together = ("start", "event_type", "owner")
