# -*- coding: utf-8 -*-
import logging

from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import BadRequest
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import ApiKeyAuthentication
from tastypie.http import (HttpUnauthorized, HttpForbidden,
                           HttpCreated, HttpBadRequest,
                           HttpUnprocessableEntity)

from django.http import HttpResponse
from django.conf.urls import url
from django.contrib.auth import get_user_model

import apidoc as doc
from doc import authdoc
from userprofile.models import Profile, Position
from event.models import Event
from userprofile.utils import get_friends, get_suggestions
from service.b64field import Base64FileField
from .models import Number
#from link import push

from allauth.socialaccount import providers
from allauth.socialaccount.models import SocialLogin, SocialToken, SocialApp
from allauth.socialaccount.providers.facebook.views import fb_complete_login
from allauth.socialaccount.helpers import complete_social_login
from allauth.account.utils import perform_login

import apifn

class PositionResource(ModelResource):
    #last = fields.CharField('last', null=True)
    class Meta:
        resource_name = 'userposition'
        queryset = Position.objects.all()
        list_allowed_methods = []
        detail_allowed_methods = ['get', 'put']
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    def get_object_list(self, request):
        return Position.objects.filter(user=request.user)

 ### WARNING need to restrict to user

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/setlast%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('setlast'), name='api_setlast'),
        ]

    def setlast(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        try:
            data = self.deserialize(request, request.body,
                                    format=request.META.get(
                                    'CONTENT_TYPE', 'application/json'))
        except:
            logging.error(u'cannot deserialize data')
            return self.create_response(request,
                                        {u'reason': u'cannot deserialize data'},
                                        HttpBadRequest )
        (req, result, status) = apifn.setlast(request, data)
        return self.create_response(req, result, status)

class UserResource(ModelResource):
    """
    An API for accessing a User, requires authentication
    """
    profile = fields.ToOneField('userprofile.api.ProfileResource',
                                'profile', full=True)
    name = fields.CharField(attribute='get_full_name', readonly=True)
    class Meta:
        resource_name = 'user'
        queryset = get_user_model().objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'put']
        excludes = ['password', 'is_superuser', 'is_staff']
        #includes = ['first_name', 'last_name']
        ordering = ['first_name']
        filtering = {'username': ALL, 'first_name': ALL}
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    def get_object_list(self, request):
        return get_user_model().objects.exclude(is_superuser=True)

    ### WARNING: must not restrict only to user because access is required
    ### when creating event with invitees => restrict to self+friends
    #def get_object_list(self, request):
        #return ( get_friends(user)
               #| User.objects.filter(id=request.user.id) )

