# -*- coding: utf-8 -*-
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

import plivo
from service.utils import is_mobile_number

from rq.decorators import job
from worker import conn

from django.conf import settings
auth_id = settings.SMS_AUTH_ID
auth_token = settings.SMS_AUTH_TOKEN
sender_phone = settings.SMS_SENDER_PHONE

@job('default', connection=conn)
def send_notification(id_list, data):
    import django
    django.setup()
    from push_notifications.models import APNSDevice, GCMDevice
    android_push = GCMDevice.objects.filter(user__id__in=id_list,
                                            active=True)
    android_push.send_message(data['message'], extra=data)
    ios_push = APNSDevice.objects.filter(user__id__in=id_list,
                                            active=True)
    ios_push.send_message(data['message'], extra=data)

def enqueue_send_notification(user_list, data):
    id_list = [u.id for u in user_list]
    send_notification.delay(id_list, data)

@job('default', connection=conn)
def send_sms(message, numbers):
    # keep only mobile numbers
    #numbers = [n for n in number_set if is_mobile_number(n)]
    logger.info("Sending %d SMS"%len(numbers))
    dest = '<'.join(numbers)
    p = plivo.RestAPI(auth_id, auth_token)
    params = {
        'src': sender_phone,
        'dst' : dest, # Receiver's phone Number with country code
        'text' : message,
    }
    response = p.send_message(params)

def enqueue_send_sms(message, number_set):
    # set to make sure no duplicates
    assert type(number_set) is set
    # each SMS take 1s and rq timeout is 180s
    # split number set in chuncks
    size = 50
    chunks = [list(number_set)[i:i+size] for i in range(0, len(number_set), size)]
    for c in chunks:
        send_sms.delay(message, c)

#def render_mail(template_prefix, emails, context):
    #"""
    #Renders an e-mail to `emails`.  `template_prefix` identifies the
    #e-mail that is to be sent, e.g. "event/email/email_confirmation"
    #"""
    #subject = render_to_string('{0}_subject.txt'.format(template_prefix),
                               #context)
    ## remove superfluous line breaks
    #subject = " ".join(subject.splitlines()).strip()

    #bodies = {}
    #for ext in ['html', 'txt']:
        #try:
            #template_name = '{0}_message.{1}'.format(template_prefix, ext)
            #bodies[ext] = render_to_string(template_name,
                                           #context).strip()
        #except TemplateDoesNotExist:
            #if ext == 'txt' and not bodies:
                ## We need at least one body
                #raise
    #if 'txt' in bodies:
        #logger.info("Sending %d emails"%len(emails))
        #msg = EmailMultiAlternatives(subject,
                                     #bodies['txt'],
                                     #settings.DEFAULT_FROM_EMAIL,
                                     #[],     #to
                                     #emails) #bcc
        #if 'html' in bodies:
            #msg.attach_alternative(bodies['html'], 'text/html')
    #else:
        #logger.info("Sending %d emails"%len(emails))
        #msg = EmailMessage(subject,
                           #bodies['html'],
                           #settings.DEFAULT_FROM_EMAIL,
                           #[],     #to
                           #emails) #bcc
        #msg.content_subtype = 'html'  # Main content is now text/html
    #return msg

#def send_mail(template_prefix, emails, context):
    #msg = render_mail(template_prefix, emails, context)
    #msg.send()
