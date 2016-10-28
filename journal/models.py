from __future__ import unicode_literals

from django.db import models
from django.conf import settings

class Record(models.Model):
    TYPESCHOICES = (('DEFAULT', ''),
                    ('NEWUSER', 'user registered on woozup'),
                    ('NEWPARTICIPANT', 'user joined an event'),
                    ('NEWEVENT', 'user created an event'),
                    ('EVENTCANCELED', 'user canceled an event'),
                    ('NEWFRIEND', 'user connected with another user'))
    record_type = models.CharField(max_length=20, choices=TYPESCHOICES,
                                   default='DEFAULT')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='Records as user+')
    refering_event = models.ForeignKey('event.event', null=True, blank=True)
    refering_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                                      blank=True)
    created_at  = models.DateTimeField(auto_now_add=True, help_text=u"""
autofield, not modifiable""")
    updated_at  = models.DateTimeField(auto_now=True, help_text=u"""
autofield, not modifiable""")
    class Meta:
        ordering = ['-updated_at']
    def __unicode__(self):
        return unicode(self.record_type) + u' ' + unicode(self.user)
