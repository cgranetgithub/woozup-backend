import os
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group

MALE   = 'MA'
FEMALE = 'FE'

def image_path(instance, filename):
    filename_base, filename_ext = os.path.splitext(filename)
    return 'user/%d%s'%(instance.id, filename_ext.lower())

class UserProfile(models.Model):
    GENDER = ( (MALE  , 'male'  ),
               (FEMALE, 'female') )
    user   = models.OneToOneField(User)
    gender = models.CharField(max_length=2, choices=GENDER,
                              blank=True, null=True)
    avatar = models.ImageField(upload_to=image_path,
                               blank=True, null=True)

class UserPosition(models.Model):
    user    = models.OneToOneField(User)
    current = models.CharField(max_length=255,
                               blank=True, null=True) # !!! WARNING to be changed

def user_post_save(sender, instance, created, **kwargs):
    """Create a user profile when a new user account is created"""
    if created and not instance.is_superuser:
        UserProfile.objects.create(user=instance)
        UserPosition.objects.create(user=instance)
        instance.groups.add(Group.objects.get(name='std'))

post_save.connect(user_post_save, sender=User)

