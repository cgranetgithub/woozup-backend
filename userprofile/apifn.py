from base64 import b64decode

from link import push
from link.models import Link

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

def setlast(request, data):
    if request.user and request.user.is_authenticated():
        last = data.get('last', '')
        pnt = GEOSGeometry(last)
        request.user.userposition.last = last
        request.user.userposition.save()
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

def register(request, data):
    username = data.get('username', '').lower().strip()
    password = data.get('password', '')
    name     = data.get('name', '')
    email    = data.get('email', '').lower().strip()
    number   = data.get('number', '')
    # check data
    reason = None
    if not username:
        reason = "Username is required"
    if not password:
        reason = "Password is required"
    if not name:
        reason = "Name is required"
    if reason:
        return (request, {u'reason': reason, u'code': '10'}, HttpBadRequest)
    try:
        user = User.objects.get(username=username)
        #do no return, if user pass correct username+passwd, we can login
    except User.DoesNotExist:
        try:
            user = User.objects.create_user(username=username, email=email, 
                                            password=password, first_name=name)
        except:
            return (request, {u'reason': u'user creation failed',
                              u'code': '300'}, HttpBadRequest)
    user = auth.authenticate(username=username, password=password)
    if user:
        if user.is_active:
            auth.login(request, user)
            user.userprofile.phone_number = number
            user.userprofile.save()
            return (request, {'api_key' : user.api_key.key,
                              'userid'  : request.user.id,
                              'username': user.username,
                              'code'    : '0'}, HttpCreated)
        else:
            return (request, {u'reason': u'inactive user',
                              u'code': '150'}, HttpForbidden)
    else:
        return (request, {u'reason': u'wrong login/password',
                          u'code': '200'}, HttpUnauthorized)

def login(request, data):
    username = data.get('username', '').lower().strip()
    password = data.get('password', '')
    user = auth.authenticate(username=username, password=password)
    if user:
        if user.is_active:
            auth.login(request, user)
            return (request, {'api_key' : user.api_key.key,
                              'userid'  : request.user.id,
                              'username': user.username}, HttpResponse)
        else:
            return (request, {u'reason': u'disabled'}, HttpForbidden)
    else:
        return (request, {u'reason': u'incorrect'}, HttpUnauthorized)


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

def gcm(request, data):
    if request.user and request.user.is_authenticated():
        name = data.get('name', '')
        device_id = data.get('device_id', '')
        if isinstance(device_id, unicode):
            device_id = str(device_id)
        registration_id = data.get('registration_id', '')
        try:
            (gcmd, created) = GCMDevice.objects.get_or_create(
                                                    user=request.user,
                                                    #name=name, 
                                                    device_id=device_id)
            gcmd.registration_id = registration_id
            gcmd.device_id = device_id
            gcmd.name = name
            gcmd.save()
            return (request, {'userid':request.user.id }, HttpResponse)
        except:
            return (request, {u'reason': u'cannot create this gcm'},
                        HttpBadRequest)
    else:
        return (request, {u'reason': u"You are not authenticated"},
                    HttpUnauthorized)

def change_link(request, sender_id, receiver_id,
                new_sender_status=None, new_receiver_status=None):
    """ Generic function for changing link status
    """
    if request.user and request.user.is_authenticated():
        try:
            link = Link.objects.get(sender=sender_id,
                                    receiver=receiver_id)
            if new_sender_status:
                link.sender_status = new_sender_status
            if new_receiver_status:
                link.receiver_status = new_receiver_status
            link.save()
            push.link_requested(link)
            return (request, {}, HttpResponse)
        except Link.DoesNotExist:
            return (request, {u'reason': u'Link not found'},
                        HttpForbidden)
        except:
            return (request, {u'reason': u'Unexpected'}, HttpForbidden)
    else:
        return (request, {u'reason': u"You are not authenticated"},
                    HttpUnauthorized)
