from django.core.management.base import BaseCommand
from service.notification import send_mail
from link.models import Invite
from link.push import invite_validated

class Command(BaseCommand):
    args = ''
    help = u'Send the personal invitation (email/SMS) to all pending invites'

    def handle(self, *args, **options):
        self.send_personal_invite_to_pending()

    def send_personal_invite_to_pending(self):
        cnt = {'emails':0, 'sms':0}
        for invite in Invite.objects.filter(status="PEN"):
            ret = invite_validated(invite)
            cnt['emails'] += ret['emails']
            cnt['sms'] += ret['sms']
        self.stdout.write('Sent %d emails / %d SMS'%(cnt['emails'], cnt['sms']))
