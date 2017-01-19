from django.apps import AppConfig
from django.db.models.signals import post_save, m2m_changed

class EventConfig(AppConfig):
    name = 'event'
    verbose_name = "Event"

    def ready(self):
        from event.push import (event_saved, comment_saved,
                                invitees_changed, contacts_changed)
        Event = self.get_model('Event')
        post_save.connect(event_saved, sender=Event)
        m2m_changed.connect(invitees_changed, sender=Event.invitees.through)
        m2m_changed.connect(contacts_changed, sender=Event.contacts.through)
        Comment = self.get_model('Comment')
        post_save.connect(comment_saved, sender=Comment)
        # pre_save.connect(event_to_be_changed, sender=Event)
        # event is never deleted
        # pre_delete.connect(event_canceled, sender=Event)
