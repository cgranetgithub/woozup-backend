#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import json, requests, datetime, random, string, pytz

#hostname = '127.0.0.1:8000'
hostname = 'geoevent.herokuapp.com'
api_url = 'http://%s/api/v1/'%hostname

def random_string():
    return ''.join([random.choice(string.ascii_lowercase) for n in xrange(3)])

types = json.loads(requests.get(api_url + 'event_type/').content)['objects']

file = open('nbuser.txt', 'r')
nb_user = int(file.read())

headers = {'content-type': 'application/json'}

if nb_user != 0:
    for i in range(7*nb_user/10):
        # login
        email = 'user%d@fr.fr'%(random.randint(1, nb_user))
        data = {'username':email, 'password':'pwd'}
        r = requests.post(api_url + 'auth/login/',
                          data = json.dumps(data),
                          headers = {'content-type': 'application/json'})
        # get api_key
        content = json.loads(r.content)
        api_key = content['api_key']
        username = email
        auth = '?username=%s&api_key=%s'%(username, api_key)
        # accept pending links
        r = requests.get(api_url + 'link/%s&receiver_status=PEN'%auth)
        content = json.loads(r.content)
        for i in content['objects']:
            r = requests.post(api_url + 'link/%s/accept/%s'%(i['id'], auth))


nb = 2

for i in range(nb):
    # create nb new users
    name = 'user%d'%(nb_user+i+1)
    email = '%s@fr.fr'%name
    r = requests.post(api_url + 'auth/register/', 
                      data=json.dumps({'username':email, 'password':'pwd',
                                       'first_name':name}),
                      headers = headers)
    # get api_key
    content = json.loads(r.content)
    api_key = content['api_key']
    username = email
    auth = '?username=%s&api_key=%s'%(username, api_key)
    # declare contacts
    if nb_user > nb:
        email_list = []
        for i in random.sample(range(1, nb_user, 1), nb_user/3):
            email_list.append({'email':'user%d@fr.fr'%i})
        r = requests.post(api_url + 'contact/sort/%s'%auth,
                        data = json.dumps(email_list),
                        headers = headers)
    # connect to contacts
    r = requests.get(api_url + 'link/%s&sender_status=NEW&receiver_status=NEW'%auth)
    content = json.loads(r.content)
    for i in content['objects']:
        r = requests.post(api_url + 'link/%s/connect/%s'%(i['id'], auth))
    # create events
    for i in range(3):
        dt = datetime.datetime.now(pytz.UTC) + datetime.timedelta(i+1)
        dt = dt.strftime("%Y-%m-%dT%H:%M:%SZ%Z")
        t = random.choice(types)
        p = "%f, %f"%(random.random() * 100, random.random() * 100)
        data = {'start' : dt, 'event_type' : t['resource_uri'], 'position' : p}
        r = requests.post(api_url + 'event/%s'%auth,
                          data = json.dumps(data),
                          headers = headers)

file = open("nbuser.txt", "w")
file.write("%d"%(nb_user+nb))
file.close()

