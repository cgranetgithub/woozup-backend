# -*- coding: utf-8 -*-

from userprofile.models import get_user_friends
from service.notification import send_notification

EVENT_CREATED = u"%s vous invite à %s le %s à %s"
EVENT_MODIFIED = u"%s a modifié '%s' (le %s à %s)"
EVENT_CANCELED = u"%s a annulé le rendez-vous '%s' (le %s à %s)"

def event_saved(sender, instance, created, **kwargs):
    if created:
        # notify owner's friends which are close enough to the event
        friends = get_user_friends(instance.owner)
        ###WARNING filter based on distance
        msg = EVENT_CREATED%(instance.owner.userprofile.name, 
                             instance.event_type.title, 
                             instance.start.date().isoformat(),
                             instance.start.time().isoformat())
        send_notification(friends, msg)

def event_to_be_changed(sender, instance, update_fields, **kwargs):
    print update_fields
    if update_fields:
        # notify only participants
        msg = EVENT_MODIFIED%(instance.owner.userprofile.name, 
                            instance.event_type.title, 
                            instance.start.date().isoformat(),
                            instance.start.time().isoformat())
        send_notification(instance.participants.all(), msg)

def event_canceled(sender, instance, **kwargs):
    # notify only participants
    msg = EVENT_CANCELED%(instance.owner.userprofile.name, 
                          instance.event_type.title, 
                          instance.start.date().isoformat(),
                          instance.start.time().isoformat())
    send_notification(instance.participants.all(), msg)