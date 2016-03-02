from django.core.management.base import BaseCommand
from service.notification import send_mail
from django.db.models import Q
from django.utils import timezone
from link.models import Invite
from link.push import send_bulk_generic_invitation

class Command(BaseCommand):
    args = ''
    help = u"""Send the generic invitation to NEW and IGN invites
(only if never sent before)"""

    def handle(self, *args, **options):
        self.send_generic_invite()

    def send_generic_invite(self):
        cnt = {'emails':0, 'sms':0}
        self.stdout.write('Total invites: %d'%(Invite.objects.count()))
        invites = Invite.objects.filter( Q(status='IGN') | Q(status='NEW')
                               ).filter( sent_at=None )
        self.stdout.write('Invites with criteria: %d'%(invites.count()))
        with_email = invites.exclude(emails='')
        self.stdout.write('Invites with emails: %d'%(with_email.count()))
        without_email = invites.filter(emails='').exclude(numbers='')
        self.stdout.write('Invites with without emails: %d'%(
                                                        without_email.count()))
        emails = []
        numbers = []
        for invite in with_email:
            e = [x.strip() for x in invite.emails.split(',')]
            emails += e
            invite.sent_at = timezone.now()
            invite.save()
        emails = list(set(emails))
        self.stdout.write('Sending %d emails'%(len(emails)))
        for invite in without_email[:700]:
            n = [x.strip() for x in invite.numbers.split(',')]
            numbers += n
            invite.sent_at = timezone.now()
            invite.save()
        numbers = list(set(numbers))
        ### hack
        french_filtered = [x for x in numbers if ( x.startswith('+336')
                                                or x.startswith('+337') )]
        ###
        self.stdout.write('Sending %d sms'%(len(french_filtered)))
        send_bulk_generic_invitation(french_filtered, emails)
        for i in invites:
            i.sent_at = timezone.now()
            i.save()
        self.stdout.write('done')
