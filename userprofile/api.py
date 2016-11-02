from tastypie import fields
from tastypie.http import HttpBadRequest
from tastypie.utils import trailing_slash
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import ApiKeyAuthentication

#from django.db.models import Q
from django.http import HttpResponse
from django.conf.urls import url
from django.contrib.auth import get_user_model

import apidoc as doc
from doc import authdoc
from userprofile.models import Profile, Position
from userprofile.utils import get_friends
from service.b64field import Base64FileField
#from link import push

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
            {   "name": u"push_notif_reg",
                "http_method": u"POST",
                "resource_type": "list",
                "summary": doc.UserResourcePushNotifReg,
                "fields": dict( authdoc.items() + doc.UserResourcePushNotifRegFields.items() )
            } ,
        ]

    def get_object_list(self, request):
        print get_user_model().objects.filter(is_superuser=False)
        return get_user_model().objects.filter(is_superuser=False)

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
            #url(r"^(?P<resource_name>%s)/invite/(?P<user_id>\w[\w/-]*)%s$" %
                #(self._meta.resource_name, trailing_slash()),
                #self.wrap_view('invite'), name="api_invite"),
            #url(r"^(?P<resource_name>%s)/ignore/(?P<user_id>\w[\w/-]*)%s$" %
                #(self._meta.resource_name, trailing_slash()),
                #self.wrap_view('ignore'), name="api_ignore"),
            url(r"^(?P<resource_name>%s)/accept/(?P<user_id>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('accept'), name="api_accept"),
            url(r"^(?P<resource_name>%s)/reject/(?P<user_id>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('reject'), name="api_reject"),
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
        #
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        (req, result, status) = apifn.check_auth(request)
        return self.create_response(req, result, status)

    def push_notif_reg(self, request, **kwargs):
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
        (req, result, status) = apifn.push_notif_reg(request, data)
        return self.create_response(req, result, status)

    #def invite(self, request, **kwargs):
        #self.method_check(request, allowed=['post'])
        #self.is_authenticated(request)
        #self.throttle_check(request)
        #sender_id   = request.user.id
        #receiver_id = kwargs['user_id']
        #new_sender_status   = 'ACC'
        #new_receiver_status = 'PEN'
        #(req, result, status,
        #link, inverted) = apifn.change_link(request, sender_id, receiver_id,
                                             #new_sender_status,
                                             #new_receiver_status)
        #push.link_requested(link, inverted)
        #return self.create_response(req, result, status)

    #def ignore(self, request, **kwargs):
        #self.method_check(request, allowed=['post'])
        #self.is_authenticated(request)
        #self.throttle_check(request)
        #sender_id   = request.user.id
        #receiver_id = kwargs['user_id']
        #new_sender_status = 'IGN'
        #(req, result, status,
         #link, inverted) = apifn.change_link(request, sender_id, receiver_id,
                                             #new_sender_status, None)
        #return self.create_response(req, result, status)
    def accept(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        #sender_id   = kwargs['user_id']
        #receiver_id = request.user.id
        #new_receiver_status = 'ACC'
        #(req, result, status,
         #link, inverted) = apifn.change_link(request, sender_id, receiver_id,
                                             #None, new_receiver_status)
        (req, result, status) = apifn.accept(request, kwargs['user_id'])
        #push.link_accepted(link, inverted)
        return self.create_response(req, result, status)
    def reject(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        #sender_id   = kwargs['user_id']
        #receiver_id = request.user.id
        #new_receiver_status = 'REJ'
        #(req, result, status,
         #link, inverted) = apifn.change_link(request, sender_id, receiver_id,
                                             #None, new_receiver_status)
        (req, result, status) = apifn.reject(request, kwargs['user_id'])
        return self.create_response(req, result, status)
    def setprofile(self, request, **kwargs):
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
        (req, result, status) = apifn.setprofile(request, data)
        return self.create_response(req, result, status)

class ProfileResource(ModelResource):
    #user = fields.ToOneField(UserResource, attribute='user', related_name='profile', full=True)
    #user = fields.ToOneField(UserResource, 'user')
    #name = fields.CharField(attribute='name', readonly=True)
    email = fields.CharField(attribute='email', readonly=True)
    #image = fields.FileField(attribute="image", null=True, blank=True)
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
            return self.create_response(request,
                                        {u'reason': u'cannot deserialize data'},
                                        HttpBadRequest )
        (req, result, status) = apifn.setpicture(request, data)
        return self.create_response(req, result, status)

class MyFriendsResource(ModelResource):
    profile = fields.ToOneField('userprofile.api.ProfileResource',
                                'profile', full=True)
    class Meta:
        resource_name = 'friends/mine'
        queryset = get_user_model().objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        ordering = ['first_name']
        filtering = {'username': ALL, 'first_name': ALL}
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    def get_object_list(self, request):
        return get_friends(request.user)

class PendingFriendsResource(ModelResource):
    profile = fields.ToOneField('userprofile.api.ProfileResource',
                                'profile', full=True)
    class Meta:
        resource_name = 'friends/pending'
        queryset = get_user_model().objects.all()
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
        return senders | receivers

class NewFriendsResource(ModelResource):
    profile = fields.ToOneField('userprofile.api.ProfileResource',
                                'profile', full=True)
    class Meta:
        resource_name = 'friends/new'
        queryset = get_user_model().objects.all()
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
        return senders | receivers

class AuthResource(ModelResource):
    """
    An API for loging in / registering, no authentication required
    """
    class Meta:
        queryset = get_user_model().objects.all()
        fields = ['username', 'first_name', 'last_name', 'email']
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
            #url(r"^(?P<resource_name>%s)/register_by_email%s$" %
                #(self._meta.resource_name, trailing_slash()),
                #self.wrap_view('register_by_email'), name="api_register_by_email"),
            url(r"^(?P<resource_name>%s)/login%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('login'), name="api_login"),
            #url(r"^(?P<resource_name>%s)/login_by_email%s$" %
                #(self._meta.resource_name, trailing_slash()),
                #self.wrap_view('login_by_email'), name="api_login_by_email"),
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

    #def register_by_email(self, request, **kwargs):
        #self.method_check(request, allowed=['post'])
        #try:
            #data = self.deserialize(request, request.body,
                                    #format=request.META.get(
                                    #'CONTENT_TYPE', 'application/json'))
        #except:
            #return self.create_response(request,
                                        #{u'reason': u'cannot deserialize data'},
                                        #HttpBadRequest )
        #(req, result, status) = apifn.register_by_email(request, data)
        #return self.create_response(req, result, status)

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

    #def login_by_email(self, request, **kwargs):
        #self.method_check(request, allowed=['post'])
        #try:
            #data = self.deserialize(request, request.body,
                                    #format=request.META.get(
                                    #'CONTENT_TYPE', 'application/json'))
        #except:
            #return self.create_response(request,
                                        #{'reason': u'cannot deserialize data'},
                                        #HttpBadRequest )
        #(req, result, status) = apifn.login_by_email(request, data)
        #return self.create_response(req, result, status)

    def reset_password(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        try:
            data = self.deserialize(request, request.body,
                                    format=request.META.get(
                                    'CONTENT_TYPE', 'application/json'))
        except:
            return self.create_response(request,
                                        {'reason': u'cannot deserialize data'},
                                        HttpBadRequest )
        (req, result, status) = apifn.reset_password(request, data)
        return self.create_response(req, result, status)

    def ping(self, request, **kwargs):
        return self.create_response(request, {}, HttpResponse)

    def get_code(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        try:
            data = self.deserialize(request, request.body,
                                    format=request.META.get(
                                    'CONTENT_TYPE', 'application/json'))
        except:
            return self.create_response(request,
                                        {'reason': u'cannot deserialize data'},
                                        HttpBadRequest )
        (req, result, status) = apifn.get_code(request, data)
        return self.create_response(req, result, status)

    def verif_code(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        try:
            data = self.deserialize(request, request.body,
                                    format=request.META.get(
                                    'CONTENT_TYPE', 'application/json'))
        except:
            return self.create_response(request,
                                        {'reason': u'cannot deserialize data'},
                                        HttpBadRequest )
        (req, result, status) = apifn.verif_code(request, data)
        return self.create_response(req, result, status)

    def is_registered(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        try:
            data = self.deserialize(request, request.body,
                                    format=request.META.get(
                                    'CONTENT_TYPE', 'application/json'))
        except:
            return self.create_response(request,
                                        {'reason': u'cannot deserialize data'},
                                        HttpBadRequest )
        (req, result, status) = apifn.is_registered(request, data)
        return self.create_response(req, result, status)
