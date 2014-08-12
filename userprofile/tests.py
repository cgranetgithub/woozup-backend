import json

from django.test import TestCase
from django.test.client import Client
from django.core.management import call_command
from django.contrib.auth.models import User

class EventTestCase(TestCase):
    c = Client()
    
    def setUp(self):
        """set up users with new events"""
        super(EventTestCase, self).setUp()
        call_command('create_initial_data')
        u01 = User.objects.create_user(username='user1@fr.fr', password='pwd')

    def test_register_user(self):
        data = {'username' : 'toto', 'password' : 'totopwd'}
        res = self.c.post('/api/v1/auth/register/',
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 201)
        content = json.loads(res.content)
        api_key = content['api_key']
        user_id = content['userid']
        #res = self.c.get('/api/v1/user/?username=%s&api_key=%s'%('toto', api_key))
        auth = '?username=%s&api_key=%s'%('toto', api_key)
        res = self.c.get('/api/v1/user/%s/%s'%(user_id, auth))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['username'], 'toto')
        
    def test_update_user(self):
        username = 'user1@fr.fr'
        api_key = self.login(username)['api_key']
        user_id = self.login(username)['userid']
        profile_id = self.login(username)['profileid']
        position_id = self.login(username)['positionid']
        auth = '?username=%s&api_key=%s'%(username, api_key)
        res = self.c.get('/api/v1/user/%s/%s'%(user_id, auth))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['first_name'], '')
        res = self.c.get('/api/v1/userprofile/%s/%s'%(profile_id, auth))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['gender'], None)
        res = self.c.get('/api/v1/userposition/%s/%s'%(position_id, auth))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['last'], None)
        data = { 'first_name' : 'john' }
        res = self.c.put('/api/v1/user/%s/%s'%(user_id, auth),
                           data = json.dumps(data),
                           content_type='application/json')
        self.assertEqual(res.status_code, 204)
        res = self.c.get('/api/v1/user/%s/%s'%(user_id, auth))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['first_name'], 'john')
        data = {'gender' : 'MA'}
        res = self.c.put('/api/v1/userprofile/%s/%s'%(profile_id, auth),
                           data = json.dumps(data),
                           content_type='application/json')
        self.assertEqual(res.status_code, 204)
        res = self.c.get('/api/v1/userprofile/%s/%s'%(profile_id, auth))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['gender'], 'MA')
        data = {'last' : '{ "type": "Point", "coordinates": [42.0, 2.0] }'}
        res = self.c.put('/api/v1/userposition/%s/%s'%(position_id, auth),
                           data = json.dumps(data),
                           content_type='application/json')
        self.assertEqual(res.status_code, 204)
        res = self.c.get('/api/v1/userposition/%s/%s'%(position_id, auth))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['last'], 'POINT (42.0000000000000000 2.0000000000000000)')

    def login(self, username):
        data = {'username':username, 'password':'pwd'}
        res = self.c.post('/api/v1/auth/login/',
                          data = json.dumps(data),
                          content_type='application/json')
        return json.loads(res.content)

