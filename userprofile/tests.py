 #-*- coding: utf-8 -*-
import json

from django.test import TestCase
from django.test.client import Client
from django.core.management import call_command
from django.contrib.auth.models import User

from userprofile.models import Profile, Position
from service.testutils import register, login
from link.models import Link

c = Client()

class AuthTestCase(TestCase):

    def setUp(self):
        super(AuthTestCase, self).setUp()
        call_command('create_initial_data')
        email = 'bbb@bbb.bbb'
        self.u01 = register(c, email)
        (api_key, self.username) = login(c, email)
        self.authParam = '?username=%s&api_key=%s'%(self.username,
                                                    api_key)

    def test_logout(self):
        res = c.get('/api/v1/user/%s/%s'%(self.u01.id, self.authParam))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['username'], self.username)
        res = c.get('/api/v1/user/logout/%s'%self.authParam)
        self.assertEqual(res.status_code, 200)
        res = c.get('/api/v1/user/logout/%s'%self.authParam)
        self.assertEqual(res.status_code, 401)
        res = c.get('/api/v1/user/%s/%s'%(self.u01.id,
                                          self.authParam))
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
        res = c.get('/api/v1/user/check_auth/?username=%s&api_key=%s'%(
                                        self.u01.username, self.u01.api_key))
        self.assertEqual(res.status_code, 401)

    def test_register(self):
        inout = [
          { 'data'  : {},
            'result': {'httpcode' : 400, 'errorcode' : '10'} },
          { 'data'  : {'email' : 'aaa@aaa.aaa'},
            'result': {'httpcode' : 400, 'errorcode' : '20'} },
          { 'data'  : {'password' : 'totopwdpwd'},
            'result': {'httpcode' : 400, 'errorcode' : '10'} },
          #password too short
          { 'data'  : {'email' : 'aaa@aaa.aaa', 'password' : 'pwd'},
            'result': {'httpcode' : 400, 'errorcode' : '300'} },
          { 'data'  : {'email' : 'bbbb.bbb', 'password' : 'totopwdpwd',
                        'name':'toto'},
            'result': {'httpcode' : 400, 'errorcode' : '300'} },
        ]
        for i in inout:
            res = c.post('/api/v1/auth/register_by_email/',
                            data = json.dumps(i['data']),
                            content_type='application/json')
            self.assertEqual(res.status_code, i['result']['httpcode'])
            content = json.loads(res.content)
            self.assertEqual(content['code'], i['result']['errorcode'])
        data = {'email' : 'aaa@aaa.aaa', 'password' : 'totopwdpwd'}
        res = c.post('/api/v1/auth/register_by_email/',
                            data = json.dumps(data),
                            content_type='application/json')
        self.assertEqual(res.status_code, 201)
        content = json.loads(res.content)
        self.assertEqual(content['code'], '0')
        api_key = content['api_key']
        user_id = content['userid']
        username = content['username']
        #res = c.get('/api/v1/user/?username=%s&api_key=%s'%('toto', api_key))
        auth = '?username=%s&api_key=%s'%(username, api_key)
        res = c.get('/api/v1/user/%s/%s'%(user_id, auth))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['username'], username)
        # 2nd time, user exists already, error
        res = c.post('/api/v1/auth/register_by_email/',
                            data = json.dumps(data),
                            content_type='application/json')
        self.assertEqual(res.status_code, 400)
        # with extra spaces and uppercase char
        data = {'email' : '  sdSDfs@sdFSfd.fr', 'password' : 'totopwdpwd'}
        res = c.post('/api/v1/auth/register_by_email/',
                            data = json.dumps(data),
                            content_type='application/json')
        self.assertEqual(res.status_code, 201)
        content = json.loads(res.content)
        self.assertEqual(content['username'], 'sdsdfs')

    def test_unmatched_auth_data(self):
        email = 'bbb@bbb.bbb'
        (api_key, username) = login(c, email)
        user = User.objects.get(username=username)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        res = c.get('/api/v1/user/%s/%s'%(user.id, auth))
        self.assertEqual(res.status_code, 200)
        auth = '?username=%s&api_key=%s'%('wrong', api_key)
        res = c.get('/api/v1/user/%s/%s'%(user.id, auth))
        self.assertEqual(res.status_code, 401)
        auth = '?username=%s&api_key=%s'%(username, 'wrong')
        res = c.get('/api/v1/user/%s/%s'%(user.id, auth))
        self.assertEqual(res.status_code, 401)

    def test_profiles_creation(self):
        # if profiles are not properly created, this will generate an error
        Profile.objects.get(user=self.u01)
        Position.objects.get(user=self.u01)

