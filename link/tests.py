import json

from django.test import TestCase
from django.test.client import Client
from django.core.management import call_command
from django.contrib.auth.models import User
#from tastypie.test import ResourceTestCase

from link.tasks import create_connections
from link.models import Link, Invite
from userprofile.models import UserProfile
from service.testutils import register, login


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

def post_contacts(c, username):
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
    # execute background task directly
    u = UserProfile.objects.get(user__username=username)
    create_connections(u, user1_contacts)

class LinkTestCase(TestCase):
    c = Client(enforce_csrf_checks=True)
    def setUp(self):
        """set up users with new links"""
        super(LinkTestCase, self).setUp()
        call_command('create_initial_data')
        self.u01 = register(self.c, 'user1@fr.fr')
        self.u02 = register(self.c, 'user2@fr.fr')
        self.u03 = register(self.c, 'user3@fr.fr')
        self.u04 = register(self.c, 'user4@fr.fr')
        self.u05 = register(self.c, 'user5@fr.fr')
        self.u06 = register(self.c, 'user6@fr.fr')
        self.u07 = register(self.c, 'user7@fr.fr')
        self.u08 = register(self.c, 'user8@fr.fr')
        self.u09 = register(self.c, 'user9@fr.fr')
        self.u10 = register(self.c, 'user10@fr.fr')
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
        self.assertEqual(self.l1.sender.user.email, 'user1@fr.fr')
        self.assertEqual(self.l1.receiver.user.email, 'user2@fr.fr')
        self.assertEqual(self.l1.sender_status, 'NEW')
        self.assertEqual(self.l1.receiver_status, 'NEW')
        self.assertEqual(self.l2.sender.user.email, 'user1@fr.fr')
        self.assertEqual(self.l2.receiver.user.email, 'user3@fr.fr')
        self.assertEqual(self.l2.sender_status, 'NEW')
        self.assertEqual(self.l2.receiver_status, 'NEW')
        email = 'user1@fr.fr'
        (api_key, username) = login(self.c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
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
        email = 'user2@fr.fr'
        (api_key, username) = login(self.c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        res = self.c.post('/api/v1/user/accept/%s/%s'%(self.u01.id, auth))
        self.assertEqual(res.status_code, 200)
        l1 = Link.objects.get(id=self.l1.id)
        self.assertEqual(l1.sender_status, 'ACC')
        self.assertEqual(l1.receiver_status, 'ACC')
        #user3 rejects connection
        email = 'user3@fr.fr'
        (api_key, username) = login(self.c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        res = self.c.post('/api/v1/user/reject/%s/%s'%(self.u01.id, auth))
        self.assertEqual(res.status_code, 200)
        l2 = Link.objects.get(id=self.l2.id)
        self.assertEqual(l2.sender_status, 'ACC')
        self.assertEqual(l2.receiver_status, 'REJ')

    def test_contact_and_connection(self):
        # first, post contacts of an existing user
        # and check what was created
        email = 'user1@fr.fr'
        (api_key, username) = login(self.c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        post_contacts(self.c, username)
        # the following should NOT raise a DoesNotExist exception
        Invite.objects.get(sender__user__username=username,
                           numbers='+33600000001')
        Invite.objects.get(sender__user__username=username,
                           numbers='+33600000002')
        Link.objects.get(sender__user__username=username,
                         receiver__user__email='user9@fr.fr')
        # then register a new user and check invites conversion
        data = {'email' : 'newuser1@fr.fr', 'password' : 'totopwd'}
        res = self.c.post('/api/v1/auth/register_by_email/',
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 201)
        #the following should NOT raise a DoesNotExist exception
        Link.objects.get(sender__user__username=username,
                         receiver__user__email='newuser1@fr.fr')

    def test_contact_big(self):
        import contact_example as ce
        email = 'user1@fr.fr'
        (api_key, username) = login(self.c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        # execute background task directly
        u = UserProfile.objects.get(user__username=username)
        create_connections(u, ce.michael)        
        create_connections(u, ce.charles)
        create_connections(u, ce.caroline)

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

class InviteTestCase(TestCase):
    c = Client(enforce_csrf_checks=True)
    def setUp(self):
        super(InviteTestCase, self).setUp()
        call_command('create_initial_data')
        self.u01 = register(self.c, 'user1@fr.fr')
    def test_invite(self):
        email = 'user1@fr.fr'
        (api_key, username) = login(self.c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        post_contacts(self.c, username)
        # check invites are NEW
        i1 = Invite.objects.get(sender__user__username=username,
                                numbers='+33600000001')
        i2 = Invite.objects.get(sender__user__username=username,
                                numbers='+33600000002')
        self.assertEqual(i1.status, 'NEW')
        self.assertEqual(i2.status, 'NEW')
        # call APIs and check invite status
        res = self.c.post('/api/v1/invite/send/%d/%s'%(i1.id, auth),
                          data = json.dumps({}),
                          content_type='application/json')
        self.assertEqual(res.status_code, 200)
        res = self.c.post('/api/v1/invite/ignore/%d/%s'%(i2.id, auth),
                          data = json.dumps({}),
                          content_type='application/json')
        self.assertEqual(res.status_code, 200)
        i1 = Invite.objects.get(sender__user__username=username,
                                numbers='+33600000001')
        i2 = Invite.objects.get(sender__user__username=username,
                                numbers='+33600000002')
        self.assertEqual(i1.status, 'PEN')
        self.assertEqual(i2.status, 'IGN')
        # wrong invite id
        res = self.c.post('/api/v1/invite/send/%d/%s'%(321, auth),
                          data = json.dumps({}),
                          content_type='application/json')
        self.assertEqual(res.status_code, 403)
        # no id
        res = self.c.post('/api/v1/invite/send/%s/%s'%('toto', auth),
                          data = json.dumps({}),
                          content_type='application/json')
        self.assertEqual(res.status_code, 403)
        # no auth
        res = self.c.post('/api/v1/invite/ignore/%d/'%(432),
                          data = json.dumps({}),
                          content_type='application/json')
        self.assertEqual(res.status_code, 401)
        
class ContactTestCase(TestCase):
    c = Client(enforce_csrf_checks=True)
    def setUp(self):
        super(ContactTestCase, self).setUp()
        call_command('create_initial_data')
        self.u01 = register(self.c, 'user1@fr.fr')
    def test_invite(self):
        # for code coverage, doesn't execute the bacground task
        email = 'user1@fr.fr'
        (api_key, username) = login(self.c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        res = self.c.post('/api/v1/contact/sort/%s'%auth,
                          data = json.dumps({}),
                          content_type='application/json')
        self.assertEqual(res.status_code, 200)
        # bad data
        res = self.c.post('/api/v1/contact/sort/%s'%auth,
                          data = "{'iij'}",
                          content_type='application/json')
        self.assertEqual(res.status_code, 400)
        # bad auth
        res = self.c.post('/api/v1/contact/sort/?username=sdf&api_key=sdf',
                          data = json.dumps({}),
                          content_type='application/json')
        self.assertEqual(res.status_code, 401)
        