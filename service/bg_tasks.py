from django.db.models import Q
from django.contrib.auth.models import User

from link.models import Link, Invite

def create_link_invite(request, data):
    # 1) determine the existing connections
    email_list=[]
    create_link_list = []
    create_invite_list = []
    for i in data:
        # skip duplicates
        if i['email'] in email_list:
            continue
        else:
            email_list.append(i['email'])
        # Existing User?
        try:
            #user = User.objects.select_related().get(username=i['email'])
            user = User.objects.get(username=i['email'])
            # YES => existing Link?
            try:
                Link.objects.get(
                    ( Q(sender=request.user) & Q(receiver=user) )
                    | ( Q(sender=user) & Q(receiver=request.user) )
                                )
                # YES => nothing to do
            except Link.DoesNotExist:
                # NO => create a new Link
                link = Link(sender=request.user, receiver=user)
                create_link_list.append(link)
        except User.DoesNotExist:
            # NO => existing Invite?
            try:
                Invite.objects.get(sender=request.user,
                                    email=i['email'])
                # YES => nothing to do
            except Invite.DoesNotExist:
                # NO => create a new Invite
                invite = Invite(sender=request.user, email=i['email'])
                create_invite_list.append(invite)
    # 2) create the missing connections (bulk for better performance)
    Link.objects.bulk_create(create_link_list)
    Invite.objects.bulk_create(create_invite_list)
