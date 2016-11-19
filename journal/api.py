from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import ApiKeyAuthentication
from django.contrib.auth import get_user_model

from .models import Record
from userprofile.api import UserResource
from event.api import AllEventsResource
from userprofile.utils import get_friends

class RecordResource(ModelResource):
    user = fields.ToOneField(UserResource, 'user', full=True)
    refering_event = fields.ToOneField(AllEventsResource, 'refering_event', full=True, null=True)
    refering_user = fields.ToOneField(UserResource, 'refering_user', full=True, null=True)
    class Meta:
        resource_name = 'record'
        queryset = Record.objects.all()
        authorization  = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        allowed_methods = ['get']

    def get_object_list(self, request):
        user = request.user
        #me = get_user_model().objects.filter(id=user.id)
        myfriends = get_friends(user)
        #concerned = me | myfriends
        concerned = myfriends
        user_records = Record.objects.filter(user__in=concerned).distinct()
        ref_records = Record.objects.filter(refering_user__in=concerned).distinct()
        return user_records | ref_records
        