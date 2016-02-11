from django.core.management.base import BaseCommand, CommandError
from service.notification import send_mail
from link.models import Invite

class Command(BaseCommand):
    args = ''
    help = u'Send the generic invitation email to all invites emails'

    def handle(self, *args, **options):
        self.send_all_invites()

    def send_all_invites(self):
        count = 0
        for invite in Invite.objects.all():
            if invite.emails:
                template_prefix = "link/email/generic_invite"
                emails = invite.emails.split(',')
                context = {}
                send_mail(template_prefix, emails, context)
                count += len(emails)
        self.stdout.write('Sent %d emails'%count)
