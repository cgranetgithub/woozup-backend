#from django.http import JsonResponse
#from django.contrib.auth import login
from django.shortcuts import render_to_response, redirect, render
#from django.contrib.auth import logout as auth_logout
#from django.contrib.auth.decorators import login_required

#def register_by_access_token(request, backend):
    #token = request.GET.get('access_token')
    #user = request.backend.do_auth(token)
    #if user:
        #login(request, user)
        #return JsonResponse({'api_key' : user.api_key.key,
                             #'userid'  : request.user.id,
                             #'username': user.username})
    #else:
        #return JsonResponse({'error':'bad user'})

#def social_login(request):
    #return render(request, 'login.html')

#@login_required(login_url='/')
def home(request):
    return render_to_response('home.html')

#def social_logout(request):
    #auth_logout(request)
    #return redirect('/')
