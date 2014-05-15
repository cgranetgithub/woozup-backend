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

if nb_user != 0:
    for i in range(7*nb_user/10):
        # login
        email = 'user%d@fr.fr'%(random.randint(1, nb_user))
        data = {'username':email, 'password':'pwd'}
        r = requests.post(api_url + 'auth/login/',
                            data = json.dumps(data),
                            headers = {'content-type': 'application/json'})
        # get sessionid + csrftoken for POST)
        cookies = r.cookies
        sessionid = cookies['sessionid']
        csrftoken = cookies['csrftoken']
        # accept pending links


nb = 2

for i in range(nb):
    # create nb new users
    name = 'user%d'%(nb_user+i+1)
    email = '%s@fr.fr'%name
    r = requests.post(api_url + 'auth/register/', 
                      data=json.dumps({'username':email, 'password':'pwd',
                                       'first_name':name}),
                      headers = {'content-type': 'application/json'})
    # get sessionid + csrftoken for POST)
    cookies = r.cookies
    sessionid = cookies['sessionid']
    csrftoken = cookies['csrftoken']
    # connect to nb friends
    if nb_user > nb:
        for i in range(nb):
            data = {'receiver' : random.randint(1, nb_user)}
            r = requests.post(api_url + 'link/connect/',
                            data = json.dumps(data),
                            headers = {'content-type': 'application/json',
                                        'X-CSRFToken' : csrftoken},
                            cookies=cookies)
    # create events
    for i in range(3):
        dt = datetime.datetime.now(pytz.UTC) + datetime.timedelta(i+1)
        dt = dt.strftime("%Y-%m-%dT%H:%M:%SZ%Z")
        t = random.choice(types)
        p = "%f, %f"%(random.random() * 100, random.random() * 100)
        data = {'start' : dt, 'type' : t['resource_uri'], 'position' : p}
        r = requests.post(api_url + 'event/',
                        data = json.dumps(data),
                        headers = {'content-type': 'application/json',
                                    'X-CSRFToken' : csrftoken},
                        cookies=cookies)

file = open("nbuser.txt", "w")
file.write("%d"%(nb_user+nb))
file.close()

