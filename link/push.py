# -*- coding: utf-8 -*-

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
