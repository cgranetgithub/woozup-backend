from django.apps import AppConfig
from django.db.models.signals import post_save
from django.conf import settings

class UserProfileConfig(AppConfig):
    name = 'userprofile'
    verbose_name = "User Profile"

    def ready(self):
        from link.tasks import (transform_invites_from_number,
                                transform_invites_from_user)
        Number = self.get_model('Number')
        post_save.connect(transform_invites_from_number, sender=Number)
        post_save.connect(transform_invites_from_user,
                          sender=settings.AUTH_USER_MODEL)
