from django.db.models import Q
from django.db.models.signals import post_save
#from django.contrib.auth.models import User
from rq.decorators import job

from worker import conn
from link.models import Link, Invite
from userprofile.models import UserProfile

@job('default', connection=conn)
def create_connections(userprofile, data):
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
        # Existing UserProfile?
        try:
            contact = UserProfile.objects.get(user__username=i)
            # YES => existing Link?
            try:
                Link.objects.get(
                    ( Q(sender=userprofile) & Q(receiver=contact) )
                    | ( Q(sender=contact) & Q(receiver=userprofile) )
                                )
                # YES => nothing to do
            except Link.DoesNotExist:
                # NO => create a new Link
                link = Link(sender=userprofile, receiver=contact)
                create_link_list.append(link)
        except UserProfile.DoesNotExist:
            # NO => existing Invite?
            try:
                Invite.objects.get(sender=userprofile, userid=i)
                # YES => nothing to do
            except Invite.DoesNotExist:
                # NO => create a new Invite
                invite = Invite(sender=userprofile, userid=i,
                                email=data[i]['email'],
                                display_name=data[i]['display_name'])
                if 'local_picture_path' in data[i]:
                    invite.local_picture_path = data[i]['local_picture_path']
                create_invite_list.append(invite)
    # 2) create the missing connections (bulk for better performance)
    Link.objects.bulk_create(create_link_list)
    Invite.objects.bulk_create(create_invite_list)

def transform_invites(sender, instance, created, **kwargs):
    #if created and not instance.is_superuser:
    if created:
        create_link_list = []
        invites = Invite.objects.filter(userid=instance.user.username
                            ).exclude(status='CLO')
        for i in invites:
            link = Link(sender=i.sender, receiver=instance)
            i.status = 'CLO'
            i.save()
            create_link_list.append(link)
        Link.objects.bulk_create(create_link_list)

post_save.connect(transform_invites, sender=UserProfile)
