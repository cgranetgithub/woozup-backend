from django.contrib.auth.models import User

def get_friends(user):
    link_as_sender = user.link_as_sender.filter(sender_status='ACC',
                                                receiver_status='ACC')
    receivers = User.objects.filter(
                                id__in=link_as_sender.values('receiver_id'))
    link_as_receiver = user.link_as_receiver.filter(sender_status='ACC',
                                                    receiver_status='ACC')
    senders = User.objects.filter(
                                id__in=link_as_receiver.values('sender_id'))
    return senders | receivers
