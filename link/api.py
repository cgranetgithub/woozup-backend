from tastypie.utils import trailing_slash
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.http import HttpUnauthorized, HttpForbidden, HttpCreated
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import SessionAuthentication

from django.conf.urls import url
from django.contrib.auth.models import User

from link.models import Link, Invite

class LinkResource(ModelResource):
    class Meta:
        resource_name = 'link'
        queryset = Link.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'put', 'delete']
        #excludes = ['email', 'password', 'is_superuser', 'is_staff']
        filtering = {
                    'receiver': ALL_WITH_RELATIONS,
                    }
        authorization  = DjangoAuthorization()
        authentication = SessionAuthentication()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/new%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('new'), name="api_new_link"),
            url(r"^(?P<resource_name>%s)/accept%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('accept'), name="api_accept_link"),
            url(r'^(?P<resource_name>%s)/reject%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('reject'), name='api_reject_link'),
        ]

    def new(self, request, **kwargs):
        """ Create a new link between the user himself, as the sender
        and the user invited, passed as an argument
        Arguments:
        <receiver> User id of the invited user """
        self.method_check(request, allowed=['post'])
        data = self.deserialize(request, request.body, 
                                format=request.META.get('CONTENT_TYPE', 
                                                        'application/json'))
        try:
            receiver = User.objects.get(id=data.get('receiver', ''))
            Link.objects.create(sender=request.user, receiver=receiver,
                                sender_status='ACC', receiver_status='PEN')
            return self.create_response(request, {'success': True}, 
                                        HttpCreated)
        except:
            return self.create_response(request, {'success': False}, 
                                        HttpUnauthorized) # to be improved

    def accept(self, request, **kwargs):
        """ Accept a new link. This action is done by the receiver
        Arguments:
        <link> Link id """
        self.method_check(request, allowed=['put'])
        data = self.deserialize(request, request.body, 
                                format=request.META.get('CONTENT_TYPE', 
                                                        'application/json'))
        try:
            link = Link.objects.get(id=data.get('link', ''))
            link.receiver_status='ACC'
            link.save()
            return self.create_response(request, {'success': True}, 
                                        HttpCreated)
        except:
            return self.create_response(request, {'success': False}, 
                                        HttpUnauthorized) # to be improved
