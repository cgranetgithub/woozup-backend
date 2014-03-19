from django.db import models
from django.contrib.auth.models import User

class EventCategory(models.Model):
    title       = models.CharField(max_length=50)
    description = models.CharField(max_length=255)

class EventType(models.Model):
    title       = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    category    = models.ForeignKey(EventCategory)

class Event(models.Model):
    title        = models.CharField(max_length=50)
    comment      = models.CharField(max_length=255)
    start_date   = models.DateField()
    start_time   = models.TimeField()
    end_date     = models.DateField()
    end_time     = models.TimeField()
    event_type   = models.ForeignKey(EventType)
    owner        = models.ForeignKey(User, related_name='events_as_owner')
    participants = models.ManyToManyField(User, related_name='events_as_participant')
    position     = models.CharField(max_length=255) # !!! WARNING to be changed
