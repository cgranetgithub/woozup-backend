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

class ProfileResource(ModelResource):
    #user = fields.ToOneField('userprofile.api.UserResource', attribute='user',
                             #related_name='userprofile')
    #allowed_methods = ['get', 'put']
    name = fields.CharField(attribute='name', readonly=True)
    allowed_methods = []
    class Meta:
        resource_name = 'profile'
        queryset = UserProfile.objects.all()
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
    
class PositionResource(ModelResource):
    last = fields.CharField(attribute='last')
    allowed_methods = []
    class Meta:
        resource_name = 'position'
        queryset = UserPosition.objects.all()
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
    
class UserResource(ModelResource):
    """
    An API for getting a user, requires authentication
    """
    profile = fields.ToOneField(ProfileResource, 
                                attribute='userprofile', full=True)
                               #'userprofile', related_name='user', full=True)
    position = fields.ToOneField(PositionResource, 
                                attribute='userposition', full=True)
                                #'userposition', related_name='user', full=True)
    class Meta:
        resource_name = 'user'
        queryset = User.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'put']
        excludes = ['password', 'is_superuser', 'is_staff']
        filtering = {
                    'username': ALL,
                    }
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        # for the doc:
        extra_actions = [ 
            {   "name": "logout",
                "http_method": "GET",
                "resource_type": "list",
                "summary": """[Custom] Logout the user. 
This API requires the api_key user authentication.""",
                "fields": authdoc
            } ,
            {   "name": "check_auth",
                "http_method": "GET",
                "resource_type": "list",
                "summary": """[Custom] Check the user authentication status.
This API requires the api_key user authentication.""",
                "fields": authdoc
            } ,
            {   "name": "gcm",
                "http_method": "POST",
                "resource_type": "list",
                "summary": """[Custom] Update the registration_id of the 
current user's device for the Google Cloud Messaging for Android.
This API requires the api_key user authentication.""",
                "fields": dict( authdoc.items() + 
                               { "name": {
                                    "type": "string",
                                    "required": True,
                                    "description": "Device name" },
                                "device_id": {
                                    "type": "string",
                                    "required": True,
                                    "description": "Device unique ID" },
                                "registration_id": {
                                    "type": "string",
                                    "required": True,
                                    "description": "Registration ID" },
                               }.items() )
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
        from service.notification import send_notification
        send_notification([request.user.id], 'checking geoevent auth')
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
                data = self.deserialize(
                            request, request.body, 
                            format=request.META.get(
                            'CONTENT_TYPE', 'application/json'))
            except:
                return self.create_response(
                            request,
                            {'reason': 'cannot deserialize data'},
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
        # for the doc:
        extra_actions = [ 
            {   "name": "register",
                "http_method": "POST",
                "resource_type": "list",
                "summary": """[Custom] Create a new user in the backend, 
authenticate and login the user automatically. Return its api_key.""",
                "fields": { "username": {
                                "type": "string",
                                "required": True,
                                "description": "username passed as a data" },
                            "password": {
                                "type": "string",
                                "required": True,
                                "description": "password passed as a data" }, }
            } ,
            {   "name": "login",
                "http_method": "POST",
                "resource_type": "list",
                "summary": """[Custom] Authenticate and login the user automatically. 
Return its api_key.""",
                "fields": { "username": {
                                "type": "string",
                                "required": True,
                                "description": "username passed as a data" },
                            "password": {
                                "type": "string",
                                "required": True,
                                "description": "password passed as a data" }, }
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
