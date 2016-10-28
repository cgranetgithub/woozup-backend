from django.apps import AppConfig
from django.db.models.signals import post_save

class UserProfileConfig(AppConfig):
    name = 'userprofile'
    verbose_name = "User profile"

    def ready(self):
        from django.conf import settings
        from .models import create_profiles
        post_save.connect(create_profiles, sender=settings.AUTH_USER_MODEL)
        from tastypie.models import create_api_key
        post_save.connect(create_api_key,  sender=settings.AUTH_USER_MODEL)
        from link.tasks import (transform_invites_from_number,
                                transform_invites_from_user)
        Number = self.get_model('Number')
        post_save.connect(transform_invites_from_number, sender=Number)
        post_save.connect(transform_invites_from_user,
                          sender=settings.AUTH_USER_MODEL)
