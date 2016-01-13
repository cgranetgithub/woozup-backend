import json, datetime

from django.test import TestCase
from django.test.client import Client
from django.core.management import call_command
from django.contrib.auth.models import User
#from tastypie.test import ResourceTestCase

from event.models import Event, EventType, EventCategory
from service.testutils import register, login


class EventTestCase(TestCase):
    c = Client()
    
    def setUp(self):
        super(EventTestCase, self).setUp()
        call_command('create_initial_data')
        u01 = register(self.c, 'aaa@aaa.aaa')
        cat = EventCategory.objects.create(name="meal")
        e = EventType.objects.create(name="meal")
        e.category.add(cat)        

    def test_owner_journey(self):
        ### do typical sequence of calls an app would do
        email = 'aaa@aaa.aaa'
        (api_key, username) = login(self.c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        #user1 creates an event
        e_id = EventType.objects.first().id
        start = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ%Z")
        data = {'event_type':'/api/v1/event_type/%d/'%e_id, 'start':start,
                'location_coords':'{ "type": "Point", "coordinates": [100.0, 0.0] }'}
        res = self.c.post('/api/v1/events/mine/%s'%auth,
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 201)
        for (i, j) in res.items():
            if i == 'Location':
                ide = j.strip('/').split('/')[-1]
                break
        e = Event.objects.get(id=ide)
        self.assertEqual(e.owner.user.email, 'aaa@aaa.aaa')
        self.assertEqual(e.event_type.id, e_id)
        self.assertEqual(e.location_coords.coords, (100.0, 0.0))
        #user1 updates the event
        data = {'location_coords':'{ "type": "Point", "coordinates": [50.0, 50.0] }'}
        res = self.c.put('/api/v1/events/mine/%s/%s'%(ide, auth),
                         data = json.dumps(data),
                         content_type='application/json')
        e = Event.objects.get(id=ide)
        self.assertEqual(e.owner.user.email, 'aaa@aaa.aaa')
        self.assertEqual(e.event_type.id, e_id)
        self.assertEqual(e.location_coords.coords, (50.0, 50.0))
        #user1 deletes the event
        res = self.c.delete('/api/v1/events/mine/%s/%s'%(ide, auth))
        res = self.c.get('/api/v1/events/mine/%s/%s'%(ide, auth))
        self.assertEqual(res.status_code, 404)
        exists = True
        try:
            Event.objects.get(id=1)
        except Event.DoesNotExist:
            exists = False
        self.assertFalse(exists)
            

    def test_my_events(self):
        ### events I can see
        email = 'aaa@aaa.aaa'
        (api_key, username) = login(self.c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        e = EventType.objects.first().id
        #start = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ%Z")
        start = datetime.datetime.now().isoformat()
        data = {'event_type':'/api/v1/event_type/%d/'%e, 'start':start,
                'location_coords':'{ "type": "Point", "coordinates": [100.0, 0.0] }'}
        res = self.c.post('/api/v1/events/mine/%s'%auth,
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 201)
        res = self.c.get('/api/v1/events/mine/%s'%auth)
        content = json.loads(res.content)
        self.assertEqual(content['meta']['total_count'], 1)
        #self.assertEqual(cmp_result(content['objects'], expected), 5)
        #self.assertEqual(cmp_result(content['objects'], unexpected), 0)

    def test_unauth_method(self):
        email = 'aaa@aaa.aaa'
        (api_key, username) = login(self.c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        data = {'last':'{ "type": "Point", "coordinates": [100.0, 0.0] }'}
        res = self.c.post('/api/v1/userposition/setlast/%s'%auth,
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 200)
        #list
        res = self.c.get('/api/v1/events/mine/%s'%auth)
        self.assertEqual(res.status_code, 200)
        res = self.c.put('/api/v1/events/mine/%s'%auth)
        self.assertEqual(res.status_code, 405)
        res = self.c.patch('/api/v1/events/mine/%s'%auth)
        self.assertEqual(res.status_code, 405)
        res = self.c.delete('/api/v1/events/mine/%s'%auth)
        self.assertEqual(res.status_code, 405)
        e = EventType.objects.first().id
        start = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ%Z")
        data = {'event_type':'/api/v1/event_type/%d/'%e, 'start':start,
                'location_coords':'{ "type": "Point", "coordinates": [100.0, 0.0] }'}
        res = self.c.post('/api/v1/events/mine/%s'%auth,
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 201)
        res = self.c.get('/api/v1/events/mine/%s'%auth)
        content = json.loads(res.content)
        self.assertEqual(content['meta']['total_count'], 1)
        event_id = content['objects'][0]['id']
        #detail
        res = self.c.get('/api/v1/events/mine/%s/%s'%(event_id, auth))
        self.assertEqual(res.status_code, 200)
        data = {'location_coords':'{ "type": "Point", "coordinates": [50.0, 50.0] }'}
        res = self.c.put('/api/v1/events/mine/%s/%s'%(event_id, auth),
                         data = json.dumps(data),
                         content_type='application/json')
        self.assertEqual(res.status_code, 204)
        res = self.c.patch('/api/v1/events/mine/%s/%s'%(event_id, auth),
                         data = json.dumps(data),
                         content_type='application/json')
        self.assertEqual(res.status_code, 405)
        res = self.c.post('/api/v1/events/mine/%s/%s'%(event_id, auth))
        self.assertEqual(res.status_code, 405)
        res = self.c.delete('/api/v1/events/mine/%s/%s'%(event_id, auth))
        self.assertEqual(res.status_code, 204)

    def test_unauth_user(self):
        res = self.c.get('/api/v1/events/mine/')
        self.assertEqual(res.status_code, 401)
        res = self.c.get('/api/v1/events/mine/1/')
        self.assertEqual(res.status_code, 401)
        
    def test_set_owner(self):
        ### try to create an event for someone else
        pass

    def test_join_leave(self):
        email = 'aaa@aaa.aaa'
        (api_key, username) = login(self.c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        # user1 creates an event
        etype = EventType.objects.first().id
        start = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ%Z")
        data = {'event_type':'/api/v1/event_type/%d/'%etype, 'start':start,
                'location_coords':'{ "type": "Point", "coordinates": [100.0, 0.0] }'}
        res = self.c.post('/api/v1/events/mine/%s'%auth,
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 201)
        ide = Event.objects.get(owner__user__username=username,
                                event_type=etype, start=start).id
        # user2 & user3 join
        email = 'bbb@bbb.bbb'
        u02 = register(self.c, 'bbb@bbb.bbb')
        (api_key, username) = login(self.c, email)
        auth2 = '?username=%s&api_key=%s'%(username, api_key)
        res = self.c.post('/api/v1/events/friends/join/%s/%s'%(ide, auth2),
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 200)
        email = 'ccc@ccc.ccc'
        u03 = register(self.c, 'ccc@ccc.ccc')
        (api_key, username) = login(self.c, email)
        auth3 = '?username=%s&api_key=%s'%(username, api_key)
        res = self.c.post('/api/v1/events/friends/join/%s/%s'%(ide, auth3),
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 200)
        e = Event.objects.get(id=ide)
        participants = [ i['user_id'] for i in e.participants.values() ]
        self.assertEqual(len(participants), 2)
        self.assertEqual(participants.sort(), [u02.id, u03.id].sort())
        # user3 leaves
        res = self.c.post('/api/v1/events/friends/leave/%s/%s'%(ide, auth3),
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 200)
        e = Event.objects.get(id=ide)
        participants = [ i['user_id'] for i in e.participants.values() ]
        self.assertEqual(len(participants), 1)
        self.assertEqual(participants.sort(), [u03.id].sort())

    def test_error_cases(self):
        email = 'aaa@aaa.aaa'
        (api_key, username) = login(self.c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        # user1 creates an event
        etype = EventType.objects.first().id
        start = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ%Z")
        data = {'event_type':'/api/v1/event_type/%d/'%etype, 'start':start,
                'location_coords':'{ "type": "Point", "coordinates": [100.0, 0.0] }'}
        res = self.c.post('/api/v1/events/mine/%s'%auth,
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 201)
        ide = Event.objects.get(owner__user__username=username,
                                event_type=etype, start=start).id
        # try to join it
        res = self.c.post('/api/v1/events/friends/join/%s/%s'%(ide, auth),
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 403)
        # wrong id
        res = self.c.post('/api/v1/events/friends/join/%s/%s'%(543, auth),
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 400)
        # join two times
        email = 'bbb@bbb.bbb'
        u02 = register(self.c, 'bbb@bbb.bbb')
        (api_key, username) = login(self.c, email)
        auth2 = '?username=%s&api_key=%s'%(username, api_key)
        res = self.c.post('/api/v1/events/friends/join/%s/%s'%(ide, auth2),
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 200)
        res = self.c.post('/api/v1/events/friends/join/%s/%s'%(ide, auth2),
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 403)
        # leave but not participant
        email = 'ccc@ccc.ccc'
        u03 = register(self.c, 'ccc@ccc.ccc')
        (api_key, username) = login(self.c, email)
        auth3 = '?username=%s&api_key=%s'%(username, api_key)
        res = self.c.post('/api/v1/events/friends/leave/%s/%s'%(ide, auth3),
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 403)
        