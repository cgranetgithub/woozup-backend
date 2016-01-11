import json
from django.contrib.auth.models import User

def register(c, email):
    data = {'email':email, 'password':'pwdpwd'}
    res = c.post('/api/v1/auth/register_by_email/', data = json.dumps(data),
                                            content_type='application/json')
    return User.objects.get(id=json.loads(res.content)['userid'])

def login(c, login):
    data = {'login':login, 'password':'pwdpwd'}
    res = c.post('/api/v1/auth/login_by_email/', data = json.dumps(data),
                                            content_type='application/json')
    content = json.loads(res.content)
    return (content['api_key'], content['username'])
