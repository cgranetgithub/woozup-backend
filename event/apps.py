from django.apps import AppConfig
from django.db.models.signals import pre_save, post_save, pre_delete
from event.push import event_to_be_changed, event_saved, event_canceled

class EventConfig(AppConfig):
    name = 'event'
    verbose_name = "Event"

    def ready(self):
        Event = self.get_model('Event')
        pre_save.connect(event_to_be_changed, sender=Event)
        post_save.connect(event_saved, sender=Event)
        pre_delete.connect(event_canceled, sender=Event)
