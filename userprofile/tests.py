 #-*- coding: utf-8 -*-
import json

from django.test import TestCase
from django.utils.http import urlquote_plus
from django.test.client import Client
from django.core.management import call_command
from django.contrib.auth.models import User

from userprofile.models import UserProfile, UserPosition

c = Client()

def login(username):
    data = {'username':username, 'password':'pwd'}
    res = c.post('/api/v1/auth/login/',
                        data = json.dumps(data),
                        content_type='application/json')
    return json.loads(res.content)

class AuthTestCase(TestCase):
    
    def setUp(self):
        super(AuthTestCase, self).setUp()
        call_command('create_initial_data')
        self.u01 = User.objects.create_user(username='+33610000001',
                                            password='pwd')
        username = '+33610000001'
        auth_data = login(username)
        api_key = auth_data['api_key']
        self.userId = auth_data['userid']
        self.authParam = '?username=%s&api_key=%s'%(urlquote_plus(username),
                                                    api_key)

    def test_logout(self):
        res = c.get('/api/v1/user/%s/%s'%(self.userId, self.authParam))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['username'], '+33610000001')
        res = c.get('/api/v1/user/logout/%s'%self.authParam)
        self.assertEqual(res.status_code, 200)
        res = c.get('/api/v1/user/logout/%s'%self.authParam)
        self.assertEqual(res.status_code, 401)
        res = c.get('/api/v1/user/%s/%s'%(self.userId, self.authParam))
        self.assertEqual(res.status_code, 401)
        
    def test_checkauth(self):
        # auth OK
        res = c.get('/api/v1/user/check_auth/%s'%self.authParam)
        self.assertEqual(res.status_code, 200)
        content = json.loads(res.content)
        self.assertEqual(content['userid'], self.u01.id)
        # wrong username / key
        res = c.get('/api/v1/user/check_auth/?username=toto&api_key=6565')
        self.assertEqual(res.status_code, 401)
        # logout
        res = c.get('/api/v1/user/logout/%s'%self.authParam)
        self.assertEqual(res.status_code, 200)
        # check (but key has changed)
        res = c.get('/api/v1/user/check_auth/%s'%self.authParam)
        self.assertEqual(res.status_code, 401)
        # double check with the new, return NOK as not logged in
        new_api_key = self.u01.api_key
        username = urlquote_plus('+33610000001')
        res = c.get('/api/v1/user/check_auth/?username=%s&api_key=%s'%(
                                                username, new_api_key))
        self.assertEqual(res.status_code, 401)        

    def test_register(self):
        inout = [
          { 'data'  : {},
            'result': {'httpcode' : 400, 'errorcode' : '10'} },
          { 'data'  : {'username' : '+33610001111'},
            'result': {'httpcode' : 400, 'errorcode' : '10'} },
          { 'data'  : {'password' : 'totopwd'},
            'result': {'httpcode' : 400, 'errorcode' : '10'} },
          { 'data'  : {'username' : '+33610001111', 'password' : 'totopwd'},
            'result': {'httpcode' : 400, 'errorcode' : '10'} },
          { 'data'  : {'username' : '+33610000001', 'password' : 'totopwd',
                        'name':'toto'},
            'result': {'httpcode' : 401, 'errorcode' : '200'} },
        ]
        for i in inout:
            res = c.post('/api/v1/auth/register/',
                            data = json.dumps(i['data']),
                            content_type='application/json')
            self.assertEqual(res.status_code, i['result']['httpcode'])
            content = json.loads(res.content)
            self.assertEqual(content['code'], i['result']['errorcode'])
        data = {'username' : '+33610001111', 'password' : 'totopwd',
                'name':'toto'}
        res = c.post('/api/v1/auth/register/',
                            data = json.dumps(data),
                            content_type='application/json')
        self.assertEqual(res.status_code, 201)
        content = json.loads(res.content)
        self.assertEqual(content['code'], '0')
        api_key = content['api_key']
        user_id = content['userid']
        #res = c.get('/api/v1/user/?username=%s&api_key=%s'%('toto', api_key))
        auth = '?username=%s&api_key=%s'%(urlquote_plus('+33610001111'), api_key)
        res = c.get('/api/v1/user/%s/%s'%(user_id, auth))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['username'], '+33610001111')
        # 2nd time, user exists already, will just login
        res = c.post('/api/v1/auth/register/',
                            data = json.dumps(data),
                            content_type='application/json')
        self.assertEqual(res.status_code, 201)
        # with extra spaces and uppercase char
        data = {'username' : '  sdSDfs@sdFSfd.fr', 'password' : 'totopwd',
                'name':'toto'}
        res = c.post('/api/v1/auth/register/',
                            data = json.dumps(data),
                            content_type='application/json')
        self.assertEqual(res.status_code, 201)
        content = json.loads(res.content)
        self.assertEqual(content['username'], 'sdsdfs@sdfsfd.fr')
        # with extra spaces and uppercase char
        data = {'username' : 'sdsdfs@sdfsfd.fr', 'password' : 'totopwd',
                'name':'toto'}
        res = c.post('/api/v1/auth/register/',
                            data = json.dumps(data),
                            content_type='application/json')
        self.assertEqual(res.status_code, 201)
        content = json.loads(res.content)
        self.assertEqual(content['username'], 'sdsdfs@sdfsfd.fr')

    def test_unmatched_auth_data(self):
        username = '+33610000001'
        auth_data = login(username)
        api_key = auth_data['api_key']
        user_id = auth_data['userid']
        auth = '?username=%s&api_key=%s'%(urlquote_plus(username), api_key)
        res = c.get('/api/v1/user/%s/%s'%(user_id, auth))
        self.assertEqual(res.status_code, 200)
        auth = '?username=%s&api_key=%s'%('wrong', api_key)
        res = c.get('/api/v1/user/%s/%s'%(user_id, auth))
        self.assertEqual(res.status_code, 401)
        auth = '?username=%s&api_key=%s'%(urlquote_plus(username), 'wrong')
        res = c.get('/api/v1/user/%s/%s'%(user_id, auth))
        self.assertEqual(res.status_code, 401)

    def test_profiles_creation(self):
        # if profiles are not properly created, this will generate an error
        UserProfile.objects.get(user=self.u01)
        UserPosition.objects.get(user=self.u01)

