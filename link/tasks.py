# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

from django.db.models import Q
from service.utils import get_clean_number
from django.contrib.auth import get_user_model

from rq.decorators import job
from worker import conn
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

def get_clean_data(contact, key):
    try:
        data = contact.get(key)
        if not data:
            return []
    except:
        return []
    raw_data_list = data.split(',')
    new_data_list = []
    for i in raw_data_list:
        i = i.strip()
        if i not in new_data_list:
            new_data_list.append(i)
    new_data_list.sort()
    return new_data_list
    
def is_email(email):
    return ( '@' in email )

def get_clean_emails(contact):
    raw_email_list = get_clean_data(contact, 'emails')
    new_email_list = []
    for i in raw_email_list:
        if is_email(i):
            new_email_list.append(i)
    return new_email_list

def get_clean_numbers(contact):
    raw_number_list = get_clean_data(contact, 'numbers')
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
def create_connections(userId, data):
    import django
    django.setup()
    from link.models import Contact, Link
    from link.push import friend_registered
    user = get_user_model().objects.get(id=userId)
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
                    friend_registered(user, u)
        # NO corresponding user => check invites
        if not users:
            name = contact.get('name', '')
            emails = ', '.join(email_list)
            numbers = ', '.join(number_list)
            photo = get_clean_data(contact, 'photo')
            if name and not name.startswith('.'):
                if emails:
                    try:
                        invite = Contact.objects.get(sender = user,
                                                     emails = emails)
                        invite.name = name
                        invite.numbers = numbers
                        invite.photo = photo
                        invite.save()
                    except Contact.DoesNotExist:
                        if numbers:
                            try:
                                invite = Contact.objects.get(sender = user,
                                                            numbers = numbers)
                                invite.name = name
                                invite.emails = emails
                                invite.photo = photo
                                invite.save()
                            except Contact.DoesNotExist:
                                Contact.objects.create(sender = user,
                                                      name=name,
                                                      emails = emails,
                                                      numbers = numbers)
                            except:
                                logger.error("""contact has no corresponding \
user, name/emails/numbers exist, more than one Contact with same numbers \
%s %s %s"""%(name, emails, numbers))
                elif numbers:
                    try:
                        invite = Contact.objects.get(sender = user,
                                                    numbers = numbers)
                        invite.name = name
                        #invite.emails = emails #not needed
                        invite.photo = photo
                        invite.save()
                    except Contact.DoesNotExist:
                        Contact.objects.create(sender = user, name=name,
                                              emails = emails,
                                              numbers = numbers,
                                              photo = photo)
                    except:
                        logger.error("""contact has no corresponding user, \
no emails, name/numbers exist, more than one Contact with same numbers \
%s %s"""%(name, numbers))


@job('default', connection=conn)
def transform_contacts(userId):
    import django
    django.setup()
    from .models import Link, Contact
    from .utils import get_link
    from .push import friend_registered
    user = get_user_model().objects.get(id=userId)
    from_email = from_num = Contact.objects.none()
    if user.email:
        from_email = Contact.objects.filter(emails__icontains=user.email
                                            ).exclude(status='CLO')
    if hasattr(user, 'number') and user.number:
        phone_number = user.number.phone_number
        from_num = Contact.objects.filter(numbers__icontains=phone_number
                                            ).exclude(status='CLO')
    contacts = from_email | from_num
    for i in contacts:
        if user != i.sender:
            # create link
            if not get_link(i.sender, user):
                Link.objects.create(sender=i.sender, receiver=user)
                i.status = 'CLO'
                i.save()
                friend_registered(user, i.sender, i.name)
            # find event as invited contact and add to invitees
            from event.models import Event
            events = Event.objects.filter(contacts=i)
            for e in events:
                e.invitees.add(user)


@receiver(post_save, sender="userprofile.Number")
def enqueue_transform_invites_from_number(sender, instance, **kwargs):
    if instance.phone_number and instance.user:
        transform_contacts.delay(instance.user.id)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def enqueue_transform_invites_from_user(sender, instance, **kwarg):
    transform_contacts.delay(instance.id)
