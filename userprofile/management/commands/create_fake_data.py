import random
import datetime as dt
from link.models import Link, Invite
from event.models import Event, EventType
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    args = u'phone number of the user'
    help = u'Create some fake data to testing'

    def handle(self, *args, **options):
        self.generate_data(args[0])
        #stdout.write('Successfully get_or_create std group')

    def gen_u_name(self):
        return '+336%s'%(random.randint(00000000, 99999999))

    def generate_data(self, username):
        # users
        u1 = User.objects.get(username=username)
        u2 = User.objects.create_user(username=self.gen_u_name(), password='pwd')
        u3 = User.objects.create_user(username=self.gen_u_name(), password='pwd')
        u4 = User.objects.create_user(username=self.gen_u_name(), password='pwd')
        u5 = User.objects.create_user(username=self.gen_u_name(), password='pwd')
        u6 = User.objects.create_user(username=self.gen_u_name(), password='pwd')
        u7 = User.objects.create_user(username=self.gen_u_name(), password='pwd')
        u8 = User.objects.create_user(username=self.gen_u_name(), password='pwd')
        # links
        l1 = Link.objects.get_or_create(sender=u1.userprofile,
                                      receiver=u2.userprofile)
        l2 = Link.objects.get_or_create(sender=u1.userprofile,
                                      receiver=u3.userprofile)
        l3 = Link.objects.get_or_create(sender=u1.userprofile,
                                      receiver=u4.userprofile)
        l4 = Link.objects.get_or_create(sender=u5.userprofile,
                                      receiver=u1.userprofile)
        l5 = Link.objects.get_or_create(sender=u6.userprofile,
                                      receiver=u1.userprofile)
        l6 = Link.objects.get_or_create(sender=u7.userprofile,
                                      receiver=u1.userprofile)
        # invites
        Invite.objects.get_or_create(sender=u1.userprofile,
                            number='+3365678956',
                            email='invite1@fr.fr',
                            name='invite1')
        Invite.objects.get_or_create(sender=u1.userprofile,
                            number='+3365678988',
                            email='invite2@fr.fr',
                            name='invite2')
        # events
        Event.objects.get_or_create(owner=u1.userprofile,
                             name='great event',
                             start=dt.datetime.now()+dt.timedelta(1),
                             event_type=EventType.objects.first(),
                             position="{ 'type':'Point', 'coordinates':[2.35, 48.853] }")
        Event.objects.get_or_create(owner=u2.userprofile,
                             name='funny event',
                             start=dt.datetime.now()+dt.timedelta(1),
                             event_type=EventType.objects.first(),
                             position="{ 'type':'Point', 'coordinates':[2.35, 48.853] }")
        Event.objects.get_or_create(owner=u3.userprofile,
                             name='crazy event',
                             start=dt.datetime.now()+dt.timedelta(1),
                             event_type=EventType.objects.first(),
                             position="{ 'type':'Point', 'coordinates':[2.35, 48.853] }")

