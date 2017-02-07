# -*- coding: utf-8 -*-

from service.notification import enqueue_send_notification, enqueue_send_sms
from django.utils import timezone
from journal.models import Record

#REQUEST_LINK = u"%s souhaite se connecter avec toi"
#ACCEPT_LINK = u"%s a accepté ton invitation"
SMS_PERSONAL = u"%s t'invite sur Woozup ! Télécharge l'appli pour iphone ou Android."
#SMS_GENERIC = u"Découvre Woozup, le meilleur moyen de voir tes amis ! Télécharge Woozup pour iphone ou Android."

#def link_saved(sender, instance, created, update_fields, **kwargs):
    #pass

#def link_requested(link, inverted, **kwargs):
    ## push notif
    #data = {u"title":u"Woozup : demande de contact",
            #u"reason":u"friendrequest"}
    #if inverted:
        #recipient = link.sender
        #sender = link.receiver
    #else:
        #recipient = link.receiver
        #sender = link.sender
    #data[u"message"] = REQUEST_LINK%(sender.get_full_name())
    #data[u"id"] = sender.id
    #if sender.profile.image:
        #data[u"image"] = sender.profile.image.url
    #enqueue_send_notification([recipient], data)
    # email
    #if recipient.user.email:
        #template_prefix = "link/email/request"
        #emails = [recipient.user.email]
        #context = {"other" : sender, "user" : recipient}
        #send_mail(template_prefix, emails, context)

#def link_accepted(link, inverted, **kwargs):
    ## push notif
    #data = {u"title":u"Woozup : nouveau contact",
            #u"reason":u"friendaccept"}
    #if inverted:
        #recipient = link.sender
        #sender = link.receiver
    #else:
        #recipient = link.receiver
        #sender = link.sender
    #data[u"message"] = ACCEPT_LINK%(sender.get_full_name())
    #data[u"id"] = sender.id
    #if sender.profile.image:
        #data[u"image"] = sender.profile.image.url
    #enqueue_send_notification([recipient], data)
    ## create journal record
    #Record.objects.create(record_type='NEWFRIEND', user=sender,
                          #refering_user=recipient)
    # email
    #if recipient.user.email:
        #template_prefix = "link/email/accept"
        #emails = [recipient.user.email]
        #context = {"other" : sender, "user" : recipient}
        #send_mail(template_prefix, emails, context)

def send_invitation(contacts, message, sms=True):
    ret = {'emails':0, 'sms':0}
    # email
    #if contact.emails:
        #emails = set([x.strip() for x in contact.emails.split(',')])
        #send_mail(template_prefix, emails, context)
        #ret['emails'] += len(emails)
        #contact.sent_at = timezone.now()
        #contact.save()
    # SMS
    for c in contacts:
        if c.numbers:
            numbers = set([x.strip() for x in c.numbers.split(',')])
            enqueue_send_sms(message, numbers)
            ret['sms'] += len(numbers)
            c.sent_at = timezone.now()
            c.save()
    return ret

def invite_validated(contact):
    #template_prefix = "link/email/personal_invite"
    #context = {"other" : contact.sender}
    message = SMS_PERSONAL%contact.sender.get_full_name()
    return send_invitation([contact], message, True)

#def invite_ignored(contact):
    #template_prefix = "link/email/generic_invite"
    #context = {}
    #return send_invitation(contact, SMS_GENERIC, template_prefix, context, True)

#def send_bulk_generic_invitation(numbers, emails):
    #assert type(numbers) is set
    #assert type(emails) is set
    #template_prefix = "link/email/generic_invite"
    #context = {}
    #send_mail(template_prefix, emails, context)
    #enqueue_send_sms(SMS_GENERIC, numbers)
