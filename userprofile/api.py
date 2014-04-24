from tastypie import fields
from tastypie.http import HttpUnauthorized, HttpForbidden, HttpCreated
from tastypie.utils import trailing_slash
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import SessionAuthentication

from django.conf.urls import url
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

class UserResource(ModelResource):
    class Meta:
        resource_name = 'user'
        queryset = User.objects.all()
        list_allowed_methods = []
        detail_allowed_methods = ['get', 'put', 'delete']
        excludes = ['email', 'password', 'is_superuser', 'is_staff']
        filtering = {
                    'username': ALL,
                    }
        authorization  = DjangoAuthorization()
        authentication = SessionAuthentication()

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/logout%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('logout'), name='api_logout'),
        ]

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, { 'success': True })
        else:
            return self.create_response(request, { 'success': False }, 
                                                 HttpUnauthorized)

class AuthResource(ModelResource):
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
        data = self.deserialize(request, request.body, 
                                format=request.META.get('CONTENT_TYPE', 
                                                        'application/json'))
        username = data.get('username', '')
        password = data.get('password', '')
        user = User.objects.create_user(username=username, 
                                        email=username, 
                                        password=password)
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                #user = authenticate(username=username, password=password)
                login(request, user)
                return self.create_response(request, {'success': True}, 
                                            HttpCreated)
            else:
                return self.create_response(request, {'success': False,
                                                      'reason': 'disabled'},
                                            HttpForbidden )
        else:
            return self.create_response(request, {'success': False,
                                                  'reason': 'incorrect'},
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
                return self.create_response(request, {'success': True})
            else:
                return self.create_response(request, {'success': False,
                                                      'reason': 'disabled'},
                                                     HttpForbidden )
        else:
            return self.create_response(request, {'success': False,
                                                  'reason': 'incorrect'},
                                                 HttpUnauthorized )
