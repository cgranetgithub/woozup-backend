from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from service.notification import send_mail
from userprofile.models import UserProfile
from service.utils import is_personal_email, is_mobile_number
from django.utils import timezone
from link.models import Contact
from link.push import send_bulk_generic_invitation

class Command(BaseCommand):
    args = ''
    help = u"""Send the generic invitation to NEW and IGN invites
(only if never sent before)"""

    def handle(self, *args, **options):
        self.send_generic_invite()

    def send_generic_invite(self):
        # get invites
        self.stdout.write('%d invites total'%(Contact.objects.count()))
        already_sent = Contact.objects.exclude( sent_at=None )
        self.stdout.write('%d already sent'%(already_sent.count()))
        invites = Contact.objects.filter(sent_at=None).exclude(status='CLO'
                                                    ).exclude(status='PEN'
                                                    ).exclude(status='ACC')
        self.stdout.write('%d invites IGN or NEW never sent'%(invites.count()))
        with_email = invites.exclude(emails='')
        self.stdout.write('%d with emails'%(with_email.count()))
        without_email = invites.filter(emails='').exclude(numbers='')
        self.stdout.write('%d without emails (=> numbers)'%(
                                                        without_email.count()))
        # compute emails and numbers that should not be sent
        sent_emails = []
        sent_numbers = []
        for invite in already_sent:
            e = [x.strip() for x in invite.emails.split(',')]
            sent_emails += e
            n = [x.strip() for x in invite.numbers.split(',')]
            sent_numbers += n
        self.stdout.write('%d emails / %d numbers from sent invites'%(
                                len(set(sent_emails)), len(set(sent_numbers))))
        user_emails = User.objects.values_list('email', flat=True)
        user_numbers = UserProfile.objects.values_list('phone_number',
                                                       flat=True)
        self.stdout.write('%d emails / %d numbers from users'%(
                                len(set(user_emails)), len(set(user_numbers))))
        sent_emails += user_emails
        sent_numbers += user_numbers
        # filter emails
        emails = []
        for invite in with_email:
            invite.sent_at = timezone.now()
            invite.save()
            e = [x.strip() for x in invite.emails.split(',')]
            emails += e
        self.stdout.write('%d emails from new invites'%(len(set(emails))))
        emails = set(emails) - set(sent_emails)
        self.stdout.write('%d emails candidates'%(len(emails)))
        # filter numbers
        numbers = []
        for invite in without_email[:100]:
            invite.sent_at = timezone.now()
            invite.save()
            s = [x.strip() for x in invite.numbers.split(',')]
            numbers += s
        self.stdout.write('%d numbers from new invites'%(len(set(numbers))))
        numbers = set(numbers) - set(sent_numbers)
        self.stdout.write('%d sms candidates'%(len(numbers)))
        send_bulk_generic_invitation(numbers, emails)
        self.stdout.write('done')
