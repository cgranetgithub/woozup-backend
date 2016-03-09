# from userprofile.models import UserProfile
#
# def get_user_friends(userprofile):
#     link_as_sender = userprofile.link_as_sender.filter(
#                             sender_status='ACC',
#                             receiver_status='ACC')
#     receivers = UserProfile.objects.filter(
#                             user_id__in=link_as_sender.values('receiver_id'))
#     link_as_receiver = userprofile.link_as_receiver.filter(
#                             sender_status='ACC',
#                             receiver_status='ACC')
#     senders = UserProfile.objects.filter(
#                             user_id__in=link_as_receiver.values('sender_id'))
#     return senders | receivers
