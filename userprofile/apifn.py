# -*- coding: utf-8 -*-
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

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

#from allauth.account.forms import SignupForm, LoginForm, ResetPasswordForm
#from allauth.account.utils import complete_signup
#from allauth.account import app_settings

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
        b64_text = data.get('file', '')
        filename = data.get('name', '')
        image_data = b64decode(b64_text)
        request.user.profile.image = ContentFile(image_data, filename)
        request.user.profile.save()
        return (request, {}, HttpResponse)
    else:
        return (request, {u'reason': u"You are not authenticated"},
                HttpUnauthorized)

def register(request, data):
    reason = "Username is required"
    try:
        username = data.get('username').lower().strip()
        if not username:
            return (request, {u'reason': reason, u'code': '10'},
                    HttpBadRequest)
    except:
        return (request, {u'reason': reason, u'code': '10'}, HttpBadRequest)
    reason = "Password is required"
    try:
        password = data.get('password', '').strip()
        if not password:
            return (request, {u'reason': reason, u'code': '11'},
                    HttpBadRequest)
    except:
        return (request, {u'reason': reason, u'code': '12'}, HttpBadRequest)
    reason = "Number is required"
    try:
        phone_number = data.get('number', '').strip()
        if not phone_number:
            return (request, {u'reason': reason, u'code': '13'},
                    HttpBadRequest)
    except:
        return (request, {u'reason': reason, u'code': '13'}, HttpBadRequest)
    reason = "Verif code is required"
    try:
        code = data.get('code', '')
        if type(code) is not int:
            try:
                code = code.strip()
                code = int(code)
            except:
                return (request, {u'reason': u'code is not a number',
                                  u'code': '15'}, HttpBadRequest)
        if not code:
            return (request, {u'reason': reason, u'code': '16'},
                    HttpBadRequest)
    except:
        return (request, {u'reason': reason, u'code': '17'}, HttpBadRequest)
    # find the number (must exist)
    try:
        number = Number.objects.get(phone_number=phone_number)
    except:
        return (request, {u'reason': u'number %s not found'%number,
                          u'code': '18'}, HttpBadRequest)
    # check if user already exists, otherwise create it
    try:
        user = User.objects.get(username=username)
        return (request, {u'reason': u'user already exists',
                            u'code': '200'}, HttpBadRequest)
    except User.DoesNotExist:
        try:
            user = User.objects.create_user(username=username, password=password)
        except:
            return (request, {u'reason': u'user creation failed',
                              u'code': '300'}, HttpBadRequest)
    # make user <--> number association
    validated = number.validate(user, phone_number, code)
    if not validated:
        return (request, {u'reason': u'user/number/code do not match',
                          u'code': '19'}, HttpBadRequest)
    # finish authentication
    user = auth.authenticate(username=username, password=password)
    if user:
        if user.is_active:
            auth.login(request, user)
            return (request, {'api_key' : user.api_key.key,
                              'userid'  : user.id,
                              'username': user.username,
                              'code'    : '0'}, HttpCreated)
        else:
            return (request, {u'reason': u'inactive user',
                              u'code': '150'}, HttpForbidden)
    else:
        return (request, {u'reason': u'unable to authenticate',
                          u'code': '400'}, HttpUnauthorized)

def login(request, data):
    username = data.get('username', '').lower().strip()
    password = data.get('password', '').strip()
    user = auth.authenticate(username=username, password=password)
    if user:
        if user.is_active:
            auth.login(request, user)
            return (request, {'api_key' : user.api_key.key,
                              'userid'  : user.id,
                              'username': user.username}, HttpResponse)
        else:
            return (request, {u'reason': u'disabled'}, HttpForbidden)
    else:
        return (request, {u'reason': u'incorrect'}, HttpUnauthorized)

def get_code(request, data):
    phone_number = data.get('phone_number', '').lower().strip()
    nb = get_clean_number(phone_number)
    if nb:
        (number, created) = Number.objects.get_or_create(phone_number=nb)
        number.get_code()
        return (request, {}, HttpResponse)
    else:
        return (request, {u'reason': u'not a number valid number'},
                HttpBadRequest)

def verif_code(request, data):
    phone_number = data.get('phone_number', '').lower().strip()
    code = data.get('code', '')
    if type(code) is not int:
        try:
            code = code.strip()
            code = int(code)
        except:
            return (request, {u'reason': u'code is not a number'}, HttpBadRequest)
    try:
        number = Number.objects.get(phone_number=phone_number)
    except Number.DoesNotExist:
        return (request, {u'reason': u'unknown phone_number'}, HttpBadRequest)
    if number.verif_code(code):
        return (request, {}, HttpResponse)
    else:
        return (request, {u'reason': u'incorrect code'}, HttpUnprocessableEntity)

def is_registered(request, data):
    phone_number = data.get('phone_number', '').lower().strip()
    try:
        number = Number.objects.get(phone_number=phone_number)
    except Number.DoesNotExist:
        return (request, {u'reason': u'unknown phone_number'}, HttpBadRequest)
    if number.validated and number.user:
        return (request, {'method':'password'}, HttpResponse)
    else:
        return (request, {u'reason': u'not registered'}, HttpForbidden)

def reset_password(request, data):
    phone_number = data.get('phone_number', '').lower().strip()
    code = data.get('code', '')
    password = data.get('password', '')
    if type(code) is not int:
        try:
            code = code.strip()
            code = int(code)
        except:
            return (request, {u'reason': u'code is not a number'}, HttpBadRequest)
    try:
        number = Number.objects.get(phone_number=phone_number)
    except Number.DoesNotExist:
        return (request, {u'reason': u'unknown phone_number'}, HttpBadRequest)
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
            return (request, {u'reason': "empty device_id"}, HttpBadRequest)
        if not device_id:
            return (request, {u'reason': "empty device_id"}, HttpBadRequest)
        try:
            platform = data.get('platform').strip()
        except:
            return (request, {u'reason': "empty platform"}, HttpBadRequest)
        try:
            registration_id = data.get('registration_id').strip()
            if not registration_id:
                return (request, {u'reason': "empty registration_id"}, HttpBadRequest)
        except:
            return (request, {u'reason': "empty platform"}, HttpBadRequest)
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
                logger.error(u'not found => created => issue')
                return (request, {u'reason': u'not found => created => issue'},
                        HttpUnprocessableEntity)
        except:
            logger.error(u'found => issue')
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
