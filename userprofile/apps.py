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
