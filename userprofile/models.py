from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group

from service.utils import image_path

from tastypie.models import create_api_key

MALE   = 'MA'
FEMALE = 'FE'

class UserProfile(models.Model):
    GENDER = ( (MALE  , 'male'  ),
               (FEMALE, 'female') )
    user   = models.OneToOneField(User)
    gender = models.CharField(max_length=2, choices=GENDER,
                              blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to=image_path,
                               blank=True, null=True)
    updated_at  = models.DateTimeField(auto_now=True)
    @property
    def name(self):
        return self.user.get_full_name()
    def __unicode__(self):
        return unicode(self.user) + ' profile'

class UserPosition(models.Model):
    user    = models.OneToOneField(User)
    last = models.CharField(max_length=255,  # !!! WARNING to be changed
                               default="48.853, 2.35")
    home = models.CharField(max_length=255,  # !!! WARNING to be changed
                               default="48.853, 2.35")
    office = models.CharField(max_length=255,  # !!! WARNING to be changed
                               default="48.853, 2.35")
    updated_at  = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return unicode(self.user) + " " + unicode(self.last)

def user_post_save(sender, instance, created, **kwargs):
    """Create a user profile when a new user account is created"""
    if created and not instance.is_superuser:
        UserProfile.objects.create(user=instance)
        UserPosition.objects.create(user=instance)
        instance.groups.add(Group.objects.get(name='std'))

post_save.connect(user_post_save, sender=User)
post_save.connect(create_api_key, sender=User)
