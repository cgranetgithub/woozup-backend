# -*- coding: utf-8 -*-
import logging, requests

from base64 import b64decode

from link.models import Link
from .models import Number
from service.utils import get_clean_number

from django.http import HttpResponse
from django.contrib import auth
from django.core.files.base import ContentFile
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.auth.models import User
from django.utils.timezone import now as datetime_now

from push_notifications.models import APNSDevice, GCMDevice
from tastypie.http import (HttpUnauthorized, HttpForbidden,
                           HttpCreated, HttpBadRequest,
                           HttpUnprocessableEntity)
from tastypie.models import ApiKey

from link import push

def setlast(request, data):
    if request.user and request.user.is_authenticated():
        try:
            last = data.get('last').strip()
        except:
            return (request, {u'reason': "empty"}, HttpBadRequest)
        if last:
            pnt = GEOSGeometry(last)
            request.user.position.last = last
            request.user.position.save()
            return (request, {}, HttpResponse)
        else:
            return (request, {u'reason': "empty"}, HttpBadRequest)
    else:
        return (request, {u'reason': u"You are not authenticated"},
                HttpUnauthorized)

def setprofile(request, data):
    if request.user and request.user.is_authenticated():
        try:
            first_name = data.get('first_name').strip()
            if first_name:
                request.user.first_name = first_name
        except:
            pass
        try:
            last_name = data.get('last_name').strip()
            if last_name:
                request.user.last_name = last_name
        except:
            pass
        #try:
            #email = data.get('email').strip()
            #if email:
                #request.user.email = email
        #except:
            #pass
        request.user.save()
        #try:
            #number = data.get('number').strip()
            #if number:
                #num = get_clean_number(number)
                #if num is not None:
                    #request.user.number.phone_number = num
            #else: # user can set empty number
                #request.user.number.phone_number = ''
        #except:
            #pass
        try:
            gender = data.get('gender').strip()
            if gender in ['MA', 'FE']:
                request.user.profile.gender = gender
        except:
            pass
        request.user.profile.save()
        return (request, {}, HttpResponse)
    else:
        return (request, {u'reason': u"You are not authenticated"},
                HttpUnauthorized)

def setpicture(request, data):
    if request.user and request.user.is_authenticated():
        b64_text = data.get('file', False)
        url_image = data.get('url_image', False)
        filename = data.get('name', 'default')
        if b64_text:
            image_data = b64decode(b64_text)
        elif url_image:
            image_data = requests.get(url_image).content
        else:
            return (request, {u'reason': u"no input provided"},
                    HttpBadRequest)
        request.user.profile.image = ContentFile(image_data, filename)
        request.user.profile.save()
        return (request, {}, HttpResponse)
    else:
        return (request, {u'reason': u"You are not authenticated"},
                HttpUnauthorized)

def login(request, username, password):
    user = auth.authenticate(username=username, password=password)
    if user:
        if user.is_active:
            auth.login(request, user)
            return (request, {'api_key' : user.api_key.key,
                              'userid'  : user.id,
                              'username': user.username}, HttpResponse)
        else:
            return (request, {u'reason': u'inactive user',
                              u'code': '150'}, HttpUnauthorized)
    else:
        return (request, {u'reason': u'unable to authenticate',
                          u'code': '400'}, HttpUnauthorized)

def get_code(request, phone_number):
    nb = get_clean_number(phone_number)
    if nb:
        (number, created) = Number.objects.get_or_create(phone_number=nb)
        number.get_code()
        return (request, {}, HttpResponse)
    else:
        logging.error(u'%s not a number valid number'%nb)
        return (request, {u'reason': u'%s not a number valid number'%nb},
                HttpBadRequest)

def reset_password(request, password, code, number):
    if number.verif_code(code):
        number.user.set_password(password)
        number.user.save()
        return (request, {}, HttpResponse)
    else:
        return (request, {u'reason': u'incorrect code'}, HttpUnprocessableEntity)

def logout(request):
    if request.user and request.user.is_authenticated():
        # change api_key
        api_key = request.user.api_key
        api_key.key = api_key.generate_key()
        api_key.created = datetime_now()
        api_key.save()
        auth.logout(request)
        return (request, {'userid':request.user.id }, HttpResponse)
    else:
        return (request, {u'reason': u"You are not authenticated"},
                HttpUnauthorized)

