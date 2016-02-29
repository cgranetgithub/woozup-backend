from django.apps import AppConfig
from django.db.models.signals import post_save
from django.conf import settings

class UserProfileConfig(AppConfig):
    name = 'userprofile'
    verbose_name = "User Profile"

    def ready(self):
        from link.tasks import (transform_invites_from_profile,
                                transform_invites_from_user)
        UserProfile = self.get_model('UserProfile')
        post_save.connect(transform_invites_from_profile, sender=UserProfile)
        post_save.connect(transform_invites_from_user,
                          sender=settings.AUTH_USER_MODEL)
