# -*- coding: utf-8 -*-

from django.contrib.gis.db import models
from django.conf import settings
from userprofile.utils import get_friends

class EventCategory(models.Model):
    name        = models.CharField(max_length=50)
    short_name  = models.CharField(max_length=20)
    description = models.CharField(max_length=255)
    order       = models.PositiveSmallIntegerField(blank=True, null=True)
    image       = models.ImageField(upload_to='category_image')
    style       = models.CharField(max_length=255, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True, help_text=u"""
autofield, not modifiable""")
    updated_at  = models.DateTimeField(auto_now=True, help_text=u"""
autofield, not modifiable""")
    def __unicode__(self):
        return self.name

class EventType(models.Model):
    name        = models.CharField(max_length=50)
    short_name  = models.CharField(max_length=20)
    description = models.CharField(max_length=255)
    category    = models.ManyToManyField(EventCategory)
    order       = models.PositiveSmallIntegerField(blank=True, null=True)
    style       = models.CharField(max_length=255, blank=True)
    icon        = models.ImageField(upload_to='type_icon',
                                    blank=True, null=True)
    background  = models.ImageField(upload_to='type_bg',
                                    blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True, help_text=u"""
autofield, not modifiable""")
    updated_at  = models.DateTimeField(auto_now=True, help_text=u"""
autofield, not modifiable""")
    def __unicode__(self):
        return self.name

class Event(models.Model):
    name       = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    special    = models.BooleanField(default=False)
    public     = models.BooleanField(default=False)
    canceled   = models.BooleanField(default=False)
    start      = models.DateTimeField()
    end        = models.DateTimeField(blank=True, null=True)
    event_type = models.ForeignKey(EventType)
    owner      = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   related_name='events_as_owner')
    closed     = models.BooleanField(default=False,
                    help_text=u"""if closed no more participants accepted""")
    p_limit    = models.IntegerField(blank=True, null=True,
                    help_text=u"""maximum number of participants""")
    location_name = models.CharField(max_length=255, blank=True)
    location_address = models.CharField(max_length=255, blank=True)
    location_id = models.CharField(max_length=255, blank=True)
    location_coords = models.GeometryField(null=True, blank=True,
                    help_text=u"""Type: Geometry, Entry format: GeoJson
(example: "{ 'type':'Point', 'coordinates':[125.6, 10.1] }")<br>""")
    #image      = models.ImageField(upload_to=image_path,
                                   #blank=True, null=True)
    image      = models.ImageField(upload_to='event_image',
                                   blank=True, null=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                          blank=True,
                                          related_name='events_as_participant')
    invitees = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                          blank=True,
                                          related_name='events_as_invitee')
    contacts = models.ManyToManyField('link.Contact', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text=u"""
autofield, not modifiable""")
    updated_at = models.DateTimeField(auto_now=True, help_text=u"""
autofield, not modifiable""")

    def __unicode__(self):
        return u"%s - %d participants, %d invités, %d contacts (%s)"%(
            self.name, self.participants.count(), self.invitees.count(),
            self.contacts.count(), self.owner.get_full_name())
    
class Comment(models.Model):
    text       = models.TextField()
    event      = models.ForeignKey(Event)
    author     = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True, help_text=u"""
autofield, not modifiable""")
    updated_at = models.DateTimeField(auto_now=True, help_text=u"""
autofield, not modifiable""")
    class Meta:
        ordering = ['-updated_at']
    def __unicode__(self):
        return u"%s %s %s"%(self.author, self.event, self.text)
