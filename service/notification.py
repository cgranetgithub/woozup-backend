from push_notifications.models import APNSDevice, GCMDevice

def send_notification(userprofilelist, data):
    #try:
    devices = GCMDevice.objects.filter(user__userprofile__in=userprofilelist)
    devices.send_message(data['msg'], extra=data)
    #except:
        #print u"!!!exception (normal on PC)!!!"


# BACKGROUND JOB VERSION

#from push_notifications.models import APNSDevice, GCMDevice
#from rq.decorators import job
#from worker import conn

#@job('low', connection=conn)
#def send_message(userlist, message):
    #devices = GCMDevice.objects.filter(user__in=userlist)
    #devices.send_message({'message':message})

#def send_notification(userlist, message):
    ## launch background processing
    #send_message.delay(userlist, message)
