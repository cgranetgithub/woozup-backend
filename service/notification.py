from push_notifications.models import APNSDevice, GCMDevice
#from push_notifications.api import GCMDeviceAuthenticatedResource
#from django.contrib.auth.models import User

#from tastypie import fields
#from tastypie.resources import ModelResource
#from tastypie.authorization import DjangoAuthorization
#from tastypie.authentication import ApiKeyAuthentication

#class GCMDeviceAuthenticatedResource(ModelResource):
    #class Meta:
        #resource_name = "device/gcm"
        #queryset = GCMDevice.objects.all()
        #list_allowed_methods = ['post']
        #detail_allowed_methods = []
        ##authorization  = DjangoAuthorization()
        ##authentication = ApiKeyAuthentication()
                
    ##def obj_create(self, bundle, **kwargs):
        ##print kwargs
        ##user = User.objects.get(username=bundle.request.user.username)
        ###kwargs['user'] = user #force owner to the authorized user
        ##print kwargs, bundle
        ##return super(GCMDeviceAuthenticatedResource, self).obj_create(
                                                        ##bundle, user=user, **kwargs)

#class Gcm(GCMDeviceAuthenticatedResource):
    #class Meta(GCMDeviceAuthenticatedResource.Meta):
        #authorization  = DjangoAuthorization()
        #authentication = ApiKeyAuthentication()

def send_notification(userlist, message):
    #if isinstance(message, unicode):
        #message = message.encode('utf-8')
    print type(message), message, userlist
    #try:
    devices = GCMDevice.objects.filter(user__in=userlist)
    print devices
    devices.send_message({'message':message})
    #except:
        #print u"!!!exception (normal on PC)!!!"