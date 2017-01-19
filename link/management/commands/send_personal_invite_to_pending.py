#from django.core.management.base import BaseCommand
#from service.notification import send_mail
#from django.db.models import Q
#from link.models import Contact
#from link.push import invite_validated
#import datetime

#class Command(BaseCommand):
    #args = ''
    #help = u'Send the personal invitation (email/SMS) to all pending invites'

    #def handle(self, *args, **options):
        #self.send_personal_invite_to_pending()

    #def send_personal_invite_to_pending(self):
        #cnt = {'emails':0, 'sms':0}
        #sometimeago = datetime.datetime.now()-datetime.timedelta(1)
        #invites = Contact.objects.filter(status="PEN").filter(
                                #Q(sent_at=None) | Q(sent_at__lte=sometimeago))
        #for invite in invites[:100]:
            #ret = invite_validated(invite)
            #cnt['emails'] += ret['emails']
            #cnt['sms'] += ret['sms']
        #self.stdout.write('Sent %d emails / %d SMS'%(cnt['emails'], cnt['sms']))
