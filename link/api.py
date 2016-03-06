from tastypie import fields
from tastypie.http import HttpUnauthorized, HttpForbidden, HttpBadRequest
from tastypie.utils import trailing_slash
from tastypie.resources import Resource, ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import ApiKeyAuthentication

from django.http import HttpResponse
from django.conf.urls import url

from doc import authdoc
from link.tasks import create_connections
from link.models import Invite
from link.push import invite_validated, invite_ignored

import apidoc as doc

def change_invite_status(request, invite_id, new_status):
    if request.user and request.user.is_authenticated():
        try:
            invite = Invite.objects.get(id=invite_id)
            invite.status = new_status
            invite.save()
            return (request, {'invite': invite}, HttpResponse)
        except Invite.DoesNotExist:
            return (request, {u'reason': u'Invite not found'}, HttpForbidden)
        except:
            return (request, {u'reason': u'Unexpected'}, HttpForbidden)
    else:
        return (request, {u'reason': u"You are not authenticated"},
                HttpUnauthorized)


class InviteResource(ModelResource):
    #sender = fields.ToOneField(UserResource, 'sender', full=True)
    class Meta:
        resource_name = 'invite'
        queryset = Invite.objects.all()
        allowed_methods = ['get']
        ordering = ['name']
        filtering = {
                    #'sender': ALL_WITH_RELATIONS,
                    'name': ALL,
                    'number': ALL,
                    'status': ALL,
                    }
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    def get_object_list(self, request):
        return Invite.objects.filter( sender=request.user.userprofile )

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/send/(?P<invite_id>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('send'), name="api_send"),
            url(r"^(?P<resource_name>%s)/ignore/(?P<invite_id>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('ignore'), name="api_ignore"),
        ]

    def send(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        invite_id = kwargs['invite_id']
        (req, result, status) = change_invite_status(request, invite_id, 'PEN')
        # send invitation
        invite = result.get('invite', False)
        if invite:
            invite_validated(invite)
        return self.create_response(req, result, status)

    def ignore(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        invite_id = kwargs['invite_id']
        (req, result, status) = change_invite_status(request, invite_id, 'IGN')
        # send invitation
        # invite = result.get('invite', False)
        # if invite:
        #     invite_ignored(invite)
        return self.create_response(req, result, status)


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
                u"summary": doc.ContactResourceSort,
                u"fields": dict( authdoc.items() + doc.ContactResourceSortFields.items())
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
            create_connections.delay(user.userprofile, data)
            #
            return self.create_response(request, {'received': True})
        else:
            return self.create_response(request, {'success': False},
                                                  HttpUnauthorized)
