from django.db import models
from django.contrib.auth.models import User

PENDING  = 'PEN'
ACCEPTED = 'ACC'
REJECTED = 'REJ'
INGNORED = 'IGN'
NONE     = 'NON'
BLOCKED  = 'BLO'
HIDDEN   = 'HID'

class Link(models.Model):
    LINK_STATUS = ( (PENDING , 'pending' ),
		    (ACCEPTED, 'accepted'),
		    (REJECTED, 'rejected'),
		    (BLOCKED , 'blocked' ) )
    sender   = models.ForeignKey(User, related_name="link_as_sender")
    receiver = models.ForeignKey(User, related_name="link_as_receiver")
    sender_status   = models.CharField(max_length=3, choices=LINK_STATUS)
    receiver_status = models.CharField(max_length=3, choices=LINK_STATUS)
    sent_at     = models.DateTimeField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return unicode(self.sender) + '  ->  ' + unicode(self.receiver)


class Invite(models.Model):
    INVITE_STATUS = ( (PENDING , 'new'),
		      (HIDDEN  , 'hidden' ) )
    sender   = models.ForeignKey(User)
    receiver = models.EmailField()
    status   = models.CharField(max_length=2, choices=INVITE_STATUS)
    sent_at  = models.DateTimeField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

""" LINK 
    sender clicks on "connect" button
        - Link created
        - sender_status=ACCEPTED
        - receiver_status=PENDING
    sender clicks on "ignore" button
        - Link created
        - sender_status=IGNORED
        - receiver_status=NONE
    receiver accepts connection
        - receiver_status=ACCEPTED
    receiver accepts connection
        - receiver_status=REJECTED
    sender/receiver blacklist someone
        - x_status=BLOCKED
"""
