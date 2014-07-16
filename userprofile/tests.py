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
        res = self.c.get('/api/v1/user/?username=%s&api_key=%s'%('toto', api_key))
        self.assertEqual(res.status_code, 200)
        content = json.loads(res.content)
        self.assertEqual(content['meta']['total_count'], 1)
        self.assertEqual(content['objects'][0]['username'], 'toto')
        
    def test_update_user(self):
        username = 'user1@fr.fr'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        res = self.c.get('/api/v1/user/%s'%auth)
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['objects'][0]['first_name'], '')
        self.assertEqual(content['objects'][0]['profile']['gender'], None)
        self.assertEqual(content['objects'][0]['position']['last'], u'48.853, 2.35')
        user_id = content['objects'][0]['id']
        data = { 'first_name' : 'john', 
                #'profile' : {'gender' : 'MA'} 
                #'position' : {'last' : '1, 1'} 
                }
        res = self.c.put('/api/v1/user/%d/%s'%(user_id, auth),
                           data = json.dumps(data),
                           content_type='application/json')
        self.assertEqual(res.status_code, 204)
        res = self.c.get('/api/v1/user/%s'%auth)
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['objects'][0]['first_name'], 'john')
        #self.assertEqual(content['objects'][0]['profile']['gender'], 'MA')
        #self.assertEqual(content['objects'][0]['position']['last'], '1, 1')

    def login(self, username):
        data = {'username':username, 'password':'pwd'}
        res = self.c.post('/api/v1/auth/login/',
                          data = json.dumps(data),
                          content_type='application/json')
        content = json.loads(res.content)
        return content['api_key']
