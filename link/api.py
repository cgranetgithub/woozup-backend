from tastypie import fields
from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie.utils import trailing_slash
from tastypie.resources import Resource, ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import ApiKeyAuthentication

from django.db.models import Q
from django.conf.urls import url
from django.contrib.auth.models import User

from link import push
from doc import authdoc
from link.models import Link, Invite
from userprofile.api import UserResource

from rq.decorators import job
#from redis import Redis
#redis_conn = Redis()
from worker import conn

class InviteResource(ModelResource):
    sender   = fields.ToOneField(UserResource, 
                                attribute='sender', full=True)
    class Meta:
        resource_name = 'invite'
        queryset = Invite.objects.all()
        allowed_methods = ['get']
        filtering = {
                    'sender': ALL_WITH_RELATIONS,
                    'receiver': ALL,
                    'status': ALL,
                    }
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    def get_object_list(self, request):
        return Invite.objects.filter( sender=request.user )

class LinkResource(ModelResource):
    sender   = fields.ToOneField(UserResource, 
                                attribute='sender', full=True)
    receiver = fields.ToOneField(UserResource, 
                                attribute='receiver', full=True)
    class Meta:
        resource_name = 'link'
        queryset = Link.objects.all()
        allowed_methods = ['get']
        #no POST: links are created by the backend
        #no PUT : links are modified via custom commands
        filtering = {
                    'sender': ALL_WITH_RELATIONS,
                    'receiver': ALL_WITH_RELATIONS,
                    'sender_status': ALL,
                    'receiver_status': ALL,
                    }
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        # for the doc:
        extra_actions = [ 
            {   u"name": u"connect",
                u"http_method": u"POST",
                #"resource_type": "list",
                u"summary": u"""[Custom] Sender requests the receiver to 
connect. This will change the link status from NEW/NEW to ACC/PEN.
This API requires the api_key user authentication.""",
                "fields": authdoc
            } ,
            {   u"name": u"accept",
                u"http_method": u"POST",
                #"resource_type": "list",
                u"summary": u"""[Custom] Receiver accepts to connect. 
This will change the link status from ACC/PEN to ACC/ACC.
This API requires the api_key user authentication.""",
                "fields": authdoc
            } ,
            {   u"name": u"reject",
                u"http_method": u"POST",
                #"resource_type": "list",
                u"summary": u"""[Custom] Receiver refuse to connect. 
This will change the link status from ACC/PEN to ACC/REJ.
This API requires the api_key user authentication.""",
                u"fields": authdoc
            } ,
        ]

    def get_object_list(self, request):
        return Link.objects.filter(  Q(sender=request.user)
                                   | Q(receiver=request.user) )

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<link_id>\w[\w/-]*)/connect%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('connect'), name="api_connect"),
            url(r"^(?P<resource_name>%s)/(?P<link_id>\w[\w/-]*)/accept%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('accept'), name="api_accept_link"),
            url(r'^(?P<resource_name>%s)/(?P<link_id>\w[\w/-]*)/reject%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('reject'), name='api_reject_link'),
        ]

    def connect(self, request, **kwargs):
        """ Invite a user to connect. This action is done by the sender
        Arguments:

        Note: we do this for security reason, to avoid someone to manipulate
        links directly with a PUT        
        """
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        if request.user and request.user.is_authenticated():
            try:
                link = Link.objects.get(id=kwargs['link_id'])
                if link.sender == request.user:
                    link.sender_status='ACC'
                    link.receiver_status='PEN'
                    link.save()
                    push.link_requested(link)
                    return self.create_response(request, {'success': True})
                else:
                    return self.create_response(
                                    request, 
                                    {u'reason': u'Link does not below to you'},
                                    HttpForbidden)
            except Link.DoesNotExist:
                return self.create_response(request, 
                                            {u'reason': u'Link not found'},
                                            HttpForbidden)
            else:
                return self.create_response(request, 
                                            {u'reason': u'Unexpected'},
                                            HttpForbidden)
        else:
            return self.create_response(
                                    request,
                                    {u'reason': u"You are not authenticated"},
                                    HttpUnauthorized )

    def accept(self, request, **kwargs):
        """ Accept a link. This action is done by the receiver.
        Arguments:

        Note: we do this for security reason, to avoid someone to manipulate
        links directly with a PUT        
        """
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        if request.user and request.user.is_authenticated():
            try:
                link = Link.objects.get(id=kwargs['link_id'])
                if link.receiver == request.user:
                    link.receiver_status='ACC'
                    link.save()
                    push.link_accepted(link)
                    return self.create_response(request, {u'success': True})
                else:
                    return self.create_response(
                                    request, 
                                    {u'reason': u'Link does not belong to you'},
                                    HttpForbidden)
            except Link.DoesNotExist:
                return self.create_response(request, 
                                            {u'reason': u'Link not found'},
                                            HttpForbidden)
            else:
                return self.create_response(request, 
                                            {u'reason': u'Unexpected'},
                                            HttpForbidden)
        else:
            return self.create_response(
                                    request,
                                    {u'reason': u"You are not authenticated"},
                                    HttpUnauthorized )
    
    def reject(self, request, **kwargs):
        """ Reject a link. This action is done by the receiver.
        Arguments:

        Note: we do this for security reason, to avoid someone to manipulate
        links directly with a PUT        
        """
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        if request.user and request.user.is_authenticated():
            try:
                link = Link.objects.get(id=kwargs['link_id'])
                if link.receiver == request.user:
                    link.receiver_status='REJ'
                    link.save()
                    return self.create_response(request, {'success': True})
                else:
                    return self.create_response(
                                    request, 
                                    {u'reason': u'Link does not below to you'},
                                    HttpForbidden)
            except Link.DoesNotExist:
                return self.create_response(request, 
                                            {u'reason': u'Link not found'},
                                            HttpForbidden)
            else:
                return self.create_response(request, 
                                            {u'reason': u'Unexpected'},
                                            HttpForbidden)
        else:
            return self.create_response(
                                    request,
                                    {u'reason': u"You are not authenticated"},
                                    HttpUnauthorized )
    
class ContactResource(Resource):
    user = None
    data = None
    class Meta:
        resource_name = 'contact'
        allowed_methods = []
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/sort%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('sort'), name='api_sort'),
        ]

    def sort(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        self.user = request.user
        if self.user and self.user.is_authenticated():
            try:
                self.data = self.deserialize(
                            request, request.body, 
                            format=request.META.get(
                            'CONTENT_TYPE', 'application/json'))
            except:
                return self.create_response(
                            request,
                            {u'reason': u'cannot deserialize data'},
                            HttpBadRequest )
            # launch background processing
            result = self.create_link_invite.delay()
            #
            return self.create_response(request, {'received': True})
        else:
            return self.create_response(request, { 'success': False }, 
                                                 HttpUnauthorized)

    @job('default', connection=conn)
    def create_link_invite(self):
        # 1) determine the existing connections
        email_list=[]
        create_link_list = []
        create_invite_list = []
        for i in self.data:
            # skip duplicates
            if i['email'] in email_list:
                continue
            else:
                email_list.append(i['email'])
            # Existing User?
            try:
                #user = User.objects.select_related().get(username=i['email'])
                user = User.objects.get(username=i['email'])
                # YES => existing Link?
                try:
                    Link.objects.get(
                        ( Q(sender=self.user) & Q(receiver=user) )
                        | ( Q(sender=user) & Q(receiver=self.user) )
                                    )
                    # YES => nothing to do
                except Link.DoesNotExist:
                    # NO => create a new Link
                    link = Link(sender=self.user, receiver=user)
                    create_link_list.append(link)
            except User.DoesNotExist:
                # NO => existing Invite?
                try:
                    Invite.objects.get(sender=self.user,
                                        email=i['email'])
                    # YES => nothing to do
                except Invite.DoesNotExist:
                    # NO => create a new Invite
                    invite = Invite(sender=self.user, email=i['email'])
                    create_invite_list.append(invite)
        # 2) create the missing connections (bulk for better performance)
        Link.objects.bulk_create(create_link_list)
        Invite.objects.bulk_create(create_invite_list)
