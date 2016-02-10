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
        sender_name = link.receiver.name
    else:
        recipient = link.receiver
        sender_name = link.sender.name
    data[u"message"] = REQUEST_LINK%(sender_name)
    send_notification([recipient], data)
    # email
    if recipient.user.email:
        template_prefix = "link/email/request"
        emails = [recipient.user.email]
        context = {"user_name" : sender_name}
        send_mail(template_prefix, emails, context)

def link_accepted(link, inverted, **kwargs):
    # push notif
    data = {u"title":u"Woozup : nouveau contact",
            u"reason":u"friendaccept", u"id":link.receiver.user.id}
    if inverted:
        recipient = link.receiver
        sender_name = link.sender.name
    else:
        recipient = link.sender
        sender_name = link.receiver.name
    data[u"message"] = ACCEPT_LINK%(sender_name)
    send_notification([recipient], data)
    # email
    if recipient.user.email:
        template_prefix = "link/email/accept"
        emails = [recipient.user.email]
        context = {"user_name" : sender_name}
        send_mail(template_prefix, emails, context)

def send_invitation(invite):
    # email
    if invite.emails:
        template_prefix = "link/email/personal_invite"
        emails = invite.emails.split(',')
        context = {"user_name" : invite.sender.name}
        if invite.sender.image:
            context["image"] = invite.sender.image.url
        send_mail(template_prefix, emails, context)

def invite_ignored(invite):
    # email
    if invite.emails:
        template_prefix = "link/email/generic_invite"
        emails = invite.emails.split(',')
        context = {}
        send_mail(template_prefix, emails, context)
