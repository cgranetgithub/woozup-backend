from django.db.models import Q
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from rq.decorators import job

from worker import conn
from link.models import Link, Invite

@job('default', connection=conn)
def create_connections(user, data):
    # 1) determine the existing connections
    username_list=[]
    create_link_list = []
    create_invite_list = []
    for i in data.iterkeys():
        # skip duplicates
        if i in username_list:
            continue
        else:
            username_list.append(i)
        # Existing User?
        try:
            contact = User.objects.get(username=i)
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
                Invite.objects.get(sender=user, userid=i)
                # YES => nothing to do
            except Invite.DoesNotExist:
                # NO => create a new Invite
                invite = Invite(sender=user, userid=i,
                                email=data[i]['email'],
                                display_name=data[i]['display_name'])
                if 'local_picture_path' in data[i]:
                    invite.local_picture_path = data[i]['local_picture_path']
                create_invite_list.append(invite)
    # 2) create the missing connections (bulk for better performance)
    Link.objects.bulk_create(create_link_list)
    Invite.objects.bulk_create(create_invite_list)

def transform_invites(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        create_link_list = []
        invites = Invite.objects.filter(userid=instance.username
                            ).exclude(status='CLO')
        for i in invites:
            link = Link(sender=i.sender, receiver=instance)
            i.status = 'CLO'
            i.save()
            create_link_list.append(link)
        Link.objects.bulk_create(create_link_list)

post_save.connect(transform_invites, sender=User)
