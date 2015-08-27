import json

from django.test import TestCase
from django.utils.http import urlquote_plus
from django.test.client import Client
from django.core.management import call_command
from django.contrib.auth.models import User
#from tastypie.test import ResourceTestCase

from link.models import Link, Invite

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
        self.u01 = User.objects.create_user(username='+33610000001', password='pwd')
        self.u02 = User.objects.create_user(username='+33610000002', password='pwd')
        self.u03 = User.objects.create_user(username='+33610000003', password='pwd')
        self.u04 = User.objects.create_user(username='+33610000004', password='pwd')
        self.u05 = User.objects.create_user(username='+33610000005', password='pwd')
        self.u06 = User.objects.create_user(username='+33610000006', password='pwd')
        self.u07 = User.objects.create_user(username='+33610000007', password='pwd')
        self.u08 = User.objects.create_user(username='+33610000008', password='pwd')
        self.u09 = User.objects.create_user(username='+33610000009', password='pwd')
        self.u10 = User.objects.create_user(username='+33610000010', password='pwd')
        self.l1 = Link.objects.create(sender=u01.userprofile,
                                      receiver=u02.userprofile)
        self.l2 = Link.objects.create(sender=u01.userprofile,
                                      receiver=u03.userprofile)
        self.l3 = Link.objects.create(sender=u01.userprofile,
                                      receiver=u04.userprofile)
        self.l4 = Link.objects.create(sender=u05.userprofile,
                                      receiver=u01.userprofile)
        self.l5 = Link.objects.create(sender=u06.userprofile,
                                      receiver=u01.userprofile)
        self.l6 = Link.objects.create(sender=u07.userprofile,
                                      receiver=u08.userprofile)
        self.l7 = Link.objects.create(sender=self.u09.userprofile,
                                      receiver=self.u10.userprofile)

    def test_journey(self):
        """do typical sequence of calls an app would do"""
        self.assertEqual(self.l1.sender.user.username, '+33610000001')
        self.assertEqual(self.l1.receiver.user.username, '+33610000002')
        self.assertEqual(self.l1.sender_status, 'NEW')
        self.assertEqual(self.l1.receiver_status, 'NEW')
        self.assertEqual(self.l2.sender.user.username, '+33610000001')
        self.assertEqual(self.l2.receiver.user.username, '+33610000003')
        self.assertEqual(self.l2.sender_status, 'NEW')
        self.assertEqual(self.l2.receiver_status, 'NEW')
        username = '+33610000001'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(urlquote_plus(username), api_key)
        #user1 wants to connect to some users
        res = self.c.post('/api/v1/user/invite/%s%s'%(self.u1.id, auth))
        res = self.c.post('/api/v1/user/invite/%s%s'%(self.u2.id, auth))
        l1 = Link.objects.get(id=self.l1.id)
        l2 = Link.objects.get(id=self.l2.id)
        self.assertEqual(l1.sender_status, 'ACC')
        self.assertEqual(l1.receiver_status, 'PEN')
        self.assertEqual(l2.sender_status, 'ACC')
        self.assertEqual(l2.receiver_status, 'PEN')
        #user2 accepts connection
        username = '+33610000002'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(urlquote_plus(username), api_key)
        res = self.c.post('/api/v1/user/accept/%s%s'%(self.u1.id, auth))
        l1 = Link.objects.get(id=self.l1.id)
        self.assertEqual(l1.sender_status, 'ACC')
        self.assertEqual(l1.receiver_status, 'ACC')
        #user3 rejects connection
        username = '+33610000003'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(urlquote_plus(username), api_key)
        res = self.c.post('/api/v1/user/reject/%s%s'%(self.u2.id, auth))
        l2 = Link.objects.get(id=self.l2.id)
        self.assertEqual(l2.sender_status, 'ACC')
        self.assertEqual(l2.receiver_status, 'REJ')

    def test_contact_and_connection(self):
        # first, post contacts of an existing user
        # and check what was created
        user1_contacts = {'+33600000001' : {'email':'newuser1@fr.fr',
                                           'name':'newuser1'},
                          '+33600000002' : {'email':'newuser2@fr.fr',
                                           'name':'newuser2'},
                           #'user11@fr.fr' : {'name':'user11',
                                             #'email':'user11@fr.fr' },
                          '+33610000009' : {'name':'user9',
                                           'email':'user9@fr.fr'}}
        username = '+33610000001'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(urlquote_plus(username), api_key)

        #res = self.c.post('/api/v1/contact/sort/%s'%auth,
                          #data = json.dumps(user1_contacts),
                          #content_type='application/json')
        #self.assertEqual(res.status_code, 200)

        # execute background task directly
        from link.tasks import create_connections
        from userprofile.models import UserProfile
        u = UserProfile.objects.get(user__username=username)
        create_connections(u, user1_contacts)
        # the following should NOT raise a DoesNotExist exception
        Invite.objects.get(sender__user__username=username,
                           number='+33600000001')
        Invite.objects.get(sender__user__username=username,
                           number='+33600000002')
        Link.objects.get(sender__user__username=username,
                         receiver__user__username='+33610000009')
        # then register a new user and check invites conversion
        data = {'username' : '+33600000001', 'password' : 'totopwd'}
        res = self.c.post('/api/v1/auth/register/',
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 201)
        #the following should NOT raise a DoesNotExist exception
        Link.objects.get(sender__user__username=username,
                         receiver__user__username='+33600000001')

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
