#import random, string
#import datetime as dt
#from link.models import Link, Invite
#from event.models import Event, EventType, EventCategory
##!/usr/bin/python
## -*- coding: utf8 -*-

#from django.contrib.auth.models import User
#from django.core.management.base import BaseCommand, CommandError

#class Command(BaseCommand):
    #args = u'phone number, password, first_name'
    #help = u'Create some fake data to testing'

    #def handle(self, *args, **options):
        #self.generate_data(args[0], args[1], args[2])
        ##stdout.write('Successfully get_or_create std group')

    #def gen_u_name(self):
        #return '+336%s'%(random.randint(11111111, 99999999))

    #def generate_data(self, username, password, first_name):
        ## users
        #(u1, created) = User.objects.get_or_create(username=username,
                                                   #password=password,
                                                   #first_name=first_name)
        #names = [u'john', u'charles', u'michael', u'bill', u'mike', u'dean',
                 #u'robert', u'gustave', u'philip', u'henry', u'simon',
                 #u'francois', u'richard', u'bernard']
        #for i in range(30):
            #name = random.sample(names,1)[0] + unicode(i)
            #(u, created) = User.objects.get_or_create(
                                      #username=self.gen_u_name(),
                                      #defaults={'password':'pwd',
                                                #'first_name':name,
                                                #'last_name':i,
                                                #'email':name + '@test.test'})
            #u.userprofile.image = 'UserProfile/%s.jpeg'%random.randint(1, 5)
            #u.userprofile.save()
        ## links
        #users = User.objects.all().exclude(username=username).exclude(username='charles')
        #for i in range(20):
            #(l, created) = Link.objects.get_or_create(
                            #sender=u1.userprofile,
                            #receiver=random.sample(users,1)[0].userprofile)
            #l.sender_status = 'ACC'
            #l.receiver_status = 'ACC'
            #l.save()
        ## invites
        #Invite.objects.get_or_create(sender=u1.userprofile,
                            #number='+3365678956',
                            #email='invite1@fr.fr',
                            #name='invite1')
        #Invite.objects.get_or_create(sender=u1.userprofile,
                            #number='+3365678988',
                            #email='invite2@fr.fr',
                            #name='invite2')
        ## events
        #cat_names = ['repas', 'verre', 'sport', 'plein air', 'jeux',
                     #'professionnel', 'travaux', 'famille']
        #for c in cat_names:
            #(ec, created) = EventCategory.objects.get_or_create(
                                        #name=c, 
                                        #defaults={'short_name':c,
                                                  #'description':c,
                                                  #'image':'glyph/alert.png'})
            #(et, created) = EventType.objects.get_or_create(
                                        #name=c, 
                                        #defaults={'short_name':c,
                                                  #'description':c,
                                                  #'image':'glyph/alert.png'})
            #et.category.add(ec)
        #types = EventType.objects.all()
        #for i in range(10):
            #Event.objects.get_or_create(owner=u1.userprofile,
                             #name=''.join(random.choice(string.lowercase) for i in range(5)),
                             #start=dt.datetime.now()+dt.timedelta(1),
                             #event_type=random.sample(types,1)[0],
                             #position="{ 'type':'Point', 'coordinates':[2.35, 48.853] }")
