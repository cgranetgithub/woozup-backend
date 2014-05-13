from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    args = ''
    help = 'Create the mandatory initial objects'

    def handle(self, *args, **options):
        self.createStdGroup()
        #self.stdout.write('Successfully create std group')

    def createStdGroup(self):
        p = []
        for i in ['add_event', 'change_event', 'delete_event',
                  'add_link' , 'change_link' , 'delete_link'] :
            p.append(Permission.objects.get(codename=i))
        grp = Group.objects.create(name='std')
        grp.permissions = p
        return grp
