from tastypie import fields
from tastypie.http import HttpUnauthorized, HttpForbidden, HttpCreated
from tastypie.utils import trailing_slash
from tastypie.resources import Resource, ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import SessionAuthentication

from django.db.models import Q
from django.conf.urls import url
from django.contrib.auth.models import User

from link.models import Link, Invite
from userprofile.api import UserResource

class InviteResource(ModelResource):
    sender   = fields.ToOneField(UserResource, 
                                attribute='sender', full=True)
    class Meta:
        resource_name = 'invite'
        queryset = Invite.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        filtering = {
                    'sender': ALL_WITH_RELATIONS,
                    'receiver': ALL,
                    'status': ALL,
                    }
        authorization  = DjangoAuthorization()
        authentication = SessionAuthentication()

    def get_object_list(self, request):
        return Invite.objects.filter( sender=request.user )

    #def apply_filters(self, request, applicable_filters):
        #semi_filtered = super(InviteResource, self
                              #).apply_filters(request, applicable_filters)
        #res = semi_filtered.filter(sender=request.user)
        #return res
        

class LinkResource(ModelResource):
    sender   = fields.ToOneField(UserResource, 
                                attribute='sender', full=True)
    receiver = fields.ToOneField(UserResource, 
                                attribute='receiver', full=True)
    class Meta:
        resource_name = 'link'
        queryset = Link.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        filtering = {
                    'sender': ALL_WITH_RELATIONS,
                    'receiver': ALL_WITH_RELATIONS,
                    'sender_status': ALL,
                    'receiver_status': ALL,
                    }
        authorization  = DjangoAuthorization()
        authentication = SessionAuthentication()

    def get_object_list(self, request):
        return Link.objects.filter(  Q(sender=request.user)
                                   | Q(receiver=request.user) )

    #def prepend_urls(self):
        #return [
            #url(r"^(?P<resource_name>%s)/new%s$" %
                #(self._meta.resource_name, trailing_slash()),
                #self.wrap_view('new'), name="api_new_link"),
            #url(r"^(?P<resource_name>%s)/accept%s$" %
                #(self._meta.resource_name, trailing_slash()),
                #self.wrap_view('accept'), name="api_accept_link"),
            #url(r'^(?P<resource_name>%s)/reject%s$' %
                #(self._meta.resource_name, trailing_slash()),
                #self.wrap_view('reject'), name='api_reject_link'),
        #]

    #def new(self, request, **kwargs):
        #""" Create a new link between the user himself, as the sender
        #and the user invited, passed as an argument
        #Arguments:
        #<receiver> User id of the invited user
        
        #Note: we do this for security reason, to avoid someone to create links
        #for others
        #"""
        #if request.user and request.user.is_authenticated():
            #self.method_check(request, allowed=['post'])
            #data = self.deserialize(request, request.body, 
                                    #format=request.META.get('CONTENT_TYPE', 
                                                           #'application/json'))
            #try:
                #receiver = User.objects.get(id=data.get('receiver', ''))
                #Link.objects.create(sender=request.user, receiver=receiver,
                                    #sender_status='ACC', receiver_status='PEN')
                #return self.create_response(request, {'success': True}, 
                                            #HttpCreated)
            #except:
                #return self.create_response(request, {'success': False}, 
                                            #HttpUnauthorized) # to be improved
        #else:
            #return self.create_response(request, { 'success': False }, 
                                                 #HttpUnauthorized)

    ## WARNING PROBABLY NOT NECESSARY, USE PUT INSTEAD
    #def accept(self, request, **kwargs):
        #""" Accept a new link. This action is done by the receiver
        #Arguments:
        #<link> Link id 

        #Note: we do this for security reason, to avoid someone to create links
        #for others        
        #"""
        #self.method_check(request, allowed=['put'])
        #if request.user and request.user.is_authenticated():
            #data = self.deserialize(request, request.body, 
                                    #format=request.META.get('CONTENT_TYPE', 
                                                           #'application/json'))
            #try:
                #link = Link.objects.get(id=data.get('link', ''))
                #link.receiver_status='ACC'
                #link.save()
                #return self.create_response(request, {'success': True}, 
                                            #HttpCreated)
            #except:
                #return self.create_response(request, {'success': False}, 
                                            #HttpUnauthorized) # to be improved
        #else:
            #return self.create_response(request, { 'success': False }, 
                                                 #HttpUnauthorized)

    #def apply_filters(self, request, applicable_filters):
        #semi_filtered = super(FriendResource, self
                              #).apply_filters(request, applicable_filters)
        #res = semi_filtered.filter(  Q(sender  =request.user)
                                   #| Q(receiver=request.user)
                                  #)
        #return res

    
class ContactResource(Resource):
    class Meta:
        resource_name = 'contact'
        #queryset = User.objects.all()
        allowed_methods = []
        #excludes = ['password', 'is_superuser', 'is_staff']
        authorization  = DjangoAuthorization()
        authentication = SessionAuthentication()

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/sort%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('sort'), name='api_sort'),
        ]

    def sort(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        if request.user and request.user.is_authenticated():                    
            data = self.deserialize(request, request.body,
                                    format=request.META.get('CONTENT_TYPE',
                                                        'application/json'))
            res = {'unknown':[], 'user':[], 'friend':[]}
            for i in data:
                # Existing User?
                try:
                    user = User.objects.select_related().get(username=i['email'])
                    print user, 'exists'
                    # YES => existing Link?
                    try:
                        Link.objects.get(
                            ( Q(sender=request.user) & Q(receiver=user) )
                          | ( Q(sender=user) & Q(receiver=request.user) )
                                        )
                        print "existing link"
                        # YES => nothing to do
                    except Link.DoesNotExist:
                        # NO => create a new Link
                        print 'must create link'
                except User.DoesNotExist:
                    # NO => existing Invite?
                    try:
                        Invite.objects.get(sender=request.user,
                                           email=i['email'])
                        print "existing invite"
                        # YES => nothing to do
                    except Invite.DoesNotExist:
                        # NO => create a new Invite
                        print 'must create invite'
            return self.create_response(request, {'received': True})
        else:
            return self.create_response(request, { 'success': False }, 
                                                 HttpUnauthorized)
