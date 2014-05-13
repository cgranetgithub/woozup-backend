from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
    
# state is independent from the notification sending #
NEW      = 'NEW' # default state after automatic creation
PENDING  = 'PEN' # waiting for action
ACCEPTED = 'ACC' # accepted by sender or receiver
REJECTED = 'REJ' # rejected by receiver
IGNORED  = 'IGN' # ignored by sender or receiver
BLOCKED  = 'BLO' # blocked by sender or receiver
CLOSED   = 'CLO'

class Link(models.Model):
    """ LINK behavior
    when a user is discovered on the device,
    a link is automatically created by the backend
        - Link created
        - sender_status=NEW
        - receiver_status=NEW
    sender clicks on "connect" button
        - sender_status=ACCEPTED
        - receiver_status=PENDING
    sender clicks on "ignore" button
        - sender_status=IGNORED
    receiver accepts connection
        - receiver_status=ACCEPTED
    receiver reject connection
        - receiver_status=REJECTED
    sender/receiver blacklist someone
        - x_status=BLOCKED
    """
    LINK_STATUS = ( (NEW     , 'new' ),
                    (PENDING , 'pending'), #only for receiver_status
                    (ACCEPTED, 'accepted'),
                    (REJECTED, 'rejected'),
                    (IGNORED , 'ignored'),
                    (BLOCKED , 'blocked' ) )
    sender   = models.ForeignKey(User, related_name="link_as_sender")
    receiver = models.ForeignKey(User, related_name="link_as_receiver")
    sender_status   = models.CharField(max_length=3, choices=LINK_STATUS)
    receiver_status = models.CharField(max_length=3, choices=LINK_STATUS)
    sent_at     = models.DateTimeField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ("sender", "receiver")
        
    def validate_unique(self, **kwargs):
        # check "reverse link"
        l = None
        try:
            l = Link.objects.get(sender=self.receiver, receiver=self.sender)
        except:
            pass
        if l:
            msg = """Link with same Sender/Receiver
(or vice-versa) couple exists."""
            raise ValidationError({'sender'  :(msg,), 'receiver':(msg,)})
        super(Link, self).validate_unique(**kwargs)
        
    def __unicode__(self):
        return unicode(self.sender) + '  ->  ' + unicode(self.receiver)


class Invite(models.Model):
    """ INVITE behavior
    when a user is discovered on the device,
    an invite is automatically created by the backend
        - Invite created
        - status=NEW
    sender clicks on "invite" button
        - status=PENDING
    sender clicks on "ignore" button
        - status=IGNORED
    receiver accepts invitation
        - status=ACCEPTED
    receiver accepted invitation from someone else or created an account
        - status=CLOSED
    """
    INVITE_STATUS = ( (NEW     , 'new'),
                      (PENDING , 'pending'),
                      (ACCEPTED, 'accepted'),
                      (IGNORED , 'ignored'),
                      (CLOSED  , 'closed' ) )
    sender = models.ForeignKey(User)
    email  = models.EmailField()
    name   = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=3, choices=INVITE_STATUS)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ("sender", "email")

