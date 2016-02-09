# -*- coding: utf-8 -*-

from service.utils import send_mail
from service.notification import send_notification

REQUEST_LINK = u"%s souhaite se connecter avec toi"
ACCEPT_LINK = u"%s a accepté ta demande de contact"

def link_requested(link, inverted, **kwargs):
    if inverted:
        msg = REQUEST_LINK%(link.receiver.name)
    else:
        msg = REQUEST_LINK%(link.sender.name)
    data = {u"title":u"Woozup : demande de contact", u"message":msg,
            u"reason":u"friendrequest", u"id":link.sender.user.id}
    if inverted:
        send_notification([link.sender], data)
    else:
        send_notification([link.receiver], data)

def link_accepted(link, inverted, **kwargs):
    if inverted:
        msg = ACCEPT_LINK%(link.sender.name)
    else:
        msg = ACCEPT_LINK%(link.receiver.name)
    data = {u"title":u"Woozup : nouveau contact", u"message":msg,
            u"reason":u"friendaccept", u"id":link.receiver.user.id}
    if inverted:
        send_notification([link.receiver], data)
    else:
        send_notification([link.sender], data)

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
