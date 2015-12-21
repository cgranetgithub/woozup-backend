# -*- coding: utf-8 -*-

from userprofile.models import get_user_friends
from service.notification import send_notification
from django.contrib.gis.functions import Distance

EVENT_CREATED = u"%s vous invite à %s"
EVENT_MODIFIED = u"%s a modifié '%s'"
EVENT_CANCELED = u"%s a annulé '%s'"
PARTICIPANT_JOINED = u"%s est partant pour '%s'"
PARTICIPANT_LEFT = u"%s a annulé '%s'"

def event_saved(sender, instance, created, **kwargs):
    if created:
        # check distance
        #print Distance(instance.owner.user.userposition.last,
                       #instance.location_coords)
        # notify owner's friends which are close enough to the event
        friends = get_user_friends(instance.owner)
        ###WARNING filter based on distance
        msg = EVENT_CREATED%(instance.owner.name, 
                             instance.event_type.name)
        data = {'ttl':'Invitation Woozup', 'msg':msg,
                'instance':'event', 'id':instance.id}
        send_notification(friends, data)

def event_to_be_changed(sender, instance, update_fields, **kwargs):
    #print update_fields ###TOBE FINISHED
    if update_fields:
        # notify only participants
        msg = EVENT_MODIFIED%(instance.owner.userprofile.name, 
                            instance.name)
        data = {'ttl':'Changement Woozup', 'msg':msg,
                'instance':'event', 'id':instance.id}
        send_notification(instance.participants.all(), data)

def event_canceled(sender, instance, **kwargs):
    # notify only participants
    msg = EVENT_CANCELED%(instance.owner.name, 
                          instance.name)
    data = {'ttl':' Annulation Woozup', 'msg':msg,
            'instance':'event', 'id':instance.id}
    send_notification(instance.participants.all(), data)

def participant_joined(userprofile, event):
    msg = PARTICIPANT_JOINED%(userprofile.name, event.name)
    #recepients = [ i['id'] for i in event.participants.values() ]
    recepients = [ i for i in event.participants.all() ]
    recepients.append(event.owner)
    recepients.remove(userprofile)
    data = {'ttl':'Woozup', 'msg':msg, 'instance':'event', 'id':event.id}
    send_notification(recepients, data)

def participant_left(userprofile, event):
    msg = PARTICIPANT_LEFT%(userprofile.name, event.name)
    #recepients = [ i['id'] for i in event.participants.values() ]
    recepients = [ i for i in event.participants.all() ]
    recepients.append(event.owner)
    data = {'ttl':'Woozup', 'msg':msg, 'instance':'event', 'id':event.id}
    send_notification(recepients, data)
