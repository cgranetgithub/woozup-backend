from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import ApiKeyAuthentication

#from django.db.models import Q
from django.conf.urls import url
from django.contrib.auth.models import User

import apidoc as doc
from doc import authdoc
from userprofile.models import UserProfile, UserPosition, get_user_friends
from service.b64field import Base64FileField
from link import push

import apifn

class PositionResource(ModelResource):
    #last = fields.CharField('last', null=True)
    class Meta:
        resource_name = 'userposition'
        queryset = UserPosition.objects.all()
        list_allowed_methods = []
        detail_allowed_methods = ['get', 'put']
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    def get_object_list(self, request):
        return UserPosition.objects.filter(user=request.user)

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
            return self.create_response(request,
                                        {u'reason': u'cannot deserialize data'},
                                        HttpBadRequest )
        (req, result, status) = apifn.setlast(request, data)
        return self.create_response(req, result, status)
    
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
        includes = ['first_name', 'last_name']
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

### WARNING need to restrict to user

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
            url(r"^(?P<resource_name>%s)/invite/(?P<user_id>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('invite'), name="api_invite"),
            url(r"^(?P<resource_name>%s)/ignore/(?P<user_id>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('ignore'), name="api_ignore"),
            url(r"^(?P<resource_name>%s)/accept/(?P<user_id>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('accept'), name="api_accept"),
            url(r"^(?P<resource_name>%s)/reject/(?P<user_id>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('reject'), name="api_reject"),
        ]

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        (req, result, status) = apifn.logout(request)
        return self.create_response(req, result, status)
        
    def check_auth(self, request, **kwargs):
        #
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        (req, result, status) = apifn.check_auth(request)
        return self.create_response(req, result, status)
        
    def gcm(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        try:
            data = self.deserialize(request, request.body, 
                                    format=request.META.get(
                                    'CONTENT_TYPE', 'application/json'))
        except:
            return self.create_response(request,
                                    {u'reason': u'cannot deserialize data'},
                                    HttpBadRequest )
        (req, result, status) = apifn.gcm(request, data)
        return self.create_response(req, result, status)
        
    def invite(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        sender_id   = request.user.id
        receiver_id = kwargs['user_id']
        new_sender_status   = 'ACC'
        new_receiver_status = 'PEN'
        (req, result, status, link, inverted) = apifn.change_link(request,
                                                    sender_id, receiver_id,
                                                    new_sender_status,
                                                    new_receiver_status)
        push.link_requested(link, inverted)
        return self.create_response(req, result, status)
    
    def ignore(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        sender_id   = kwargs['user_id']
        receiver_id = request.user.id
        new_sender_status = 'IGN'
        (req, result, status) = apifn.change_link(request, sender_id,
                                                receiver_id, new_sender_status,
                                                None)
        return self.create_response(req, result, status)
    def accept(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        sender_id   = kwargs['user_id']
        receiver_id = request.user.id
        new_receiver_status = 'ACC'
        (req, result, status, link, inverted) = apifn.change_link(request,
                                                    sender_id, receiver_id,
                                                    None, new_receiver_status)
        push.link_accepted(link, inverted)
        return self.create_response(req, result, status)
    def reject(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        sender_id   = kwargs['user_id']
        receiver_id = request.user.id
        new_receiver_status = 'REJ'
        (req, result, status) = apifn.change_link(request, sender_id,
                                                receiver_id, None,
                                                new_receiver_status)
        return self.create_response(req, result, status)

class ProfileResource(ModelResource):
    user = fields.ToOneField(UserResource, 'user', full=True)
    name = fields.CharField(attribute='name', readonly=True)
    email = fields.CharField(attribute='email', readonly=True)
    #image = fields.FileField(attribute="image", null=True, blank=True)
    image_field = Base64FileField("image", null=True, blank=True)
    class Meta:
        resource_name = 'userprofile'
        queryset = UserProfile.objects.all()
        list_allowed_methods = []
        ordering = ['user']
        detail_allowed_methods = ['get', 'put', 'patch']
        #filtering = {'user' : ALL_WITH_RELATIONS}
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    def get_object_list(self, request):
        return UserProfile.objects.filter(user=request.user)
    
### WARNING need to restrict to user

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
            return self.create_response(request,
                                        {u'reason': u'cannot deserialize data'},
                                        HttpBadRequest )
        (req, result, status) = apifn.setpicture(request, data)
        return self.create_response(req, result, status)

class MyFriendsResource(ModelResource):
    user = fields.ToOneField(UserResource, 'user', full=True)
    name = fields.CharField(attribute='name', readonly=True)
    class Meta:
        resource_name = 'friends/mine'
        queryset = UserProfile.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        ordering = ['user']
        #filtering = {'user' : ALL_WITH_RELATIONS}
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    def get_object_list(self, request):
        userprofile = request.user.userprofile
        return get_user_friends(userprofile)

class PendingFriendsResource(ModelResource):
    user = fields.ToOneField(UserResource, 'user', full=True)
    name = fields.CharField(attribute='name', readonly=True)
    class Meta:
        resource_name = 'friends/pending'
        queryset = UserProfile.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        ordering = ['user']
        #filtering = {'user' : ALL_WITH_RELATIONS}
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    def get_object_list(self, request):
        userprofile = request.user.userprofile
        links = userprofile.link_as_receiver.filter(receiver_status='PEN')
        senders = UserProfile.objects.filter(
                                    user_id__in=links.values('sender_id'))
        links = userprofile.link_as_sender.filter(sender_status='PEN')
        receivers = UserProfile.objects.filter(
                                    user_id__in=links.values('receiver_id'))
        return senders | receivers

class NewFriendsResource(ModelResource):
    user = fields.ToOneField(UserResource, 'user', full=True)
    name = fields.CharField(attribute='name', readonly=True)
    class Meta:
        resource_name = 'friends/new'
        queryset = UserProfile.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        ordering = ['user']
        #filtering = {'user' : ALL_WITH_RELATIONS}
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    def get_object_list(self, request):
        userprofile = request.user.userprofile
        links = userprofile.link_as_sender.filter(sender_status='NEW')
        receivers = UserProfile.objects.filter(
                                    user_id__in=links.values('receiver_id'))
        links = userprofile.link_as_receiver.filter(receiver_status='NEW')
        senders = UserProfile.objects.filter(
                                    user_id__in=links.values('sender_id'))
        return senders | receivers

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
        (req, result, status) = apifn.register(request, data)
        return self.create_response(req, result, status)
    
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
        (req, result, status) = apifn.login(request, data)
        return self.create_response(req, result, status)
