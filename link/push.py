# -*- coding: utf-8 -*-

from userprofile.models import get_user_friends
from service.notification import send_notification

REQUEST_LINK = u"%s souhaite se connecter avec vous"
ACCEPT_LINK = u"%s a accepté votre demande de connection"

def link_requested(link, **kwargs):
    msg = REQUEST_LINK%(link.sender)
    send_notification([link.receiver], msg)

def link_accepted(link, **kwargs):
    msg = ACCEPT_LINK%(link.receiver)
    send_notification([link.sender], msg)
