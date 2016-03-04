import json

from django.db import IntegrityError
from django.test import TestCase
from django.test.client import Client
from django.core.management import call_command
from django.core.exceptions import ValidationError
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

user1_contacts = [
    {'name':'newuser1', 'numbers':'+33600000001',
                                'emails':'newuser1@fr.fr, newuser11@fr.fr'},
    {'name':'newuser2', 'numbers':'+33600000002',
                                'emails':'newuser2@fr.fr, newuser21@fr.fr'},
    {'name':'newuser3', 'numbers':'+33600000003',
                                'emails':'newuser23@fr.fr, newuser21@fr.fr'},
    {'name':'newuser1', 'numbers':'+33600000010',
                        'emails':'newuser10@fr.fr'},  #existing user
    {'name':'user9', 'numbers':'+33610000009',
                     'emails':'user9@fr.fr'},  #existing user
    {'name':'localnumber', 'numbers':'0634567890'},
    {'name':'intnumber', 'numbers':'+33610077009'},
    {'name':'wrongnumber', 'numbers':'666'},
    {'name':'duplnumber', 'numbers':'+33 601 203 003, 06 01 20 30 03'},
    {'name':'2numbers', 'numbers':'+33602200010, 0675894632'},
    {'name':'common-1&2&3', 'numbers':'+33612312300'},
]
user2_contacts = [
    {'name':'only-2(1)', 'numbers':'+33621212121'},
    {'name':'only-2(2)', 'emails':'only22@fr.fr'}, #no number => rejected
    {'name':'only-2(3)', 'numbers':'+33623232323', 'emails':'only23@fr.fr'},
    {'name':'common-1&2(1)', 'numbers':'+33610077009'},
    {'name':'common-1&2(2)', 'emails':'user9@fr.fr'}, #existing user
    {'name':'common-1&2(3)', 'numbers':'+33600000001',
                'emails':'newuser1@fr.fr, newuser11@fr.fr'},  #existing user
    {'name':'common-2&3', 'numbers':'+33623323300',
                                                'emails':'common23@fr.fr'},
    {'name':'common-1&2&3', 'numbers':'+33612312300'},
]
user3_contacts = [
    {'name':'only-3(1)', 'numbers':'+33631313131'},
    {'name':'only-3(2)', 'emails':'only32@fr.fr'}, #no number => rejected
    {'name':'only-3(3)', 'numbers':'+33633333333', 'emails':'only33@fr.fr'},
    {'name':'common-1&3(1)', 'numbers':'+33 601 203 003'},
    {'name':'common-2&3', 'numbers':'+33623323300',
                                                'emails':'common23@fr.fr'},
    {'name':'common-1&2&3', 'numbers':'+33612312300'},
]

