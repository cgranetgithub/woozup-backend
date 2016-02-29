# -*- coding: utf-8 -*-

from userprofile.utils import get_user_friends
from service.notification import send_notification, send_mail
#from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D # ``D`` is a shortcut for ``Distance``

EVENT_CREATED = u"%s t'invite à : %s"
EVENT_MODIFIED = u"%s a modifié : %s"
EVENT_CANCELED = u"%s a annulé : %s"
PARTICIPANT_JOINED = u"%s est partant pour : %s"
PARTICIPANT_LEFT = u"%s ne participe pas à : %s"

def get_event_context(instance):
    context = {"type"   : instance.event_type.name,
               "title"  : instance.name,
               "when"   : instance.start,
               "icon"   : u"",
               "address": instance.location_address}
    if instance.event_type.icon:
        context["icon"] = instance.event_type.icon.url
    return context

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
    # context["user"] = request.user.userprofile
    context["other"] = instance.owner
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
    # context["user"] = request.user.userprofile
    context["other"] = instance.owner
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

def participant_joined(request, userprofile, event):
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
    # context["user"] = request.user.userprofile
    context["other"] = userprofile
    send_mail(template_prefix, emails, context)

def participant_left(request, userprofile, event):
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
    context["other"] = userprofile
    send_mail(template_prefix, emails, context)