class ProfileTestCase(TestCase):
    def setUp(self):
        super(ProfileTestCase, self).setUp()
        call_command('create_initial_data')
        email = 'bbb@bbb.bbb'
        self.u01 = register(c, email)
        (api_key, self.username) = login(c, email)
        self.authParam = '?username=%s&api_key=%s'%(self.username,
                                                    api_key)

    def test_update_user(self):
        res = c.get('/api/v1/user/%s/%s'%(self.u01.id,
                                          self.authParam))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['first_name'], '')
        data = { 'first_name' : 'john' }
        res = c.put('/api/v1/user/%s/%s'%(self.u01.id,
                                          self.authParam),
                           data = json.dumps(data),
                           content_type='application/json')
        self.assertEqual(res.status_code, 204)
        res = c.get('/api/v1/user/%s/%s'%(self.u01.id,
                                          self.authParam))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['first_name'], 'john')

    #def test_update_userprofile(self):
        #res = c.get('/api/v1/userprofile/%s/%s'%(self.u01.id, self.authParam))
        #content = json.loads(res.content)
        #self.assertEqual(res.status_code, 200)
        #self.assertEqual(content['gender'], '')
        #data = {'gender' : 'MA'}
        #res = c.put('/api/v1/userprofile/%s/%s'%(self.u01.id, self.authParam),
                           #data = json.dumps(data),
                           #content_type='application/json')
        #self.assertEqual(res.status_code, 204)
        #res = c.get('/api/v1/userprofile/%s/%s'%(self.u01.id, self.authParam))
        #content = json.loads(res.content)
        #self.assertEqual(res.status_code, 200)
        #self.assertEqual(content['gender'], 'MA')

    def test_update_userposition(self):
        res = c.get('/api/v1/userposition/%s/%s'%(self.u01.id,
                                                  self.authParam))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['last'], None)
        data = {'last' : '{ "type": "Point", "coordinates": [42.0, 2.0] }'}
        res = c.put('/api/v1/userposition/%s/%s'%(self.u01.id,
                                                  self.authParam),
                                            data = json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(res.status_code, 204)
        res = c.get('/api/v1/userposition/%s/%s'%(self.u01.id, self.authParam))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['last'],
                         u'SRID=4326;POINT (42.0000000000000000 2.0000000000000000)')