def push_notif_reg(request, data):
    if request.user and request.user.is_authenticated():
        try:
            device_id = data.get('device_id').strip()
        except:
            logging.error(u"missing device_id")
            return (request, {u'reason': u"empty device_id"}, HttpBadRequest)
        if not device_id:
            logging.error(u"empty device_id")
            return (request, {u'reason': u"empty device_id"}, HttpBadRequest)
        try:
            platform = data.get('platform').strip()
        except:
            logging.error(u"empty platform")
            return (request, {u'reason': u"empty platform"}, HttpBadRequest)
        try:
            registration_id = data.get('registration_id').strip()
            if not registration_id:
                logging.error(u"empty registration_id")
                return (request, {u'reason': u"empty registration_id"}, HttpBadRequest)
        except:
            logging.error(u"empty platform")
            return (request, {u'reason': u"empty platform"}, HttpBadRequest)
        try:
            if platform == 'ios':
                (device, created) = APNSDevice.objects.get_or_create(
                                                    user=request.user,
                                                    device_id=device_id)
            elif platform == 'android':
                (device, created) = GCMDevice.objects.get_or_create(
                                                    user=request.user,
                                                    device_id=device_id)
            else:
                logging.error(u"unknown platform")
                return (request, {u'reason': "unknown platform"}, HttpBadRequest)
            device.registration_id = registration_id
            try:
                name = data.get('name').strip()
                if name:
                    device.name = name
            except:
                pass
            device.save()
            return (request, {'userid':request.user.id }, HttpResponse)
        except:
            logging.error(u"error during registration")
            return (request, {u'reason': u'error during registration'},
                        HttpBadRequest)
    else:
        return (request, {u'reason': u"You are not authenticated"},
                    HttpUnauthorized)

def accept(request, receiver_id):
    sender = request.user
    receiver = User.objects.get(id=receiver_id)
    if request.user and request.user.is_authenticated():
        inverted = False
        try:
            link = Link.objects.get(sender=sender, receiver=receiver)
            if link.sender_status == 'NEW' and link.receiver_status == 'NEW':
                link.receiver_status = 'PEN'
                push.link_requested(link, inverted)
            elif link.sender_status == 'PEN' and link.receiver_status == 'ACC':
                push.link_accepted(link, inverted)
            link.sender_status = 'ACC'
            link.save()
        except Link.DoesNotExist:
            try:
                (link, created) = Link.objects.get_or_create(sender=receiver,
                                                             receiver=sender)
                inverted = True
                if link.sender_status == 'NEW' and link.receiver_status == 'NEW':
                    link.sender_status = 'PEN'
                    push.link_requested(link, inverted)
                elif link.sender_status == 'ACC' and link.receiver_status == 'PEN':
                    push.link_accepted(link, inverted)
                link.receiver_status = 'ACC'
                link.save()
            except:
                logging.error(u'not found => created => issue')
                return (request, {u'reason': u'not found => created => issue'},
                        HttpUnprocessableEntity)
        except:
            logging.error(u'found => issue')
            return (request, {u'reason': u'found => issue'},
                    HttpUnprocessableEntity)
        return (request, {}, HttpResponse)
    else:
        return (request, {u'reason': u"You are not authenticated"},
                HttpUnauthorized)

def reject(request, receiver_id):
    sender = request.user
    receiver = User.objects.get(id=receiver_id)
    if request.user and request.user.is_authenticated():
        inverted = False
        try:
            link = Link.objects.get(sender=sender, receiver=receiver)
            if link.sender_status == 'NEW':
                link.sender_status = 'IGN'
            elif link.sender_status == 'PEN':
                link.sender_status = 'REJ'
            else:
                link.sender_status = 'BLO'
            link.save()
        except Link.DoesNotExist:
            try:
                link = Link.objects.get(sender=receiver, receiver=sender)
                inverted = True
                if link.receiver_status == 'NEW':
                    link.receiver_status = 'IGN'
                elif link.receiver_status == 'PEN':
                    link.receiver_status = 'REJ'
                else:
                    link.receiver_status = 'BLO'
                link.save()
            except Link.DoesNotExist:
                return (request, {u'reason': u'Link not found'},
                        HttpForbidden)
            except:
                return (request, {u'reason': u'Link found but error'},
                        HttpForbidden)
        except:
            return (request, {u'reason': u'Unexpected'},
                    HttpForbidden)
        return (request, {}, HttpResponse)
    else:
        return (request, {u'reason': u"You are not authenticated"},
                HttpUnauthorized)
