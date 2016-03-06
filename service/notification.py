# -*- coding: utf-8 -*-
# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

import plivo
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template import TemplateDoesNotExist
from service.utils import is_mobile_number
from django.conf import settings

def render_mail(template_prefix, emails, context):
    """
    Renders an e-mail to `emails`.  `template_prefix` identifies the
    e-mail that is to be sent, e.g. "event/email/email_confirmation"
    """
    subject = render_to_string('{0}_subject.txt'.format(template_prefix),
                               context)
    # remove superfluous line breaks
    subject = " ".join(subject.splitlines()).strip()

    bodies = {}
    for ext in ['html', 'txt']:
        try:
            template_name = '{0}_message.{1}'.format(template_prefix, ext)
            bodies[ext] = render_to_string(template_name,
                                           context).strip()
        except TemplateDoesNotExist:
            if ext == 'txt' and not bodies:
                # We need at least one body
                raise
    if 'txt' in bodies:
        logger.info("Sending %d emails"%len(emails))
        msg = EmailMultiAlternatives(subject,
                                     bodies['txt'],
                                     settings.DEFAULT_FROM_EMAIL,
                                     [],     #to
                                     emails) #bcc
        if 'html' in bodies:
            msg.attach_alternative(bodies['html'], 'text/html')
    else:
        logger.info("Sending %d emails"%len(emails))
        msg = EmailMessage(subject,
                           bodies['html'],
                           settings.DEFAULT_FROM_EMAIL,
                           [],     #to
                           emails) #bcc
        msg.content_subtype = 'html'  # Main content is now text/html
    return msg

def send_mail(template_prefix, emails, context):
    msg = render_mail(template_prefix, emails, context)
    msg.send()

def send_notification(userprofile_list, data):
    from push_notifications.models import APNSDevice, GCMDevice

    ### temporary, to be removed
    data['msg'] = data['message']
    data['ttl'] = data['title']
    ###

    android_push = GCMDevice.objects.filter(user__userprofile__in=userprofile_list,
                                            active=True)
    android_push.send_message(data['message'], extra=data)
    ios_push = APNSDevice.objects.filter(user__userprofile__in=userprofile_list)
    ios_push.send_message(data['message'], extra=data)

def send_sms(message, number_set):
    # set to make sure no duplicates
    assert type(number_set) is set
    # keep only mobile numbers
    numbers = [n for n in number_set if is_mobile_number(n)]
    logger.info("Sending %d SMS"%len(numbers))
    dest = '<'.join(numbers)
    auth_id = settings.SMS_AUTH_ID
    auth_token = settings.SMS_AUTH_TOKEN
    sender_phone = settings.SMS_SENDER_PHONE
    p = plivo.RestAPI(auth_id, auth_token)
    params = {
        'src': sender_phone, # Sender's phone number with country code
        'dst' : dest, # Receiver's phone Number with country code
        'text' : message,
    }
    response = p.send_message(params)
