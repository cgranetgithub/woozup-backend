from tastypie.http import HttpUnauthorized, HttpForbidden, HttpBadRequest
from django.http import HttpResponse
from event.models import Event
from event import push

def run_checks(request, event_id):
    if request.user and request.user.is_authenticated():
        profile = request.user.userprofile
        try:
            event = Event.objects.get(id=event_id)
            if profile != event.owner:
                return (True, (profile, event))
            else:
                return (False, (request, {u'reason': u'This is your own event'},
                                HttpForbidden))
        except Event.DoesNotExist:
            return (False, (request, {u'reason': u'Event not found'},
                            HttpBadRequest))
        except:
            return (False, (request, {u'reason': u'Unexpected'},
                            HttpBadRequest))
    else:
        return (False, (request, {u'reason': u"You are not authenticated"},
                        HttpUnauthorized))

def join(request, event_id):
    (good, result) = run_checks(request, event_id)
    if good:
        (profile, event) = result
        if profile not in event.participants.all():
            event.participants.add(profile)
            event.save()
            push.participant_joined(request, profile, event)
            return (request, {}, HttpResponse)
        else:
            return (request, {u'reason': u'You are already a participant'},
                    HttpForbidden)
    else:
        return result

def leave(request, event_id):
    (good, result) = run_checks(request, event_id)
    if good:
        (profile, event) = result
        if profile in event.participants.all():
            event.participants.remove(profile)
            event.save()
            push.participant_left(request, profile, event)
            return (request, {}, HttpResponse)
        else:
            return (request, {u'reason': u'You are not a participant'},
                    HttpForbidden)
    else:
        return result

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
            #myfriends = get_user_friends(profile)
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
