# -*- coding: utf-8 -*-

from service.notification import send_notification, send_mail

REQUEST_LINK = u"%s souhaite se connecter avec toi"
ACCEPT_LINK = u"%s a accepté ton invitation"

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

def send_invitation(invite):
    # email
    if invite.emails:
        template_prefix = "link/email/personal_invite"
        emails = invite.emails.split(',')
        context = {"other" : invite.sender}
        send_mail(template_prefix, emails, context)

def invite_ignored(invite):
    # email
    if invite.emails:
        template_prefix = "link/email/generic_invite"
        emails = invite.emails.split(',')
        context = {}
        send_mail(template_prefix, emails, context)
