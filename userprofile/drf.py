from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
from userprofile.models import Profile, Position

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class NewFriendsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        #fields = ('first_name', 'last_name')

class NewFriendsViewSet(viewsets.ModelViewSet):
    #queryset = Profile.objects.all()
    serializer_class = NewFriendsSerializer
    def get_queryset(self):
        #user = self.request.user
        #return Purchase.objects.filter(purchaser=user)
        profile = self.request.user.profile
        links = profile.link_as_sender.filter(sender_status='NEW')
        receivers = Profile.objects.filter(
                                    user_id__in=links.values('receiver_id'))
        links = profile.link_as_receiver.filter(receiver_status='NEW')
        senders = Profile.objects.filter(
                                    user_id__in=links.values('sender_id'))
        return senders | receivers

