from django.contrib import admin
from .models import Link, Invite

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    pass

@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_filter = ('sender', 'status')
    ordering = ['sender', 'name']
