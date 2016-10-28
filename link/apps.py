from django.apps import AppConfig
from django.db.models.signals import post_save

class LinkConfig(AppConfig):
    name = 'link'
    verbose_name = "Link"

    def ready(self):
        from link.push import link_saved
        Link = self.get_model('Link')
        post_save.connect(link_saved, sender=Link)
