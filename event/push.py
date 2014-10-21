# -*- coding: utf-8 -*-

from userprofile.models import get_user_friends
from service.notification import send_notification

EVENT_CREATED = u"%s vous invite à %s le %s à %s"
EVENT_MODIFIED = u"%s a modifié '%s' (le %s à %s)"
EVENT_CANCELED = u"%s a annulé le rendez-vous '%s' (le %s à %s)"
PARTICIPANT_JOINED = u"%s est partant pour '%s'"
PARTICIPANT_LEFT = u"%s a annulé pour '%s'"

def event_saved(sender, instance, created, **kwargs):
    if created:
        # notify owner's friends which are close enough to the event
        friends = get_user_friends(instance.owner)
        ###WARNING filter based on distance
        msg = EVENT_CREATED%(instance.owner.name, 
                             instance.event_type.name, 
                             instance.start.date().isoformat(),
                             instance.start.time().isoformat())
        send_notification(friends, msg)

def event_to_be_changed(sender, instance, update_fields, **kwargs):
    #print update_fields ###TOBE FINISHED
    if update_fields:
        # notify only participants
        msg = EVENT_MODIFIED%(instance.owner.userprofile.name, 
                            instance.event_type.name, 
                            instance.start.date().isoformat(),
                            instance.start.time().isoformat())
        send_notification(instance.participants.all(), msg)

def event_canceled(sender, instance, **kwargs):
    # notify only participants
    msg = EVENT_CANCELED%(instance.owner.userprofile.name, 
                          instance.event_type.name, 
                          instance.start.date().isoformat(),
                          instance.start.time().isoformat())
    send_notification(instance.participants.all(), msg)

def participant_joined(user, event):
    msg = PARTICIPANT_JOINED%(user.userprofile.name, event.event_type.name)
    recepients = [ i['id'] for i in event.participants.values() ]
    recepients.append(event.owner.id)
    recepients.remove(user.id)
    send_notification(recepients, msg)

def participant_left(user, event):
    msg = PARTICIPANT_LEFT%(user.userprofile.name, event.event_type.name)
    recepients = [ i['id'] for i in event.participants.values() ]
    recepients.append(event.owner.id)
    send_notification(recepients, msg)
