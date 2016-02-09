# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

from django.db.models import Q
from rq.decorators import job
from django.apps import apps as django_apps
from worker import conn
import phonenumbers
import django
from userprofile.models import UserProfile
from link.models import Link, Invite

def is_email(email):
    return ( '@' in email )

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
        # check if validate num
        if (phonenumbers and phonenumbers.is_possible_number(ph)
            and phonenumbers.is_valid_number(ph)):
                num = phonenumbers.format_number(ph, phonenumbers.PhoneNumberFormat.E164)
                # skip duplicates
                if num not in new_number_list:
                    new_number_list.append(num)
    #result = list(set(new_number_list))
    new_number_list.sort()
    return new_number_list

def find_users_from_email_list(email_list):
    l1 = UserProfile.objects.filter(user__username__in=email_list)
    l2 = UserProfile.objects.filter(user__email__in=email_list)
    return l1 | l2

def find_users_from_number_list(number_list):
    l1 = UserProfile.objects.filter(user__username__in=number_list)
    l2 = UserProfile.objects.filter(phone_number__in=number_list)
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
        profiles = profiles | find_users_from_number_list(number_list)
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
            if name and not name.startswith('.'):
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
                            except:
                                logger.error("""contact has no corresponding \
profile, name/emails/numbers exist, more than one Invite with same numbers \
%s %s %s"""%(name, emails, numbers))
                elif numbers:
                    try:
                        invite = Invite.objects.get(sender = profile,
                                                    numbers = numbers)
                        invite.name = name
                        #invite.emails = emails #not needed
                        invite.photo = photo
                        invite.save()
                    except Invite.DoesNotExist:
                        Invite.objects.create(sender = profile, name=name,
                                              emails = emails,
                                              numbers = numbers,
                                              photo = photo)
                    except:
                        logger.error("""contact has no corresponding profile, \
no emails, name/numbers exist, more than one Invite with same numbers \
%s %s"""%(name, numbers))

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
