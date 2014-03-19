from django.db import models
from django.contrib.auth.models import User

PENDING  = 'PE'
SENT     = 'SE'
ACCEPTED = 'AC'
REJECTED = 'RE'
BLOCKED  = 'BL'
HIDDEN   = 'HI'

class Link(models.Model):
    LINK_STATUS = ( (PENDING , 'pending' ),
		    (SENT    , 'sent'    ),
		    (ACCEPTED, 'accepted'),
		    (REJECTED, 'rejected'),
		    (BLOCKED , 'blocked' ) )
    initiator = models.ForeignKey(User, related_name="links_as_initiator")
    receiver  = models.ForeignKey(User, related_name="links_as_receiver")
    status    = models.CharField(max_length=2, choices=LINK_STATUS)

class Invite(models.Model):
    INVITE_STATUS = ( (PENDING , 'pending'),
		      (SENT    , 'sent'   ),
		      (HIDDEN  , 'hidden' ) )
    initiator = models.ForeignKey(User)
    receiver  = models.EmailField()
    status    = models.CharField(max_length=2, choices=INVITE_STATUS)
