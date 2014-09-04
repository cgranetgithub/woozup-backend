import json

from django.test import TestCase
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
        if (i['sender']['username'], i['receiver']['username']) in searchfor:
            found += 1
    return found

class LinkTestCase(TestCase):
    c = Client(enforce_csrf_checks=True)
    
    def setUp(self):
        """set up users with new links"""
        super(LinkTestCase, self).setUp()
        call_command('create_initial_data')
        u01 = User.objects.create_user(username='user1@fr.fr', password='pwd')
        u02 = User.objects.create_user(username='user2@fr.fr', password='pwd')
        u03 = User.objects.create_user(username='user3@fr.fr', password='pwd')
        u04 = User.objects.create_user(username='user4@fr.fr', password='pwd')
        u05 = User.objects.create_user(username='user5@fr.fr', password='pwd')
        u06 = User.objects.create_user(username='user6@fr.fr', password='pwd')
        u07 = User.objects.create_user(username='user7@fr.fr', password='pwd')
        u08 = User.objects.create_user(username='user8@fr.fr', password='pwd')
        u09 = User.objects.create_user(username='user9@fr.fr', password='pwd')
        u10 = User.objects.create_user(username='user10@fr.fr', password='pwd')
        self.l1 = Link.objects.create(sender=u01, receiver=u02)
        self.l2 = Link.objects.create(sender=u01, receiver=u03)
        self.l3 = Link.objects.create(sender=u01, receiver=u04)
        self.l4 = Link.objects.create(sender=u05, receiver=u01)
        self.l5 = Link.objects.create(sender=u06, receiver=u01)
        self.l6 = Link.objects.create(sender=u07, receiver=u08)
        self.l7 = Link.objects.create(sender=u09, receiver=u10)

    def test_journey(self):
        """do typical sequence of calls an app would do"""
        self.assertEqual(self.l1.sender.username, 'user1@fr.fr')
        self.assertEqual(self.l1.receiver.username, 'user2@fr.fr')
        self.assertEqual(self.l1.sender_status, 'NEW')
        self.assertEqual(self.l1.receiver_status, 'NEW')
        self.assertEqual(self.l2.sender.username, 'user1@fr.fr')
        self.assertEqual(self.l2.receiver.username, 'user3@fr.fr')
        self.assertEqual(self.l2.sender_status, 'NEW')
        self.assertEqual(self.l2.receiver_status, 'NEW')
        username = 'user1@fr.fr'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        #user1 wants to connect to some users
        res = self.c.post('/api/v1/link/%s/connect/%s'%(self.l1.id, auth))
        res = self.c.post('/api/v1/link/%s/connect/%s'%(self.l2.id, auth))
        l1 = Link.objects.get(id=self.l1.id)
        l2 = Link.objects.get(id=self.l2.id)
        self.assertEqual(l1.sender_status, 'ACC')
        self.assertEqual(l1.receiver_status, 'PEN')
        self.assertEqual(l2.sender_status, 'ACC')
        self.assertEqual(l2.receiver_status, 'PEN')
        #user2 accepts connection
        username = 'user2@fr.fr'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        res = self.c.post('/api/v1/link/%s/accept/%s'%(self.l1.id, auth))
        l1 = Link.objects.get(id=self.l1.id)
        self.assertEqual(l1.sender_status, 'ACC')
        self.assertEqual(l1.receiver_status, 'ACC')
        #user3 rejects connection
        username = 'user3@fr.fr'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        res = self.c.post('/api/v1/link/%s/reject/%s'%(self.l2.id, auth))
        l2 = Link.objects.get(id=self.l2.id)
        self.assertEqual(l2.sender_status, 'ACC')
        self.assertEqual(l2.receiver_status, 'REJ')

    def test_my_links(self):
        """links that belong to me"""
        username = 'user1@fr.fr'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        res = self.c.get('/api/v1/link/%s'%auth)
        content = json.loads(res.content)
        self.assertEqual(content['meta']['total_count'], 5)
        expected = ( ('user1@fr.fr', 'user2@fr.fr'),
                     ('user1@fr.fr', 'user3@fr.fr'),
                     ('user1@fr.fr', 'user4@fr.fr'),
                     ('user5@fr.fr', 'user1@fr.fr'),
                     ('user6@fr.fr', 'user1@fr.fr') )
        self.assertEqual(cmp_result(content['objects'], expected), 5)
        unexpected = ( ('user1@fr.fr', 'user1@fr.fr'),
                       ('user2@fr.fr', 'user1@fr.fr'),
                       ('user1@fr.fr', 'user5@fr.fr'),
                       ('user7@fr.fr', 'user8@fr.fr'),
                       ('user9@fr.fr', 'user10@fr.fr') )
        self.assertEqual(cmp_result(content['objects'], unexpected), 0)

    def test_unauth_method(self):
        username = 'user1@fr.fr'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        #list
        res = self.c.get('/api/v1/link/%s'%auth)
        self.assertEqual(res.status_code, 200)
        res = self.c.put('/api/v1/link/%s'%auth)
        self.assertEqual(res.status_code, 405)
        res = self.c.post('/api/v1/link/%s'%auth)
        self.assertEqual(res.status_code, 405)
        res = self.c.delete('/api/v1/link/%s'%auth)
        self.assertEqual(res.status_code, 405)
        #detail
        res = self.c.get('/api/v1/link/%s/%s'%(self.l1.id, auth))
        self.assertEqual(res.status_code, 200)
        res = self.c.put('/api/v1/link/%s/%s'%(self.l1.id, auth))
        self.assertEqual(res.status_code, 405)
        res = self.c.post('/api/v1/link/%s/%s'%(self.l1.id, auth))
        self.assertEqual(res.status_code, 405)
        res = self.c.delete('/api/v1/link/%s/%s'%(self.l1.id, auth))
        self.assertEqual(res.status_code, 405)
        #connect
        res = self.c.get('/api/v1/link/%s/connect/%s'%(self.l1.id, auth))
        self.assertEqual(res.status_code, 405)
        res = self.c.put('/api/v1/link/%s/connect/%s'%(self.l1.id, auth))
        self.assertEqual(res.status_code, 405)
        res = self.c.post('/api/v1/link/%s/connect/%s'%(self.l1.id, auth))
        self.assertEqual(res.status_code, 200)
        res = self.c.delete('/api/v1/link/%s/connect/%s'%(self.l1.id, auth))
        self.assertEqual(res.status_code, 405)
        #accept
        res = self.c.get('/api/v1/link/%s/accept/%s'%(self.l4.id, auth))
        self.assertEqual(res.status_code, 405)
        res = self.c.put('/api/v1/link/%s/accept/%s'%(self.l4.id, auth))
        self.assertEqual(res.status_code, 405)
        res = self.c.post('/api/v1/link/%s/accept/%s'%(self.l4.id, auth))
        self.assertEqual(res.status_code, 200)
        res = self.c.delete('/api/v1/link/%s/accept/%s'%(self.l4.id, auth))
        self.assertEqual(res.status_code, 405)
        #reject
        res = self.c.get('/api/v1/link/%s/reject/%s'%(self.l5.id, auth))
        self.assertEqual(res.status_code, 405)
        res = self.c.put('/api/v1/link/%s/reject/%s'%(self.l5.id, auth))
        self.assertEqual(res.status_code, 405)
        res = self.c.post('/api/v1/link/%s/reject/%s'%(self.l5.id, auth))
        self.assertEqual(res.status_code, 200)
        res = self.c.delete('/api/v1/link/%s/reject/%s'%(self.l5.id, auth))
        self.assertEqual(res.status_code, 405)

    def test_unauth_user(self):
        res = self.c.get('/api/v1/link/')
        self.assertEqual(res.status_code, 401)
        res = self.c.get('/api/v1/link/1/')
        self.assertEqual(res.status_code, 401)

    def test_link_detail(self):
        """test access to links that belong to me or not"""
        # can access my link detail
        username = 'user1@fr.fr'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        res = self.c.get('/api/v1/link/%s/%s'%(self.l1.id, auth))
        self.assertEqual(res.status_code, 200)
        res = self.c.get('/api/v1/link/%s/%s'%(self.l4.id, auth))
        self.assertEqual(res.status_code, 200)
        # cannot access others link detail
        res = self.c.get('/api/v1/link/%s/%s'%(self.l7.id, auth))
        self.assertEqual(res.status_code, 404)
        #make sure link exists, in case of...
        Link.objects.get(id=self.l7.id) #will raise an exception if doesnotexist

    def test_contact_and_connection(self):
        # first, post contacts of an existing user
        # and check what was created
        user1_contacts = {'newuser1@fr.fr' : {'email':'newuser1@fr.fr',
                                               'name':'newuser1'},
                           'newuser2@fr.fr' : {'email':'newuser2@fr.fr',
                                               'name':'newuser2'},
                           #'user11@fr.fr' : {'name':'user11',
                                             #'email':'user11@fr.fr' },
                           'user9@fr.fr' : {'name':'user9',
                                             'email':'user9@fr.fr'}}
        username = 'user1@fr.fr'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        res = self.c.post('/api/v1/contact/sort/%s'%auth,
                          data = json.dumps(user1_contacts),
                          content_type='application/json')
        self.assertEqual(res.status_code, 200)
        import time
        time.sleep(1)
        #the following should NOT raise a DoesNotExist exception
        Invite.objects.get(sender__username=username,
                           userid='newuser1@fr.fr')
        Invite.objects.get(sender__username=username,
                           userid='newuser2@fr.fr')
        Link.objects.get(sender__username=username,
                         receiver__username='user9@fr.fr')
        # then register a new user and check invites conversion
        data = {'username' : 'newuser1@fr.fr', 'password' : 'totopwd'}
        res = self.c.post('/api/v1/auth/register/',
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 201)
        #the following should NOT raise a DoesNotExist exception
        Link.objects.get(sender__username=username,
                         receiver__username='newuser1@fr.fr')

    def login(self, username):
        data = {'username':username, 'password':'pwd'}
        res = self.c.post('/api/v1/auth/login/',
                          data = json.dumps(data),
                          content_type='application/json')
        content = json.loads(res.content)
        return content['api_key']