def sort_contact(c, username, contacts):
    # execute background task directly
    u = UserProfile.objects.get(user__username=username)
    create_connections(u, contacts)

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
        self.u11 = register(self.c, 'user11@fr.fr')
        self.u12 = register(self.c, 'user12@fr.fr')
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
        sort_contact(self.c, username, user1_contacts)
        self.assertEqual(Link.objects.count(), 8) #7initial+user9
        self.assertEqual(Invite.objects.count(), 9)
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
        self.assertEqual(Link.objects.count(), 9) #+newuser1
        #the following MUST raise a DoesNotExist exception
        with self.assertRaises(Link.DoesNotExist):
            Link.objects.get(sender=self.u01.userprofile,
                             receiver=self.u11.userprofile)
            Link.objects.get(sender=self.u01.userprofile,
                             receiver=self.u12.userprofile)
        # Now post a second user
        email = 'user2@fr.fr'
        (api_key, username) = login(self.c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        sort_contact(self.c, username, user2_contacts)
        self.assertEqual(Link.objects.count(), 11) #+user9 +newuser1
        self.assertEqual(Invite.objects.count(), 14)
        #the following MUST raise a DoesNotExist exception
        with self.assertRaises(Link.DoesNotExist):
            Link.objects.get(sender=self.u02.userprofile,
                             receiver=self.u11.userprofile)
            Link.objects.get(sender=self.u02.userprofile,
                             receiver=self.u12.userprofile)
        # And for a third user
        email = 'user3@fr.fr'
        (api_key, username) = login(self.c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        sort_contact(self.c, username, user3_contacts)
        self.assertEqual(Link.objects.count(), 11)
        self.assertEqual(Invite.objects.count(), 19)
        #the following MUST raise a DoesNotExist exception
        with self.assertRaises(Link.DoesNotExist):
            Link.objects.get(sender=self.u03.userprofile,
                             receiver=self.u11.userprofile)
            Link.objects.get(sender=self.u03.userprofile,
                             receiver=self.u12.userprofile)
        # register the common friend, should create 3 links
        email = 'common@fr.fr'
        register(self.c, email)
        (api_key, username) = login(self.c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        res = self.c.post('/api/v1/userprofile/setprofile/%s'%auth,
                          data = json.dumps({'number':'+33612312300'}),
                          content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Link.objects.count(), 14)

    def test_number_treatment(self):
        email = 'user1@fr.fr'
        (api_key, username) = login(self.c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        sort_contact(self.c, username, user1_contacts)
        self.assertEqual(Link.objects.count(), 8)
        self.assertEqual(Invite.objects.count(), 9)
        # check invites created (must not throw error)
        Invite.objects.get(sender__user__username=username,
                           name='localnumber', numbers='+33634567890')
        Invite.objects.get(sender__user__username=username,
                           name='intnumber', numbers='+33610077009')
        with self.assertRaises(Invite.DoesNotExist):
            Invite.objects.get(sender__user__username=username,
                               name='wrongnumber', numbers='666'),
        Invite.objects.get(sender__user__username=username,
                           name='duplnumber', numbers='+33601203003'),
        Invite.objects.get(sender__user__username=username, name='2numbers',
                           numbers='+33602200010, +33675894632'),

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
        with self.assertRaises(ValidationError):
            with self.assertRaises(IntegrityError):
                Link.objects.create(sender=self.u09.userprofile,
                                    receiver=self.u10.userprofile)
        with self.assertRaises(ValidationError):
            Link.objects.create(sender=self.u10.userprofile,
                                receiver=self.u09.userprofile)
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
        sort_contact(self.c, username, user1_contacts)
        self.assertEqual(Link.objects.count(), 0)
        self.assertEqual(Invite.objects.count(), 10)
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
        # for code coverage purpose, doesn't execute the bacground task
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

class TransformTestCase(TestCase):
    c = Client(enforce_csrf_checks=True)
    def setUp(self):
        super(TransformTestCase, self).setUp()
        call_command('create_initial_data')
        email = 'user1@fr.fr'
        self.u01 = register(self.c, email)
        (api_key, username) = login(self.c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        sort_contact(self.c, username, user1_contacts)
    def test_creating_user(self):
        self.assertEqual(Link.objects.count(), 0)
        self.assertEqual(Invite.objects.count(), 10)
        # new user whom email is in an invite
        register(self.c, 'newuser1@fr.fr')
        # must NOT throw any error:
        self.assertEqual(Link.objects.count(), 1)
        Link.objects.get(sender__user__email='user1@fr.fr',
                         receiver__user__email='newuser1@fr.fr')
    def test_changing_email(self):
        # new user, email unknown (not in any invite)
        email = 'unknown@bidon.com'
        register(self.c, email)
        (api_key, username) = login(self.c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        self.assertEqual(Link.objects.count(), 0)
        self.assertEqual(Invite.objects.count(), 10)
        # change email into something known
        res = self.c.post('/api/v1/userprofile/setprofile/%s'%auth,
                          data = json.dumps({'email':'newuser21@fr.fr'}),
                          content_type='application/json')
        self.assertEqual(res.status_code, 200)
        # must NOT throw any error:
        self.assertEqual(Link.objects.count(), 1)
        Link.objects.get(sender__user__email='user1@fr.fr',
                         receiver__user__email='newuser21@fr.fr')
        # change email into something known, but still the same user
        res = self.c.post('/api/v1/userprofile/setprofile/%s'%auth,
                          data = json.dumps({'email':'newuser2@fr.fr'}),
                          content_type='application/json')
        self.assertEqual(res.status_code, 200)
        # must NOT throw any error:
        self.assertEqual(Link.objects.count(), 1) # not change, same user
        Link.objects.get(sender__user__email='user1@fr.fr',
                         receiver__user__email='newuser2@fr.fr')
    def test_changing_number(self):
        self.assertEqual(Link.objects.count(), 0)
        self.assertEqual(Invite.objects.count(), 10)
        # new user, email unknown (not in any invite)
        email = 'unknown2@bidon2.com'
        register(self.c, email)
        (api_key, username) = login(self.c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        # change number into something known
        res = self.c.post('/api/v1/userprofile/setprofile/%s'%auth,
                          data = json.dumps({'number':'+33610077009'}),
                          content_type='application/json')
        self.assertEqual(res.status_code, 200)
        # must NOT throw any error:
        self.assertEqual(Link.objects.count(), 1)
        Link.objects.get(sender__user__email='user1@fr.fr',
                         receiver__phone_number='+33610077009')
        # new user, email unknown (not in any invite)
        email = 'unknown3@bidon3.com'
        register(self.c, email)
        (api_key, username) = login(self.c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        # change number into something known
        res = self.c.post('/api/v1/userprofile/setprofile/%s'%auth,
                          data = json.dumps({'number':'0675894632'}),
                          content_type='application/json')
        self.assertEqual(res.status_code, 200)
        # must NOT throw any error:
        self.assertEqual(Link.objects.count(), 2)
        Link.objects.get(sender__user__email='user1@fr.fr',
                         receiver__phone_number='+33675894632')
