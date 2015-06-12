import json

from django.test import TestCase
from django.utils.http import urlquote_plus
from django.test.client import Client
from django.core.management import call_command
from django.contrib.auth.models import User

from userprofile.models import UserProfile, UserPosition

class ProfileTestCase(TestCase):
    c = Client()
    
    def setUp(self):
        super(ProfileTestCase, self).setUp()
        call_command('create_initial_data')
        self.u01 = User.objects.create_user(username='+33610000001', password='pwd')

    def test_register_user(self):
        data = {'username' : '+33610001111', 'password' : 'totopwd'}
        res = self.c.post('/api/v1/auth/register/',
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 201)
        content = json.loads(res.content)
        api_key = content['api_key']
        user_id = content['userid']
        #res = self.c.get('/api/v1/user/?username=%s&api_key=%s'%('toto', api_key))
        auth = '?username=%s&api_key=%s'%(urlquote_plus('+33610001111'), api_key)
        res = self.c.get('/api/v1/user/%s/%s'%(user_id, auth))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['username'], '+33610001111')
        
    def test_update_user(self):
        username = '+33610000001'
        auth_data = self.login(username)
        api_key = auth_data['api_key']
        user_id = auth_data['userid']
        auth = '?username=%s&api_key=%s'%(urlquote_plus(username), api_key)
        res = self.c.get('/api/v1/user/%s/%s'%(user_id, auth))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['first_name'], '')
        res = self.c.get('/api/v1/userprofile/%s/%s'%(user_id, auth))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['gender'], None)
        res = self.c.get('/api/v1/userposition/%s/%s'%(user_id, auth))
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
        res = self.c.put('/api/v1/userprofile/%s/%s'%(user_id, auth),
                           data = json.dumps(data),
                           content_type='application/json')
        self.assertEqual(res.status_code, 204)
        res = self.c.get('/api/v1/userprofile/%s/%s'%(user_id, auth))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['gender'], 'MA')
        data = {'last' : '{ "type": "Point", "coordinates": [42.0, 2.0] }'}
        res = self.c.put('/api/v1/userposition/%s/%s'%(user_id, auth),
                           data = json.dumps(data),
                           content_type='application/json')
        self.assertEqual(res.status_code, 204)
        res = self.c.get('/api/v1/userposition/%s/%s'%(user_id, auth))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['last'], 'POINT (42.0000000000000000 2.0000000000000000)')

    def test_unmatched_auth_data(self):
        username = '+33610000001'
        auth_data = self.login(username)
        api_key = auth_data['api_key']
        user_id = auth_data['userid']
        auth = '?username=%s&api_key=%s'%(urlquote_plus(username), api_key)
        res = self.c.get('/api/v1/user/%s/%s'%(user_id, auth))
        self.assertEqual(res.status_code, 200)
        auth = '?username=%s&api_key=%s'%('wrong', api_key)
        res = self.c.get('/api/v1/user/%s/%s'%(user_id, auth))
        self.assertEqual(res.status_code, 401)
        auth = '?username=%s&api_key=%s'%(urlquote_plus(username), 'wrong')
        res = self.c.get('/api/v1/user/%s/%s'%(user_id, auth))
        self.assertEqual(res.status_code, 401)

    def test_profiles_creation(self):
        # if profiles are not properly created, this will generate an error
        UserProfile.objects.get(user=self.u01)
        UserPosition.objects.get(user=self.u01)

    def login(self, username):
        data = {'username':username, 'password':'pwd'}
        res = self.c.post('/api/v1/auth/login/',
                          data = json.dumps(data),
                          content_type='application/json')
        return json.loads(res.content)

