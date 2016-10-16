# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

from django.db.models import Q
from rq.decorators import job
from worker import conn
import django
from service.utils import get_clean_number
from django.contrib.auth import get_user_model

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
    for i in raw_number_list:
        num = get_clean_number(i)
        # skip duplicates
        if num and num not in new_number_list:
            new_number_list.append(num)
    new_number_list.sort()
    return new_number_list

#def find_users_from_email_list(email_list):
    #if email_list:
        #l1 = Profile.objects.filter(user__username__in=email_list)
        #l2 = Profile.objects.filter(user__email__in=email_list)
        #return l1 | l2
    #else:
        #return Profile.objects.none()

def find_users_from_number_list(number_list):
    if number_list:
        l1 = get_user_model().objects.filter(username__in=number_list)
        l2 = get_user_model().objects.filter(number__phone_number__in=number_list)
        return l1 | l2
    else:
        return get_user_model().objects.none()

@job('default', connection=conn)
def create_connections(userid, data):
    import django
    django.setup()
    from link.models import Invite, Link
    user = get_user_model().objects.get(id=userid)
    # for each contact
    for contact in data:
        email_list = get_clean_emails(contact)
        number_list = get_clean_numbers(contact)
        # find corresponding users
        #profiles = find_users_from_email_list(email_list)
        users = find_users_from_number_list(number_list)
        # exist => check links
        for u in users:
            if user != u:
                # existing Link?
                try:
                    Link.objects.get(
                        ( Q(sender=user) & Q(receiver=u) )
                        | ( Q(sender=u) & Q(receiver=user) )
                                    )
                    # YES => nothing to do
                except Link.DoesNotExist:
                    # NO => create a new Link
                    Link.objects.create(sender=user, receiver=u)
        # NO corresponding user => check invites
        if not users:
            name = contact.get('name', '')
            emails = ', '.join(email_list)
            numbers = ', '.join(number_list)
            photo = contact.get('photo', '')
            if name and not name.startswith('.'):
                if emails:
                    try:
                        invite = Invite.objects.get(sender = user,
                                                    emails = emails)
                        invite.name = name
                        invite.numbers = numbers
                        invite.photo = photo
                        invite.save()
                    except Invite.DoesNotExist:
                        if numbers:
                            try:
                                invite = Invite.objects.get(sender = user,
                                                            numbers = numbers)
                                invite.name = name
                                invite.emails = emails
                                invite.photo = photo
                                invite.save()
                            except Invite.DoesNotExist:
                                Invite.objects.create(sender = user,
                                                      name=name,
                                                      emails = emails,
                                                      numbers = numbers)
                            except:
                                logger.error("""contact has no corresponding \
user, name/emails/numbers exist, more than one Invite with same numbers \
%s %s %s"""%(name, emails, numbers))
                elif numbers:
                    try:
                        invite = Invite.objects.get(sender = user,
                                                    numbers = numbers)
                        invite.name = name
                        #invite.emails = emails #not needed
                        invite.photo = photo
                        invite.save()
                    except Invite.DoesNotExist:
                        Invite.objects.create(sender = user, name=name,
                                              emails = emails,
                                              numbers = numbers,
                                              photo = photo)
                    except:
                        logger.error("""contact has no corresponding user, \
no emails, name/numbers exist, more than one Invite with same numbers \
%s %s"""%(name, numbers))

# called by userprofile.apps on post_save signal
def transform_invites_from_number(sender, instance, **kwargs):
    from userprofile.models import Number
    assert type(instance) is Number
    if (not instance.phone_number) or (not instance.user):
        return 0
    user = instance.user
    cnt = 0
    from link.models import Link, Invite
    invites = Invite.objects.filter(numbers__icontains=instance.phone_number
                                    ).exclude(status='CLO')
    for i in invites:
        if user != i.sender:
            try:
                Link.objects.get(sender=user, receiver=i.sender)
            except Link.DoesNotExist:
                try:
                    Link.objects.get(sender=i.sender, receiver=user)
                except Link.DoesNotExist:
                    Link.objects.create(sender=i.sender, receiver=user)
                    i.status = 'CLO'
                    i.save()
                    cnt += 1
    return cnt

# called by userprofile.apps on post_save signal
def transform_invites_from_user(sender, instance, **kwarg):
    assert type(instance) is get_user_model()
    user = instance
    if not user.email:
        return 0
    cnt = 0
    from link.models import Link, Invite
    invites = Invite.objects.filter(emails__icontains=user.email
                                    ).exclude(status='CLO')
    for i in invites:
        if user != i.sender:
            try:
                Link.objects.get(sender=user, receiver=i.sender)
            except Link.DoesNotExist:
                try:
                    Link.objects.get(sender=i.sender,
                                     receiver=user)
                except Link.DoesNotExist:
                    Link.objects.create(sender=i.sender,
                                        receiver=user)
                    i.status = 'CLO'
                    i.save()
                    cnt += 1
    return cnt
