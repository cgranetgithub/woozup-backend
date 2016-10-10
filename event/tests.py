import json, datetime
from django.utils import timezone

from django.test import TestCase
from django.test.client import Client
from django.core.management import call_command
from django.contrib.auth.models import User
#from tastypie.test import ResourceTestCase

from event.models import Event, EventType, EventCategory
from link.models import Link
from service.testutils import register, login

c = Client()

class EventTestCase(TestCase):
    def setUp(self):
        super(EventTestCase, self).setUp()
        call_command('create_initial_data')
        self.u01 = register(c, 'aaa@aaa.aaa')
        cat = EventCategory.objects.create(name="meal")
        e = EventType.objects.create(name="meal")
        e.category.add(cat)

    def test_owner_journey(self):
        ### do typical sequence of calls an app would do
        email = 'aaa@aaa.aaa'
        (api_key, username) = login(c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        #user1 creates an event
        e_id = EventType.objects.first().id
        start = timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ%Z")
        data = {'event_type':'/api/v1/event_type/%d/'%e_id, 'start':start,
                'location_coords':'{ "type": "Point", "coordinates": [100.0, 0.0] }'}
        res = c.post('/api/v1/events/mine/%s'%auth,
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
        res = c.put('/api/v1/events/mine/%s/%s'%(ide, auth),
                         data = json.dumps(data),
                         content_type='application/json')
        e = Event.objects.get(id=ide)
        self.assertEqual(e.owner.user.email, 'aaa@aaa.aaa')
        self.assertEqual(e.event_type.id, e_id)
        self.assertEqual(e.location_coords.coords, (50.0, 50.0))
        #user1 deletes the event
        res = c.delete('/api/v1/events/mine/%s/%s'%(ide, auth))
        res = c.get('/api/v1/events/mine/%s/%s'%(ide, auth))
        self.assertEqual(res.status_code, 200)
        e = Event.objects.get(id=ide)
        self.assertEqual(e.canceled, True)
        exists = True
        try:
            Event.objects.get(id=1)
        except Event.DoesNotExist:
            exists = False
        self.assertFalse(exists)

    def test_my_events(self):
        ### events I can see
        email = 'aaa@aaa.aaa'
        (api_key, username) = login(c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        e = EventType.objects.first().id
        #start = timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ%Z")
        start = timezone.now().isoformat()
        data = {'event_type':'/api/v1/event_type/%d/'%e, 'start':start,
                'location_coords':'{ "type": "Point", "coordinates": [100.0, 0.0] }'}
        res = c.post('/api/v1/events/mine/%s'%auth,
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 201)
        res = c.get('/api/v1/events/mine/%s'%auth)
        content = json.loads(res.content)
        self.assertEqual(content['meta']['total_count'], 1)
        #self.assertEqual(cmp_result(content['objects'], expected), 5)
        #self.assertEqual(cmp_result(content['objects'], unexpected), 0)

    def test_unauth_method(self):
        email = 'aaa@aaa.aaa'
        (api_key, username) = login(c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        data = {'last':'{ "type": "Point", "coordinates": [100.0, 0.0] }'}
        res = c.post('/api/v1/userposition/setlast/%s'%auth,
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 200)
        #list
        res = c.get('/api/v1/events/mine/%s'%auth)
        self.assertEqual(res.status_code, 200)
        res = c.put('/api/v1/events/mine/%s'%auth)
        self.assertEqual(res.status_code, 405)
        res = c.patch('/api/v1/events/mine/%s'%auth)
        self.assertEqual(res.status_code, 405)
        res = c.delete('/api/v1/events/mine/%s'%auth)
        self.assertEqual(res.status_code, 405)
        e = EventType.objects.first().id
        start = timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ%Z")
        data = {'event_type':'/api/v1/event_type/%d/'%e, 'start':start,
                'location_coords':'{ "type": "Point", "coordinates": [100.0, 0.0] }'}
        res = c.post('/api/v1/events/mine/%s'%auth,
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 201)
        res = c.get('/api/v1/events/mine/%s'%auth)
        content = json.loads(res.content)
        self.assertEqual(content['meta']['total_count'], 1)
        event_id = content['objects'][0]['id']
        #detail
        res = c.get('/api/v1/events/mine/%s/%s'%(event_id, auth))
        self.assertEqual(res.status_code, 200)
        data = {'location_coords':'{ "type": "Point", "coordinates": [50.0, 50.0] }'}
        res = c.put('/api/v1/events/mine/%s/%s'%(event_id, auth),
                         data = json.dumps(data),
                         content_type='application/json')
        self.assertEqual(res.status_code, 204)
        res = c.patch('/api/v1/events/mine/%s/%s'%(event_id, auth),
                         data = json.dumps(data),
                         content_type='application/json')
        self.assertEqual(res.status_code, 405)
        res = c.post('/api/v1/events/mine/%s/%s'%(event_id, auth))
        self.assertEqual(res.status_code, 405)
        res = c.delete('/api/v1/events/mine/%s/%s'%(event_id, auth))
        self.assertEqual(res.status_code, 204)

    def test_unauth_user(self):
        res = c.get('/api/v1/events/mine/')
        self.assertEqual(res.status_code, 401)
        res = c.get('/api/v1/events/mine/1/')
        self.assertEqual(res.status_code, 401)

    def test_set_owner(self):
        ### try to create an event for someone else
        pass

    def test_join_leave(self):
        email = 'aaa@aaa.aaa'
        (api_key, username) = login(c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        # user1 creates an event
        etype = EventType.objects.first().id
        start = timezone.now().replace(microsecond=0)
        strstart = start.strftime("%Y-%m-%dT%H:%M:%SZ%Z")
        data = {'event_type':'/api/v1/event_type/%d/'%etype, 'start':strstart,
                'location_coords':'{ "type": "Point", "coordinates": [100.0, 0.0] }'}
        res = c.post('/api/v1/events/mine/%s'%auth,
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 201)
        ide = Event.objects.get(owner__user__username=username,
                                event_type=etype, start=start).id
        # user2 & user3 join
        email = 'bbb@bbb.bbb'
        u02 = register(c, 'bbb@bbb.bbb')
        (api_key, username) = login(c, email)
        auth2 = '?username=%s&api_key=%s'%(username, api_key)
        res = c.post('/api/v1/events/friends/join/%s/%s'%(ide, auth2),
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 200)
        email = 'ccc@ccc.ccc'
        u03 = register(c, 'ccc@ccc.ccc')
        (api_key, username) = login(c, email)
        auth3 = '?username=%s&api_key=%s'%(username, api_key)
        res = c.post('/api/v1/events/friends/join/%s/%s'%(ide, auth3),
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 200)
        e = Event.objects.get(id=ide)
        participants = [ i['user_id'] for i in e.participants.values() ]
        self.assertEqual(len(participants), 2)
        self.assertEqual(participants.sort(), [u02.id, u03.id].sort())
        # user3 leaves
        res = c.post('/api/v1/events/friends/leave/%s/%s'%(ide, auth3),
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 200)
        e = Event.objects.get(id=ide)
        participants = [ i['user_id'] for i in e.participants.values() ]
        self.assertEqual(len(participants), 1)
        self.assertEqual(participants.sort(), [u03.id].sort())

    def test_error_cases(self):
        email = 'aaa@aaa.aaa'
        (api_key, username) = login(c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        # user1 creates an event
        etype = EventType.objects.first().id
        start = timezone.now().replace(microsecond=0)
        strstart = start.strftime("%Y-%m-%dT%H:%M:%SZ%Z")
        data = {'event_type':'/api/v1/event_type/%d/'%etype, 'start':strstart,
                'location_coords':'{ "type": "Point", "coordinates": [100.0, 0.0] }'}
        res = c.post('/api/v1/events/mine/%s'%auth,
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 201)
        ide = Event.objects.get(owner__user__username=username,
                                event_type=etype, start=start).id
        # try to join it
        res = c.post('/api/v1/events/friends/join/%s/%s'%(ide, auth),
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 403)
        # wrong id
        res = c.post('/api/v1/events/friends/join/%s/%s'%(543, auth),
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 400)
        # join two times
        email = 'bbb@bbb.bbb'
        u02 = register(c, 'bbb@bbb.bbb')
        (api_key, username) = login(c, email)
        auth2 = '?username=%s&api_key=%s'%(username, api_key)
        res = c.post('/api/v1/events/friends/join/%s/%s'%(ide, auth2),
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 200)
        res = c.post('/api/v1/events/friends/join/%s/%s'%(ide, auth2),
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 403)
        # leave but not participant
        email = 'ccc@ccc.ccc'
        u03 = register(c, 'ccc@ccc.ccc')
        (api_key, username) = login(c, email)
        auth3 = '?username=%s&api_key=%s'%(username, api_key)
        res = c.post('/api/v1/events/friends/leave/%s/%s'%(ide, auth3),
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 403)

    def test_invitees(self):
        email = 'aaa@aaa.aaa'
        (api_key, username) = login(c, email)
        auth = '?username=%s&api_key=%s'%(username, api_key)
        # create some friends
        emails_list = ['friend1@ccc.ccc', 'friend2@ccc.ccc', 'friend3@ccc.ccc']
        friends_list = []
        for i in emails_list:
            u = register(c, i)
            friends_list.append(u)
            Link.objects.create(sender=self.u01.profile,
                                receiver=u.profile,
                                sender_status="ACC", receiver_status="ACC")
        # create an event for all friends
        etype = EventType.objects.first().id
        start = timezone.now().replace(microsecond=0)
        strstart = start.strftime("%Y-%m-%dT%H:%M:%SZ%Z")
        data = {'event_type':'/api/v1/event_type/%d/'%etype, 'start':strstart,
                'location_coords':'{ "type": "Point", "coordinates": [100.0, 0.0] }'}
        res = c.post('/api/v1/events/mine/%s'%auth,
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 201)
        ide = Event.objects.get(owner__user__username=username,
                                event_type=etype, start=start)
        emails = []
        for i in ide.get_invitees():
            emails.append(i.user.email)
        emails.sort()
        self.assertEqual(emails, emails_list)
        # create an event with selected invitees
        etype = EventType.objects.first().id
        start += datetime.timedelta(1)
        strstart = start.strftime("%Y-%m-%dT%H:%M:%SZ%Z")
        data = {'event_type':'/api/v1/event_type/%d/'%etype, 'start':strstart,
                'location_coords':'{ "type": "Point", "coordinates": [100.0, 0.0] }',
                'invitees':['/api/v1/userprofile/%d/'%friends_list[0].id,
                            '/api/v1/userprofile/%d/'%friends_list[1].id]}
        res = c.post('/api/v1/events/mine/%s'%auth,
                          data = json.dumps(data),
                          content_type='application/json')
        self.assertEqual(res.status_code, 201)
        ide = Event.objects.get(owner__user__username=username,
                                event_type=etype, start=start)
        emails = []
        for i in ide.get_invitees():
            emails.append(i.user.email)
        emails.sort()
        self.assertEqual(emails, ['friend1@ccc.ccc', 'friend2@ccc.ccc'])


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
        # create relations
        Link.objects.create(sender=self.u1.profile, sender_status='ACC',
                            receiver=self.u2.profile, receiver_status='ACC')
        Link.objects.create(sender=self.u1.profile, sender_status='ACC',
                            receiver=self.u3.profile, receiver_status='ACC')
        Link.objects.create(sender=self.u2.profile, sender_status='ACC',
                            receiver=self.u4.profile, receiver_status='ACC')
        # create categorie & type
        cat = EventCategory.objects.create(name="meal")
        etype = EventType.objects.create(name="meal")
        etype.category.add(cat)
        # create some events for u1
        e1 = Event.objects.create(owner=self.u1.profile, event_type=etype,
                                  start=timezone.now(),
                                  name="u1 breakfast",
                                  location_coords='{ "type": "Point", "coordinates": [50.0, 50.0] }')
        e2 = Event.objects.create(owner=self.u1.profile, event_type=etype,
                                  start=timezone.now(),
                                  name="u1 lunch",
                                  location_coords='{ "type": "Point", "coordinates": [50.0, 50.0] }')
        e2.participants.add(self.u2.profile)
        e3 = Event.objects.create(owner=self.u1.profile, event_type=etype,
                                  start=timezone.now(),
                                  name="u1 diner",
                                  location_coords='{ "type": "Point", "coordinates": [50.0, 50.0] }')
        e3.participants.add(self.u2.profile)
        e3.participants.add(self.u3.profile)
        # create some events for u2
        e1 = Event.objects.create(owner=self.u2.profile, event_type=etype,
                                  start=timezone.now(),
                                  name="u2 breakfast",
                                  location_coords='{ "type": "Point", "coordinates": [50.0, 50.0] }')
        e2 = Event.objects.create(owner=self.u2.profile, event_type=etype,
                                  start=timezone.now(),
                                  name="u2 lunch",
                                  location_coords='{ "type": "Point", "coordinates": [50.0, 50.0] }')
        e2.invitees.add(self.u1.profile)
        e2.participants.add(self.u1.profile)
        e3 = Event.objects.create(owner=self.u2.profile, event_type=etype,
                                  start=timezone.now(),
                                  name="u2 diner",
                                  location_coords='{ "type": "Point", "coordinates": [50.0, 50.0] }')
        e3.invitees.add(self.u4.profile)
        e3.participants.add(self.u4.profile)
        # create some events for u3
        e1 = Event.objects.create(owner=self.u3.profile, event_type=etype,
                                  start=timezone.now(),
                                  name="u3 breakfast",
                                  location_coords='{ "type": "Point", "coordinates": [50.0, 50.0] }')
        e2 = Event.objects.create(owner=self.u3.profile, event_type=etype,
                                  start=timezone.now(),
                                  name="u3 lunch",
                                  location_coords='{ "type": "Point", "coordinates": [50.0, 50.0] }')
        e2.participants.add(self.u1.profile)
        # create some events for u4
        e1 = Event.objects.create(owner=self.u4.profile, event_type=etype,
                                  start=timezone.now(),
                                  name="u4 breakfast",
                                  location_coords='{ "type": "Point", "coordinates": [50.0, 50.0] }')
        e2 = Event.objects.create(owner=self.u4.profile, event_type=etype,
                                  start=timezone.now(),
                                  name="u4 lunch",
                                  location_coords='{ "type": "Point", "coordinates": [50.0, 50.0] }')
        e2.participants.add(self.u2.profile)

    def test_AllEvents(self):
        res = c.get('/api/v1/events/all/%s'%(self.auth1))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 8)
        res = c.get('/api/v1/events/all/%s'%(self.auth2))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 8)
        res = c.get('/api/v1/events/all/%s'%(self.auth4))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 5)
        res = c.get('/api/v1/events/all/%s'%(self.auth4))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 5)
        res = c.get('/api/v1/events/all/%s'%(self.auth5))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 0)
    def test_MyAgenda(self):
        res = c.get('/api/v1/events/agenda/%s'%(self.auth1))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 5)
        res = c.get('/api/v1/events/agenda/%s'%(self.auth2))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 6)
        res = c.get('/api/v1/events/agenda/%s'%(self.auth3))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 3)
        res = c.get('/api/v1/events/agenda/%s'%(self.auth4))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 3)
        res = c.get('/api/v1/events/agenda/%s'%(self.auth5))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 0)
    def test_MyEvents(self):
        res = c.get('/api/v1/events/mine/%s'%(self.auth1))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 3)
        res = c.get('/api/v1/events/mine/%s'%(self.auth2))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 3)
        res = c.get('/api/v1/events/mine/%s'%(self.auth3))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 2)
        res = c.get('/api/v1/events/mine/%s'%(self.auth4))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 2)
        res = c.get('/api/v1/events/mine/%s'%(self.auth5))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 0)
    def test_FriendsEvents(self):
        res = c.get('/api/v1/events/friends/%s'%(self.auth1))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 4)
        res = c.get('/api/v1/events/friends/%s'%(self.auth2))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 5)
        res = c.get('/api/v1/events/friends/%s'%(self.auth3))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 3)
        res = c.get('/api/v1/events/friends/%s'%(self.auth4))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 2)
        res = c.get('/api/v1/events/friends/%s'%(self.auth5))
        content = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(content['meta']['total_count'], 0)
