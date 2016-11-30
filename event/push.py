# -*- coding: utf-8 -*-

from service.notification import send_notification
#from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D # ``D`` is a shortcut for ``Distance``
from journal.models import Record

#def get_event_context(instance):
    #context = {"type"   : instance.event_type.name,
               #"title"  : instance.name,
               #"when"   : instance.start,
               #"icon"   : u"",
               #"address": instance.location_address}
    #if instance.event_type.icon:
        #context["icon"] = instance.event_type.icon.url
    #return context

# def event_modified(sender, instance, **kwargs):
#     # notify only participants
#     friends = instance.participants.all()
#     # push notification
#     EVENT_MODIFIED = u"%s a modifié : %s"
#     msg = EVENT_MODIFIED%(instance.owner.get_full_name(),
#                         instance.name)
#     data = {u"title":u"Changement Woozup", u"message":msg,
#             u"reason":u"eventchanged", u"id":instance.id}
#     send_notification(friends, data)
#     # email
#     template_prefix = "event/email/event_modified"
#     emails = friends.values_list('user__email', flat=True)
#     context = get_event_context(instance)
#     context["user_name"] = instance.owner.get_full_name()
#     send_mail(template_prefix, emails, context)

def event_created(sender, instance, **kwargs):
    # # notify owner's friends who are close enough to the event
    # friends = instance.owner.get_friends()
    # ###WARNING filter based on distance
    # close_friends = friends.filter(
    #             user__userposition__last__distance_lte=(
    #                         instance.location_coords, D(km=100)))
    # create journal record
    Record.objects.create(record_type='NEWEVENT', user=instance.owner,
                          refering_event=instance)
    # push notification
    EVENT_CREATED = u"%s t'invite à : %s"
    msg = EVENT_CREATED%(instance.owner.get_full_name(),
                         instance.event_type.name)
    data = {u"title": u"Nouvelle invitation",
            u"message": msg,
            u"reason": u"newevent",
            u"id": instance.id}
    if instance.owner.profile.image:
        data[u'image'] = instance.owner.profile.image.url
    # send_notification(close_friends, data)
    send_notification(instance.get_invitees(), data)
    # email
    #template_prefix = "event/email/event_created"
    # emails = close_friends.values_list('user__email', flat=True)
    #emails = instance.get_invitees().values_list('user__email', flat=True)
    #context = get_event_context(instance)
    ## context["user"] = request.user
    #context["other"] = instance.owner
    #send_mail(template_prefix, emails, context)

def event_canceled(sender, instance, **kwargs):
    # create journal record
    Record.objects.create(record_type='EVENTCANCELED', user=instance.owner,
                          refering_event=instance)
    # notify only participants
    friends = instance.participants.all()
    # push notification
    EVENT_CANCELED = u"%s a annulé"
    msg = EVENT_CANCELED%(instance.owner.get_full_name())
    data = {u"title": u"%s - annulé"%instance.name,
            u"message": msg,
            u"reason": u"eventcanceled",
            u"id": instance.id}
    if instance.owner.profile.image:
        data[u'image'] = instance.owner.profile.image.url
    send_notification(friends, data)
    # email
    #template_prefix = "event/email/event_canceled"
    #emails = friends.values_list('user__email', flat=True)
    #context = get_event_context(instance)
    ## context["user"] = request.user
    #context["other"] = instance.owner
    #send_mail(template_prefix, emails, context)

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

def participant_joined(request, user, event):
    # create journal record
    Record.objects.create(record_type='NEWPARTICIPANT', user=user,
                          refering_event=event)
    #recepients = [ i[u"id"] for i in event.participants.values() ]
    recepients = [ i for i in event.participants.all() ]
    recepients.append(event.owner)
    recepients.remove(user)
    # push notification
    PARTICIPANT_JOINED = u"%s est partant"
    msg = PARTICIPANT_JOINED%(user.get_full_name())
    data = {u"title": event.name,
            u"message": msg,
            u"reason": u"joinevent",
            u"id": event.id}
    if user.profile.image:
        data[u'image'] = user.profile.image.url
    send_notification(recepients, data)
    # email
    #template_prefix = "event/email/participant_joined"
    #emails = [r.user.email for r in recepients]
    #context = get_event_context(event)
    ## context["user"] = request.user
    #context["other"] = user
    #send_mail(template_prefix, emails, context)

def participant_left(request, user, event):
    #recepients = [ i[u"id"] for i in event.participants.values() ]
    recepients = [ i for i in event.participants.all() ]
    recepients.append(event.owner)
    # push notification
    PARTICIPANT_LEFT = u"%s ne viendra pas"
    msg = PARTICIPANT_LEFT%(user.get_full_name())
    data = {u"title": event.name,
            u"message": msg,
            u"reason": u"leftevent",
            u"id": event.id}
    if user.profile.image:
        data[u'image'] = user.profile.image.url
    send_notification(recepients, data)
    # email
    #template_prefix = "event/email/participant_left"
    #emails = [r.user.email for r in recepients]
    #context = get_event_context(event)
    #context["other"] = user
    #send_mail(template_prefix, emails, context)

def comment_saved(sender, instance, created, update_fields, **kwargs):
    if created:
        # create journal record
        Record.objects.create(record_type='NEWCOMMENT',
                              user=instance.author,
                              refering_event=instance.event)
        # push notification
        recepients = [ i for i in instance.event.participants.all() ]
        recepients.append(instance.event.owner)
        if instance.author in recepients:
            recepients.remove(instance.author)
        if (len(instance.text) > 75) :
            trunc_text = (instance.text[:75] + '..')
        else:
            trunc_text = instance.text
        NEW_COMMENT = u"%s : %s"
        msg = NEW_COMMENT%(instance.author.get_full_name(),
                           trunc_text)
        data = {u"title": instance.event.name,
                u"message":msg,
                u"reason":u"newcomment",
                u"id":instance.event.id}
        if instance.author.profile.image:
            data[u'image'] = instance.author.profile.image.url
        send_notification(recepients, data)
    elif update_fields:
        pass
    