from userprofile.models import UserProfile

def get_user_friends(userprofile):
    #return UserProfile.objects.filter(
                        #( Q(link_as_sender__sender    =userprofile) |
                          #Q(link_as_sender__receiver  =userprofile) |
                          #Q(link_as_receiver__sender  =userprofile) |
                          #Q(link_as_receiver__receiver=userprofile) ),
                        #( Q(link_as_sender__sender_status='ACC') &
                          #Q(link_as_sender__receiver_status='ACC') ) |
                        #( Q(link_as_receiver__sender_status='ACC') &
                          #Q(link_as_receiver__receiver_status='ACC') ) )
    link_as_sender = userprofile.link_as_sender.filter(
                            sender_status='ACC',
                            receiver_status='ACC')
    receivers = UserProfile.objects.filter(
                            user_id__in=link_as_sender.values('receiver_id'))
    link_as_receiver = userprofile.link_as_receiver.filter(
                            sender_status='ACC',
                            receiver_status='ACC')
    senders = UserProfile.objects.filter(
                            user_id__in=link_as_receiver.values('sender_id'))
    return senders | receivers
