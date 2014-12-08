from django.db.models import Q
from rq.decorators import job
from django.apps import apps as django_apps
from worker import conn
import django

@job('default', connection=conn)
def create_connections(u_profile_id, data):
    django.setup()
    UserProfile = django_apps.get_model('userprofile', 'UserProfile')
    Link        = django_apps.get_model('link', 'Link')
    Invite      = django_apps.get_model('link', 'Invite')
    user_profile = UserProfile.objects.get(id=u_profile_id)
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
                    ( Q(sender=user_profile) & Q(receiver=contact) )
                    | ( Q(sender=contact) & Q(receiver=user_profile) )
                                )
                # YES => nothing to do
            except Link.DoesNotExist:
                # NO => create a new Link
                link = Link(sender=user_profile, receiver=contact)
                create_link_list.append(link)
        except UserProfile.DoesNotExist:
            # NO => existing Invite?
            try:
                Invite.objects.get(sender=user_profile, number=i)
                # YES => nothing to do
            except Invite.DoesNotExist:
                # NO => create a new Invite
                invite = Invite(sender=user_profile, number=i,
                                email=data[i]['email'],
                                name=data[i]['name'])
                if 'photo' in data[i]:
                    invite.photo = data[i]['photo']
                create_invite_list.append(invite)
    # 2) create the missing connections (bulk for better performance)
    Link.objects.bulk_create(create_link_list)
    Invite.objects.bulk_create(create_invite_list)

def transform_invites(sender, instance, created, **kwargs):
    django.setup()
    Link = django_apps.get_model('link', 'Link')
    Invite = django_apps.get_model('link', 'Invite')
    #if created and not instance.is_superuser:
    if created:
        create_link_list = []
        invites = Invite.objects.filter(number=instance.user.username
                            ).exclude(status='CLO')
        for i in invites:
            link = Link(sender=i.sender, receiver=instance)
            i.status = 'CLO'
            i.save()
            create_link_list.append(link)
        Link.objects.bulk_create(create_link_list)

#post_save.connect(transform_invites, sender=UserProfile)
