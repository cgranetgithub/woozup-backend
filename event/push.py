# -*- coding: utf-8 -*-

from service.utils import send_mail
from userprofile.utils import get_user_friends
from service.notification import send_notification
#from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D # ``D`` is a shortcut for ``Distance``

EVENT_CREATED = u"%s vous invite à %s"
EVENT_MODIFIED = u"%s a modifié '%s'"
EVENT_CANCELED = u"%s a annulé '%s'"
PARTICIPANT_JOINED = u"%s est partant pour '%s'"
PARTICIPANT_LEFT = u"%s ne participe pas '%s'"

def get_event_context(instance):
    return {"type":instance.event_type.name,
            "title":instance.name,
            "when":instance.start,
            "icon":instance.event_type.icon,
            "address":instance.location_address}

# def event_modified(sender, instance, **kwargs):
#     # notify only participants
#     friends = instance.participants.all()
#     # push notification
#     msg = EVENT_MODIFIED%(instance.owner.name,
#                         instance.name)
#     data = {u"title":u"Changement Woozup", u"message":msg,
#             u"reason":u"eventchanged", u"id":instance.id}
#     send_notification(friends, data)
#     # email
#     template_prefix = "event/email/event_modified"
#     emails = friends.values_list('user__email', flat=True)
#     context = get_event_context(instance)
#     context["user_name"] = instance.owner.name
#     send_mail(template_prefix, emails, context)

def event_created(sender, instance, **kwargs):
    # notify owner's friends who are close enough to the event
    friends = get_user_friends(instance.owner)
    ###WARNING filter based on distance
    close_friends = friends.filter(
                user__userposition__last__distance_lte=(
                            instance.location_coords, D(km=100)))
    # push notification
    msg = EVENT_CREATED%(instance.owner.name,
                         instance.event_type.name)
    data = {u"title":u"Invitation Woozup", u"message":msg,
            u"reason":u"newevent", u"id":instance.id}
    send_notification(close_friends, data)
    # email
    template_prefix = "event/email/event_created"
    emails = close_friends.values_list('user__email', flat=True)
    context = get_event_context(instance)
    context["user_name"] = instance.owner.name
    send_mail(template_prefix, emails, context)

def event_canceled(sender, instance, **kwargs):
    # notify only participants
    friends = instance.participants.all()
    # push notification
    msg = EVENT_CANCELED%(instance.owner.name,
                          instance.name)
    data = {u"title":u"Annulation Woozup", u"message":msg,
            u"reason":u"eventcanceled", u"id":instance.id}
    send_notification(friends, data)
    # email
    template_prefix = "event/email/event_canceled"
    emails = friends.values_list('user__email', flat=True)
    context = get_event_context(instance)
    context["user_name"] = instance.owner.name
    send_mail(template_prefix, emails, context)

def event_saved(sender, instance, created, update_fields, **kwargs):
    if created:
        event_created(sender, instance, **kwargs)
    elif update_fields:
        if 'canceled' in update_fields:
            event_canceled(sender, instance, **kwargs)
    #     else:
    #         event_modified(sender, instance, **kwargs)
    # else:
    #     event_modified(sender, instance, **kwargs)

def participant_joined(userprofile, event):
    msg = PARTICIPANT_JOINED%(userprofile.name, event.name)
    #recepients = [ i[u"id"] for i in event.participants.values() ]
    recepients = [ i for i in event.participants.all() ]
    recepients.append(event.owner)
    recepients.remove(userprofile)
    # push notification
    data = {u"title":u"Woozup", u"message":msg, u"reason":u"joinevent",
            u"id":event.id}
    send_notification(recepients, data)
    # email
    template_prefix = "event/email/participant_joined"
    emails = [r.user.email for r in recepients]
    context = get_event_context(event)
    context["user_name"] = userprofile.name
    send_mail(template_prefix, emails, context)

def participant_left(userprofile, event):
    msg = PARTICIPANT_LEFT%(userprofile.name, event.name)
    #recepients = [ i[u"id"] for i in event.participants.values() ]
    recepients = [ i for i in event.participants.all() ]
    recepients.append(event.owner)
    # push notification
    data = {u"title":u"Woozup", u"message":msg, u"reason":u"leftevent",
            u"id":event.id}
    send_notification(recepients, data)
    # email
    template_prefix = "event/email/participant_left"
    emails = [r.user.email for r in recepients]
    context = get_event_context(event)
    context["user_name"] = userprofile.name
    send_mail(template_prefix, emails, context)
