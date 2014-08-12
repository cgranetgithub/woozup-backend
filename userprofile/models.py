from django.db.models import Q
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group

from service.utils import image_path

from tastypie.models import create_api_key

MALE   = 'MA'
FEMALE = 'FE'

def get_user_friends(user):
    return User.objects.filter(
                        ( Q(link_as_sender__sender    =user) | 
                          Q(link_as_sender__receiver  =user) | 
                          Q(link_as_receiver__sender  =user) | 
                          Q(link_as_receiver__receiver=user) ),
                        ( Q(link_as_sender__sender_status='ACC') & 
                          Q(link_as_sender__receiver_status='ACC') ) | 
                        ( Q(link_as_receiver__sender_status='ACC') & 
                          Q(link_as_receiver__receiver_status='ACC') ) )

class UserProfile(models.Model):
    GENDER = ( (MALE  , 'male'  ),
               (FEMALE, 'female') )
    user   = models.OneToOneField(User)
    gender = models.CharField(max_length=2, choices=GENDER,
                              blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to=image_path,
                               blank=True, null=True)
    updated_at  = models.DateTimeField(auto_now=True, help_text=u"""
autofield, not modifiable""")
    @property
    def name(self):
        return self.user.get_full_name()
    def __unicode__(self):
        return u'%s profile'%self.user

class UserPosition(models.Model):
    user   = models.OneToOneField(User)
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

def user_post_save(sender, instance, created, **kwargs):
    """Create a user profile when a new user account is created"""
    if created and not instance.is_superuser:
        UserProfile.objects.create(user=instance)
        UserPosition.objects.create(user=instance)
        instance.groups.add(Group.objects.get(name='std'))

post_save.connect(user_post_save, sender=User)
post_save.connect(create_api_key, sender=User)
