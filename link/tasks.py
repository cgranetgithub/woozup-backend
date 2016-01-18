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

def get_clean_emails(contact):
    try:
        emails = contact.get('emails')
        emails = emails.strip()
        if not emails:
            return []
    except:
        return []
    raw_email_list = emails.split(',')
    new_email_list = []
    for i in raw_email_list:
        if is_email(i):
            new_email_list.append(i.strip())
    result = list(set(new_email_list))
    result.sort()
    return result

def get_clean_numbers(contact):
    try:
        numbers = contact.get('numbers')
        numbers = numbers.strip()
        if not numbers:
            return []
    except:
        return []
    raw_number_list = numbers.split(',')
    new_number_list = []
    ### hardcoded, need to fix it
    country_code = 'FR'
    ###
    for i in raw_number_list:
        # normalize phonenumber and skip if fail
        ph = None
        try:
            ph = phonenumbers.parse(i, None)
        except phonenumbers.NumberParseException:
            try:
                ph = phonenumbers.parse(i, country_code)
            except:
                continue
        # chck if validate num
        if (phonenumbers and phonenumbers.is_possible_number(ph)
            and phonenumbers.is_valid_number(ph)):
                num = phonenumbers.format_number(ph, phonenumbers.PhoneNumberFormat.E164)
                # skip duplicates
                if num not in new_number_list:
                    new_number_list.append(num)
    #result = list(set(new_number_list))
    #result.sort()
    return new_number_list

#def find_users_from_email(email):
    #profiles = []
    #try:
        #contact = UserProfile.objects.get(user__username=email)
        #profiles.append(contact)
    #except UserProfile.DoesNotExist:
        #pass
    #contacts = UserProfile.objects.filter(user__email=email)
    #for c in contacts:
        #profiles.append(c)
    #return set(profiles)

def find_users_from_email_list(email_list):
    #profiles = []
    #for email in email_list:
        #profiles += find_users_from_email(email)
    l1 = UserProfile.objects.filter(user__username__in=email_list)
    l2 = UserProfile.objects.filter(user__email__in=email_list)
    return l1 | l2


@job('default', connection=conn)
def create_connections(profile, data):
    django.setup()
    # for each contact
    for contact in data:
        email_list = get_clean_emails(contact)
        number_list = get_clean_numbers(contact)
        # find corresponding users
        profiles = find_users_from_email_list(email_list)
        # exist => check links
        for p in profiles:
            if profile != p:
                # existing Link?
                try:
                    Link.objects.get(
                        ( Q(sender=profile) & Q(receiver=p) )
                        | ( Q(sender=p) & Q(receiver=profile) )
                                    )
                    # YES => nothing to do
                except Link.DoesNotExist:
                    # NO => create a new Link
                    Link.objects.create(sender=profile, receiver=p)
        # NO corresponding user => check invites
        if not profiles:
            name = contact.get('name', '')
            emails = ', '.join(email_list)
            numbers = ', '.join(number_list)
            photo = contact.get('photo', '')
            if name:
                if emails:
                    try:
                        invite = Invite.objects.get(sender = profile,
                                                    emails = emails)
                        invite.name = name
                        invite.numbers = numbers
                        invite.photo = photo
                        invite.save()
                    except Invite.DoesNotExist:
                        if numbers:
                            try:
                                invite = Invite.objects.get(sender = profile,
                                                            numbers = numbers)
                                invite.name = name
                                invite.emails = emails
                                invite.photo = photo
                                invite.save()
                            except Invite.DoesNotExist:
                                Invite.objects.create(sender = profile,
                                                      name=name,
                                                      emails = emails,
                                                      numbers = numbers)
                elif numbers:
                    try:
                        invite = Invite.objects.get(sender = profile,
                                                    numbers = numbers)
                        invite.name = name
                        invite.emails = emails
                        invite.photo = photo
                        invite.save()
                    except Invite.DoesNotExist:
                        Invite.objects.create(sender = profile, name=name,
                                              emails = emails,
                                              numbers = numbers,
                                              photo = photo)

# called by userprofile.apps on post_save signal
def transform_invites(sender, instance, created, **kwargs):
    django.setup()
    if created:
        create_link_list = []
        invites = Invite.objects.none()
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
