from django.conf import settings
from django.db.models import Q
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import Group
from tastypie.models import create_api_key
from phonenumber_field.modelfields import PhoneNumberField
from service.utils import image_path
#from link.tasks import transform_invites

MALE   = 'MA'
FEMALE = 'FE'

class UserProfile(models.Model):
    GENDER = ( (MALE  , 'male'  ),
               (FEMALE, 'female') )
    user   = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    gender = models.CharField(max_length=2, choices=GENDER, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    phone_number = PhoneNumberField(blank=True)
    locale = models.CharField(max_length=3, blank=True)
    image = models.ImageField(upload_to=image_path,
                              blank=True, null=True)
    updated_at  = models.DateTimeField(auto_now=True, help_text=u"""
autofield, not modifiable""")
    @property
    def name(self):
        return self.user.get_full_name()
    @property
    def email(self):
        return self.user.email
    def __unicode__(self):
        return u'%s profile'%self.user
    class Meta:
        app_label = 'userprofile'

class UserPosition(models.Model):
    user   = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    last   = models.GeometryField(null=True, blank=True, help_text=u"""
Type: Geometry, Entry format: GeoJson (example: "{ 'type' : 'Point',
'coordinates' : [125.6, 10.1] }")<br>""")
    home   = models.GeometryField(null=True, blank=True, help_text=u"""
Type: Geometry, Entry format: GeoJson (example: "{ 'type' : 'Point',
'coordinates' : [125.6, 10.1] }")<br>""")
    office = models.GeometryField(null=True, blank=True, help_text=u"""
Type: Geometry, Entry format: GeoJson (example: "{ 'type' : 'Point',
'coordinates' : [125.6, 10.1] }")<br>""")
    updated_at  = models.DateTimeField(auto_now=True, help_text=u"""
autofield, not modifiable""")
    # overriding the default manager with a GeoManager instance.
    objects = models.GeoManager()
    def __unicode__(self):
        return u'%s %s'%(self.user, self.last)
    class Meta:
        app_label = 'userprofile'

def create_profiles(sender, instance, created, **kwargs):
    """Create a user profile when a new user account is created"""
    if created and not instance.is_superuser:
        UserProfile.objects.create(user=instance)
        UserPosition.objects.create(user=instance)
        instance.groups.add(Group.objects.get(name='std'))

post_save.connect(create_profiles  , sender=settings.AUTH_USER_MODEL)
post_save.connect(create_api_key   , sender=settings.AUTH_USER_MODEL)
#post_save.connect(transform_invites, sender=settings.AUTH_USER_MODEL)

def get_user_friends(userprofile):
    #return UserProfile.objects.filter(
                        #( Q(link_as_sender__sender    =userprofile) |
                          #Q(link_as_sender__receiver  =userprofile) |
                          #Q(link_as_receiver__sender  =userprofile) |
                          #Q(link_as_receiver__receiver=userprofile) ),
                        #( Q(link_as_sender__sender_status='ACC') &
                          #Q(link_as_sender__receiver_status='ACC') ) |
                        #( Q(link_as_receiver__sender_status='ACC') &
                          #Q(link_as_receiver__receiver_status='ACC') ) )
    link_as_sender = userprofile.link_as_sender.filter(
                            sender_status='ACC',
                            receiver_status='ACC')
    receivers = UserProfile.objects.filter(
                            user_id__in=link_as_sender.values('receiver_id'))
    link_as_receiver = userprofile.link_as_receiver.filter(
                            sender_status='ACC',
                            receiver_status='ACC')
    senders = UserProfile.objects.filter(
                            user_id__in=link_as_receiver.values('sender_id'))
    return senders | receivers
