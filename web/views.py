#from django.http import JsonResponse
#from django.contrib.auth import login
#from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
#from service.notification import send_mail
from django.shortcuts import render_to_response, redirect, render
from django.db.models import Count
from event.models import Event
from event.push import get_event_context

def home(request):
    return render_to_response('home.html')

#@login_required(login_url='/accounts/login/')
#def emails(request):
    #if request.POST:
        #event = Event.objects.last()
        #emails = [request.user.email]
        #context = get_event_context(event)
        #context["user"] = request.user.userprofile
        #if '_signup_confirmation' in request.POST:
             #pass
        #elif '_password_reset_key' in request.POST:
             #pass
        #elif '_event_canceled' in request.POST:
            #template_prefix = "event/email/event_canceled"
            #send_mail(template_prefix, emails, context)
        #elif '_event_created' in request.POST:
            #template_prefix = "event/email/event_created"
            #send_mail(template_prefix, emails, context)
        #elif '_participant_joined' in request.POST:
            #template_prefix = "event/email/participant_joined"
            #send_mail(template_prefix, emails, context)
        #elif '_participant_left' in request.POST:
            #template_prefix = "event/email/participant_left"
            #send_mail(template_prefix, emails, context)
        #elif '_request_connection' in request.POST:
            #template_prefix = "link/email/request"
            #send_mail(template_prefix, emails, context)
        #elif '_accept_connection' in request.POST:
            #template_prefix = "link/email/accept"
            #send_mail(template_prefix, emails, context)
        #elif '_personal_invite' in request.POST:
            #template_prefix = "link/email/personal_invite"
            #send_mail(template_prefix, emails, context)
        #elif '_generic_invite' in request.POST:
            #template_prefix = "link/email/generic_invite"
            #del context['user']
            #send_mail(template_prefix, emails, context)
    #return render(request, 'web/emails.html')

def users(request):
    data = User.objects.extra(
                # get specific dates (not hours for example)
                {'date':"date(date_joined)"}
                # get a values list of only "joined" defined earlier
                ).values('date'
                ).order_by('-date'
                # annotate each day by Count of Guidoism objects
                ).annotate(number=Count('id'))
    return render(request, 'web/users.html',
                  {'data': data, 'total': User.objects.count()})

def events(request):
    return render_to_response('home.html')

def profile(request):
    return render(request, 'web/profile.html', {'user': request.user})

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

#def social_logout(request):
    #auth_logout(request)
    #return redirect('/')
