import json

from django.test import TestCase
from django.utils.http import urlquote_plus
from django.test.client import Client
from django.core.management import call_command
from django.contrib.auth.models import User
#from tastypie.test import ResourceTestCase

from link.tasks import create_connections
from link.models import Link, Invite
from userprofile.models import UserProfile


def cmp_result(content, searchfor):
    """
    compare content with expected result
    - content is a list of dict return by the API
    - expected is a tuple of tuple
    """
    found = 0
    for i in content:
        if ( i['sender']['user']['username'],
             i['receiver']['user']['username'] ) in searchfor:
            found += 1
    return found

class LinkTestCase(TestCase):
    c = Client(enforce_csrf_checks=True)
    
    def setUp(self):
        """set up users with new links"""
        #super(LinkTestCase, self).setUp()
        call_command('create_initial_data')
        self.u01 = User.objects.create_user(username='user1@fr.fr', password='pwd')
        self.u02 = User.objects.create_user(username='user2@fr.fr', password='pwd')
        self.u03 = User.objects.create_user(username='user3@fr.fr', password='pwd')
        self.u04 = User.objects.create_user(username='user4@fr.fr', password='pwd')
        self.u05 = User.objects.create_user(username='user5@fr.fr', password='pwd')
        self.u06 = User.objects.create_user(username='user6@fr.fr', password='pwd')
        self.u07 = User.objects.create_user(username='user7@fr.fr', password='pwd')
        self.u08 = User.objects.create_user(username='user8@fr.fr', password='pwd')
        self.u09 = User.objects.create_user(username='user9@fr.fr', password='pwd')
        self.u10 = User.objects.create_user(username='user10@fr.fr', password='pwd')
        self.l1 = Link.objects.create(sender=self.u01.userprofile,
                                      receiver=self.u02.userprofile)
        self.l2 = Link.objects.create(sender=self.u01.userprofile,
                                      receiver=self.u03.userprofile)
        self.l3 = Link.objects.create(sender=self.u01.userprofile,
                                      receiver=self.u04.userprofile)
        self.l4 = Link.objects.create(sender=self.u05.userprofile,
                                      receiver=self.u01.userprofile)
        self.l5 = Link.objects.create(sender=self.u06.userprofile,
                                      receiver=self.u01.userprofile)
        self.l6 = Link.objects.create(sender=self.u07.userprofile,
                                      receiver=self.u08.userprofile)
        self.l7 = Link.objects.create(sender=self.u09.userprofile,
                                      receiver=self.u10.userprofile)

    def test_journey(self):
        """do typical sequence of calls an app would do"""
        self.assertEqual(self.l1.sender.user.username, 'user1@fr.fr')
        self.assertEqual(self.l1.receiver.user.username, 'user2@fr.fr')
        self.assertEqual(self.l1.sender_status, 'NEW')
        self.assertEqual(self.l1.receiver_status, 'NEW')
        self.assertEqual(self.l2.sender.user.username, 'user1@fr.fr')
        self.assertEqual(self.l2.receiver.user.username, 'user3@fr.fr')
        self.assertEqual(self.l2.sender_status, 'NEW')
        self.assertEqual(self.l2.receiver_status, 'NEW')
        username = 'user1@fr.fr'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(urlquote_plus(username), api_key)
        #user1 wants to connect to some users
        res = self.c.post('/api/v1/user/invite/%s/%s'%(self.u02.id, auth))
        self.assertEqual(res.status_code, 200)
        l1 = Link.objects.get(id=self.l1.id)
        self.assertEqual(l1.sender_status, 'ACC')
        self.assertEqual(l1.receiver_status, 'PEN')
        res = self.c.post('/api/v1/user/invite/%s/%s'%(self.u03.id, auth))
        self.assertEqual(res.status_code, 200)
        l2 = Link.objects.get(id=self.l2.id)
        self.assertEqual(l2.sender_status, 'ACC')
        self.assertEqual(l2.receiver_status, 'PEN')
        #user2 accepts connection
        username = 'user2@fr.fr'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(urlquote_plus(username), api_key)
        res = self.c.post('/api/v1/user/accept/%s/%s'%(self.u01.id, auth))
        self.assertEqual(res.status_code, 200)
        l1 = Link.objects.get(id=self.l1.id)
        self.assertEqual(l1.sender_status, 'ACC')
        self.assertEqual(l1.receiver_status, 'ACC')
        #user3 rejects connection
        username = 'user3@fr.fr'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(urlquote_plus(username), api_key)
        res = self.c.post('/api/v1/user/reject/%s/%s'%(self.u01.id, auth))
        self.assertEqual(res.status_code, 200)
        l2 = Link.objects.get(id=self.l2.id)
        self.assertEqual(l2.sender_status, 'ACC')
        self.assertEqual(l2.receiver_status, 'REJ')

    def test_contact_and_connection(self):
        # first, post contacts of an existing user
        # and check what was created
        user1_contacts = [
{'name':'newuser1', 'numbers':'+33600000001',
                    'emails':'newuser1@fr.fr, newuser11@fr.fr'},
{'name':'newuser2', 'numbers':'+33600000002',
                    'emails':'newuser2@fr.fr, newuser21@fr.fr'},
{'name':'newuser3', 'numbers':'+33600000003',
                    'emails':'newuser23@fr.fr, newuser21@fr.fr'},
{'name':'newuser1', 'numbers':'+33600000010',
                    'emails':'newuser10@fr.fr'},
{'name':'user9', 'numbers':'+33610000009', 'emails':'user9@fr.fr'},
        ]
        username = 'user1@fr.fr'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(urlquote_plus(username), api_key)
        # execute background task directly
        u = UserProfile.objects.get(user__username=username)
        create_connections(u, user1_contacts)
        # the following should NOT raise a DoesNotExist exception
        Invite.objects.get(sender__user__username=username,
                           numbers='+33600000001')
        Invite.objects.get(sender__user__username=username,
                           numbers='+33600000002')
        Link.objects.get(sender__user__username=username,
                         receiver__user__username='user9@fr.fr')
        # then register a new user and check invites conversion
        data = {'username' : 'newuser1@fr.fr', 'password' : 'totopwd',
                'name':'toto', 'email' : 'newuser1@fr.fr'}
        res = self.c.post('/api/v1/auth/register/',
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 201)
        #the following should NOT raise a DoesNotExist exception
        Link.objects.get(sender__user__username=username,
                         receiver__user__username='newuser1@fr.fr')

    def test_uniqueness(self):
        from django.db import IntegrityError
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            with self.assertRaises(IntegrityError):
                Link.objects.create(sender=self.u09.userprofile,
                                    receiver=self.u10.userprofile)
        with self.assertRaises(ValidationError):
            Link.objects.create(sender=self.u10.userprofile,
                                receiver=self.u09.userprofile)
        with self.assertRaises(ValidationError):
            Link.objects.create(sender=self.u09.userprofile,
                                receiver=self.u09.userprofile)

    def login(self, username):
        data = {'username':username, 'password':'pwd'}
        res = self.c.post('/api/v1/auth/login/',
                          data = json.dumps(data),
                          content_type='application/json')
        content = json.loads(res.content)
        return content['api_key']
