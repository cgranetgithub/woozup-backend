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

from link.models import Link
from userprofile.models import UserProfile

class ProfileResource(ModelResource):
    name = fields.CharField(attribute='name', readonly=True)
    allowed_methods = []
    class Meta:
        resource_name = 'profile'
        queryset = UserProfile.objects.all()
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
    
class UserResource(ModelResource):
    """
    An API for getting a user, requires authentication
    """
    profile = fields.ToOneField(ProfileResource, 
                                attribute='userprofile', full=True)
    class Meta:
        resource_name = 'user'
        queryset = User.objects.all()
        list_allowed_methods = []
        detail_allowed_methods = ['get', 'patch', 'delete']
        excludes = ['password', 'is_superuser', 'is_staff']
        filtering = {
                    'username': ALL,
                    }
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

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
     #WARNING must restrict to the use himself

    def check_auth(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        #
        from service.notification import send_notification
        send_notification([request.user.id], {'geoevent message':'checking geoevent auth'})
        #
        if request.user and request.user.is_authenticated():
            return self.create_response(request, { 'success': True })
        else:
            return self.create_response(request, { 'success': False }, 
                                                 HttpUnauthorized)

    def gcm(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        if request.user and request.user.is_authenticated():
            try:
                data = self.deserialize(request, request.body, 
                                        format=request.META.get(
                                            'CONTENT_TYPE', 'application/json'))
            except:
                return self.create_response(request,
                                            {'reason': 'cannot deserialize data'},
                                            HttpBadRequest )
            name = data.get('name', '')
            device_id = data.get('device_id', '')
            registration_id = data.get('registration_id', '')
            try:
                GCMDevice.objects.create(user=request.user,
                                         name=name, 
                                         device_id=device_id, 
                                         registration_id=registration_id)
                return self.create_response(request, { 'success': True })
            except:
                return self.create_response(request,
                                            {'reason': 'cannot create this gcm'},
                                            HttpBadRequest )
        else:
            return self.create_response(request, { 'success': False }, 
                                                 HttpUnauthorized)

class AuthResource(ModelResource):
    """
    An API for loging in / registering, no authentication required
    """
    class Meta:
        queryset = User.objects.all()
        fields = ['first_name', 'last_name', 'email']
        allowed_methods = []
        resource_name = 'auth'

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
                                        {'reason': 'cannot deserialize data'},
                                        HttpBadRequest )
        username = data.get('username', '')
        password = data.get('password', '')
        try:
            user = User.objects.create_user(username=username, 
                                            email=username, 
                                            password=password)
        except:
            return self.create_response(request,
                                        {'reason': 'cannot create this user'},
                                        HttpBadRequest )
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                #user = authenticate(username=username, password=password)
                login(request, user)
                return self.create_response(request,
                                            {'api_key': user.api_key.key}, 
                                            HttpCreated )
            else:
                return self.create_response(request,
                                            {'reason': 'disabled'},
                                            HttpForbidden )
        else:
            return self.create_response(request,
                                        {'reason': 'incorrect'},
                                        HttpUnauthorized )

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        data = self.deserialize(request, request.body, 
                                format=request.META.get('CONTENT_TYPE', 
                                                        'application/json'))
        username = data.get('username', '')
        password = data.get('password', '')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return self.create_response(request,
                                            {'api_key': user.api_key.key} )
            else:
                return self.create_response(request,
                                            {'reason': 'disabled'},
                                            HttpForbidden )
        else:
            return self.create_response(request,
                                        {'reason': 'incorrect'},
                                        HttpUnauthorized )
