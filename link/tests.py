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

    def test_my_links(self):
        """links that belong to me"""
        (sessionid, csrftoken) = self.login()
        res = self.c.get('/api/v1/link/', sessionid=sessionid)
        data = json.loads(res.content)
        self.assertEqual(data['meta']['total_count'], 5)
        expected = ( ('user1@fr.fr', 'user2@fr.fr'),
                     ('user1@fr.fr', 'user3@fr.fr'),
                     ('user1@fr.fr', 'user4@fr.fr'),
                     ('user5@fr.fr', 'user1@fr.fr'),
                     ('user6@fr.fr', 'user1@fr.fr') )
        self.assertEqual(cmp_result(data['objects'], expected), 5)
        unexpected = ( ('user1@fr.fr', 'user1@fr.fr'),
                       ('user2@fr.fr', 'user1@fr.fr'),
                       ('user1@fr.fr', 'user5@fr.fr'),
                       ('user7@fr.fr', 'user8@fr.fr'),
                       ('user9@fr.fr', 'user10@fr.fr') )
        self.assertEqual(cmp_result(data['objects'], unexpected), 0)

    def test_my_friends(self):
        """users I am connected to"""
        (sessionid, csrftoken) = self.login()
        res = self.c.get('/api/v1/link/?sender_status=ACC&receiver_status=ACC',
                         sessionid=sessionid)
        data = json.loads(res.content)
        self.assertEqual(data['meta']['total_count'], 0)
        # need more tests

    def test_user_to_connect_to(self):
        """user I can connect to"""
        pass

    def test_link_detail(self):
        """test access to links that belong to me or not"""
        # can access my link detail
        # cannot access others link detail
        pass

    def test_not_auth(self):
        """trying as non-authorized user"""
        pass

    def test_forbidden_method(self):
        pass
    
    def test_accept_link(self):
        pass
        

    def login(self):
        data = {'username':'user1@fr.fr', 'password':'pwd'}
        res = self.c.post('/api/v1/auth/login/',
                          data = json.dumps(data),
                          content_type='application/json')
        cookies = res.cookies
        sessionid = cookies['sessionid']
        csrftoken = cookies['csrftoken']
        return (sessionid, csrftoken)
