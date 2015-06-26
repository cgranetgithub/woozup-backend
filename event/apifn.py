from tastypie.http import HttpUnauthorized, HttpForbidden, HttpBadRequest
from django.http import HttpResponse
from event.models import Event
from event import push

def join(request):
    if request.user and request.user.is_authenticated():
        try:
            event = Event.objects.get(id=kwargs['event_id'])
            if request.user is not event.owner.user:
                #participants = [ i['id'] for i in event.participants.values() ]
                #if request.user.id not in participants:
                if request.user.userprofile not in event.participants.all():
                    event.participants.add(request.user.userprofile)
                    event.save()
                    push.participant_joined(request.user.userprofile,
                                            event)
                    return (request, {}, HttpResponse)
                else:
                    return (request, {u'reason': u'You are already a participant'},
                            HttpForbidden)
            else:
                return (request, {u'reason': u'You cannot join your own event'},
                        HttpForbidden)
        except Event.DoesNotExist:
            return (request, {u'reason': u'Event not found'}, HttpForbidden)
        except:
            return (request, {u'reason': u'Unexpected'}, HttpForbidden)
    else:
        return (request, {u'reason': u"You are not authenticated"},
                HttpUnauthorized)

def leave(request):
    if request.user and request.user.is_authenticated():
        try:
            event = Event.objects.get(id=kwargs['event_id'])
            if request.user is not event.owner.user:
                #participants = [ i['id'] for i in event.participants.values() ]
                #if request.user.id in participants:
                if request.user.userprofile in event.participants.all():
                    event.participants.remove(request.user.userprofile)
                    event.save()
                    push.participant_left(request.user.userprofile, event)
                    return (request, {}, HttpResponse)
                else:
                    return (request, {u'reason': u'You are already a participant'},
                            HttpForbidden)
            else:
                return (request, {u'reason': u'You cannot join your own event'},
                        HttpForbidden)
        except Event.DoesNotExist:
            return (request, {u'reason': u'Event not found'}, HttpForbidden)
        except:
            return (request, {u'reason': u'Unexpected'}, HttpForbidden)
    else:
        return (request, {u'reason': u"You are not authenticated"},
                HttpUnauthorized)

#def attending(self, request, **kwargs):
    #""" Get list of events the user attends."""
    #self.method_check(request, allowed=['get'])
    #self.is_authenticated(request)
    #self.throttle_check(request)
    #self.log_throttled_access(request)
    #if request.user and request.user.is_authenticated():
        #try:
            #events = Event.objects.filter(
                                        #Q( owner__user=request.user )
                                    #| Q( participants__user=request.user )
                                    #).distinct()
            #objects = []
            #for result in events:
                #bundle = self.build_bundle(obj=result, request=request)
                #bundle = self.full_dehydrate(bundle)
                #objects.append(bundle)
            #object_list = { 'objects': objects, }
            #return self.create_response(request, object_list)
        #except Event.DoesNotExist:
            #return self.create_response(request,
                                        #{u'reason': u'Event not found'},
                                        #HttpForbidden)
        #except:
            #return self.create_response(request,
                                        #{u'reason': u'Unexpected'},
                                        #HttpForbidden)
    #else:
        #return self.create_response(
                                #request,
                                #{u'reason': u"You are not authenticated"},
                                #HttpUnauthorized )

#def not_attending(self, request, **kwargs):
    #""" Get list of events the user does not attend."""
    #self.method_check(request, allowed=['get'])
    #self.is_authenticated(request)
    #self.throttle_check(request)
    #self.log_throttled_access(request)
    #if request.user and request.user.is_authenticated():
        #try:
            #myfriends = get_user_friends(request.user.userprofile)
            #events = Event.objects.filter(owner__in=myfriends
                                    #).exclude(
                                        #Q( owner__user=request.user )
                                    #| Q(participants__user=request.user)
                                    #).distinct()
            #objects = []
            #for result in events:
                #bundle = self.build_bundle(obj=result, request=request)
                #bundle = self.full_dehydrate(bundle)
                #objects.append(bundle)
            #object_list = { 'objects': objects, }
            #return self.create_response(request, object_list)
        #except Event.DoesNotExist:
            #return self.create_response(request,
                                        #{u'reason': u'Event not found'},
                                        #HttpForbidden)
        #except:
            #return self.create_response(request,
                                        #{u'reason': u'Unexpected'},
                                        #HttpForbidden)
    #else:
        #return self.create_response(
                                #request,
                                #{u'reason': u"You are not authenticated"},
                                #HttpUnauthorized )
