from base64 import b64decode

from link.models import Link
from service.utils import get_clean_number

from django.http import HttpResponse
from django.contrib import auth
from django.core.files.base import ContentFile
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.auth.models import User
from django.utils.timezone import now as datetime_now

from push_notifications.models import APNSDevice, GCMDevice
from tastypie.http import (HttpUnauthorized, HttpForbidden,
                           HttpCreated, HttpBadRequest)
from tastypie.models import ApiKey

from allauth.account.forms import SignupForm, LoginForm, ResetPasswordForm
from allauth.account.utils import complete_signup
from allauth.account import app_settings

def setlast(request, data):
    if request.user and request.user.is_authenticated():
        try:
            last = data.get('last').strip()
        except:
            return (request, {u'reason': "empty"}, HttpBadRequest)
        if last:
            pnt = GEOSGeometry(last)
            request.user.userposition.last = last
            request.user.userposition.save()
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
        try:
            email = data.get('email').strip()
            if email:
                request.user.email = email
        except:
            pass
        request.user.save()
        try:
            number = data.get('number').strip()
            if number:
                num = get_clean_number(number)
                if num is not None:
                    request.user.userprofile.phone_number = num
            else: # user can set empty number
                request.user.userprofile.phone_number = ''
        except:
            pass
        try:
            gender = data.get('gender').strip()
            if gender in ['MA', 'FE']:
                request.user.userprofile.gender = gender
        except:
            pass
        request.user.userprofile.save()
        return (request, {}, HttpResponse)
    else:
        return (request, {u'reason': u"You are not authenticated"},
                HttpUnauthorized)

def setpicture(request, data):
    if request.user and request.user.is_authenticated():
        b64_text = data.get('file', '')
        filename = data.get('name', '')
        image_data = b64decode(b64_text)
        request.user.userprofile.image = ContentFile(image_data, filename)
        request.user.userprofile.save()
        return (request, {}, HttpResponse)
    else:
        return (request, {u'reason': u"You are not authenticated"},
                HttpUnauthorized)

#def register(request, data):
    #reason = "Username is required"
    #try:
        #username = data.get('username').lower().strip()
        #if not username:
            #return (request, {u'reason': reason, u'code': '10'},
                    #HttpBadRequest)
    #except:
        #return (request, {u'reason': reason, u'code': '10'}, HttpBadRequest)
    #reason = "Password is required"
    #try:
        #password = data.get('password', '').strip()
        #if not password:
            #return (request, {u'reason': reason, u'code': '10'},
                    #HttpBadRequest)
    #except:
        #return (request, {u'reason': reason, u'code': '10'}, HttpBadRequest)
    #try:
        #user = User.objects.get(username=username)
        #return (request, {u'reason': u'user already exists',
                            #u'code': '200'}, HttpBadRequest)
    #except User.DoesNotExist:
        #try:
            #user = User.objects.create_user(username=username, password=password)
        #except:
            #return (request, {u'reason': u'user creation failed',
                              #u'code': '300'}, HttpBadRequest)
    #user = auth.authenticate(username=username, password=password)
    #if user:
        #if user.is_active:
            #auth.login(request, user)
            ##user.userprofile.phone_number = number
            ##user.userprofile.save()
            #return (request, {'api_key' : user.api_key.key,
                              #'userid'  : request.user.id,
                              #'username': user.username,
                              #'code'    : '0'}, HttpCreated)
        #else:
            #return (request, {u'reason': u'inactive user',
                              #u'code': '150'}, HttpForbidden)
    #else:
        #return (request, {u'reason': u'unable to authenticate',
                          #u'code': '400'}, HttpUnauthorized)

def register_by_email(request, data):
    if 'email' not in data:
        return (request, {u'reason': "'email' required", u'code': '10'},
                HttpBadRequest)
    if 'password' not in data:
        return (request, {u'reason': "password required", u'code': '20'},
                HttpBadRequest)
    data['password1'] = data['password']
    data['password2'] = data['password']
    try:
        form = SignupForm(data)
    except:
        return (request, {u'reason': u'user creation failed',
                            u'code': '300'}, HttpBadRequest)
    if form.is_valid():
        user = form.save(request)
        complete_signup(request, user,
                        app_settings.EMAIL_VERIFICATION, None)
        return (request, {'api_key' : user.api_key.key,
                          'userid'  : request.user.id,
                          'username': user.username,
                          'code'    : '0'}, HttpCreated)
    else:
        return (request, {u'reason': form.errors,
                            u'code': '300'}, HttpBadRequest)


#def login(request, data):
    #username = data.get('username', '').lower().strip()
    #password = data.get('password', '').strip()
    #user = auth.authenticate(username=username, password=password)
    #if user:
        #if user.is_active:
            #auth.login(request, user)
            #return (request, {'api_key' : user.api_key.key,
                              #'userid'  : request.user.id,
                              #'username': user.username}, HttpResponse)
        #else:
            #return (request, {u'reason': u'disabled'}, HttpForbidden)
    #else:
        #return (request, {u'reason': u'incorrect'}, HttpUnauthorized)

def login_by_email(request, data):
    if 'login' not in data:
        return (request, {u'reason': "'login' missing"}, HttpBadRequest)
    if 'password' not in data:
        return (request, {u'reason': "'password' missing"}, HttpBadRequest)
    form = LoginForm(data)
    if form.is_valid():
        form.login(request)
        return (request, {'api_key' : form.user.api_key.key,
                          'userid'  : form.user.id,
                          'username': form.user.username}, HttpResponse)
    else:
        return (request, {u'reason': form.errors}, HttpUnauthorized)

def reset_password(request, data):
    form = ResetPasswordForm(data)
    if form.is_valid():
        form.save(request)
        return (request, {}, HttpResponse)
    else:
        return (request, {u'reason': form.errors}, HttpBadRequest)

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

def check_auth(request):
    #
    #from service.notification import send_notification
    #send_notification([request.user.id], 'checking geoevent auth')
    #
    if request.user and request.user.is_authenticated():
        return (request, {'userid':request.user.id },
                    HttpResponse)
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

def change_link(request, sender_id, receiver_id,
                new_sender_status=None, new_receiver_status=None):
    """ Generic function for changing link status
    """
    if request.user and request.user.is_authenticated():
        inverted = False
        try:
            link = Link.objects.get(sender=sender_id,
                                    receiver=receiver_id)
            if new_sender_status:
                link.sender_status = new_sender_status
            if new_receiver_status:
                link.receiver_status = new_receiver_status
        except Link.DoesNotExist:
            try:
                link = Link.objects.get(sender=receiver_id,
                                        receiver=sender_id)
                if new_sender_status:
                    link.receiver_status = new_sender_status
                if new_receiver_status:
                    link.sender_status = new_receiver_status
                inverted = True
            except Link.DoesNotExist:
                return (request, {u'reason': u'Link not found'},
                        HttpForbidden, None, None)
            except:
                return (request, {u'reason': u'Unexpected'},
                        HttpForbidden, None, None)
        link.save()
        return (request, {}, HttpResponse, link, inverted)
    else:
        return (request, {u'reason': u"You are not authenticated"},
                HttpUnauthorized, None, None)
