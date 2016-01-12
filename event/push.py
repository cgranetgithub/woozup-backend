# -*- coding: utf-8 -*-

from userprofile.utils import get_user_friends
from service.notification import send_notification
#from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D # ``D`` is a shortcut for ``Distance``

EVENT_CREATED = u"%s vous invite à %s"
EVENT_MODIFIED = u"%s a modifié '%s'"
EVENT_CANCELED = u"%s a annulé '%s'"
PARTICIPANT_JOINED = u"%s est partant pour '%s'"
PARTICIPANT_LEFT = u"%s a annulé '%s'"

def event_saved(sender, instance, created, **kwargs):
    if created:
        # notify owner's friends who are close enough to the event
        friends = get_user_friends(instance.owner)
        close_friends = friends.filter(
                    user__userposition__last__distance_lte=(
                                instance.location_coords, D(km=100)))
        ###WARNING filter based on distance
        msg = EVENT_CREATED%(instance.owner.name, 
                             instance.event_type.name)
        data = {u"title":u"Invitation Woozup", u"message":msg,
                u"reason":u"newevent", u"id":instance.id}
        send_notification(close_friends, data)

def event_to_be_changed(sender, instance, update_fields, **kwargs):
    #print update_fields ### TO BE FINISHED
    if update_fields:
        # notify only participants
        msg = EVENT_MODIFIED%(instance.owner.userprofile.name, 
                            instance.name)
        data = {u"title":u"Changement Woozup", u"message":msg,
                u"reason":u"eventchanged", u"id":instance.id}
        send_notification(instance.participants.all(), data)

def event_canceled(sender, instance, **kwargs):
    # notify only participants
    msg = EVENT_CANCELED%(instance.owner.name, 
                          instance.name)
    data = {u"title":u"Annulation Woozup", u"message":msg,
            u"reason":u"eventcanceled", u"id":instance.id}
    send_notification(instance.participants.all(), data)

def participant_joined(userprofile, event):
    msg = PARTICIPANT_JOINED%(userprofile.name, event.name)
    #recepients = [ i[u"id"] for i in event.participants.values() ]
    recepients = [ i for i in event.participants.all() ]
    recepients.append(event.owner)
    recepients.remove(userprofile)
    data = {u"title":u"Woozup", u"message":msg, u"reason":u'joinevent",
            u"id":event.id}
    send_notification(recepients, data)

def participant_left(userprofile, event):
    msg = PARTICIPANT_LEFT%(userprofile.name, event.name)
    #recepients = [ i[u"id"] for i in event.participants.values() ]
    recepients = [ i for i in event.participants.all() ]
    recepients.append(event.owner)
    data = {u"title":u"Woozup", u"message":msg, u"reason":u"leftevent",
            u"id":event.id}
    send_notification(recepients, data)
