from django.apps import AppConfig
from django.db.models.signals import post_save

class EventConfig(AppConfig):
    name = 'event'
    verbose_name = "Event"

    def ready(self):
        from event.push import event_saved
        Event = self.get_model('Event')
        post_save.connect(event_saved, sender=Event)
        # pre_save.connect(event_to_be_changed, sender=Event)
        # event is never deleted
        # pre_delete.connect(event_canceled, sender=Event)
