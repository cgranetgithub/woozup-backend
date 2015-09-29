from django.db.models import Q
from rq.decorators import job
from django.apps import apps as django_apps
from worker import conn
import phonenumbers
import django
from userprofile.models import UserProfile
from link.models import Link, Invite

def is_email(email):
    return True

def find_users_from_email(email):
    profiles = []
    try:
        contact = UserProfile.objects.get(user__username=email)
        profiles.append(contact)
    except UserProfile.DoesNotExist:
        pass
    contacts = UserProfile.objects.filter(user__email=email)
    for c in contacts:
        profiles.append(c)
    return profiles

def find_users_from_email_list(email_list):
    profiles = []
    for email in email_list:
        email = email.strip()
        if is_email(email):
            profiles += find_users_from_email(email)
    profiles = list(set(profiles))
    return profiles


@job('default', connection=conn)
def create_connections(profile, data):
    django.setup()
    create_link_list = []
    create_invite_list = []
    # for each contact
    for contact in data:
        emails = contact.get('emails', '').split(',')
        # find corresponding users
        profiles = find_users_from_email_list(emails)
        # exist => check links
        for p in profiles:
            # existing Link?
            try:
                Link.objects.get(
                    ( Q(sender=profile) & Q(receiver=p) )
                    | ( Q(sender=p) & Q(receiver=profile) )
                                )
                # YES => nothing to do
            except Link.DoesNotExist:
                # NO => create a new Link
                link = Link(sender=profile, receiver=p)
                create_link_list.append(link)
        # NO corresponding user => check invites
        if not profiles:
            name = contact.get('name', '')
            if name:
                Invite.objects.get_or_create(sender = profile, name=name,
                                             numbers = contact.get('numbers', ''),
                                             emails = contact.get('emails', ''),
                                             photo = contact.get('photo', ''))
    # create the missing connections (bulk for better performance)
    Link.objects.bulk_create(create_link_list)
    #Invite.objects.bulk_create(create_invite_list)
           

#@job('default', connection=conn)
#def create_connections(profile, data):
    #django.setup()
    ##UserProfile = django_apps.get_model('userprofile', 'UserProfile')
    ##Link        = django_apps.get_model('link', 'Link')
    ##Invite      = django_apps.get_model('link', 'Invite')
    #country_code = phonenumbers.parse(profile.user.username,
                                      #None).country_code
    ## 1) determine the existing connections
    #number_list=[]
    #create_link_list = []
    #create_invite_list = []
    #for i in data.iterkeys():
        ## normalize phonenumber and skip if fail
        #ph = None
        #try:
            #ph = phonenumbers.parse(i, None)
        #except phonenumbers.NumberParseException:
            #try:
                #ph = phonenumbers.parse(i, country_code)
            #except:
                #pass
        #ph = phonenumbers.format_number(ph, phonenumbers.PhoneNumberFormat.E164)
        #if ph is None:
            #continue
        ## skip duplicates
        #if ph in number_list:
            #continue
        #else:
            #number_list.append(ph)
        ## Existing UserProfile?
        #try:
            #contact = UserProfile.objects.get(user__username=ph)
            ## YES => existing Link?
            #try:
                #Link.objects.get(
                    #( Q(sender=profile) & Q(receiver=contact) )
                    #| ( Q(sender=contact) & Q(receiver=profile) )
                                #)
                ## YES => nothing to do
            #except Link.DoesNotExist:
                ## NO => create a new Link
                #link = Link(sender=profile, receiver=contact)
                #create_link_list.append(link)
        #except UserProfile.DoesNotExist:
            ## NO => existing Invite?
            #try:
                #Invite.objects.get(sender=profile, number=ph)
                ## YES => nothing to do
            #except Invite.DoesNotExist:
                ## NO => create a new Invite
                #invite = Invite(sender=profile, number=ph,
                                #email=data[i]['email'],
                                #name=data[i]['name'])
                #if 'photo' in data[i]:
                    #invite.photo = data[i]['photo']
                #create_invite_list.append(invite)
    ## 2) create the missing connections (bulk for better performance)
    #Link.objects.bulk_create(create_link_list)
    #Invite.objects.bulk_create(create_invite_list)

# called by userprofile.apps on post_save signal
def transform_invites(sender, instance, created, **kwargs):
    django.setup()
    if created:
        create_link_list = []
        invites = Invite.objects.filter(
                                numbers__icontains=instance.user.username
                                ).exclude(status='CLO')
        invites = invites | Invite.objects.filter(
                                emails__icontains=instance.user.username
                                ).exclude(status='CLO')
        if instance.phone_number:
            invites = invites | Invite.objects.filter(
                                    numbers__icontains=instance.phone_number
                                    ).exclude(status='CLO')
        if instance.user.email:
            invites = invites | Invite.objects.filter(
                                    emails__icontains=instance.user.email
                                    ).exclude(status='CLO')
        for i in invites:
            link = Link(sender=i.sender, receiver=instance)
            create_link_list.append(link)
            i.status = 'CLO'
            i.save()
        Link.objects.bulk_create(create_link_list)
