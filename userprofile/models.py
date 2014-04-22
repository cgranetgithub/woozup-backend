import os
from django.db import models
from django.contrib.auth.models import User

MALE   = 'MA'
FEMALE = 'FE'

def image_path(instance, filename):
    filename_base, filename_ext = os.path.splitext(filename)
    return 'user/%d%s'%(instance.id, filename_ext.lower())

class UserProfile(models.Model):
    GENDER = ( 	(MALE  , 'male'  ),
		(FEMALE, 'female') )
    user   = models.OneToOneField(User)
    gender = models.CharField(max_length=2, choices=GENDER,
                              blank=True, null=True)
    avatar = models.ImageField(upload_to=image_path,
                               blank=True, null=True)

class UserPosition(models.Model):
    user    = models.OneToOneField(User)
    current = models.CharField(max_length=255) # !!! WARNING to be changed
