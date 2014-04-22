 #!/usr/bin/python
 # -*- coding: utf-8 -*-

import json, requests, datetime
from requests.auth import HTTPBasicAuth

def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

types      = json.loads(requests.get('http://127.0.0.1:8000/api/v1/type/'
                                     ).content)

# ID : username (password is the username)
users = {1 : "john" , 2 : "jack", 3 : "dick"   , 4 : "alex",
         5 : "chuck", 6 : "mike", 7 : "charles", 8 : "michael"}

#for (i, u) in users.iteritems():
    #for t in types['objects']:
        #dt = datetime.datetime.now()
        #data = {'start' : dt, 'type' : t['resource_uri'], 'position' : "", 'owner' : 1}
        #r = requests.post('http://127.0.0.1:8000/api/v1/event/',
                      #data = json.dumps(data, default=date_handler),
                      #headers = {'content-type': 'application/json'},
                      #auth=HTTPBasicAuth(u, u))

#create user
#r = requests.post('http://127.0.0.1:8000/api/v1/auth/register/', 
                  #data=json.dumps({'username':'titi8', 'password':'titi8'}), 
                  #headers = {'content-type': 'application/json'})

#login
#r = requests.post('http://127.0.0.1:8000/api/v1/auth/login/', 
                  #data=json.dumps({'username':'fr@fr.fr', 'password':'fr'}), 
                  #headers = {'content-type': 'application/json'})
#print r, dir(r)
#print r.cookies

r = requests.get('http://127.0.0.1:8000/api/v1/event/',
                cookies={'sessionid':'jidwhs007v27om5kq8cagk2zpq2esvd9'})
print r.request, dir(r.request)
print r.request.headers

r = requests.get('http://127.0.0.1:8000/api/v1/event/',
                  headers = {'Cookie': 'sessionid=jidwhs007v27om5kq8cagk2zpq2esvd9'})
print r.request, dir(r.request)
print r.request.headers, r.request.body