class ProfileTestCase(TestCase):
    c = Client()
    
    def setUp(self):
        super(ProfileTestCase, self).setUp()
        call_command('create_initial_data')
        self.u01 = User.objects.create_user(username='+33610000001',
                                            password='pwd')
        username = '+33610000001'
        auth_data = login(username)
        api_key = auth_data['api_key']
        self.userId = auth_data['userid']
        self.authParam = '?username=%s&api_key=%s'%(urlquote_plus(username),
                                                    api_key)

    def test_update_user(self):
        res = c.get('/api/v1/user/%s/%s'%(self.userId, self.authParam))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['first_name'], '')
        data = { 'first_name' : 'john' }
        res = c.put('/api/v1/user/%s/%s'%(self.userId, self.authParam),
                           data = json.dumps(data),
                           content_type='application/json')
        self.assertEqual(res.status_code, 204)
        res = c.get('/api/v1/user/%s/%s'%(self.userId, self.authParam))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['first_name'], 'john')

    def test_update_userprofile(self):
        res = c.get('/api/v1/userprofile/%s/%s'%(self.userId, self.authParam))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['gender'], '')
        data = {'gender' : 'MA'}
        res = c.put('/api/v1/userprofile/%s/%s'%(self.userId, self.authParam),
                           data = json.dumps(data),
                           content_type='application/json')
        self.assertEqual(res.status_code, 204)
        res = c.get('/api/v1/userprofile/%s/%s'%(self.userId, self.authParam))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['gender'], 'MA')

    def test_update_userposition(self):
        res = c.get('/api/v1/userposition/%s/%s'%(self.userId, self.authParam))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['last'], None)
        data = {'last' : '{ "type": "Point", "coordinates": [42.0, 2.0] }'}
        res = c.put('/api/v1/userposition/%s/%s'%(self.userId, self.authParam),
                           data = json.dumps(data),
                           content_type='application/json')
        self.assertEqual(res.status_code, 204)
        res = c.get('/api/v1/userposition/%s/%s'%(self.userId, self.authParam))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['last'], u'SRID=4326;POINT (42.0000000000000000 2.0000000000000000)')

class RelationshipTestCase(TestCase):
    c = Client()
    
    def setUp(self):
        super(RelationshipTestCase, self).setUp()
        call_command('create_initial_data')
        username = '+33610000001'
        self.u01 = User.objects.create_user(username=username, password='pwd')
        auth_data = login(username)
        api_key = auth_data['api_key']
        self.userId = auth_data['userid']
        self.authParam = '?username=%s&api_key=%s'%(urlquote_plus(username),
                                                    api_key)
        username = '+33610000002'
        self.u02 = User.objects.create_user(username=username, password='pwd')

    def test_invite(self):
        pass
