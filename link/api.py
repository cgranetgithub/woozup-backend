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
from link.models import Contact, Link
from link.push import invite_validated

import apidoc as doc

import json

class LinkResource(ModelResource):
    sender = fields.ToOneField('userprofile.api.UserResource',
                                'sender', full=True)
    receiver = fields.ToOneField('userprofile.api.UserResource',
                                'receiver', full=True)
    class Meta:
        resource_name = 'link'
        queryset = Link.objects.all()
        allowed_methods = ['get']
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True

    def get_object_list(self, request):
        as_sender = Link.objects.filter(sender=request.user)
        as_receiver = Link.objects.filter(receiver=request.user)
        return as_sender | as_receiver
    
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/withuser/(?P<user_id>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('withuser'), name="api_withuser"),
        ]

    def withuser(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        user_id = kwargs['user_id']
        as_sender = Link.objects.filter(sender=request.user, receiver__id=user_id)
        as_receiver = Link.objects.filter(receiver=request.user, sender__id=user_id)
        result = as_sender | as_receiver
        if len(result) == 0:
            return self.create_response(request, False, HttpResponse)
        elif len(result) == 1:
            res = LinkResource()
            link_bundle = res.build_bundle(request=request, obj=result[0])
            link_json = res.serialize(None, res.full_dehydrate(link_bundle), "application/json")
            return self.create_response(request, link_json, HttpResponse)
        else:
            return self.create_response(request, {u'reason': u'multiple links between 2 users!'}, HttpBadRequest)


def change_contact_status(request, contact_id, new_status):
    if request.user and request.user.is_authenticated():
        try:
            contact = Contact.objects.get(id=contact_id)
            contact.status = new_status
            contact.save()
            return (request, {'contact': contact}, HttpResponse)
        except Contact.DoesNotExist:
            return (request, {u'reason': u'Contact not found'}, HttpForbidden)
        except:
            return (request, {u'reason': u'Unexpected'}, HttpForbidden)
    else:
        return (request, {u'reason': u"You are not authenticated"},
                HttpUnauthorized)


class ContactResource(ModelResource):
    #sender = fields.ToOneField(UserResource, 'sender', full=True)
    class Meta:
        resource_name = 'contact'
        queryset = Contact.objects.all()
        allowed_methods = ['get']
        ordering = ['name']
        filtering = {
                    ##'sender': ALL_WITH_RELATIONS,
                    #'name': ALL,
                    #'number': ALL,
                    'status': ALL,
                    }
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True

    def get_object_list(self, request):
        return Contact.objects.filter( sender=request.user )

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/send/(?P<contact_id>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('send'), name="api_send"),
            url(r"^(?P<resource_name>%s)/ignore/(?P<contact_id>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('ignore'), name="api_ignore"),
            url(r'^(?P<resource_name>%s)/sort%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('sort'), name='api_sort'),
        ]

    def send(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        contact_id = kwargs['contact_id']
        (req, result, status) = change_contact_status(request, contact_id, 'PEN')
        # send invitation
        contact = result.get('contact', False)
        if contact:
            invite_validated(contact)
        return self.create_response(req, result, status)

    def ignore(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        contact_id = kwargs['contact_id']
        (req, result, status) = change_contact_status(request, contact_id, 'IGN')
        # send invitation
        # contact = result.get('contact', False)
        # if contact:
        #     invite_ignored(contact)
        return self.create_response(req, result, status)


#class ContactResource(Resource):
    #class Meta:
        #resource_name = 'contact'
        #allowed_methods = []
        #authorization  = DjangoAuthorization()
        #authentication = ApiKeyAuthentication()
        ## for the doc:
        #extra_actions = [
            #{   u"name": u"sort",
                #u"http_method": u"POST",
                #"resource_type": "list",
                #u"summary": doc.ContactResourceSort,
                #u"fields": dict( authdoc.items() + doc.ContactResourceSortFields.items())
            #} ]
    #def prepend_urls(self):
        #return [
            #url(r'^(?P<resource_name>%s)/sort%s$' %
                #(self._meta.resource_name, trailing_slash()),
                #self.wrap_view('sort'), name='api_sort'),
        #]

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
            create_connections.delay(user.id, data)
            #
            return self.create_response(request, {'received': True})
        else:
            return self.create_response(request, {'success': False},
                                                  HttpUnauthorized)

class InviteResource(ContactResource):
    class Meta(ContactResource.Meta):
        resource_name = 'invite'
