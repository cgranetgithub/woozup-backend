from push_notifications.models import APNSDevice, GCMDevice

from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import SessionAuthentication

from userprofile.api import UserResource

class GCMDeviceAuthenticatedResource(ModelResource):
    user = fields.ToOneField(UserResource, "user")

    class Meta:
        resource_name = "device/gcm"
        queryset = GCMDevice.objects.all()
        list_allowed_methods = ['post']
        detail_allowed_methods = []
        authorization  = DjangoAuthorization()
        authentication = SessionAuthentication()
                
    def obj_create(self, bundle, **kwargs):
            # See https://github.com/toastdriven/django-tastypie/issues/854
            return super(GCMDeviceAuthenticatedResource, self).obj_create(
                                bundle, user=bundle.request.user, **kwargs)

def send_notification(userlist, message):
    try:
        devices = GCMDevice.objects.filter(user__in=userlist)
        print devices
        devices.send_message(message)
    except:
        print "!!!exception!!!"
