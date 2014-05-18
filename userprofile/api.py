from tastypie import fields
from tastypie.http import HttpUnauthorized, HttpForbidden, HttpCreated
from tastypie.utils import trailing_slash
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import SessionAuthentication

from django.db.models import Q
from django.conf.urls import url
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from link.models import Link
from userprofile.models import UserProfile

class ProfileResource(ModelResource):
    name = fields.CharField(attribute='name', readonly=True)
    allowed_methods = []
    class Meta:
        resource_name = 'profile'
        queryset = UserProfile.objects.all()
        authorization  = DjangoAuthorization()
        authentication = SessionAuthentication()
    
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
        authentication = SessionAuthentication()

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/logout%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('logout'), name='api_logout'),
            url(r'^(?P<resource_name>%s)/check_auth%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('check_auth'), name='api_check_auth'),
        ]

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, { 'success': True })
        else:
            return self.create_response(request, { 'success': False }, 
                                                 HttpUnauthorized)
     #WARNING must restrict to the use himself

    def check_auth(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            return self.create_response(request, { 'success': True })
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

#class FriendResource(ModelResource):
    #"""
    #An API to get friends list, authentication required
    #"""
    #profile = fields.ToOneField(ProfileResource, 
                                #attribute='userprofile', full=True)
    #class Meta:
        #resource_name = 'friends'
        #queryset = User.objects.all()
        #list_allowed_methods = ['get']
        #detail_allowed_methods = []
        #excludes = ['password', 'is_superuser', 'is_staff']
        #filtering = {
                    #'username': ALL,
                    #}
        #authorization  = DjangoAuthorization()
        #authentication = SessionAuthentication()

    ##def build_filters(self, filters=None):
        ##if filters is None:
            ##filters = {}
        ##orm_filters = super(FriendResource, self).build_filters(filters)
        ##if('query' in filters):
            ##query = filters['query']
            ##qset = (
                    ##Q(name__icontains=query) |
                    ##Q(description__icontains=query) |
                    ##Q(email__icontains=query)
                    ##)
            ##orm_filters.update({'custom': qset})
        ##return orm_filters

    #def apply_filters(self, request, applicable_filters):
        ##if 'custom' in applicable_filters:
            ##custom = applicable_filters.pop('custom')
        ##else:
            ##custom = None
        #semi_filtered = super(FriendResource, self).apply_filters(
                                                            #request,
                                                            #applicable_filters)
        #res = semi_filtered.filter(
            #( Q(link_as_sender__sender    =request.user) | 
              #Q(link_as_sender__receiver  =request.user) | 
              #Q(link_as_receiver__sender  =request.user) | 
              #Q(link_as_receiver__receiver=request.user) ),
            #( Q(link_as_sender__sender_status='ACC') & 
              #Q(link_as_sender__receiver_status='ACC') ) | 
            #( Q(link_as_receiver__sender_status='ACC') & 
              #Q(link_as_receiver__receiver_status='ACC') ) ).exclude(
                  #username=request.user.username)
        #return res
        ##return semi_filtered.filter(custom) if custom else semi_filtered

    ##def myfriends(self, request, **kwargs):
        ##""" Get my friends list, that users which have an ACC/ACC link with me
        ##Arguments: """
        ###self.method_check(request, allowed=['get'])
        ###data = self.deserialize(request, request.body, 
                                ###format=request.META.get('CONTENT_TYPE', 
                                                        ###'application/json'))
        ###try:
        ##friends = User.objects.filter(
            ##( Q(link_as_sender__sender    =request.user) | 
              ##Q(link_as_sender__receiver  =request.user) | 
              ##Q(link_as_receiver__sender  =request.user) | 
              ##Q(link_as_receiver__receiver=request.user) ),
            ##link_as_sender__sender_status='ACC',
            ##link_as_receiver__sender_status='ACC',
        ###| Q(link__receiver=request.user), Q(link__receiver_status='ACC')
            ##)
        ##print friends
        ##from django.core import serializers
        ##data = serializers.serialize("json", friends)
        ##print data
        ###import json
        ###print json.dumps(friends)
        ##return self.create_response(request, {'objects': data}, 
                                    ##HttpCreated)
        ###except:
            ###return self.create_response(request, {'success': False}, 
                                        ###HttpUnauthorized) # to be improved

#class UserToConnectResource(FriendResource):
    #"""
    #An API to get list of User I can connect to, authentication required
    #"""
    #class Meta(FriendResource.Meta):
        #resource_name = 'userstoconnect'

    #def apply_filters(self, request, applicable_filters):
        #semi_filtered = super(FriendResource, self).apply_filters(
                                                            #request,
                                                            #applicable_filters)
        #res = semi_filtered.filter(
                  #(  Q(link_as_sender__sender=request.user)
                   #& Q(link_as_sender__sender_status='NEW')
                  #)
                #| (  Q(link_as_receiver__sender=request.user)
                   #& Q(link_as_receiver__sender_status='NEW') 
                  #)
                #| (  Q(link_as_sender__receiver=request.user)
                   #& Q(link_as_sender__receiver_status__in=['NEW', 'PEN'])
                  #)
                #| (  Q(link_as_receiver__receiver=request.user)
                   #& Q(link_as_receiver__receiver_status__in=['NEW', 'PEN']) 
                  #)
                #).exclude(username=request.user.username)
        #return res

#class PeopleToInviteResource(FriendResource):
    #"""
    #An API to get list of non-User I can invite, authentication required
    #"""
    #class Meta(FriendResource.Meta):
        #resource_name = 'peopletoinvite'

    #def apply_filters(self, request, applicable_filters):
        #semi_filtered = super(FriendResource, self).apply_filters(
                                                            #request,
                                                            #applicable_filters)
        #res = semi_filtered.filter(
                  #(  Q(invite__sender=request.user)
                   #& Q(invite__status='NEW')
                  #) )
        #return res
