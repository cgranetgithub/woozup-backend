# -*- coding: utf-8 -*-

from service.notification import send_notification

REQUEST_LINK = u"%s souhaite se connecter avec vous"
ACCEPT_LINK = u"%s a accepté votre demande de contact"

def link_requested(link, inverted, **kwargs):
    if inverted:
        msg = REQUEST_LINK%(link.receiver.name)
    else:
        msg = REQUEST_LINK%(link.sender.name)
    data = {'ttl':'Woozup : demande de contact', 'msg':msg,
            'reason':'friendrequest', 'id':link.sender.user.id}
    if inverted:
        send_notification([link.sender], data)
    else:
        send_notification([link.receiver], data)

def link_accepted(link, inverted, **kwargs):
    if inverted:
        msg = ACCEPT_LINK%(link.sender.name)
    else:
        msg = ACCEPT_LINK%(link.receiver.name)
    data = {'ttl':'Woozup : nouveau contact', 'msg':msg,
            'reason':'friendaccept', 'id':link.receiver.user.id}
    if inverted:
        send_notification([link.receiver], data)
    else:
        send_notification([link.sender], data)
