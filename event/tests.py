import json, datetime

from django.test import TestCase
from django.test.client import Client
from django.core.management import call_command
from django.contrib.auth.models import User
#from tastypie.test import ResourceTestCase

from event.models import Event, EventType, EventCategory

class EventTestCase(TestCase):
    c = Client()
    
    def setUp(self):
        """set up users with new events"""
        super(EventTestCase, self).setUp()
        call_command('create_initial_data')
        u01 = User.objects.create_user(username='user1@fr.fr', password='pwd')

    def test_owner_journey(self):
        """do typical sequence of calls an app would do"""
        username = 'user1@fr.fr'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        #user1 creates an event
        start = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ%Z")
        data = {'event_type':'/api/v1/event_type/1/', 'start':start,
                'position':'{ "type": "Point", "coordinates": [100.0, 0.0] }'}
        res = self.c.post('/api/v1/event/%s'%auth,
                          data = json.dumps(data),
                          content_type='application/json')
        for (i, j) in res.items():
            if i == 'Location':
                ide = j.strip('/').split('/')[-1]
                break
        e = Event.objects.get(id=ide)
        self.assertEqual(e.owner.username, 'user1@fr.fr')
        self.assertEqual(e.event_type.id, 1)
        self.assertEqual(e.position.coords, (100.0, 0.0))
        #user1 updates the event
        data = {'position':'{ "type": "Point", "coordinates": [50.0, 50.0] }'}
        res = self.c.put('/api/v1/event/%s/%s'%(ide, auth),
                         data = json.dumps(data),
                         content_type='application/json')
        e = Event.objects.get(id=ide)
        self.assertEqual(e.owner.username, 'user1@fr.fr')
        self.assertEqual(e.event_type.id, 1)
        self.assertEqual(e.position.coords, (50.0, 50.0))
        #user1 deletes the event
        res = self.c.delete('/api/v1/event/%s/%s'%(ide, auth))
        res = self.c.get('/api/v1/event/%s/%s'%(ide, auth))
        self.assertEqual(res.status_code, 404)
        exists = True
        try:
            Event.objects.get(id=1)
        except Event.DoesNotExist:
            exists = False
        self.assertFalse(exists)
            

    def test_my_events(self):
        """events I can see"""
        username = 'user1@fr.fr'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        start = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ%Z")
        data = {'event_type':'/api/v1/event_type/1/', 'start':start,
                'position':'{ "type": "Point", "coordinates": [100.0, 0.0] }'}
        res = self.c.post('/api/v1/event/%s'%auth,
                          data = json.dumps(data),
                          content_type='application/json')
        res = self.c.get('/api/v1/event/%s'%auth)
        content = json.loads(res.content)
        self.assertEqual(content['meta']['total_count'], 1)
        #self.assertEqual(cmp_result(content['objects'], expected), 5)
        #self.assertEqual(cmp_result(content['objects'], unexpected), 0)

    def test_unauth_method(self):
        username = 'user1@fr.fr'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        #list
        res = self.c.get('/api/v1/event/%s'%auth)
        self.assertEqual(res.status_code, 200)
        res = self.c.put('/api/v1/event/%s'%auth)
        self.assertEqual(res.status_code, 405)
        res = self.c.patch('/api/v1/event/%s'%auth)
        self.assertEqual(res.status_code, 405)
        res = self.c.delete('/api/v1/event/%s'%auth)
        self.assertEqual(res.status_code, 405)
        start = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ%Z")
        data = {'event_type':'/api/v1/event_type/1/', 'start':start,
                'position':'{ "type": "Point", "coordinates": [100.0, 0.0] }'}
        res = self.c.post('/api/v1/event/%s'%auth,
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 201)
        res = self.c.get('/api/v1/event/%s'%auth)
        content = json.loads(res.content)
        self.assertEqual(content['meta']['total_count'], 1)
        event_id = content['objects'][0]['id']
        #detail
        res = self.c.get('/api/v1/event/%s/%s'%(event_id, auth))
        self.assertEqual(res.status_code, 200)
        data = {'position':'{ "type": "Point", "coordinates": [50.0, 50.0] }'}
        res = self.c.put('/api/v1/event/%s/%s'%(event_id, auth),
                         data = json.dumps(data),
                         content_type='application/json')
        self.assertEqual(res.status_code, 204)
        res = self.c.patch('/api/v1/event/%s/%s'%(event_id, auth),
                         data = json.dumps(data),
                         content_type='application/json')
        self.assertEqual(res.status_code, 405)
        res = self.c.post('/api/v1/event/%s/%s'%(event_id, auth))
        self.assertEqual(res.status_code, 405)
        res = self.c.delete('/api/v1/event/%s/%s'%(event_id, auth))
        self.assertEqual(res.status_code, 204)

    def test_unauth_user(self):
        res = self.c.get('/api/v1/event/')
        self.assertEqual(res.status_code, 401)
        res = self.c.get('/api/v1/event/1/')
        self.assertEqual(res.status_code, 401)
        
    def test_set_owner(self):
        """try to create an event for someone else"""
        pass

    def test_join_leave(self):
        u02 = User.objects.create_user(username='user2@fr.fr', password='pwd')
        u03 = User.objects.create_user(username='user3@fr.fr', password='pwd')
        username = 'user1@fr.fr'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        # user1 creates an event
        start = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ%Z")
        data = {'event_type':'/api/v1/event_type/1/', 'start':start,
                'position':'{ "type": "Point", "coordinates": [100.0, 0.0] }'}
        res = self.c.post('/api/v1/event/%s'%auth,
                          data = json.dumps(data),
                          content_type='application/json')
        for (i, j) in res.items():
            if i == 'Location':
                ide = j.strip('/').split('/')[-1]
                break
        # user2 & user3 join
        username = 'user2@fr.fr'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        res = self.c.post('/api/v1/event/%s/join%s'%(ide, auth),
                          data = json.dumps(data),
                          content_type='application/json')
        username = 'user3@fr.fr'
        api_key = self.login(username)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        res = self.c.post('/api/v1/event/%s/join%s'%(ide, auth),
                          data = json.dumps(data),
                          content_type='application/json')
        e = Event.objects.get(id=ide)
        print e.participants.values()
        participants = [ i['username'] for i in e.participants.values() ]
        self.assertEqual(len(participants), 2)
        self.assertEqual(participants.sort(),
                         ['user2@fr.fr', 'user3@fr.fr'].sort())

    def login(self, username):
        data = {'username':username, 'password':'pwd'}
        res = self.c.post('/api/v1/auth/login/',
                          data = json.dumps(data),
                          content_type='application/json')
        content = json.loads(res.content)
        return content['api_key']
