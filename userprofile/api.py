from tastypie import fields
from tastypie.http import HttpUnauthorized, HttpForbidden, HttpCreated
from tastypie.utils import trailing_slash
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import SessionAuthentication

from django.conf.urls import url
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
#from django.contrib.auth.hashers import make_password


class UserResource(ModelResource):
    class Meta:
        resource_name = 'user'
        queryset = User.objects.all()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        excludes = ['email', 'password', 'is_superuser', 'is_staff']
        filtering = {
                    'username': ALL,
                    }
        authorization  = DjangoAuthorization()
        authentication = SessionAuthentication()

class AuthResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        fields = ['first_name', 'last_name', 'email']
        allowed_methods = ['get', 'post']
        resource_name = 'auth'

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/register%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('register'), name="api_register"),
            url(r"^(?P<resource_name>%s)/login%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('login'), name="api_login"),
            url(r'^(?P<resource_name>%s)/logout%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('logout'), name='api_logout'),
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

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, { 'success': True })
        else:
            return self.create_response(request, { 'success': False }, 
                                                 HttpUnauthorized)

#class SigninResource(ModelResource):
    #class Meta:
        #resource_name = 'signin'
        #queryset = User.objects.all()
        #list_allowed_methods = ['post']
        #detail_allowed_methods = []
        #fields = ['username', 'password']
        #authorization  = Authorization()
        
    #def obj_create(self, bundle, **kwargs):
        ##return super(SignupResource, self).obj_create(bundle)
        #user = authenticate(username=bundle.data['username'],
                            #password=bundle.data['password'])
        #if user is not None:
            #if user.is_active:
                #return login(bundle.request, user)
                ##return self.create_response(bundle.request, 
                                            ##{'success': True})
        #raise BadRequest('username/password incorrect')
#class SignupResource(ModelResource):
    #class Meta:
        #resource_name = 'signup'
        #queryset = User.objects.all()
        #list_allowed_methods = ['post']
        #detail_allowed_methods = []
        #fields = ['username', 'password', 'first_name']
        #authorization  = Authorization()

    #def obj_create(self, bundle, **kwargs):
        #hashed_passwd = make_password(bundle.data['password'])
        #bundle.data['password'] = hashed_passwd
        #return super(SignupResource, self).obj_create(bundle)
