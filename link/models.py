from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
 
from service.utils import image_path

# state is independent of the notification sending
NEW      = 'NEW' # default state after automatic creation
PENDING  = 'PEN' # waiting for action
ACCEPTED = 'ACC' # accepted by sender or receiver
REJECTED = 'REJ' # rejected by receiver
IGNORED  = 'IGN' # ignored by sender or receiver
BLOCKED  = 'BLO' # blocked by sender or receiver
CLOSED   = 'CLO'

class Link(models.Model):
    """ LINK behavior see API doc """
    LINK_STATUS = ( (NEW     , 'new' ),
                    (PENDING , 'pending'), #only for receiver_status
                    (ACCEPTED, 'accepted'),
                    (REJECTED, 'rejected'),
                    (IGNORED , 'ignored'),
                    (BLOCKED , 'blocked' ) )
    sender   = models.ForeignKey(User, related_name='link_as_sender')
    receiver = models.ForeignKey(User, related_name='link_as_receiver')
    sender_status   = models.CharField(max_length=3, choices=LINK_STATUS,
                                                     default=NEW)
    receiver_status = models.CharField(max_length=3, choices=LINK_STATUS,
                                                     default=NEW)
    sent_at     = models.DateTimeField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True, help_text=u"""
autofield, not modifiable""")
    updated_at  = models.DateTimeField(auto_now=True, help_text=u"""
autofield, not modifiable""")
    class Meta:
        unique_together = ("sender", "receiver")
        
    def validate_unique(self, **kwargs):
        # check "reverse link" and ensure uniqueness
        l = None
        try:
            l = Link.objects.get(sender=self.receiver, receiver=self.sender)
        except:
            pass
        if l:
            msg = u"""Link with same Sender/Receiver
(or vice-versa) couple exists."""
            raise ValidationError({u'sender'  :(msg,), u'receiver':(msg,)})
        super(Link, self).validate_unique(**kwargs)
        
    def __unicode__(self):
        return u'[%d] %s(%s) -> %s(%s)'%(self.id, self.sender,
                                                 self.sender_status,
                                                 self.receiver,
                                                 self.receiver_status)

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
    receiver       = models.CharField(max_length=50, help_text=u'username')
    receiver_email = models.EmailField(blank=True)
    receiver_name  = models.CharField(max_length=255, blank=True,
                                help_text='name to be displayed in the app')
    avatar = models.ImageField(upload_to=image_path,
                               blank=True, null=True,
                               help_text='not used for now')
    status = models.CharField(max_length=3, choices=INVITE_STATUS)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True, help_text=u"""
autofield, not modifiable""")
    updated_at  = models.DateTimeField(auto_now=True, help_text=u"""
autofield, not modifiable""")
    class Meta:
        unique_together = ('sender', 'receiver')

    def __unicode__(self):
        return u'%s(%d) -> %s|%s|%s'%(self.sender, self.sender.id,
                                      self.receiver, self.receiver_name,
                                      self.receiver_email)
