from django.db.models import Q
from django.contrib.auth.models import User
from rq.decorators import job

from worker import conn
from link.models import Link, Invite

@job('default', connection=conn)
def create_connections(user, data):
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
            #contact = User.objects.select_related().get(username=i['email'])
            contact = User.objects.get(username=i['email'])
            # YES => existing Link?
            try:
                Link.objects.get(
                    ( Q(sender=user) & Q(receiver=contact) )
                    | ( Q(sender=contact) & Q(receiver=user) )
                                )
                # YES => nothing to do
            except Link.DoesNotExist:
                # NO => create a new Link
                link = Link(sender=user, receiver=contact)
                create_link_list.append(link)
        except User.DoesNotExist:
            # NO => existing Invite?
            try:
                Invite.objects.get(sender=user,
                                    email=i['email'])
                # YES => nothing to do
            except Invite.DoesNotExist:
                # NO => create a new Invite
                invite = Invite(sender=user, email=i['email'])
                create_invite_list.append(invite)
    # 2) create the missing connections (bulk for better performance)
    Link.objects.bulk_create(create_link_list)
    Invite.objects.bulk_create(create_invite_list)

def transform_invites(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        create_link_list = []
        invites = Invite.objects.filter(receiver=instance.username
                            ).exclude(status='CLO')
        for i in invites:
            link = Link(sender=i.sender, receiver=instance)
            i.status = 'CLO'
            i.save()
            create_link_list.append(link)
        Link.objects.bulk_create(create_link_list)
