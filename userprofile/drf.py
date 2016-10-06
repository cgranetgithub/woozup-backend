from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
from userprofile.models import UserProfile, UserPosition

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class NewFriendsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        #fields = ('first_name', 'last_name')

class NewFriendsViewSet(viewsets.ModelViewSet):
    #queryset = UserProfile.objects.all()
    serializer_class = NewFriendsSerializer
    def get_queryset(self):
        #user = self.request.user
        #return Purchase.objects.filter(purchaser=user)
        userprofile = self.request.user.userprofile
        links = userprofile.link_as_sender.filter(sender_status='NEW')
        receivers = UserProfile.objects.filter(
                                    user_id__in=links.values('receiver_id'))
        links = userprofile.link_as_receiver.filter(receiver_status='NEW')
        senders = UserProfile.objects.filter(
                                    user_id__in=links.values('sender_id'))
        return senders | receivers

