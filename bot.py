 #!/usr/bin/python
 # -*- coding: utf-8 -*-

import json, requests, datetime, random, string, pytz

#hostname = '127.0.0.1:8000'
hostname = 'geoevent.herokuapp.com'
api_url = 'http://%s/api/v1/'%hostname

def random_string():
    return ''.join([random.choice(string.ascii_lowercase) for n in xrange(3)])

types = json.loads(requests.get(api_url + 'type/').content)['objects']

for i in range(2):
    # create new users
    email = '%s@%s.%s'%(random_string(), random_string(), random_string())
    r = requests.post(api_url + 'auth/register/', 
                      data=json.dumps({'username':email, 'password':'pwd',
                                       'first_name':random_string()}),
                      headers = {'content-type': 'application/json'})
    # get sessionid + csrftoken for POST)
    cookies = r.cookies
    sessionid = cookies['sessionid']
    csrftoken = cookies['csrftoken']
    # connect to friends
    data = {'receiver' : 2}
    r = requests.post(api_url + 'link/connect/',
                      data = json.dumps(data),
                      headers = {'content-type': 'application/json',
                                 'X-CSRFToken' : csrftoken},
                      cookies=cookies)
    # create events
    dt = datetime.datetime.now(pytz.UTC) + datetime.timedelta(1)
    dt = dt.strftime("%Y-%m-%dT%H:%M:%SZ%Z")
    t = random.choice(types)
    p = "%f, %f"%(random.random() * 100, random.random() * 100)
    data = {'start' : dt, 'type' : t['resource_uri'], 'position' : p}
    r = requests.post(api_url + 'event/',
                      data = json.dumps(data),
                      headers = {'content-type': 'application/json',
                                 'X-CSRFToken' : csrftoken},
                      cookies=cookies)


    # get events
    #r = requests.get(api_url + 'event/',
                      #cookies=cookies)
