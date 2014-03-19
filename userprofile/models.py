from django.db import models
from django.contrib.auth.models import User

MALE   = 'MA'
FEMALE = 'FE'

class UserProfile(models.Model):
    GENDER = ( 	(MALE  , 'male'  ),
		(FEMALE, 'female') )
    user   = models.OneToOneField(User)
    gender = models.CharField(max_length=2, choices=GENDER)

class UserPosition(models.Model):
    user        = models.OneToOneField(User)
    current_pos = models.CharField(max_length=255) # !!! WARNING to be changed
