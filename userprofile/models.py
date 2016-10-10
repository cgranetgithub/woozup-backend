# -*- coding: utf-8 -*-
import random
from django.conf import settings
from django.db.models import Q
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import Group
from tastypie.models import create_api_key
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from service.notification import send_sms

MALE   = 'MA'
FEMALE = 'FE'

def a_random_number():
    return random.randint(1234, 9876)
    
class Number(models.Model):
    phone_number = PhoneNumberField(unique=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True)
    validation_code = models.IntegerField(null=True)
    validated = models.BooleanField(default=False)
    code_sent_at = models.DateTimeField(null=True)
    
    def get_code(self):
        self.validation_code = a_random_number()
        self.code_sent_at = timezone.now()
        self.save()
        send_sms('Code de vérification Woozup : %s'%self.validation_code,
                 set([unicode(self.phone_number)]))
        
    def verif_code(self, code):
        return (code == self.validation_code)

    def validate(self, user, number, code):
        if (self.phone_number == number) and (code == self.validation_code):
            self.validated = True
            self.user = user
            self.save()
            return True
        else:
            return False

    def __unicode__(self):
        return unicode(self.phone_number)

class Profile(models.Model):
    GENDER = ( (MALE  , 'male'  ),
               (FEMALE, 'female') )
    user   = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    gender = models.CharField(max_length=2, choices=GENDER, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    locale = models.CharField(max_length=3, blank=True)
    #image = models.ImageField(upload_to=image_path,
                              #blank=True, null=True)
    image = models.ImageField(upload_to='profile_picture',
                              blank=True, null=True)
    updated_at  = models.DateTimeField(auto_now=True, help_text=u"""
autofield, not modifiable""")
    @property
    def name(self):
        return self.user.get_full_name() or self.user.username
    @property
    def email(self):
        return self.user.email
    def __unicode__(self):
        return u'%s profile (%d)'%(self.user, self.user.id)
    #class Meta:
        #app_label = 'profile'

    def get_friends(self):
        link_as_sender = self.link_as_sender.filter(
                                sender_status='ACC',
                                receiver_status='ACC')
        receivers = Profile.objects.filter(
                                user_id__in=link_as_sender.values('receiver_id'))
        link_as_receiver = self.link_as_receiver.filter(
                                sender_status='ACC',
                                receiver_status='ACC')
        senders = Profile.objects.filter(
                                user_id__in=link_as_receiver.values('sender_id'))
        return senders | receivers

class Position(models.Model):
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
    def __unicode__(self):
        return u'%s %s'%(self.user, self.last)
    #class Meta:
        #app_label = 'position'

def create_profiles(sender, instance, created, **kwargs):
    """Create a user profile when a new user account is created"""
    if created and not instance.is_superuser:
        Profile.objects.create(user=instance)
        Position.objects.create(user=instance)
        instance.groups.add(Group.objects.get(name='std'))
        
post_save.connect(create_profiles, sender=settings.AUTH_USER_MODEL)
post_save.connect(create_api_key,  sender=settings.AUTH_USER_MODEL)
