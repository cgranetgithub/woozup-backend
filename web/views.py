 #-*- coding: utf-8 -*-

import datetime
from django.utils import timezone
from django.shortcuts import render_to_response, redirect, render
from django.db.models import Count
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django import forms
from django.contrib.admin.views.decorators import staff_member_required

#from django.http import JsonResponse
#from django.contrib.auth import login
#from django.contrib.auth import logout as auth_logout
#from django.contrib.auth.decorators import login_required
#from service.notification import send_mail
from event.models import Event
from link.models import Link, Contact
from journal.models import Record
#from event.push import get_event_context
from service.notification import enqueue_send_notification

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

@staff_member_required
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

@staff_member_required
def records(request):
    data = Record.objects.all()
    return render(request, 'web/records.html',
                  {'data': data})

def events(request):
    return render_to_response('home.html')

def profile(request):
    return render(request, 'web/profile.html', {'user': request.user})

@staff_member_required
def stats(request):
    today = timezone.now()
    week = datetime.timedelta(days=7)
    users = User.objects.count()
    users_new = User.objects.filter(last_login__gte=today-week).count()
    users_active = User.objects.filter(date_joined__gte=today-week).count()
    links_total = Link.objects.count()
    links_new = Link.objects.filter(sender_status='NEW', receiver_status='NEW'
                                    ).count()
    links_pen = Link.objects.filter(Q(sender_status='PEN')
                                    | Q(receiver_status='PEN')).count()
    links_acc = Link.objects.filter(sender_status='ACC', receiver_status='ACC'
                                    ).count()
    contacts_total = Contact.objects.count()
    contacts_new = Contact.objects.filter(status='NEW').count()
    contacts_pen = Contact.objects.filter(status='PEN').count()
    contacts_acc = Contact.objects.filter(status='CLO').count()
    events_total     = Event.objects.count()
    events_last_week = Event.objects.filter(created_at__gte=today-week).count()
    events_coming    = Event.objects.filter(start__gte=today).count()
    return render(request, 'web/stats.html',
                  {'users':users, 'users_new':users_new,
                   'users_active':users_active,
                   'links_total':links_total,
                   'links_new':links_new, 'links_pen':links_pen,
                   'links_acc':links_acc, 'links_acc':links_acc,
                   'contacts_total':contacts_total,
                   'contacts_new':contacts_new,
                   'contacts_pen':contacts_pen,
                   'contacts_acc':contacts_acc,
                   'events_total':events_total,
                   'events_last_week':events_last_week,
                   'events_coming':events_coming, })

class GlobalNotificationForm(forms.Form):
    message = forms.CharField(label=u"""Notification à tous les users""",
                              widget=forms.Textarea)

@staff_member_required
def notif(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = GlobalNotificationForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            data = {u"title": u"News de Woozup",
                    u"message": form.cleaned_data["message"]}
            recepients = User.objects.all()
            #recepients = User.objects.filter(first_name__icontains="charles")
            enqueue_send_notification(recepients, data)
            # redirect to a new URL:
            return HttpResponse('Envoyé à %s'%recepients.count())
    # if a GET (or any other method) we'll create a blank form
    else:
        form = GlobalNotificationForm()
    return render(request, 'web/notif.html', {'form': form})

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
