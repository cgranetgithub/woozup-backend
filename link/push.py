# -*- coding: utf-8 -*-

from service.notification import send_notification, send_mail, send_sms
from django.utils import timezone

REQUEST_LINK = u"%s souhaite se connecter avec toi"
ACCEPT_LINK = u"%s a accepté ton invitation"
SMS_PERSONAL = u"%s t'invite sur Woozup ! Télécharge l'appli dans l'AppStore ou le PlayStore."
SMS_GENERIC = u"Découvre Woozup, l'appli pour passer du temps avec ses amis ! Télécharge Woozup dans l'AppStore ou le PlayStore."

def link_requested(link, inverted, **kwargs):
    # push notif
    data = {u"title":u"Woozup : demande de contact",
            u"reason":u"friendrequest", u"id":link.sender.user.id}
    if inverted:
        recipient = link.sender
        sender = link.receiver
    else:
        recipient = link.receiver
        sender = link.sender
    data[u"message"] = REQUEST_LINK%(sender.name)
    send_notification([recipient], data)
    # email
    if recipient.user.email:
        template_prefix = "link/email/request"
        emails = [recipient.user.email]
        context = {"other" : sender, "user" : recipient}
        send_mail(template_prefix, emails, context)

def link_accepted(link, inverted, **kwargs):
    # push notif
    data = {u"title":u"Woozup : nouveau contact",
            u"reason":u"friendaccept", u"id":link.receiver.user.id}
    if inverted:
        recipient = link.receiver
        sender = link.sender
    else:
        recipient = link.sender
        sender = link.receiver
    data[u"message"] = ACCEPT_LINK%(sender.name)
    send_notification([recipient], data)
    # email
    if recipient.user.email:
        template_prefix = "link/email/accept"
        emails = [recipient.user.email]
        context = {"other" : sender, "user" : recipient}
        send_mail(template_prefix, emails, context)

def send_invitation(invite, message, template_prefix, context, sms=False):
    ret = {'emails':0, 'sms':0}
    # email
    if invite.emails:
        emails = set([x.strip() for x in invite.emails.split(',')])
        send_mail(template_prefix, emails, context)
        ret['emails'] += len(emails)
        invite.sent_at = timezone.now()
        invite.save()
    # SMS
    elif (invite.numbers and sms):
        numbers = set([x.strip() for x in invite.numbers.split(',')])
        send_sms(message, numbers)
        ret['sms'] += len(numbers)
        invite.sent_at = timezone.now()
        invite.save()
    return ret

def invite_validated(invite):
    template_prefix = "link/email/personal_invite"
    context = {"other" : invite.sender}
    message = SMS_PERSONAL%invite.sender.name
    return send_invitation(invite, message, template_prefix, context, True)

def invite_ignored(invite):
    template_prefix = "link/email/generic_invite"
    context = {}
    return send_invitation(invite, SMS_GENERIC, template_prefix, context, True)

def send_bulk_generic_invitation(numbers, emails):
    assert type(numbers) is set
    assert type(emails) is set
    template_prefix = "link/email/generic_invite"
    context = {}
    send_mail(template_prefix, emails, context)
    send_sms(SMS_GENERIC, numbers)
