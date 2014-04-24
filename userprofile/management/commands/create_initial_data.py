from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    args = ''
    help = 'Create the mandatory initial objects'

    def handle(self, *args, **options):
        self.createStdGroup()
        self.stdout.write('Successfully create std group')

    def createStdGroup(self):
        p1 = Permission.objects.get(codename='add_event')
        p2 = Permission.objects.get(codename='change_event')
        p3 = Permission.objects.get(codename='delete_event')
        grp = Group.objects.create(name='std')
        grp.permissions.add(p1, p2, p3)
        return grp
        