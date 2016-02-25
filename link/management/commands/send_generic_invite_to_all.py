from django.core.management.base import BaseCommand
from service.notification import send_mail
from link.models import Invite
from link.push import invite_ignored

class Command(BaseCommand):
    args = ''
    help = u'Send the generic invitation email to all emails found in invites'

    def handle(self, *args, **options):
        self.send_generic_invite_to_all()

    def send_generic_invite_to_all(self):
        cnt = {'emails':0, 'sms':0}
        for invite in Invite.objects.all():
            ret = invite_ignored(invite)
            cnt['emails'] += ret['emails']
            cnt['sms'] += ret['sms']
        self.stdout.write('Sent %d emails / %d SMS'%(cnt['emails'], cnt['sms']))
