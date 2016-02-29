from django.core.management.base import BaseCommand
from userprofile.models import UserProfile
from link.tasks import (transform_invites_from_profile,
                        transform_invites_from_user)

class Command(BaseCommand):
    args = ''
    help = u'Send the personal invitation (email/SMS) to all pending invites'

    def handle(self, *args, **options):
        self.launch_transform_invite()

    def launch_transform_invite(self):
        cnt_p = 0
        cnt_u = 0
        for u in UserProfile.objects.all():
            cnt_p += transform_invites_from_profile(None, u)
            cnt_u += transform_invites_from_user(None, u.user)
        self.stdout.write('''Created %d links from profile (phone number)
and %d from user (email)'''%(cnt_p, cnt_u))
