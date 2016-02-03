
def send_notification(userprofilelist, data):
    from push_notifications.models import APNSDevice, GCMDevice

    ### temporary, to be removed
    data['msg'] = data['message']
    data['ttl'] = data['title']
    ###

    android_push = GCMDevice.objects.filter(user__userprofile__in=userprofilelist,
                                            active=True)
    android_push.send_message(data['message'], extra=data)
    ios_push = APNSDevice.objects.filter(user__userprofile__in=userprofilelist)
    ios_push.send_message(data['message'], extra=data)


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