### WARNING need to restrict to user

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/logout%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('logout'), name='api_logout'),
            url(r'^(?P<resource_name>%s)/check_auth%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('check_auth'), name='api_check_auth'),
            url(r'^(?P<resource_name>%s)/push_notif_reg%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('push_notif_reg'), name='api_push_notif_reg'),
            url(r"^(?P<resource_name>%s)/accept/(?P<user_id>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('accept'), name="api_accept"),
            url(r"^(?P<resource_name>%s)/reject/(?P<user_id>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('reject'), name="api_reject"),
            url(r"^(?P<resource_name>%s)/friendscount/(?P<user_id>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('friendscount'), name="api_friendscount"),
            url(r"^(?P<resource_name>%s)/eventscount/(?P<user_id>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('eventscount'), name="api_eventscount"),
            url(r'^(?P<resource_name>%s)/setprofile%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('setprofile'), name='api_setprofile'),
        ]

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        (req, result, status) = apifn.logout(request)
        return self.create_response(req, result, status)

    def check_auth(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        if request.user and request.user.is_authenticated():
            res = UserResource()
            user_bundle = res.build_bundle(request=request, obj=request.user)
            user_json = res.serialize(None, res.full_dehydrate(user_bundle),
                                      "application/json")
            return self.create_response(request, user_json, HttpResponse)
        else:
            return self.create_response(request,
                                    {u'reason': u"You are not authenticated"},
                                    HttpUnauthorized)

    def push_notif_reg(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        try:
            data = self.deserialize(request, request.body,
                                    format=request.META.get(
                                    'CONTENT_TYPE', 'application/json'))
        except:
            logging.error(u'cannot deserialize data: %s'%request.body)
            return self.create_response(request,
                                    {u'reason': u'cannot deserialize data'},
                                    HttpBadRequest )
        (req, result, status) = apifn.push_notif_reg(request, data)
        return self.create_response(req, result, status)

    def accept(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        (req, result, status) = apifn.accept(request, kwargs['user_id'])
        return self.create_response(req, result, status)

    def reject(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        (req, result, status) = apifn.reject(request, kwargs['user_id'])
        return self.create_response(req, result, status)

    def friendscount(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        user = get_user_model().objects.get(id=kwargs['user_id'])
        count = get_friends(user).count()
        return self.create_response(request, count, HttpResponse)

    def eventscount(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        user = get_user_model().objects.get(id=kwargs['user_id'])
        count = Event.objects.filter(owner=user).count()
        return self.create_response(request, count, HttpResponse)

    def setprofile(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        try:
            data = self.deserialize(request, request.body,
                                    format=request.META.get(
                                    'CONTENT_TYPE', 'application/json'))
        except:
            logging.error(u'cannot deserialize data')
            return self.create_response(request,
                                        {u'reason': u'cannot deserialize data'},
                                        HttpBadRequest )
        (req, result, status) = apifn.setprofile(request, data)
        return self.create_response(req, result, status)

class ProfileResource(ModelResource):
    email = fields.CharField(attribute='email', readonly=True)
    image_field = Base64FileField("image", null=True, blank=True)
    class Meta:
        resource_name = 'profile'
        queryset = Profile.objects.all()
        #list_allowed_methods = ['get']
        #ordering = ['first_name']
        #detail_allowed_methods = ['get']
        #filtering = {'user' : ALL_WITH_RELATIONS}
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    ### WARNING: must not restrict only to user because access is required
    ### when creating event with invitees => restrict to self+friends
    #def get_object_list(self, request):
        #return ( User.objects.get(request.user).get_friends()
               #| Profile.objects.filter(user=request.user) )

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/setpicture%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('setpicture'), name='api_setpicture'),
        ]

    def setpicture(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        try:
            data = self.deserialize(request, request.body,
                                    format=request.META.get(
                                    'CONTENT_TYPE', 'application/json'))
        except:
            logging.error(u'cannot deserialize data')
            return self.create_response(request,
                                        {u'reason': u'cannot deserialize data'},
                                        HttpBadRequest )
        (req, result, status) = apifn.setpicture(request, data)
        return self.create_response(req, result, status)

class SuggestionsResource(ModelResource):
    profile = fields.ToOneField('userprofile.api.ProfileResource',
                                'profile', full=True)
    name = fields.CharField(attribute='get_full_name', readonly=True)
    class Meta:
        resource_name = 'suggestions'
        queryset = get_user_model().objects.all()
        excludes = ['password', 'is_superuser', 'is_staff']
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        ordering = ['first_name']
        filtering = {'username': ALL, 'first_name': ALL}
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    def get_object_list(self, request):
        return get_suggestions(request.user).exclude(is_superuser=True)

class MyFriendsResource(ModelResource):
    profile = fields.ToOneField('userprofile.api.ProfileResource',
                                'profile', full=True)
    class Meta:
        resource_name = 'friends/mine'
        queryset = get_user_model().objects.all()
        excludes = ['password', 'is_superuser', 'is_staff']
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        ordering = ['first_name']
        filtering = {'username': ALL, 'first_name': ALL}
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    def get_object_list(self, request):
        return get_friends(request.user).exclude(is_superuser=True)

class PendingFriendsResource(ModelResource):
    profile = fields.ToOneField('userprofile.api.ProfileResource',
                                'profile', full=True)
    class Meta:
        resource_name = 'friends/pending'
        queryset = get_user_model().objects.all()
        excludes = ['password', 'is_superuser', 'is_staff']
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        ordering = ['first_name']
        filtering = {'username': ALL, 'first_name': ALL}
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    def get_object_list(self, request):
        user = request.user
        links = user.link_as_receiver.filter(receiver_status='PEN')
        senders = get_user_model().objects.filter(
                                    id__in=links.values('sender_id'))
        links = user.link_as_sender.filter(sender_status='PEN')
        receivers = get_user_model().objects.filter(
                                    id__in=links.values('receiver_id'))
        ret = senders | receivers
        return ret.exclude(is_superuser=True)

class NewFriendsResource(ModelResource):
    profile = fields.ToOneField('userprofile.api.ProfileResource',
                                'profile', full=True)
    class Meta:
        resource_name = 'friends/new'
        queryset = get_user_model().objects.all()
        excludes = ['password', 'is_superuser', 'is_staff']
        #list_allowed_methods = ['get']
        #detail_allowed_methods = []
        ordering = ['first_name']
        filtering = {'username': ALL, 'first_name': ALL}
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    def get_object_list(self, request):
        user = request.user
        links = user.link_as_sender.filter(sender_status='NEW')
        receivers = get_user_model().objects.filter(
                                    id__in=links.values('receiver_id'))
        links = user.link_as_receiver.filter(receiver_status='NEW')
        senders = get_user_model().objects.filter(
                                    id__in=links.values('sender_id'))
        ret = senders | receivers
        return ret.exclude(is_superuser=True)

class AuthResource(ModelResource):
    """
    An API for loging in / registering, no authentication required
    """
    class Meta:
        queryset = get_user_model().objects.all()
        excludes = ['password', 'is_superuser', 'is_staff']
        fields = ['username', 'first_name', 'last_name', 'email']
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
            url(r"^(?P<resource_name>%s)/social_register%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('social_register'), name="api_social_register"),
            url(r"^(?P<resource_name>%s)/social_login%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('social_login'), name="api_social_login"),
            url(r"^(?P<resource_name>%s)/reset_password%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('reset_password'), name="api_reset_password"),
            url(r"^(?P<resource_name>%s)/ping%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('ping'), name="api_ping"),
            url(r"^(?P<resource_name>%s)/get_code%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_code'), name="api_get_code"),
            url(r"^(?P<resource_name>%s)/verif_code%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('verif_code'), name="api_verif_code"),
            url(r"^(?P<resource_name>%s)/is_registered%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('is_registered'), name="api_is_registered"),
        ]

    def get_clean_data(self, request):
        try:
            data = self.deserialize(request, request.body,
                format=request.META.get('CONTENT_TYPE', 'application/json'))
            return data
        except:
            bad_request = {'reason': u'cannot deserialize data'}
            logging.error(bad_request)
            raise BadRequest(bad_request)

    def get_clean_username(self, data):
        try:
            username = data.get('username').lower().strip()
            if not username:
                bad_request = {u'reason': u"empty username", u'code': u'10'}
                logging.error(bad_request)
                raise BadRequest(bad_request)
            return username
        except:
            bad_request = {u'reason': u"invalid or missing username",
                           u'code': u'10'}
            logging.error(bad_request)
            raise BadRequest(bad_request)

    def get_clean_password(self, data):
        try:
            password = data.get('password').strip()
            if not password:
                bad_request = {u'reason': u"empty password", u'code': u'11'}
                logging.error(bad_request)
                raise BadRequest(bad_request)
            return password
        except:
            bad_request = {u'reason': u"invalid or missing password",
                           u'code': u'11'}
            logging.error(bad_request)
            raise BadRequest(bad_request)
    
    def get_clean_number(self, data):
        try:
            phone_number = data.get('phone_number').strip()
            if not phone_number:
                bad_request = {u'reason': u"empty number", u'code': u'13'}
                logging.error(bad_request)
                raise BadRequest(bad_request)
            return phone_number
        except:
            bad_request = {u'reason': u"invalid or missing number",
                           u'code': u'13'}
            logging.error(bad_request)
            raise BadRequest(bad_request)
        
    def get_clean_code(self, data):
        try:
            code = data.get('code')
            if not code:
                bad_request = {u'reason': u"empty code", u'code': u'15'}
                logging.error(bad_request)
                raise BadRequest(bad_request)
            if type(code) is not int:
                try:
                    code = int(code.strip())
                except:
                    bad_request = {u'reason': u"code not int", u'code': u'15'}
                    logging.error(bad_request)
                    raise BadRequest(bad_request)
            return code
        except:
            bad_request = {u'reason': u"invalid or missing code",
                           u'code': u'15'}
            logging.error(bad_request)
            raise BadRequest(bad_request)

    def get_clean_token(self, data):
        try:
            access_token = data.get('access_token').strip()
            if not access_token:
                bad_request = {u'reason': u"empty access_token"}
                logging.error(bad_request)
                raise BadRequest(bad_request)
            return access_token
        except:
            bad_request = {u'reason': u"invalid or missing access_token"}
            logging.error(bad_request)
            raise BadRequest(bad_request)

    def find_number(self, phone_number):
        try:
            number = Number.objects.get(phone_number=phone_number)
            return number
        except:
            bad_request = {u'reason': u'number %s not found'%phone_number,
                           u'code': '18'}
            logging.error(bad_request)
            raise BadRequest(bad_request)

    def link_user_number(self, user, code, number, phone_number):
        # make user <--> number association
        validated = number.validate(user, phone_number, code)
        if not validated:
            bad_request = {u'reason': u'user/number/code do not match',
                           u'code': '19'}
            logging.error(bad_request)
            raise BadRequest(bad_request)

    def register(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        # pre register (control inputs)
        try:
            data         = self.get_clean_data(request)
            username     = self.get_clean_username(data)
            password     = self.get_clean_password(data)
            phone_number = self.get_clean_number(data)
            code         = self.get_clean_code(data)
            number       = self.find_number(phone_number)
        except:
            return self.create_response(request,
                                        u'something wrong with args',
                                        HttpBadRequest)
        # check if user already exists, otherwise create it
        try:
            user = get_user_model().objects.get(username=username)
            bad_request = {u'reason': u'user already exists', u'code': '200'}
            logging.error(bad_request)
            return self.create_response(request, bad_request, HttpBadRequest)
        except get_user_model().DoesNotExist:
            try:
                user = get_user_model().objects.create_user(username=username,
                                                            password=password)
            except:
                bad_request = {u'reason': u'user creation failed',
                               u'code': '300'}
                logging.error(bad_request)
                return self.create_response(request, bad_request,
                                            HttpBadRequest)
        # link user number
        try:
            self.link_user_number(user, code, number, phone_number)
        except:
            return self.create_response(request,
                                        u'link_user_number failed',
                                        HttpBadRequest)
        # finish authentication
        (req, result, status) = apifn.login(request, username, password)
        result[u'code'] = u'0'
        status = HttpCreated
        return self.create_response(req, result, status)

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        try:
            data     = self.get_clean_data(request)
            username = self.get_clean_username(data)
            password = self.get_clean_password(data)
        except:
            return self.create_response(request,
                                        u'something wrong with args',
                                        HttpBadRequest)
        (req, result, status) = apifn.login(request, username, password)
        return self.create_response(req, result, status)

    def reset_password(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        try:
            data         = self.get_clean_data(request)
            password     = self.get_clean_password(data)
            phone_number = self.get_clean_number(data)
            code         = self.get_clean_code(data)
            number       = self.find_number(phone_number)
        except:
            return self.create_response(request,
                                        u'something wrong with args',
                                        HttpBadRequest)
        (req, result, status) = apifn.reset_password(request, password, code,
                                                     number)
        return self.create_response(req, result, status)

    def ping(self, request, **kwargs):
        return self.create_response(request, {}, HttpResponse)

    def get_code(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        try:
            data         = self.get_clean_data(request)
            phone_number = self.get_clean_number(data)
        except:
            return self.create_response(request,
                                        u'something wrong with args',
                                        HttpBadRequest)
        (req, result, status) = apifn.get_code(request, phone_number)
        return self.create_response(req, result, status)

    def verif_code(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        try:
            data         = self.get_clean_data(request)
            phone_number = self.get_clean_number(data)
            code         = self.get_clean_code(data)
            number       = self.find_number(phone_number)
        except:
            return self.create_response(request,
                                        u'something wrong with args',
                                        HttpBadRequest)
        if number.verif_code(code):
            return self.create_response(request, {}, HttpResponse)
        else:
            return self.create_response(request,
                                        {u'reason': u'incorrect code'},
                                        HttpUnprocessableEntity)

    def is_registered(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        try:
            data         = self.get_clean_data(request)
            phone_number = self.get_clean_number(data)
        except:
            logging.error(u'something wrong with args')
            return self.create_response(request,
                                        u'something wrong with args',
                                        HttpBadRequest)
        try:
            number = self.find_number(phone_number)
        except:
            logging.error(u'new number')
            return self.create_response(request,
                                        {u'reason': u'new number'},
                                        HttpUnauthorized)
        if number.validated and number.user:
            return self.create_response(request, {'method':'password'},
                                        HttpResponse)
        else:
            logging.error(u'not registered')
            return self.create_response(request,
                                        {u'reason': u'not registered'},
                                        HttpUnauthorized)

    def social(self, request, access_token):
        app = SocialApp.objects.get(provider="facebook")
        token = SocialToken(app=app, token=access_token)
        login = fb_complete_login(request, app, token)
        login.token = token
        login.state = SocialLogin.state_from_request(request)
        complete_social_login(request, login)
        return (request, login.user)

    def social_login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        # new way
        try:
            data         = self.get_clean_data(request)
            access_token = self.get_clean_token(data)
        except:
            return self.create_response(request,
                                        u'something wrong with args',
                                        HttpBadRequest)
        if 'phone_number' in data:
            phone_number = self.get_clean_number(data)
            number       = self.find_number(phone_number)
            if number.validated and number.user:
                perform_login(request, number.user, None)
                user = number.user
        else:
            # social registration (legacy)
            try:
                data = self.get_clean_data(request)
                access_token = self.get_clean_token(data)
                (request, user) = self.social(request, access_token)
            except:
                logging.error(u'something went wrong with FB')
                return self.create_response(request,
                                            {u'something went wrong with FB'},
                                            HttpBadRequest)
            ###############
        result =  {u'api_key' : user.api_key.key, u'userid' : user.id,
                    u'username': user.username}
        return self.create_response(request, result, HttpResponse)

    def social_register(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        # pre register (control inputs)
        try:
            data         = self.get_clean_data(request)
            phone_number = self.get_clean_number(data)
            code         = self.get_clean_code(data)
            access_token = self.get_clean_token(data)
            number       = self.find_number(phone_number)
        except:
            logging.error(u'something went wrong with args')
            return self.create_response(request,
                                        u'something wrong with args',
                                        HttpBadRequest)
        # social registration
        try:
            (request, user) = self.social(request, access_token)
        except:
            logging.error(u'something went wrong with FB')
            return self.create_response(request,
                                        {u'something went wrong with FB'},
                                        HttpBadRequest)
        #link user number
        try:
            self.link_user_number(user, code, number, phone_number)
        except:
            return self.create_response(request,
                                        u'link_user_number failed',
                                        HttpBadRequest)
        result =  {u'api_key' : user.api_key.key, u'userid' : user.id,
                   u'username': user.username,    u'code':u'0'}
        return self.create_response(request, result, HttpCreated)