class PositionTestCase(TestCase):
    def setUp(self):
        super(PositionTestCase, self).setUp()
        call_command('create_initial_data')
        email = 'bbb@bbb.bbb'
        self.u01 = register(c, email)
        (api_key, self.username) = login(c, email)
        self.authParam = '?username=%s&api_key=%s'%(self.username,
                                                    api_key)

    def test_setlast(self):
        # no position
        res = c.post('/api/v1/userposition/setlast/%s'%self.authParam,
                        data = json.dumps({}),
                        content_type='application/json')
        self.assertEqual(res.status_code, 400)
        # empty position
        res = c.post('/api/v1/userposition/setlast/%s'%self.authParam,
                        data = json.dumps({'last':''}),
                        content_type='application/json')
        self.assertEqual(res.status_code, 400)
        # no auth
        res = c.post('/api/v1/userposition/setlast/',
                        data = json.dumps({}),
                        content_type='application/json')
        self.assertEqual(res.status_code, 401)
        #
        res = c.post('/api/v1/userposition/setlast/%s'%self.authParam,
                        data = json.dumps({'last':'{ "type": "Point", "coordinates": [42.0, 2.0] }'}),
                        content_type='application/json')
        self.assertEqual(self.u01.position.last.geojson,
                         u'{"type": "Point", "coordinates": [42.0, 2.0]}')

    def test_setprofile(self):
        data = {'first_name':'toto', 'last_name':'tata',
                'email':'toto@gmail.com', 'number':'+33667890343',
                'gender':'MA'}
        res = c.post('/api/v1/userprofile/setprofile/%s'%self.authParam,
                        data = json.dumps(data),
                        content_type='application/json')
        u01 = User.objects.get(username=self.username)
        self.assertEqual(u01.first_name, 'toto')
        self.assertEqual(u01.last_name, 'tata')
        self.assertEqual(u01.email, 'toto@gmail.com')
        self.assertEqual(u01.profile.phone_number, '+33667890343')
        self.assertEqual(u01.profile.gender, 'MA')

    def test_resetpassword(self):
        # just call the API for code coverage, if no error raised, fine!
        res = c.post('/api/v1/auth/reset_password/%s'%self.authParam,
                        data = json.dumps({}),
                        content_type='application/json')

    def test_pushnotifreg(self):
        u01 = User.objects.get(username=self.username)
        data = {'device_id': '16146319360533899348',
                'platform' : 'android',
                'name'     : 'SM-N9005'}
        res = c.post('/api/v1/user/push_notif_reg/%s'%self.authParam,
                        data = json.dumps(data),
                        content_type='application/json')
        self.assertEqual(res.status_code, 400)
        data = {'registration_id':'fUsO4fSkoik:APA91bHKLLyjWOyKTzlQ1M7KINv30LWLEvP769hNOqNoIWTQdkt4goHc59uYaFz0Bp34ZFZDvwWL7zJeZix_l33ttHZNsyajVLqQbs3plI5dIZHMjL5EpIULLiX1_BXJx-j-cokt_387',
                'platform' : 'android',
                'name'     : 'SM-N9005'}
        res = c.post('/api/v1/user/push_notif_reg/%s'%self.authParam,
                        data = json.dumps(data),
                        content_type='application/json')
        self.assertEqual(res.status_code, 400)
        data = {'registration_id':'fUsO4fSkoik:APA91bHKLLyjWOyKTzlQ1M7KINv30LWLEvP769hNOqNoIWTQdkt4goHc59uYaFz0Bp34ZFZDvwWL7zJeZix_l33ttHZNsyajVLqQbs3plI5dIZHMjL5EpIULLiX1_BXJx-j-cokt_387',
                'device_id': '16146319360533899348',
                'name'     : 'SM-N9005'}
        res = c.post('/api/v1/user/push_notif_reg/%s'%self.authParam,
                        data = json.dumps(data),
                        content_type='application/json')
        self.assertEqual(res.status_code, 400)
        data = {'registration_id':'fUsO4fSkoik:APA91bHKLLyjWOyKTzlQ1M7KINv30LWLEvP769hNOqNoIWTQdkt4goHc59uYaFz0Bp34ZFZDvwWL7zJeZix_l33ttHZNsyajVLqQbs3plI5dIZHMjL5EpIULLiX1_BXJx-j-cokt_387',
                'device_id': '899348',
                'platform' : 'android'}
        res = c.post('/api/v1/user/push_notif_reg/%s'%self.authParam,
                        data = json.dumps(data),
                        content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = {'registration_id':'fUsO4fSkoik:APA91bHKLLyjWOyKTzlQ1M7KINv30LWLEvP769hNOqNoIWTQdkt4goHc59uYaFz0Bp34ZFZDvwWL7zJeZix_l33ttHZNsyajVLqQbs3plI5dIZHMjL5EpIULLiX1_BXJx-j-cokt_387',
                'device_id': '60533899348',
                'platform' : 'android',
                'name'     : 'SM-N9005'}
        res = c.post('/api/v1/user/push_notif_reg/%s'%self.authParam,
                        data = json.dumps(data),
                        content_type='application/json')
        self.assertEqual(res.status_code, 200)
        from push_notifications.models import APNSDevice, GCMDevice
        gcm = GCMDevice.objects.get(user=u01, device_id='60533899348')
        self.assertEqual(gcm.registration_id, 'fUsO4fSkoik:APA91bHKLLyjWOyKTzlQ1M7KINv30LWLEvP769hNOqNoIWTQdkt4goHc59uYaFz0Bp34ZFZDvwWL7zJeZix_l33ttHZNsyajVLqQbs3plI5dIZHMjL5EpIULLiX1_BXJx-j-cokt_387')
        self.assertEqual(gcm.device_id, int('60533899348', 16))
        self.assertEqual(gcm.name, 'SM-N9005')
        # iOS
        data = {'registration_id':'853963aad5c73f1d28efb57e9b89e2db8effe6e34ad9f5424871b76792a40d84',
                'device_id': '5a1972adee554154800f9d3c84889fda',
                'platform' : 'ios',
                'name'     : 'iPad2,5'}
        res = c.post('/api/v1/user/push_notif_reg/%s'%self.authParam,
                        data = json.dumps(data),
                        content_type='application/json')
        self.assertEqual(res.status_code, 200)
        from push_notifications.models import APNSDevice, GCMDevice
        apns = APNSDevice.objects.get(user=u01, device_id='5a1972adee554154800f9d3c84889fda')
        self.assertEqual(apns.registration_id, '853963aad5c73f1d28efb57e9b89e2db8effe6e34ad9f5424871b76792a40d84')
        self.assertEqual(apns.device_id.hex, '5a1972adee554154800f9d3c84889fda')
        self.assertEqual(apns.name, 'iPad2,5')

class RelationshipTestCase(TestCase):
    def setUp(self):
        super(RelationshipTestCase, self).setUp()
        call_command('create_initial_data')
        email = 'aaa@aaa.aaa'
        self.u1 = register(c, email)
        (api_key, username) = login(c, email)
        self.auth1 = '?username=%s&api_key=%s'%(username, api_key)
        email = 'bbb@bbb.bbb'
        self.u2 = register(c, email)
        (api_key, username) = login(c, email)
        self.auth2 = '?username=%s&api_key=%s'%(username, api_key)
        email = 'ccc@ccc.ccc'
        self.u3 = register(c, email)
        (api_key, username) = login(c, email)
        self.auth3 = '?username=%s&api_key=%s'%(username, api_key)
        email = 'ddd@ddd.ddd'
        self.u4 = register(c, email)
        (api_key, username) = login(c, email)
        self.auth4 = '?username=%s&api_key=%s'%(username, api_key)

    def test_oneway(self):
        l1 = Link.objects.create(sender=self.u1.profile,
                                 receiver=self.u2.profile)
        l2 = Link.objects.create(sender=self.u1.profile,
                                 receiver=self.u3.profile)
        l3 = Link.objects.create(sender=self.u1.profile,
                                 receiver=self.u4.profile)
        self.assertEqual(l1.sender_status, 'NEW')
        self.assertEqual(l2.sender_status, 'NEW')
        self.assertEqual(l3.sender_status, 'NEW')
        self.assertEqual(l1.receiver_status, 'NEW')
        self.assertEqual(l2.receiver_status, 'NEW')
        self.assertEqual(l3.receiver_status, 'NEW')
        # u1 invites u2
        res = c.post('/api/v1/user/invite/%d/%s'%(self.u2.id, self.auth1),
                        data = json.dumps({}),
                        content_type='application/json')
        self.assertEqual(res.status_code, 200)
        l1 = Link.objects.get(sender=self.u1.profile,
                              receiver=self.u2.profile)
        self.assertEqual(l1.sender_status, 'ACC')
        self.assertEqual(l1.receiver_status, 'PEN')
        # u2 accepts u1
        res = c.post('/api/v1/user/accept/%d/%s'%(self.u1.id, self.auth2),
                        data = json.dumps({}),
                        content_type='application/json')
        self.assertEqual(res.status_code, 200)
        l1 = Link.objects.get(sender=self.u1.profile,
                              receiver=self.u2.profile)
        self.assertEqual(l1.sender_status, 'ACC')
        self.assertEqual(l1.receiver_status, 'ACC')
        # u1 ignore u3
        res = c.post('/api/v1/user/ignore/%d/%s'%(self.u3.id, self.auth1),
                        data = json.dumps({}),
                        content_type='application/json')
        self.assertEqual(res.status_code, 200)
        l2 = Link.objects.get(sender=self.u1.profile,
                              receiver=self.u3.profile)
        self.assertEqual(l2.sender_status, 'IGN')
        self.assertEqual(l2.receiver_status, 'NEW')
        # u1 invites u4
        res = c.post('/api/v1/user/invite/%d/%s'%(self.u4.id, self.auth1),
                        data = json.dumps({}),
                        content_type='application/json')
        self.assertEqual(res.status_code, 200)
        l3 = Link.objects.get(sender=self.u1.profile,
                              receiver=self.u4.profile)
        self.assertEqual(l3.sender_status, 'ACC')
        self.assertEqual(l3.receiver_status, 'PEN')
        # u4 accepts u1
        res = c.post('/api/v1/user/reject/%d/%s'%(self.u1.id, self.auth4),
                        data = json.dumps({}),
                        content_type='application/json')
        self.assertEqual(res.status_code, 200)
        l3 = Link.objects.get(sender=self.u1.profile,
                              receiver=self.u4.profile)
        self.assertEqual(l3.sender_status, 'ACC')
        self.assertEqual(l3.receiver_status, 'REJ')

    def test_theotherway(self):
        l1 = Link.objects.create(receiver=self.u1.profile,
                                 sender=self.u2.profile)
        l2 = Link.objects.create(receiver=self.u1.profile,
                                 sender=self.u3.profile)
        l3 = Link.objects.create(receiver=self.u1.profile,
                                 sender=self.u4.profile)
        self.assertEqual(l1.sender_status, 'NEW')
        self.assertEqual(l2.sender_status, 'NEW')
        self.assertEqual(l3.sender_status, 'NEW')
        self.assertEqual(l1.receiver_status, 'NEW')
        self.assertEqual(l2.receiver_status, 'NEW')
        self.assertEqual(l3.receiver_status, 'NEW')
        # u1 invites u2
        res = c.post('/api/v1/user/invite/%d/%s'%(self.u2.id, self.auth1),
                        data = json.dumps({}),
                        content_type='application/json')
        self.assertEqual(res.status_code, 200)
        l1 = Link.objects.get(receiver=self.u1.profile,
                              sender=self.u2.profile)
        self.assertEqual(l1.receiver_status, 'ACC')
        self.assertEqual(l1.sender_status, 'PEN')
        # u2 accepts u1
        res = c.post('/api/v1/user/accept/%d/%s'%(self.u1.id, self.auth2),
                        data = json.dumps({}),
                        content_type='application/json')
        self.assertEqual(res.status_code, 200)
        l1 = Link.objects.get(receiver=self.u1.profile,
                              sender=self.u2.profile)
        self.assertEqual(l1.receiver_status, 'ACC')
        self.assertEqual(l1.sender_status, 'ACC')
        # u1 ignore u3
        res = c.post('/api/v1/user/ignore/%d/%s'%(self.u3.id, self.auth1),
                        data = json.dumps({}),
                        content_type='application/json')
        self.assertEqual(res.status_code, 200)
        l2 = Link.objects.get(receiver=self.u1.profile,
                              sender=self.u3.profile)
        self.assertEqual(l2.receiver_status, 'IGN')
        self.assertEqual(l2.sender_status, 'NEW')
        # u1 invites u4
        res = c.post('/api/v1/user/invite/%d/%s'%(self.u4.id, self.auth1),
                        data = json.dumps({}),
                        content_type='application/json')
        self.assertEqual(res.status_code, 200)
        l3 = Link.objects.get(receiver=self.u1.profile,
                              sender=self.u4.profile)
        self.assertEqual(l3.receiver_status, 'ACC')
        self.assertEqual(l3.sender_status, 'PEN')
        # u4 accepts u1
        res = c.post('/api/v1/user/reject/%d/%s'%(self.u1.id, self.auth4),
                        data = json.dumps({}),
                        content_type='application/json')
        self.assertEqual(res.status_code, 200)
        l3 = Link.objects.get(receiver=self.u1.profile,
                              sender=self.u4.profile)
        self.assertEqual(l3.receiver_status, 'ACC')
        self.assertEqual(l3.sender_status, 'REJ')

class ResourcesTestCase(TestCase):
    def setUp(self):
        super(ResourcesTestCase, self).setUp()
        call_command('create_initial_data')
        # create some users
        email = 'aaa@aaa.aaa'
        self.u1 = register(c, email)
        (api_key, username) = login(c, email)
        self.auth1 = '?username=%s&api_key=%s'%(username, api_key)
        email = 'bbb@bbb.bbb'
        self.u2 = register(c, email)
        (api_key, username) = login(c, email)
        self.auth2 = '?username=%s&api_key=%s'%(username, api_key)
        email = 'ccc@ccc.ccc'
        self.u3 = register(c, email)
        (api_key, username) = login(c, email)
        self.auth3 = '?username=%s&api_key=%s'%(username, api_key)
        email = 'ddd@ddd.ddd'
        self.u4 = register(c, email)
        (api_key, username) = login(c, email)
        self.auth4 = '?username=%s&api_key=%s'%(username, api_key)
        email = 'eee@eee.eee'
        self.u5 = register(c, email)
        (api_key, username) = login(c, email)
        self.auth5 = '?username=%s&api_key=%s'%(username, api_key)
        email = 'fff@fff.fff'
        self.u6 = register(c, email)
        (api_key, username) = login(c, email)
        self.auth6 = '?username=%s&api_key=%s'%(username, api_key)
        email = 'ggg@ggg.ggg'
        self.u7 = register(c, email)
        (api_key, username) = login(c, email)
        self.auth7 = '?username=%s&api_key=%s'%(username, api_key)
        email = 'hhh@hhh.hhh'
        self.u8 = register(c, email)
        (api_key, username) = login(c, email)
        self.auth8 = '?username=%s&api_key=%s'%(username, api_key)
        email = 'iii@iii.iii'
        self.u9 = register(c, email)
        (api_key, username) = login(c, email)
        self.auth9 = '?username=%s&api_key=%s'%(username, api_key)
        email = 'jjj@jjj.jjj'
        self.u10 = register(c, email)
        (api_key, username) = login(c, email)
        self.auth10 = '?username=%s&api_key=%s'%(username, api_key)
        email = 'kkk@kk.kkk'
        self.u11 = register(c, email)
        (api_key, username) = login(c, email)
        self.auth11 = '?username=%s&api_key=%s'%(username, api_key)
        email = 'lll@lll.lll'
        self.u12 = register(c, email)
        (api_key, username) = login(c, email)
        self.auth12 = '?username=%s&api_key=%s'%(username, api_key)
        email = 'mmm@mmm.mmm'
        self.u13 = register(c, email)
        (api_key, username) = login(c, email)
        self.auth13 = '?username=%s&api_key=%s'%(username, api_key)
        email = 'nnn@nnn.nnn'
        self.u14 = register(c, email)
        (api_key, username) = login(c, email)
        self.auth14 = '?username=%s&api_key=%s'%(username, api_key)
        email = 'ooo@ooo.ooo'
        self.u15 = register(c, email)
        (api_key, username) = login(c, email)
        self.auth15 = '?username=%s&api_key=%s'%(username, api_key)
        email = 'ppp@ppp.ppp'
        self.u16 = register(c, email)
        (api_key, username) = login(c, email)
        self.auth16 = '?username=%s&api_key=%s'%(username, api_key)
        email = 'qqq@qqq.qqq'
        self.u17 = register(c, email)
        (api_key, username) = login(c, email)
        self.auth17 = '?username=%s&api_key=%s'%(username, api_key)
        # create relations for u1
        Link.objects.create(sender=self.u1.profile, sender_status='NEW',
                            receiver=self.u2.profile, receiver_status='NEW')
        Link.objects.create(sender=self.u1.profile, sender_status='NEW',
                            receiver=self.u3.profile, receiver_status='IGN')
        Link.objects.create(sender=self.u1.profile, sender_status='IGN',
                            receiver=self.u4.profile, receiver_status='NEW')
        Link.objects.create(sender=self.u1.profile, sender_status='ACC',
                            receiver=self.u5.profile, receiver_status='PEN')
        Link.objects.create(sender=self.u1.profile, sender_status='PEN',
                            receiver=self.u6.profile, receiver_status='ACC')
        Link.objects.create(sender=self.u1.profile, sender_status='ACC',
                            receiver=self.u7.profile, receiver_status='REJ')
        Link.objects.create(sender=self.u1.profile, sender_status='REJ',
                            receiver=self.u8.profile, receiver_status='ACC')
        Link.objects.create(sender=self.u1.profile, sender_status='ACC',
                            receiver=self.u9.profile, receiver_status='ACC')
        Link.objects.create(sender=self.u10.profile, sender_status='NEW',
                            receiver=self.u1.profile, receiver_status='NEW')
        Link.objects.create(sender=self.u11.profile, sender_status='NEW',
                            receiver=self.u1.profile, receiver_status='IGN')
        Link.objects.create(sender=self.u12.profile, sender_status='IGN',
                            receiver=self.u1.profile, receiver_status='NEW')
        Link.objects.create(sender=self.u13.profile, sender_status='ACC',
                            receiver=self.u1.profile, receiver_status='PEN')
        Link.objects.create(sender=self.u14.profile, sender_status='PEN',
                            receiver=self.u1.profile, receiver_status='ACC')
        Link.objects.create(sender=self.u15.profile, sender_status='ACC',
                            receiver=self.u1.profile, receiver_status='REJ')
        Link.objects.create(sender=self.u16.profile, sender_status='REJ',
                            receiver=self.u1.profile, receiver_status='ACC')
        Link.objects.create(sender=self.u17.profile, sender_status='ACC',
                            receiver=self.u1.profile, receiver_status='ACC')
        # create relations for u2
        Link.objects.create(sender=self.u2.profile, sender_status='PEN',
                            receiver=self.u3.profile, receiver_status='ACC')
        Link.objects.create(sender=self.u2.profile, sender_status='PEN',
                            receiver=self.u5.profile, receiver_status='ACC')
        Link.objects.create(sender=self.u2.profile, sender_status='PEN',
                            receiver=self.u7.profile, receiver_status='ACC')
        Link.objects.create(sender=self.u2.profile, sender_status='PEN',
                            receiver=self.u9.profile, receiver_status='ACC')
        Link.objects.create(sender=self.u2.profile, sender_status='PEN',
                            receiver=self.u10.profile, receiver_status='ACC')
        # create relations for u3
        Link.objects.create(sender=self.u3.profile, sender_status='NEW',
                            receiver=self.u6.profile, receiver_status='NEW')
        Link.objects.create(sender=self.u3.profile, sender_status='NEW',
                            receiver=self.u8.profile, receiver_status='NEW')
        Link.objects.create(sender=self.u3.profile, sender_status='NEW',
                            receiver=self.u10.profile, receiver_status='NEW')
        Link.objects.create(sender=self.u3.profile, sender_status='ACC',
                            receiver=self.u12.profile, receiver_status='ACC')
        Link.objects.create(sender=self.u3.profile, sender_status='ACC',
                            receiver=self.u14.profile, receiver_status='ACC')

    def test_MyFriends(self):
        res = c.get('/api/v1/friends/mine/%s'%(self.auth1))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 2)
        res = c.get('/api/v1/friends/mine/%s'%(self.auth2))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 0)
        res = c.get('/api/v1/friends/mine/%s'%(self.auth3))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 2)
    def test_PendingFriends(self):
        res = c.get('/api/v1/friends/pending/%s'%(self.auth1))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 2)
        res = c.get('/api/v1/friends/pending/%s'%(self.auth2))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 5)
        res = c.get('/api/v1/friends/pending/%s'%(self.auth3))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 0)
    def test_NewFriends(self):
        res = c.get('/api/v1/friends/new/%s'%(self.auth1))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 4)
        res = c.get('/api/v1/friends/new/%s'%(self.auth2))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 1)
        res = c.get('/api/v1/friends/new/%s'%(self.auth3))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 3)
    def test_profile_access(self):
        res = c.get('/api/v1/userprofile/%d/%s'%(self.u1.id, self.auth1))
        self.assertEqual(res.status_code, 200)
        res = c.get('/api/v1/userprofile/%d/%s'%(self.u9.id, self.auth1))
        self.assertEqual(res.status_code, 200)
        res = c.get('/api/v1/userprofile/%d/%s'%(self.u17.id, self.auth1))
        self.assertEqual(res.status_code, 200)
        res = c.get('/api/v1/userprofile/%d/%s'%(self.u4.id, self.auth1))
        self.assertEqual(res.status_code, 404)
        res = c.get('/api/v1/userprofile/%d/%s'%(self.u5.id, self.auth1))
        self.assertEqual(res.status_code, 404)
