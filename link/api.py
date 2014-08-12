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
from worker import conn

@job('default', connection=conn)
def create_link_invite(user, data):
    # 1) determine the existing connections
    email_list=[]
    create_link_list = []
    create_invite_list = []
    for i in data:
        # skip duplicates
        if i['email'] in email_list:
            continue
        else:
            email_list.append(i['email'])
        # Existing User?
        try:
            #contact = User.objects.select_related().get(username=i['email'])
            contact = User.objects.get(username=i['email'])
            # YES => existing Link?
            try:
                Link.objects.get(
                    ( Q(sender=user) & Q(receiver=contact) )
                    | ( Q(sender=contact) & Q(receiver=user) )
                                )
                # YES => nothing to do
            except Link.DoesNotExist:
                # NO => create a new Link
                link = Link(sender=user, receiver=contact)
                create_link_list.append(link)
        except User.DoesNotExist:
            # NO => existing Invite?
            try:
                Invite.objects.get(sender=user,
                                    email=i['email'])
                # YES => nothing to do
            except Invite.DoesNotExist:
                # NO => create a new Invite
                invite = Invite(sender=user, email=i['email'])
                create_invite_list.append(invite)
    # 2) create the missing connections (bulk for better performance)
    Link.objects.bulk_create(create_link_list)
    Invite.objects.bulk_create(create_invite_list)

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
            { u'name' : u'  ***  DESCRIPTION OF THE LINK BEHAVIOR  ***  ',
              u'http_method':u'',
              u'resource_type':'',
              u'summary': u""" 
When a user registers, its contact list is sent to the backend 
(API contact/sort/).<br>A Link is created between the user and each contact 
already registered as a user.<br>In parallel, the backend will look for all 
Invites where the receiver is the new user and transform it into a link.<br>
<ul>
<li>sender_status = NEW</li>
<li>receiver_status = NEW</li>
</ul> <br> <br>
If the sender clicks on "connect" button in the app (API link/id/connect/)
<ul>
<li>sender_status => ACCEPTED</li>
<li>receiver_status => PENDING</li>
</ul> <br> <br>
If the receiver accepts the request for connection (API link/id/accept/)
<ul>
<li>sender_status = ACCEPTED</li>
<li>receiver_status => ACCEPTED</li>
</ul> <br> <br>
If the receiver rejects the request for connection (API link/id/reject/)
<ul>
<li>sender_status = ACCEPTED</li>
<li>receiver_status => REJECTED</li>
</ul> <br> <br>
If the sender or the receiver blacklist someone (API link/id/?/)
<ul>
<li>x_status => BLOCKED</li>
</ul>""",
              "fields": authdoc},
            {   u"name": u"connect",
                u"http_method": u"POST",
                #"resource_type": "list",
                u"summary": u"""[Custom API] - Requires authentication<br><br>
Sender requests the receiver to connect.<br>This will change the Link status 
from NEW/NEW to ACC/PEN.""",
                "fields": authdoc
            } ,
            {   u"name": u"accept",
                u"http_method": u"POST",
                #"resource_type": "list",
                u"summary": u"""[Custom API] - Requires authentication<br><br>
Receiver accepts to connect.<br>
This will change the Link status from ACC/PEN to ACC/ACC.""",
                "fields": authdoc
            } ,
            {   u"name": u"reject",
                u"http_method": u"POST",
                #"resource_type": "list",
                u"summary": u"""[Custom API] - Requires authentication<br><br>
Receiver refuse to connect.<br>
This will change the Link status from ACC/PEN to ACC/REJ.""",
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
    class Meta:
        resource_name = 'contact'
        allowed_methods = []
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        # for the doc:
        extra_actions = [ 
            {   u"name": u"sort",
                u"http_method": u"POST",
                "resource_type": "list",
                u"summary": u"""[Custom API] - Requires authentication<br><br>
Takes a list of usernames and triggers a background job that will create the 
appropriate INVITE and LINK between the user and each person in the list""",
                u"fields": dict( authdoc.items() + { u"username list": {
                                u"type": "json list",
                                u"required": True,
                                u"description": u"""The list of username that 
will be passed to the BG job.""" } }.items() )
            } ]
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
        user = request.user
        if user and user.is_authenticated():
            try:
                data = self.deserialize(request, request.body, 
                                        format=request.META.get(
                                        'CONTENT_TYPE', 'application/json'))
            except:
                return self.create_response(
                                    request,
                                    {u'reason': u'cannot deserialize data'},
                                    HttpBadRequest )
            # launch background processing
            create_link_invite.delay(user, data)
            #
            return self.create_response(request, {'received': True})
        else:
            return self.create_response(request, { 'success': False }, 
                                                 HttpUnauthorized)
