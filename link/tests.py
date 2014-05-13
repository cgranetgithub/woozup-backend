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
    c = Client()
    
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
        Link.objects.create(sender=u01, receiver=u02)
        Link.objects.create(sender=u01, receiver=u03)
        Link.objects.create(sender=u01, receiver=u04)
        Link.objects.create(sender=u05, receiver=u01)
        Link.objects.create(sender=u06, receiver=u01)
        Link.objects.create(sender=u07, receiver=u08)
        Link.objects.create(sender=u09, receiver=u10)

    def test_journey(self):
        """do typical sequence of calls an app would do"""
        l = Link.objects.get(id=1)
        self.assertEqual(l.sender.username, 'user1@fr.fr')
        self.assertEqual(l.receiver.username, 'user2@fr.fr')
        self.assertEqual(l.sender_status, 'NEW')
        self.assertEqual(l.receiver_status, 'NEW')
        l = Link.objects.get(id=2)
        self.assertEqual(l.sender.username, 'user1@fr.fr')
        self.assertEqual(l.receiver.username, 'user3@fr.fr')
        self.assertEqual(l.sender_status, 'NEW')
        self.assertEqual(l.receiver_status, 'NEW')
        (sessionid, csrftoken) = self.login('user1@fr.fr')
        #user1 wants to connect to some users
        res = self.c.post('/api/v1/link/1/connect/', sessionid=sessionid)
        res = self.c.post('/api/v1/link/2/connect/', sessionid=sessionid)
        l = Link.objects.get(id=1)
        self.assertEqual(l.sender_status, 'ACC')
        self.assertEqual(l.receiver_status, 'PEN')
        l = Link.objects.get(id=2)
        self.assertEqual(l.sender_status, 'ACC')
        self.assertEqual(l.receiver_status, 'PEN')
        #user2 accepts connection
        (sessionid, csrftoken) = self.login('user2@fr.fr')
        res = self.c.post('/api/v1/link/1/accept/', sessionid=sessionid)
        l = Link.objects.get(id=1)
        self.assertEqual(l.sender_status, 'ACC')
        self.assertEqual(l.receiver_status, 'ACC')
        #user3 rejects connection
        (sessionid, csrftoken) = self.login('user3@fr.fr')
        res = self.c.post('/api/v1/link/2/reject/', sessionid=sessionid)
        l = Link.objects.get(id=2)
        self.assertEqual(l.sender_status, 'ACC')
        self.assertEqual(l.receiver_status, 'REJ')


    def test_my_links(self):
        """links that belong to me"""
        (sessionid, csrftoken) = self.login('user1@fr.fr')
        res = self.c.get('/api/v1/link/', sessionid=sessionid)
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
        (sessionid, csrftoken) = self.login('user1@fr.fr')
        #list
        res = self.c.get('/api/v1/link/', sessionid=sessionid)
        self.assertEqual(res.status_code, 200)
        res = self.c.put('/api/v1/link/', sessionid=sessionid)
        self.assertEqual(res.status_code, 405)
        res = self.c.post('/api/v1/link/', sessionid=sessionid)
        self.assertEqual(res.status_code, 405)
        res = self.c.delete('/api/v1/link/', sessionid=sessionid)
        self.assertEqual(res.status_code, 405)
        #detail
        res = self.c.get('/api/v1/link/1/', sessionid=sessionid)
        self.assertEqual(res.status_code, 200)
        res = self.c.put('/api/v1/link/1/', sessionid=sessionid)
        self.assertEqual(res.status_code, 405)
        res = self.c.post('/api/v1/link/1/', sessionid=sessionid)
        self.assertEqual(res.status_code, 405)
        res = self.c.delete('/api/v1/link/1/', sessionid=sessionid)
        self.assertEqual(res.status_code, 405)
        #connect
        res = self.c.get('/api/v1/link/1/connect/', sessionid=sessionid)
        self.assertEqual(res.status_code, 405)
        res = self.c.put('/api/v1/link/1/connect/', sessionid=sessionid)
        self.assertEqual(res.status_code, 405)
        res = self.c.post('/api/v1/link/1/connect/', sessionid=sessionid)
        self.assertEqual(res.status_code, 200)
        res = self.c.delete('/api/v1/link/1/connect/', sessionid=sessionid)
        self.assertEqual(res.status_code, 405)
        #accept
        res = self.c.get('/api/v1/link/4/accept/', sessionid=sessionid)
        self.assertEqual(res.status_code, 405)
        res = self.c.put('/api/v1/link/4/accept/', sessionid=sessionid)
        self.assertEqual(res.status_code, 405)
        res = self.c.post('/api/v1/link/4/accept/', sessionid=sessionid)
        self.assertEqual(res.status_code, 200)
        res = self.c.delete('/api/v1/link/4/accept/', sessionid=sessionid)
        self.assertEqual(res.status_code, 405)
        #reject
        res = self.c.get('/api/v1/link/5/reject/', sessionid=sessionid)
        self.assertEqual(res.status_code, 405)
        res = self.c.put('/api/v1/link/5/reject/', sessionid=sessionid)
        self.assertEqual(res.status_code, 405)
        res = self.c.post('/api/v1/link/5/reject/', sessionid=sessionid)
        self.assertEqual(res.status_code, 200)
        res = self.c.delete('/api/v1/link/5/reject/', sessionid=sessionid)
        self.assertEqual(res.status_code, 405)

    def test_unauth_user(self):
        res = self.c.get('/api/v1/link/')
        self.assertEqual(res.status_code, 401)
        res = self.c.get('/api/v1/link/1/')
        self.assertEqual(res.status_code, 401)

    def test_link_detail(self):
        """test access to links that belong to me or not"""
        # can access my link detail
        (sessionid, csrftoken) = self.login('user1@fr.fr')
        res = self.c.get('/api/v1/link/1/', sessionid=sessionid)
        self.assertEqual(res.status_code, 200)
        res = self.c.get('/api/v1/link/4/', sessionid=sessionid)
        self.assertEqual(res.status_code, 200)
        # cannot access others link detail
        res = self.c.get('/api/v1/link/7/', sessionid=sessionid)
        self.assertEqual(res.status_code, 404)
        #make sure link exists, in case of...
        Link.objects.get(id=7) #will raise an exception if doesnotexist

    def login(self, username):
        data = {'username':username, 'password':'pwd'}
        res = self.c.post('/api/v1/auth/login/',
                          data = json.dumps(data),
                          content_type='application/json')
        cookies = res.cookies
        sessionid = cookies['sessionid']
        csrftoken = cookies['csrftoken']
        return (sessionid, csrftoken)
