from django.contrib import admin
from .models import Link, Contact

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    pass

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_filter = ('sender', 'status')
    ordering = ['sender', 'name']
