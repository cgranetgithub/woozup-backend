from .models import Link

def get_link(user1, user2):
    try:
        return Link.objects.get(sender=user1, receiver=user2)
    except Link.DoesNotExist:
        try:
            return Link.objects.get(sender=user2, receiver=user1)
        except Link.DoesNotExist:
            return None

def accept_link(user_who_accept, user2):
    try:
        l = Link.objects.get(sender=user_who_accept, receiver=user2)
        l.sender_status = 'ACC'
        if l.receiver_status not in ['ACC', 'BLO']:
            l.receiver_status = 'PEN'
        l.save()
    except Link.DoesNotExist:
        (l, created) = Link.objects.get_or_create(sender=user2,
                                                  receiver=user_who_accept)
        l.receiver_status = 'ACC'
        if l.sender_status not in ['ACC', 'BLO']:
            l.sender_status = 'PEN'
        l.save()
