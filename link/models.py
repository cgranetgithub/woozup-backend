from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
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
    sender   = models.ForeignKey('userprofile.UserProfile', related_name='link_as_sender')
    receiver = models.ForeignKey('userprofile.UserProfile', related_name='link_as_receiver')
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
        unique_together = (("sender", "receiver"), )
        
    def validate_unique(self, **kwargs):
        # check don't link the same person
        if self.sender == self.receiver:
            msg = u"""Sender/Receiver are the same!"""
            raise ValidationError({u'sender'  :(msg,), u'receiver':(msg,)})
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

    def save(self, *args, **kwargs):
        # custom unique validate
        self.validate_unique()
        super(Link, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'[%d] %s(%s) -> %s(%s)'%(self.id, self.sender,
                                                 self.sender_status,
                                                 self.receiver,
                                                 self.receiver_status)

class Invite(models.Model):
    """ INVITE behavior
    when a user is discovered on the device,
    an invite is automatically created by the backend
        - status=NEW
    sender clicks on "invite" button, a message is sent to the receiver
        - status=PENDING
    sender clicks on "ignore" button
        - status=IGNORED
    receiver registered in the service => a link is created and the invitation is closed
        - status=CLOSED
    """
    INVITE_STATUS = ( (NEW     , 'new'),
                      (PENDING , 'pending'),
                      (ACCEPTED, 'accepted'),
                      (IGNORED , 'ignored'),
                      (CLOSED  , 'closed' ) )
    sender  = models.ForeignKey('userprofile.UserProfile')
    name    = models.CharField(max_length=255, blank=True,
                               help_text='name to be displayed in the app')
    numbers = models.CharField(max_length=255, blank=True,
                               help_text=u'phone numbers list')
    emails  = models.CharField(max_length=255, blank=True,
                               help_text=u'email addresses list')
    photo   = models.CharField(max_length=255, blank=True,
                             help_text='local path in the device to a picture')
    avatar  = models.ImageField(upload_to=image_path,
                               blank=True, null=True,
                               help_text='not used for now')
    status  = models.CharField(max_length=3, choices=INVITE_STATUS, default=NEW)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True, help_text=u"""
autofield, not modifiable""")
    updated_at  = models.DateTimeField(auto_now=True, help_text=u"""
autofield, not modifiable""")
    class Meta:
        unique_together = (('sender', 'numbers'), ('sender', 'emails'))

    def __unicode__(self):
        return u'%s(%d) -> %s (%s | %s)'%(self.sender, self.sender.user_id,
                                      self.name, self.emails, self.numbers)
