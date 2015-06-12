from tastypie import fields
from tastypie.http import (HttpUnauthorized, HttpForbidden,
                           HttpCreated, HttpBadRequest)
from tastypie.utils import trailing_slash
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import ApiKeyAuthentication

from django.db.models import Q
from django.conf.urls import url
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from push_notifications.models import APNSDevice, GCMDevice

from doc import authdoc
from link.models import Link
from userprofile.models import UserProfile, UserPosition

import apidoc as doc

class PositionResource(ModelResource):
    #last = fields.CharField('last', null=True)
    class Meta:
        resource_name = 'userposition'
        queryset = UserPosition.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'put']
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
    
class UserResource(ModelResource):
    """
    An API for accessing a User, requires authentication
    """
    #profile = fields.ToOneField(ProfileResource, 
                                #'userprofile', full=True)
                               ##'userprofile', related_name='user', full=True)
    class Meta:
        resource_name = 'user'
        queryset = User.objects.all()
        list_allowed_methods = []
        detail_allowed_methods = ['get', 'put']
        excludes = ['password', 'is_superuser', 'is_staff']
        filtering = {
                    'username': ALL,
                    }
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        # for the doc:
        extra_actions = [ 
            {   "name": u"logout",
                "http_method": u"GET",
                "resource_type": u"list",
                "summary": doc.UserResourceLogout,
                "fields": authdoc
            } ,
            {   "name": u"check_auth",
                "http_method": u"GET",
                "resource_type": u"list",
                "summary": doc.UserResourceCheckAuth,
                "fields": authdoc
            } ,
            {   "name": u"gcm",
                "http_method": u"POST",
                "resource_type": "list",
                "summary": doc.UserResourceGCM,
                "fields": dict( authdoc.items() + doc.UserResourceGCMfields.items() )
            } ,
        ]

    def get_object_list(self, request):
        return User.objects.filter(id=request.user.id)

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/logout%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('logout'), name='api_logout'),
            url(r'^(?P<resource_name>%s)/check_auth%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('check_auth'), name='api_check_auth'),
            url(r'^(?P<resource_name>%s)/gcm%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('gcm'), name='api_gcm'),
        ]

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, { 'success': True })
        else:
            return self.create_response(request, { 'success': False }, 
                                                 HttpUnauthorized)

    def check_auth(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        #
        #from service.notification import send_notification
        #send_notification([request.user.id], 'checking geoevent auth')
        #
        if request.user and request.user.is_authenticated():
            return self.create_response( request,
                              { 'success'   : True,
                                'userid'    : request.user.id } )
        else:
            return self.create_response(request, { 'success': False }, 
                                                 HttpUnauthorized)

    def gcm(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        if request.user and request.user.is_authenticated():
            try:
                data = self.deserialize(
                            request, request.body, 
                            format=request.META.get(
                            'CONTENT_TYPE', 'application/json'))
            except:
                return self.create_response(
                            request,
                            {u'reason': u'cannot deserialize data'},
                            HttpBadRequest )
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
                return self.create_response(request, { 'success': True })
            except:
                return self.create_response(
                            request,
                            {u'reason': u'cannot create this gcm'},
                            HttpBadRequest )
        else:
            return self.create_response(request, { 'success': False }, 
                                                 HttpUnauthorized)

class ProfileResource(ModelResource):
    ###WARNING to be finshed, must restrict to the auth user
    user = fields.ToOneField(UserResource, 'user', full=True)
    name = fields.CharField(attribute='name', readonly=True)
    class Meta:
        resource_name = 'userprofile'
        queryset = UserProfile.objects.all()
        #allowed_methods = []
        list_allowed_methods = []
        detail_allowed_methods = ['get', 'put']
        filtering = {'user' : ALL_WITH_RELATIONS}
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

class FriendResource(ModelResource):
    ###WARNING to be finshed, must restrict to the auth user
    user = fields.ToOneField(UserResource, 'user', full=True)
    name = fields.CharField(attribute='name', readonly=True)
    class Meta:
        resource_name = 'friend'
        queryset = UserProfile.objects.all()
        #allowed_methods = []
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        #filtering = {'user' : ALL_WITH_RELATIONS}
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    def get_object_list(self, request):
        userprofile = request.user.userprofile
        links = userprofile.link_as_sender.filter(sender_status='ACC',
                                                  receiver_status='ACC')
        receivers = UserProfile.objects.filter(
                                    user_id__in=links.values('receiver_id'))
        links = userprofile.link_as_receiver.filter(sender_status='ACC',
                                                    receiver_status='ACC')
        senders = UserProfile.objects.filter(
                                    user_id__in=links.values('sender_id'))
        return senders | receivers

class PendingResource(ModelResource):
    ###WARNING to be finshed, must restrict to the auth user
    user = fields.ToOneField(UserResource, 'user', full=True)
    name = fields.CharField(attribute='name', readonly=True)
    class Meta:
        resource_name = 'pending'
        queryset = UserProfile.objects.all()
        #allowed_methods = []
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        #filtering = {'user' : ALL_WITH_RELATIONS}
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    def get_object_list(self, request):
        userprofile = request.user.userprofile
        links = userprofile.link_as_receiver.filter(receiver_status='PEN')
        pending = UserProfile.objects.filter(
                                    user_id__in=links.values('sender_id'))
        return pending

class AuthResource(ModelResource):
    """
    An API for loging in / registering, no authentication required
    """
    class Meta:
        queryset = User.objects.all()
        fields = ['first_name', 'last_name', 'email']
        allowed_methods = []
        resource_name = 'auth'
        # for the doc:
        extra_actions = [ 
            {"name": u"register",
             "http_method": u"POST",
             "resource_type": u"list",
             "summary": doc.AuthResourceRegister,
             "fields": doc.AuthResourceRegisterFields
            } ,
            {"name": "login",
             "http_method": "POST",
             "resource_type": "list",
             "summary": doc.AuthResourceLogin,
             "fields": doc.AuthResourceLoginFields
            } ,
        ]

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/register%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('register'), name="api_register"),
            url(r"^(?P<resource_name>%s)/login%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('login'), name="api_login"),
        ]

    def register(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        try:
            data = self.deserialize(request, request.body, 
                                    format=request.META.get(
                                    'CONTENT_TYPE', 'application/json'))
        except:
            return self.create_response(request,
                                        {u'reason': u'cannot deserialize data'},
                                        HttpBadRequest )
        username = data.get('username', '')
        password = data.get('password', '')
        name     = data.get('name', '')
        email    = data.get('email', '')
        try:
            user = User.objects.create_user(username=username, 
                                            email=email, 
                                            password=password,
                                            first_name=name)
        except:
            return self.create_response(request,
                                        {u'reason': u'cannot create this user'},
                                        HttpBadRequest )
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return self.create_response(request,
                               {'api_key'   : user.api_key.key,
                                'userid'    : request.user.id},
                                HttpCreated )
            else:
                return self.create_response(request,
                                            {u'reason': u'disabled'},
                                            HttpForbidden )
        else:
            return self.create_response(request,
                                        {u'reason': u'incorrect'},
                                        HttpUnauthorized )

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        try:
            data = self.deserialize(request, request.body, 
                                    format=request.META.get(
                                    'CONTENT_TYPE', 'application/json'))
        except:
            return self.create_response(request,
                                        {'reason': u'cannot deserialize data'},
                                        HttpBadRequest )
        username = data.get('username', '')
        password = data.get('password', '')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return self.create_response(request,
                               {'api_key'   : user.api_key.key,
                                'userid'    : request.user.id})
            else:
                return self.create_response(request,
                                            {u'reason': u'disabled'},
                                            HttpForbidden )
        else:
            return self.create_response(request,
                                        {u'reason': u'incorrect'},
                                        HttpUnauthorized )
