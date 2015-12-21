from django.apps import AppConfig
from django.db.models.signals import post_save

class UserProfileConfig(AppConfig):
    name = 'userprofile'
    verbose_name = "User Profile"
    
    def ready(self):
        UserProfile = self.get_model('UserProfile')
        from link.tasks import transform_invites
        post_save.connect(transform_invites, sender=UserProfile)
